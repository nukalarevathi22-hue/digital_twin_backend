# app/shared_state.py
from datetime import datetime
from typing import Dict, Any, List
from fastapi import WebSocket
import asyncio

# Global simulation states dictionary
simulation_states: Dict[str, Dict[str, Any]] = {}

# Patient metrics dictionary  
patient_metrics: Dict[str, Dict[str, Any]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append(websocket)
        print(f"WebSocket connected for patient {patient_id}. Total connections: {len(self.active_connections[patient_id])}")
    
    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            self.active_connections[patient_id].remove(websocket)
            if not self.active_connections[patient_id]:
                del self.active_connections[patient_id]
        print(f"WebSocket disconnected for patient {patient_id}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_patient(self, message: Dict[str, Any], patient_id: str):
        if patient_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending to WebSocket: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection, patient_id)
    
    async def broadcast_simulation_update(self, patient_id: str, simulation_id: str, status: str, progress: int, message: str):
        update_message = {
            "type": "simulation_update",
            "patient_id": patient_id,
            "simulation_id": simulation_id,
            "status": status,
            "progress": progress,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_patient(update_message, patient_id)
    
    async def broadcast_metrics_update(self, patient_id: str, metrics: Dict[str, Any]):
        update_message = {
            "type": "metrics_update",
            "patient_id": patient_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        await self.broadcast_to_patient(update_message, patient_id)

# Create global manager instance
manager = ConnectionManager()

def initialize_simulation_state(simulation_id: str, patient_id: str, simulation_type: str = "biomechanical"):
    """Initialize a new simulation state"""
    simulation_states[simulation_id] = {
        "patient_id": patient_id,
        "status": "initializing",
        "progress": 0,
        "message": "Starting simulation...",
        "timestamp": datetime.now().isoformat(),
        "simulation_type": simulation_type,
        "results": None
    }
    return simulation_states[simulation_id]

def update_simulation_state(simulation_id: str, **updates):
    """Update simulation state"""
    if simulation_id in simulation_states:
        simulation_states[simulation_id].update(updates)
        simulation_states[simulation_id]["timestamp"] = datetime.now().isoformat()
    return simulation_states.get(simulation_id)

def get_simulation_state(simulation_id: str):
    """Get simulation state"""
    return simulation_states.get(simulation_id)

def delete_simulation_state(simulation_id: str):
    """Remove simulation state"""
    if simulation_id in simulation_states:
        del simulation_states[simulation_id]