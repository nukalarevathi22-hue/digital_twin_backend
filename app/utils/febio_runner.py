# app/services/febio_runner.py
import subprocess
import os
import math
from typing import Dict, Any
import asyncio
from datetime import datetime

from app.shared_state import update_simulation_state, manager

class FEBioRunner:
    def __init__(self, febio_path: str = "febio2"):
        self.febio_path = febio_path
        self.results_dir = "simulation_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    async def run_simulation(self, simulation_id: str, febio_config: Dict[str, Any]):
        """
        Run FEBio simulation asynchronously
        """
        try:
            patient_id = febio_config.get("patient_id", "unknown")
            
            # Update status and notify via WebSocket
            update_simulation_state(
                simulation_id, 
                status="running", 
                progress=10, 
                message="Creating FEBio input file..."
            )
            await manager.broadcast_simulation_update(
                patient_id, simulation_id, "running", 10, "Creating FEBio input file..."
            )
            
            # Create FEBio input file
            feb_file = await self.create_febio_input(simulation_id, febio_config)
            
            # Run FEBio simulation
            update_simulation_state(
                simulation_id,
                progress=30,
                message="Running FEBio simulation..."
            )
            await manager.broadcast_simulation_update(
                patient_id, simulation_id, "running", 30, "Running FEBio simulation..."
            )
            
            result = await self.execute_febio(feb_file, simulation_id)
            
            # Parse results
            update_simulation_state(
                simulation_id,
                progress=80,
                message="Processing simulation results..."
            )
            await manager.broadcast_simulation_update(
                patient_id, simulation_id, "running", 80, "Processing simulation results..."
            )
            
            results = await self.parse_results(simulation_id)
            
            update_simulation_state(
                simulation_id,
                status="completed",
                progress=100,
                message="Simulation completed successfully",
                results=results
            )
            await manager.broadcast_simulation_update(
                patient_id, simulation_id, "completed", 100, "Simulation completed successfully"
            )
            
            return results
            
        except Exception as e:
            patient_id = febio_config.get("patient_id", "unknown")
            update_simulation_state(
                simulation_id,
                status="failed", 
                progress=0,
                message=f"Simulation failed: {str(e)}"
            )
            await manager.broadcast_simulation_update(
                patient_id, simulation_id, "failed", 0, f"Simulation failed: {str(e)}"
            )
            raise e
    
    async def create_febio_input(self, simulation_id: str, config: Dict[str, Any]) -> str:
        """
        Create FEBio .feb input file from configuration
        """
        feb_content = self.generate_febio_xml(config)
        feb_file = os.path.join(self.results_dir, f"{simulation_id}.feb")
        
        with open(feb_file, 'w') as f:
            f.write(feb_content)
        
        return feb_file
    
    def generate_febio_xml(self, config: Dict[str, Any]) -> str:
        """
        Generate FEBio XML input file
        """
        feb_xml = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="2.5">
    <Module type="solid"/>
    
    <Control>
        <time_steps>{config['solver_settings']['time_steps']}</time_steps>
        <step_size>{config['solver_settings']['step_size']}</step_size>
        <solver type="{config['solver_settings']['solver']}"/>
        <plot_level>PLOT_MUST_POINTS</plot_level>
        <plot_zero_state>1</plot_zero_state>
    </Control>
    
    <Material>
        <material id="1" name="cardiac_tissue" type="Mooney-Rivlin">
            <c1>0.05</c1>
            <c2>0.02</c2>
            <k>2.0</k>
        </material>
    </Material>
    
    <Output>
        <plotfile type="febio">
            <var type="displacement"/>
            <var type="stress"/>
            <var type="strain"/>
        </plotfile>
    </Output>
</febio_spec>"""
        return feb_xml
    
    async def execute_febio(self, feb_file: str, simulation_id: str):
        """
        Execute FEBio simulation
        """
        try:
            # For now, simulate FEBio execution since we might not have FEBio installed
            # In production, you would run the actual FEBio command
            await asyncio.sleep(2)  # Simulate computation time
            
            return {
                "success": True,
                "log_file": feb_file.replace('.feb', '.log'),
                "output_file": feb_file.replace('.feb', '.xplt')
            }
            
        except Exception as e:
            raise Exception(f"FEBio execution error: {str(e)}")
    
    async def parse_results(self, simulation_id: str) -> Dict[str, Any]:
        """
        Parse FEBio output files and prepare for visualization
        """
        # For now, return sample data structure
        return {
            "simulation_id": simulation_id,
            "vertices": self.generate_sample_vertices(),
            "faces": self.generate_sample_faces(),
            "displacements": self.generate_sample_displacements(),
            "metadata": {
                "time_steps": 50,
                "max_displacement": 0.15,
                "simulation_type": "biomechanical"
            }
        }
    
    def generate_sample_vertices(self):
        """Generate sample vertices"""
        vertices = []
        for i in range(100):
            theta = (i / 100) * 2 * math.pi
            vertices.append([
                math.cos(theta) * 2,
                math.sin(theta) * 2,
                (i / 100) * 3 - 1.5
            ])
        return vertices
    
    def generate_sample_faces(self):
        """Generate sample faces"""
        faces = []
        for i in range(98):
            faces.append([i, i+1, i+2])
        return faces
    
    def generate_sample_displacements(self):
        """Generate sample displacement data"""
        displacements = []
        for t in range(50):
            time_step = {
                "time": t * 0.01,
                "displacements": []
            }
            for i in range(100):
                displacement = [
                    math.sin(t * 0.1 + i * 0.1) * 0.1,
                    math.cos(t * 0.1 + i * 0.1) * 0.1,
                    math.sin(t * 0.2) * 0.05
                ]
                time_step["displacements"].append(displacement)
            displacements.append(time_step)
        return displacements