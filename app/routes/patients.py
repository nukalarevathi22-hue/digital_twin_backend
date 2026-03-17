from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
from datetime import datetime
from app.database import get_db_connection
from app.models import PatientData, PatientCreate, APIResponse, MedicalImageUpload
from app.services.twin_engine import twin_engine

router = APIRouter()

@router.post("/submit-data", response_model=APIResponse)
async def submit_patient_data(data: PatientData):
    """Submit new patient monitoring data and update digital twin"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert patient data
        cursor.execute('''
            INSERT INTO patient_data 
            (patient_id, timestamp, weight_kg, heart_rate, steps, symptoms, 
             blood_pressure_systolic, blood_pressure_diastolic, spo2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.patient_id,
            data.timestamp or datetime.now().isoformat(),
            data.weight_kg,
            data.heart_rate,
            data.steps,
            data.symptoms,
            data.blood_pressure_systolic,
            data.blood_pressure_diastolic,
            data.spo2
        ))
        
        conn.commit()
        conn.close()
        
        # Update digital twin with simulation data
        twin_analysis = twin_engine.update_digital_twin(data.dict(), use_simulation=True)
        
        return APIResponse(
            status="success",
            message="Patient data submitted and digital twin updated",
            data={"digital_twin": twin_analysis}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}/data")
async def get_patient_data(patient_id: str, limit: int = Query(10, le=1000)):
    """Get historical data for a patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM patient_data 
            WHERE patient_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (patient_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        data = [dict(row) for row in results]
        
        return APIResponse(
            status="success",
            message=f"Retrieved {len(data)} records for patient {patient_id}",
            data={"patient_data": data}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patients")
async def get_all_patients():
    """Get list of all patients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT patient_id, name, age, gender, baseline_weight, baseline_ef, medical_history
            FROM patients
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        patients = [dict(row) for row in results]
        
        return APIResponse(
            status="success",
            message=f"Found {len(patients)} patients",
            data={"patients": patients}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/create")
async def create_patient(patient: PatientCreate):
    """Create a new patient"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO patients 
            (patient_id, name, age, gender, baseline_weight, baseline_ef, medical_history)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            patient.patient_id,
            patient.name,
            patient.age,
            patient.gender,
            patient.baseline_weight,
            patient.baseline_ef,
            patient.medical_history or ""
        ))
        
        conn.commit()
        conn.close()
        
        return APIResponse(
            status="success",
            message=f"Patient {patient.name} created successfully",
            data={"patient_id": patient.patient_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient/{patient_id}/upload-mri")
async def upload_mri_image(
    patient_id: str,
    file: UploadFile = File(...),
    image_type: str = Form(...),
    acquisition_date: str = Form(None)
):
    """Upload MRI/CT image for processing"""
    try:
        # Validate patient exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT patient_id FROM patients WHERE patient_id = ?', (patient_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Create upload directory
        upload_dir = f"data/medical_images/{patient_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store in database
        cursor.execute('''
            INSERT INTO medical_images 
            (patient_id, image_type, original_filename, stored_path, acquisition_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            patient_id,
            image_type,
            file.filename,
            file_path,
            acquisition_date or datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return APIResponse(
            status="success",
            message="Medical image uploaded successfully",
            data={
                "filename": file.filename,
                "patient_id": patient_id,
                "file_path": file_path
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))