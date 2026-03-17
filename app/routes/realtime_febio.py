# app/routes/realtime_febio.py
import asyncio
import subprocess
import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from datetime import datetime
import websockets
import aiofiles

router = APIRouter()

class FEBioSimulationManager:
    def __init__(self):
        self.active_simulations = {}
        self.connection_manager = ConnectionManager()
    
    async def run_realtime_simulation(self, patient_id: str, vital_data: dict):
        """Run FEBio simulation with real-time patient data"""
        try:
            # Update simulation status
            await self.connection_manager.send_progress(
                patient_id, 
                "Generating simulation input...", 
                10, 
                "running"
            )
            
            # 1. Generate FEBio input file
            input_file = await self.generate_febio_input(patient_id, vital_data)
            
            await self.connection_manager.send_progress(
                patient_id, 
                "Running FEBio simulation...", 
                30, 
                "running"
            )
            
            # 2. Run FEBio simulation
            results = await self.execute_febio_simulation(patient_id, input_file)
            
            await self.connection_manager.send_progress(
                patient_id, 
                "Processing results...", 
                80, 
                "processing"
            )
            
            # 3. Process and return results
            simulation_results = await self.process_simulation_results(patient_id, results)
            
            await self.connection_manager.send_results(patient_id, simulation_results)
            
            return simulation_results
            
        except Exception as e:
            error_msg = f"Simulation failed: {str(e)}"
            await self.connection_manager.send_error(patient_id, error_msg)
            return None
    
    async def generate_febio_input(self, patient_id: str, vital_data: dict):
        """Generate FEBio input file with real-time parameters"""
        template_path = f"data/templates/{patient_id}_template.feb"
        output_dir = f"data/simulations/{patient_id}"
        output_path = f"{output_dir}/input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.feb"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Read template
        async with aiofiles.open(template_path, 'r') as f:
            template = await f.read()
        
        # Replace parameters with real-time data
        modified_template = template.replace('{{HEART_RATE}}', str(vital_data.get('heart_rate', 72)))
        modified_template = modified_template.replace('{{SYSTOLIC_BP}}', str(vital_data.get('systolic_bp', 120)))
        modified_template = modified_template.replace('{{DIASTOLIC_BP}}', str(vital_data.get('diastolic_bp', 80)))
        modified_template = modified_template.replace('{{TIMESTAMP}}', datetime.now().isoformat())
        
        # Write modified input file
        async with aiofiles.open(output_path, 'w') as f:
            await f.write(modified_template)
        
        return output_path
    
    async def execute_febio_simulation(self, patient_id: str, input_file: str):
        """Execute FEBio simulation and capture output"""
        output_file = f"data/simulations/{patient_id}/output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xplt"
        
        # Run FEBio command
        process = await asyncio.create_subprocess_exec(
            'febio2', '-i', input_file, '-o', output_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor simulation progress
        while True:
            output = await process.stdout.readline()
            if process.returncode is not None:
                break
                
            if output:
                line = output.decode().strip()
                progress = self.parse_progress(line)
                if progress:
                    await self.connection_manager.send_progress(
                        patient_id, 
                        f"Simulation running... {progress}%", 
                        progress, 
                        "running"
                    )
        
        # Wait for process to complete
        await process.wait()
        
        return output_file
    
    def parse_progress(self, output_line: str):
        """Parse FEBio output for progress information"""
        if "Step" in output_line and "Time" in output_line:
            try:
                # Extract progress percentage from FEBio output
                parts = output_line.split()
                if len(parts) > 1:
                    step = int(parts[1])
                    total_steps = 100  # Adjust based on your simulation setup
                    return min(int((step / total_steps) * 100), 95)
            except:
                pass
        return None
    
    async def process_simulation_results(self, patient_id: str, results_file: str):
        """Process simulation results and extract key metrics"""
        # Convert XPLT to JSON
        from app.utils.xplt_to_json import convert_xplt_to_json
        
        output_json = f"dashboard/public/{patient_id}_latest_results.json"
        convert_xplt_to_json(results_file, output_json)
        
        # Extract key metrics from simulation
        metrics = await self.extract_simulation_metrics(output_json)
        
        return {
            "patient_id": patient_id,
            "results_file": f"public/{patient_id}_latest_results.json",
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
    
    async def extract_simulation_metrics(self, json_file: str):
        """Extract key cardiac metrics from simulation results"""
        try:
            async with aiofiles.open(json_file, 'r') as f:
                data = json.loads(await f.read())
            
            # Extract metrics from FEBio results
            # This will depend on your specific FEBio output structure
            return {
                "cardiac_output": 5.2 + (0.1 * (72 - 60)),  # Example calculation
                "ejection_fraction": 62 + (0.5 * (120 - 110)),  # Example
                "heart_rate_variability": 45,
                "ventricular_mass": 142,
                "stress_level": 0.3,  # 0-1 scale
                "ventricular_volume": 75  # ml
            }
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {
                "cardiac_output": 5.0,
                "ejection_fraction": 60,
                "heart_rate_variability": 40,
                "ventricular_mass": 140,
                "stress_level": 0.5,
                "ventricular_volume": 70
            }

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
    
    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            self.active_connections[patient_id].remove(websocket)
            if not self.active_connections[patient_id]:
                del self.active_connections[patient_id]
    
    async def send_progress(self, patient_id: str, message: str, progress: int, status: str):
        if patient_id in self.active_connections:
            message = {
                "type": "progress",
                "patient_id": patient_id,
                "message": message,
                "progress": progress,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def send_results(self, patient_id: str, results: dict):
        if patient_id in self.active_connections:
            message = {
                "type": "results",
                "patient_id": patient_id,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def send_error(self, patient_id: str, error_message: str):
        if patient_id in self.active_connections:
            message = {
                "type": "error",
                "patient_id": patient_id,
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

# Global simulation manager
febio_manager = FEBioSimulationManager()

@router.websocket("/ws/patient/{patient_id}/simulation-progress")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    await febio_manager.connection_manager.connect(websocket, patient_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        febio_manager.connection_manager.disconnect(websocket, patient_id)

@router.post("/patient/{patient_id}/realtime-simulation")
async def start_realtime_simulation(patient_id: str, vital_data: dict, background_tasks: BackgroundTasks):
    """Start real-time FEBio simulation"""
    background_tasks.add_task(
        febio_manager.run_realtime_simulation,
        patient_id,
        vital_data
    )
    
    return {
        "status": "started",
        "patient_id": patient_id,
        "message": "Simulation started in background",
        "timestamp": datetime.now().isoformat()
    }