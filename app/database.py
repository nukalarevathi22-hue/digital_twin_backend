import sqlite3
import json
from datetime import datetime
import os

def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect('chf_digital_twin.db')
    cursor = conn.cursor()
    
    # Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            baseline_weight REAL,
            baseline_ef REAL,
            medical_history TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Patient monitoring data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            weight_kg REAL,
            heart_rate INTEGER,
            steps INTEGER,
            symptoms TEXT,
            blood_pressure_systolic INTEGER,
            blood_pressure_diastolic INTEGER,
            spo2 INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Medical images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            image_type TEXT,
            original_filename TEXT,
            stored_path TEXT,
            acquisition_date TIMESTAMP,
            processing_status TEXT DEFAULT 'uploaded',
            segmentation_path TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Simulation results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            simulation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mesh_file_path TEXT,
            febio_config_path TEXT,
            febio_results_path TEXT,
            ejection_fraction REAL,
            max_wall_stress REAL,
            avg_wall_stress REAL,
            stroke_volume REAL,
            cardiac_output REAL,
            lvedv REAL,
            lvesv REAL,
            strain_data JSON,
            stress_distribution JSON,
            simulation_parameters JSON,
            processing_status TEXT DEFAULT 'completed',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Digital twin states table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_twin_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ejection_fraction REAL,
            wall_stress REAL,
            cardiac_output REAL,
            stroke_volume REAL,
            risk_score INTEGER,
            alert_level TEXT,
            recommendations TEXT,
            simulation_based BOOLEAN DEFAULT FALSE,
            simulation_id INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (simulation_id) REFERENCES simulation_results (id)
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            alert_type TEXT,
            severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT FALSE,
            simulation_triggered BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
    ''')
    
    # Insert sample patients
    sample_patients = [
        ('patient_001', 'John Doe', 65, 'male', 70.0, 55.0, 'Hypertension, Previous MI'),
        ('patient_002', 'Jane Smith', 58, 'female', 62.0, 48.0, 'Diabetes, CHF'),
        ('patient_003', 'Robert Brown', 72, 'male', 78.0, 35.0, 'Severe CHF, CKD')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO patients 
        (patient_id, name, age, gender, baseline_weight, baseline_ef, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_patients)
    
    conn.commit()
    conn.close()
    print("✅ Complete database initialized successfully!")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect('chf_digital_twin.db')
    conn.row_factory = sqlite3.Row
    return conn