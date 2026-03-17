from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Symptoms(str, Enum):
    FEELING_GOOD = "feeling_good"
    FATIGUE = "fatigue"
    SHORT_OF_BREATH = "short_of_breath"
    SHORT_OF_BREATH_REST = "short_of_breath_rest"
    SWELLING = "swelling"
    CHEST_PAIN = "chest_pain"
    DIZZINESS = "dizziness"

class ImageType(str, Enum):
    MRI = "mri"
    CT = "ct"
    ECHO = "echo"
    OTHER = "other"

class ProcessingStatus(str, Enum):
    UPLOADED = "uploaded"
    SEGMENTING = "segmenting"
    SEGMENTED = "segmented"
    MESHING = "meshing"
    MESHED = "meshed"
    SIMULATING = "simulating"
    COMPLETED = "completed"
    FAILED = "failed"

# Patient Data Models
class PatientData(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    timestamp: Optional[str] = None
    weight_kg: float = Field(..., ge=30, le=200, description="Weight in kilograms")
    heart_rate: int = Field(..., ge=30, le=200, description="Heart rate in BPM")
    steps: int = Field(..., ge=0, le=50000, description="Daily step count")
    symptoms: str
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=150)
    spo2: Optional[int] = Field(None, ge=70, le=100, description="Oxygen saturation %")

class PatientCreate(BaseModel):
    patient_id: str
    name: str
    age: int = Field(..., ge=0, le=120)
    gender: str
    baseline_weight: float
    baseline_ef: float = Field(..., ge=10, le=80, description="Baseline ejection fraction")
    medical_history: Optional[str] = None

class MedicalImageUpload(BaseModel):
    patient_id: str
    image_type: str
    acquisition_date: Optional[str] = None

class SimulationParameters(BaseModel):
    patient_id: str
    mesh_file_path: str
    material_properties: Dict[str, Any] = Field(default_factory=dict)
    boundary_conditions: Dict[str, Any] = Field(default_factory=dict)
    simulation_duration: float = Field(1.0, ge=0.1, le=10.0)

# Response Models
class DigitalTwinResponse(BaseModel):
    patient_id: str
    timestamp: str
    ejection_fraction: float
    wall_stress: float
    cardiac_output: float
    stroke_volume: float
    risk_score: int
    alert_level: str
    recommendations: List[str]
    simulation_based: bool
    simulation_id: Optional[int]

class SimulationResponse(BaseModel):
    id: int
    patient_id: str
    simulation_date: str
    ejection_fraction: float
    max_wall_stress: float
    stroke_volume: float
    cardiac_output: float
    processing_status: str
    stress_distribution: Optional[Dict[str, Any]] = None

class MedicalImageResponse(BaseModel):
    id: int
    patient_id: str
    image_type: str
    original_filename: str
    processing_status: str
    created_date: str

class AlertResponse(BaseModel):
    id: int
    patient_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: str
    acknowledged: bool
    simulation_triggered: bool

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None