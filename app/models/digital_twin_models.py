# app/models/digital_twin_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DigitalTwinResponse(BaseModel):
    patient_id: str
    status: str
    simulation_data: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, float]] = None
    alerts: Optional[List[str]] = None
    last_updated: datetime
    message: Optional[str] = None

class AlertData(BaseModel):
    patient_id: str
    alert_type: str  # "critical", "warning", "info"
    message: str
    severity: str
    timestamp: datetime
    resolved: bool = False

class SimulationData(BaseModel):
    simulation_id: str
    patient_id: str
    type: str
    status: str
    parameters: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None