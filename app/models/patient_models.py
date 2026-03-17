# app/models/patient_models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    medical_history: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, str]] = None

class PatientData(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    medical_history: Dict[str, Any]
    contact_info: Dict[str, str]
    created_at: datetime
    updated_at: datetime

class MedicalImageUpload(BaseModel):
    patient_id: str
    image_type: str  # "mri", "ct", "echo"
    image_data: str  # base64 encoded or file path
    metadata: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime