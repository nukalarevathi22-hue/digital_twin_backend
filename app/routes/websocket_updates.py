# app/routes/websocket_updates.py
# app/routes/websocket_updates.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

from app.shared_state import manager, simulation_states, patient_metrics
router = APIRouter()

@router.websocket("/patient/{patient_id}/digital-twin")
async def websocket_digital_twin(websocket: WebSocket, patient_id: str):
    """
    WebSocket endpoint for real-time digital twin updates
    """
    await manager.connect(websocket, patient_id)
    try:
        # Send initial state when client connects
        initial_data = {
            "type": "connection_established",
            "patient_id": patient_id,
            "message": "Connected to digital twin updates",
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(initial_data), websocket)
        
        # Send current simulation states for this patient
        patient_simulations = {
            sim_id: data for sim_id, data in simulation_states.items()
            if data.get("patient_id") == patient_id
        }
        
        if patient_simulations:
            simulations_data = {
                "type": "initial_simulations",
                "patient_id": patient_id,
                "simulations": patient_simulations
            }
            await manager.send_personal_message(json.dumps(simulations_data), websocket)
        
        # Send current patient metrics
        if patient_id in patient_metrics:
            metrics_data = {
                "type": "initial_metrics",
                "patient_id": patient_id,
                "metrics": patient_metrics[patient_id]
            }
            await manager.send_personal_message(json.dumps(metrics_data), websocket)
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from client if needed
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}),
                        websocket
                    )
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, patient_id)
    except Exception as e:
        print(f"WebSocket error for patient {patient_id}: {e}")
        manager.disconnect(websocket, patient_id)

@router.websocket("/simulation/{simulation_id}")
async def websocket_simulation_updates(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint for specific simulation updates
    """
    if simulation_id not in simulation_states:
        await websocket.close(code=1008, reason="Simulation not found")
        return
    
    patient_id = simulation_states[simulation_id].get("patient_id")
    await manager.connect(websocket, patient_id)
    
    try:
        # Send current simulation state
        current_state = simulation_states[simulation_id]
        initial_data = {
            "type": "simulation_state",
            "simulation_id": simulation_id,
            "patient_id": patient_id,
            "state": current_state
        }
        await manager.send_personal_message(json.dumps(initial_data), websocket)
        
        # Keep connection alive
        while True:
            await websocket.receive_text()  # Just keep connection open
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, patient_id)
    except Exception as e:
        print(f"Simulation WebSocket error: {e}")
        manager.disconnect(websocket, patient_id)