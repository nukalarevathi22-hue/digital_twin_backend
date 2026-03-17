# app/models/simulation_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class FEBioSimulationRequest(BaseModel):
    patient_id: str
    simulation_type: str = "biomechanical"  # or "fluid", "fsi"
    mesh_file: str
    material_properties: Dict[str, Any]
    boundary_conditions: Dict[str, Any]
    solver_settings: Dict[str, Any] = {
        "time_steps": 100,
        "step_size": 0.01,
        "solver": "BFGS"
    }

class SimulationStatus(BaseModel):
    simulation_id: str
    patient_id: str
    status: str  # "running", "completed", "failed"
    progress: int
    message: str
    created_at: datetime
    updated_at: datetime

class FEBioResults(BaseModel):
    simulation_id: str
    patient_id: str
    vertices: List[List[float]]
    faces: List[List[int]]
    displacements: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    visualization_data: Dict[str, Any]