# app/realtime_manager.py
from fastapi import WebSocket
from datetime import datetime
import asyncio
import json
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.patient_data: Dict[str, Dict] = {}  # In-memory storage
    
    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append(websocket)
        print(f"✅ Patient {patient_id} connected. Total connections: {len(self.active_connections[patient_id])}")
    
    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            self.active_connections[patient_id].remove(websocket)
            if not self.active_connections[patient_id]:
                del self.active_connections[patient_id]
        print(f"❌ Patient {patient_id} disconnected.")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    async def broadcast_to_patient(self, patient_id: str, message: dict):
        if patient_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"❌ WebSocket error for patient {patient_id}: {e}")
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                self.disconnect(connection, patient_id)
    
    def store_patient_data(self, patient_id: str, data: dict):
        """Store patient data in memory"""
        if patient_id not in self.patient_data:
            self.patient_data[patient_id] = {}
        self.patient_data[patient_id].update(data)
        self.patient_data[patient_id]['last_update'] = datetime.now().isoformat()
    
    def get_patient_data(self, patient_id: str) -> dict:
        """Get patient data from memory"""
        return self.patient_data.get(patient_id, {})

# Global instance
manager = ConnectionManager()