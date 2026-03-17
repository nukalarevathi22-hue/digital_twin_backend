
from fastapi import APIRouter
from datetime import datetime
from app.shared_state import patient_metrics

router = APIRouter()

@router.post("/patient/{patient_id}/vitals")
async def update_vitals(patient_id: str, data: dict):
    patient_metrics[patient_id] = {
        "heart_rate": data.get("heart_rate"),
        "blood_pressure": data.get("blood_pressure"),
        "spo2": data.get("spo2"),
        "ecg": data.get("ecg"),
        "timestamp": datetime.now().isoformat()
    }
    return {"status": "ok", "message": f"Vitals updated for {patient_id}"}
