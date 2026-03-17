# app/routes/digital_twin.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models import APIResponse, DigitalTwinResponse

router = APIRouter()

# Sample digital twin data for demonstration
digital_twins_db = {}

@router.get("/patient/{patient_id}/digital-twin", response_model=APIResponse)
async def get_digital_twin(patient_id: str):
    """Get digital twin data for a patient"""
    try:
        if patient_id not in digital_twins_db:
            # Create a sample digital twin if it doesn't exist
            digital_twins_db[patient_id] = DigitalTwinResponse(
                patient_id=patient_id,
                status="active",
                metrics={
                    "ejection_fraction": 55.0,
                    "stroke_volume": 70.0,
                    "cardiac_output": 5.0,
                    "heart_rate": 72
                },
                alerts=["System initialized"],
                last_updated=datetime.now(),
                message="Digital twin is active and monitoring"
            ).dict()
        
        return APIResponse(
            status="success",
            message="Digital twin data retrieved successfully",
            data=digital_twins_db[patient_id],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{patient_id}/digital-twin/update", response_model=APIResponse)
async def update_digital_twin(patient_id: str, update_data: dict):
    """Update digital twin data"""
    try:
        if patient_id not in digital_twins_db:
            digital_twins_db[patient_id] = {}
        
        digital_twins_db[patient_id].update(update_data)
        digital_twins_db[patient_id]["last_updated"] = datetime.now()
        
        return APIResponse(
            status="success",
            message="Digital twin updated successfully",
            data=digital_twins_db[patient_id],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))