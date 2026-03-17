# app/routes/simulations.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models import APIResponse, SimulationData

router = APIRouter()

# Sample simulations data for demonstration
simulations_db = {}

@router.get("/patient/{patient_id}/simulations", response_model=APIResponse)
async def get_patient_simulations(patient_id: str):
    """Get all simulations for a patient"""
    try:
        patient_simulations = simulations_db.get(patient_id, [])
        
        return APIResponse(
            status="success",
            message="Simulations retrieved successfully",
            data={"simulations": patient_simulations},
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{patient_id}/simulations", response_model=APIResponse)
async def create_simulation(patient_id: str, simulation: SimulationData):
    """Create a new simulation for a patient"""
    try:
        if patient_id not in simulations_db:
            simulations_db[patient_id] = []
        
        simulation_data = simulation.dict()
        simulation_data["created_at"] = datetime.now()
        simulations_db[patient_id].append(simulation_data)
        
        return APIResponse(
            status="success",
            message="Simulation created successfully",
            data={"simulation": simulation_data},
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))