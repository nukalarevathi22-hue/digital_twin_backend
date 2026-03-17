# app/routes/febio_visualization.py
import os
import json
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from datetime import datetime
import asyncio

router = APIRouter()

class FEBioVisualizationManager:
    def __init__(self):
        self.active_visualizations = {}
    
    async def get_simulation_visualization(self, patient_id: str, xplt_file_path: str):
        """Get visualization data for FEBio simulation"""
        try:
            from app.utils.xplt_parser import parse_xplt_file
            
            # Parse the XPLT file
            visualization_data = parse_xplt_file(xplt_file_path)
            
            # Save as JSON for frontend
            output_json = f"dashboard/public/{patient_id}_febio_viz.json"
            os.makedirs(os.path.dirname(output_json), exist_ok=True)
            
            with open(output_json, 'w') as f:
                json.dump(visualization_data, f, indent=2)
            
            return {
                "status": "success",
                "visualization_data": visualization_data,
                "json_path": f"/public/{patient_id}_febio_viz.json"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Visualization error: {str(e)}")

febio_viz_manager = FEBioVisualizationManager()

@router.get("/patient/{patient_id}/febio-visualization")
async def get_febio_visualization(patient_id: str):
    """Get FEBio visualization data for patient"""
    try:
        # Find latest XPLT file
        simulation_dir = f"data/simulations/{patient_id}"
        if not os.path.exists(simulation_dir):
            raise HTTPException(status_code=404, detail="No simulation data found")
        
        xplt_files = [f for f in os.listdir(simulation_dir) if f.endswith('.xplt')]
        if not xplt_files:
            raise HTTPException(status_code=404, detail="No XPLT files found")
        
        # Get most recent file
        latest_file = max(xplt_files, key=lambda f: os.path.getctime(os.path.join(simulation_dir, f)))
        xplt_path = os.path.join(simulation_dir, latest_file)
        
        # Generate visualization data
        result = await febio_viz_manager.get_simulation_visualization(patient_id, xplt_path)
        
        return {
            **result,
            "patient_id": patient_id,
            "simulation_file": latest_file,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.websocket("/ws/patient/{patient_id}/visualization-updates")
async def visualization_websocket(websocket: WebSocket, patient_id: str):
    """WebSocket for real-time visualization updates"""
    await websocket.accept()
    try:
        while True:
            # Send periodic visualization updates
            data = await get_visualization_update(patient_id)
            await websocket.send_json(data)
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except WebSocketDisconnect:
        print(f"Visualization WebSocket disconnected for patient {patient_id}")

async def get_visualization_update(patient_id: str):
    """Get updated visualization data"""
    # This could monitor for new simulation results
    return {
        "type": "visualization_update",
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }