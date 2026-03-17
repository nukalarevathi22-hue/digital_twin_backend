# app/routes/alerts.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models import APIResponse, AlertData, DigitalTwinResponse

router = APIRouter()

# Sample alerts data for demonstration
alerts_db = {}

@router.get("/patient/{patient_id}/alerts", response_model=APIResponse)
async def get_patient_alerts(patient_id: str):
    """Get alerts for a specific patient"""
    try:
        patient_alerts = alerts_db.get(patient_id, [])
        
        return APIResponse(
            status="success",
            message="Alerts retrieved successfully",
            data={"alerts": patient_alerts},
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{patient_id}/alerts", response_model=APIResponse)
async def create_alert(patient_id: str, alert: AlertData):
    """Create a new alert for a patient"""
    try:
        if patient_id not in alerts_db:
            alerts_db[patient_id] = []
        
        alert_data = alert.dict()
        alert_data["timestamp"] = datetime.now()
        alerts_db[patient_id].append(alert_data)
        
        return APIResponse(
            status="success",
            message="Alert created successfully",
            data={"alert": alert_data},
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts", response_model=APIResponse)
async def get_all_alerts():
    """Get all alerts across all patients"""
    return APIResponse(
        status="success",
        message="All alerts retrieved successfully",
        data={"alerts": alerts_db},
        timestamp=datetime.now()
    )