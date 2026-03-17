# app/routes/realtime_processor.py
import datetime
from fastapi import APIRouter, BackgroundTasks
import asyncio

router = APIRouter()

@router.post("/patient/{patient_id}/process-realtime-data")
async def process_realtime_data(
    patient_id: str, 
    vital_data: dict, 
    background_tasks: BackgroundTasks
):
    """Process real-time patient data and trigger simulations"""
    
    # Store real-time data
    from app.shared_state import patient_metrics
    patient_metrics[patient_id] = {
        **patient_metrics.get(patient_id, {}),
        **vital_data,
        "last_update": datetime.now().isoformat()
    }
    
    # Trigger simulation if significant changes detected
    if should_trigger_simulation(patient_id, vital_data):
        background_tasks.add_task(
            trigger_febio_simulation, 
            patient_id, 
            vital_data
        )
    
    return {
        "status": "processed",
        "simulation_triggered": should_trigger_simulation(patient_id, vital_data),
        "timestamp": datetime.now().isoformat()
    }

def should_trigger_simulation(patient_id: str, new_data: dict) -> bool:
    """Determine if new data warrants a simulation"""
    from app.shared_state import patient_metrics
    
    previous_data = patient_metrics.get(patient_id, {})
    
    # Check for significant changes in key parameters
    significant_changes = False
    
    if 'heart_rate' in new_data and 'heart_rate' in previous_data:
        hr_change = abs(new_data['heart_rate'] - previous_data['heart_rate'])
        if hr_change > 10:  # 10 BPM threshold
            significant_changes = True
    
    if 'systolic_bp' in new_data and 'systolic_bp' in previous_data:
        bp_change = abs(new_data['systolic_bp'] - previous_data['systolic_bp'])
        if bp_change > 15:  # 15 mmHg threshold
            significant_changes = True
    
    return significant_changes

async def trigger_febio_simulation(patient_id: str, vital_data: dict):
    """Trigger FEBio simulation with new data"""
    from app.routes.realtime_febio import febio_manager
    await febio_manager.run_realtime_simulation(patient_id, vital_data)