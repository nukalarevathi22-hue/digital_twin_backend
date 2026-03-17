# app/routes/febio_simulations.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid

# Now we can import from models since we've fixed the structure
from app.models import FEBioSimulationRequest
from app.services.febio_runner import FEBioRunner
from app.shared_state import simulation_states, initialize_simulation_state, update_simulation_state

router = APIRouter()
febio_runner = FEBioRunner()

@router.post("/patient/{patient_id}/run-simulation")
async def run_simulation(
    patient_id: str,
    request: FEBioSimulationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new FEBio simulation for a patient
    """
    simulation_id = str(uuid.uuid4())
    
    # Initialize simulation state
    initialize_simulation_state(
        simulation_id, 
        patient_id, 
        request.simulation_type
    )
    
    # Run simulation in background
    background_tasks.add_task(
        run_simulation_background,
        simulation_id,
        request.dict()
    )
    
    return {
        "status": "success",
        "simulation_id": simulation_id,
        "message": "Simulation started successfully"
    }

async def run_simulation_background(simulation_id: str, config: Dict[str, Any]):
    """Run simulation in background"""
    try:
        await febio_runner.run_simulation(simulation_id, config)
    except Exception as e:
        update_simulation_state(
            simulation_id,
            status="failed",
            message=f"Simulation error: {str(e)}"
        )

@router.get("/simulation/{simulation_id}/status")
async def get_simulation_status(simulation_id: str):
    """
    Get current status of a simulation
    """
    if simulation_id not in simulation_states:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulation_states[simulation_id]

@router.get("/patient/{patient_id}/simulations")
async def get_patient_simulations(patient_id: str):
    """
    Get all simulations for a patient
    """
    patient_simulations = {
        sim_id: data for sim_id, data in simulation_states.items()
        if data.get("patient_id") == patient_id
    }
    
    return {
        "patient_id": patient_id,
        "simulations": patient_simulations
    }