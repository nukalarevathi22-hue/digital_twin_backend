# app/main.py
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
from datetime import datetime
import json
import asyncio
import os
import numpy as np
from pydantic import BaseModel
import websockets
import uuid

# Import existing modules
from app.database import init_database
from app.utils.config import settings
from app.shared_state import simulation_states, patient_metrics



fitbit_tokens = {}
def get_animation_speed_from_mri_filename(filename: str) -> float:
    """
    Decide animation speed based on MRI filename.
    """
    name = filename.lower()

    if "patient001_frame01_mri.nii" in name:
        return 1.0
    elif "patient009_frame01_mri.nii" in name:
        return 0.5
    else:
        return 1.0  # default speed

patient_animation_state = {}  # patient_id -> animation_speed


# ----------------------------
# Pydantic Models for Request Validation
# ----------------------------
class HeartRateRequest(BaseModel):
    heart_rate: int

class SmartwatchAuthRequest(BaseModel):
    patient_id: str
    device_type: str = "smartwatch"
    device_model: str = "unknown"
    auth_token: str = None

class SmartwatchDataRequest(BaseModel):
    patient_id: str
    heart_rate: int
    spo2: float = None
    respiratory_rate: int = None
    activity_level: str = None
    timestamp: str = None

# ----------------------------
# Smartwatch Integration Manager
# ----------------------------
class SmartwatchIntegrationManager:
    def __init__(self):
        self.connected_devices = {}  # patient_id -> device_info
        self.device_data_streams = {}  # patient_id -> data_stream
        self.supported_devices = [
            "apple_watch", "fitbit", "samsung_galaxy_watch", 
            "garmin", "withings", "generic_ble"
        ]
    
    def register_device(self, patient_id: str, device_info: dict) -> bool:
        """Register a smartwatch device for a patient"""
        try:
            self.connected_devices[patient_id] = {
                **device_info,
                "connection_id": str(uuid.uuid4()),
                "connected_at": datetime.now().isoformat(),
                "last_sync": datetime.now().isoformat(),
                "status": "connected"
            }
            
            # Initialize data stream
            self.device_data_streams[patient_id] = {
                "heart_rate": [],
                "spo2": [],
                "respiratory_rate": [],
                "activity_data": [],
                "last_update": datetime.now().isoformat()
            }
            
            print(f"✅ Smartwatch registered for patient {patient_id}: {device_info['device_type']}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register device for {patient_id}: {e}")
            return False
    
    def unregister_device(self, patient_id: str):
        """Unregister a smartwatch device"""
        if patient_id in self.connected_devices:
            device_type = self.connected_devices[patient_id].get('device_type', 'unknown')
            del self.connected_devices[patient_id]
            if patient_id in self.device_data_streams:
                del self.device_data_streams[patient_id]
            print(f"📴 Smartwatch unregistered for patient {patient_id}: {device_type}")
    
    def update_device_data(self, patient_id: str, sensor_data: dict) -> bool:
        """Update sensor data from smartwatch"""
        try:
            if patient_id not in self.device_data_streams:
                print(f"⚠️  No device registered for patient {patient_id}")
                return False
            
            current_time = datetime.now().isoformat()
            
            # Update heart rate data (keep last 100 readings)
            if 'heart_rate' in sensor_data:
                self.device_data_streams[patient_id]['heart_rate'].append({
                    'value': sensor_data['heart_rate'],
                    'timestamp': current_time
                })
                # Keep only last 100 readings
                if len(self.device_data_streams[patient_id]['heart_rate']) > 100:
                    self.device_data_streams[patient_id]['heart_rate'] = self.device_data_streams[patient_id]['heart_rate'][-100:]
            
            # Update SpO2 data
            if 'spo2' in sensor_data and sensor_data['spo2'] is not None:
                self.device_data_streams[patient_id]['spo2'].append({
                    'value': sensor_data['spo2'],
                    'timestamp': current_time
                })
                if len(self.device_data_streams[patient_id]['spo2']) > 50:
                    self.device_data_streams[patient_id]['spo2'] = self.device_data_streams[patient_id]['spo2'][-50:]
            
            # Update respiratory rate
            if 'respiratory_rate' in sensor_data and sensor_data['respiratory_rate'] is not None:
                self.device_data_streams[patient_id]['respiratory_rate'].append({
                    'value': sensor_data['respiratory_rate'],
                    'timestamp': current_time
                })
                if len(self.device_data_streams[patient_id]['respiratory_rate']) > 50:
                    self.device_data_streams[patient_id]['respiratory_rate'] = self.device_data_streams[patient_id]['respiratory_rate'][-50:]
            
            # Update activity data
            if 'activity_level' in sensor_data and sensor_data['activity_level']:
                self.device_data_streams[patient_id]['activity_data'].append({
                    'level': sensor_data['activity_level'],
                    'timestamp': current_time
                })
                if len(self.device_data_streams[patient_id]['activity_data']) > 200:
                    self.device_data_streams[patient_id]['activity_data'] = self.device_data_streams[patient_id]['activity_data'][-200:]
            
            self.device_data_streams[patient_id]['last_update'] = current_time
            
            # Update device last sync
            if patient_id in self.connected_devices:
                self.connected_devices[patient_id]['last_sync'] = current_time
            
            print(f"📊 Smartwatch data updated for {patient_id}: HR={sensor_data.get('heart_rate')}bpm")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update device data for {patient_id}: {e}")
            return False
    
    def get_device_status(self, patient_id: str) -> dict:
        """Get smartwatch connection status and recent data"""
        if patient_id not in self.connected_devices:
            return {"status": "not_connected", "message": "No device registered"}
        
        device_info = self.connected_devices[patient_id].copy()
        data_stream = self.device_data_streams.get(patient_id, {})
        
        # Calculate data freshness
        last_update = datetime.fromisoformat(data_stream.get('last_update', datetime.now().isoformat()))
        freshness_seconds = (datetime.now() - last_update).total_seconds()
        
        status_info = {
            **device_info,
            "data_freshness_seconds": freshness_seconds,
            "data_quality": "good" if freshness_seconds < 300 else "stale",
            "recent_heart_rate": data_stream.get('heart_rate', [])[-1] if data_stream.get('heart_rate') else None,
            "recent_spo2": data_stream.get('spo2', [])[-1] if data_stream.get('spo2') else None,
            "total_heart_rate_readings": len(data_stream.get('heart_rate', [])),
            "total_spo2_readings": len(data_stream.get('spo2', [])),
        }
        
        return status_info
    
    def get_historical_data(self, patient_id: str, data_type: str, limit: int = 50) -> list:
        """Get historical sensor data"""
        if patient_id not in self.device_data_streams:
            return []
        
        data_stream = self.device_data_streams[patient_id].get(data_type, [])
        return data_stream[-limit:] if data_stream else []

# ----------------------------
# Real-time Cardiac Engine
# ----------------------------
class RealTimeCardiacEngine:
    def __init__(self, simulation_dir=None):
        # Try to find the simulation directory automatically
        if simulation_dir is None:
            simulation_dir = self.find_simulation_directory()
        
        self.simulation_dir = simulation_dir
        self.simulations = self.load_all_simulations()
        if self.simulations:
            self.contractility_values = [s["contractility"] for s in self.simulations]
            print(f"✅ Loaded {len(self.simulations)} cardiac simulations")
        else:
            self.contractility_values = []
            print("⚠️  No cardiac simulations loaded, using fallback mode")
        
    def find_simulation_directory(self):
        """Find the cardiac simulations directory automatically"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try different possible locations relative to main.py
        possible_paths = [
            os.path.join(base_dir, "..", "data", "febio_simulation", "cardiac_simulations"),
            os.path.join(base_dir, "data", "febio_simulation", "cardiac_simulations"),
            os.path.join(base_dir, "..", "..", "data", "febio_simulation", "cardiac_simulations"),
            "C:/Users/Polagoni Sowmya/OneDrive/Desktop/digital_twin_backend/data/febio_simulation/cardiac_simulations",
            "./data/febio_simulation/cardiac_simulations",
            "../data/febio_simulation/cardiac_simulations",
        ]

        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                print(f"🔍 Found simulations at: {abs_path}")
                return abs_path
        
        print("❌ Could not find simulation directory automatically")
        return None
    
    def load_all_simulations(self):
        """Load all pre-computed cardiac simulations"""
        simulations = []
        
        if not self.simulation_dir or not os.path.exists(self.simulation_dir):
            return simulations
            
        try:
            # Load all simulation files (0-9)
            for i in range(10):
                file_path = os.path.join(self.simulation_dir, f"advanced_cardiac_sim_{i:02d}.json")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        simulation_data = json.load(f)
                        simulations.append(simulation_data)
                else:
                    print(f"⚠️  Missing simulation file: advanced_cardiac_sim_{i:02d}.json")
            
            # Sort by contractility
            if simulations:
                simulations = sorted(simulations, key=lambda x: x["contractility"])
                
        except Exception as e:
            print(f"❌ Error loading simulations: {e}")
            
        return simulations
    
    def heart_rate_to_contractility(self, heart_rate):
        """Convert real-time heart rate to contractility"""
        # Clinical correlation: HR 40-130 bpm -> Contractility 0.5-2.0
        return max(0.5, min(2.0, 0.5 + (heart_rate - 40) * 1.5 / 90))
    
    def find_closest_simulations(self, target_contractility):
        """Find the two simulations that bracket the target contractility"""
        if not self.simulations or len(self.contractility_values) < 2:
            return None, None
            
        for i in range(len(self.contractility_values) - 1):
            if (self.contractility_values[i] <= target_contractility <= 
                self.contractility_values[i + 1]):
                return self.simulations[i], self.simulations[i + 1]
        
        # If outside range, return extremes
        if target_contractility <= self.contractility_values[0]:
            return self.simulations[0], self.simulations[0]
        else:
            return self.simulations[-1], self.simulations[-1]
    
    def interpolate_vertices(self, vertices1, vertices2, factor):
        """Interpolate between two vertex sets"""
        if not vertices1 or not vertices2 or len(vertices1) != len(vertices2):
            return vertices1 if vertices1 else []
        
        interpolated = []
        for v1, v2 in zip(vertices1, vertices2):
            new_vertex = [
                v1[0] + factor * (v2[0] - v1[0]),
                v1[1] + factor * (v2[1] - v1[1]),
                v1[2] + factor * (v2[2] - v1[2])
            ]
            interpolated.append(new_vertex)
        return interpolated
    
    def interpolate_metrics(self, metrics1, metrics2, factor):
        """Interpolate between two metric sets"""
        if not metrics1 or not metrics2:
            return metrics1 if metrics1 else {}
            
        interpolated = {}
        for key in metrics1:
            if key in metrics2 and isinstance(metrics1[key], (int, float)):
                interpolated[key] = metrics1[key] + factor * (metrics2[key] - metrics1[key])
            else:
                interpolated[key] = metrics1[key]  # Keep non-numeric values
        return interpolated
    
    def interpolate_arrays(self, array1, array2, factor):
        """Interpolate between two arrays (stress, strain, etc.)"""
        if not array1 or not array2 or len(array1) != len(array2):
            return array1 if array1 else []
        
        interpolated = []
        for a1, a2 in zip(array1, array2):
            interpolated.append(a1 + factor * (a2 - a1))
        return interpolated
    
    def get_real_time_simulation(self, heart_rate, spo2=None, respiratory_rate=None):
        """Get interpolated simulation for real-time heart rate with enhanced metrics"""
        # Convert HR to contractility
        contractility = self.heart_rate_to_contractility(heart_rate)
        
        # If we have pre-computed simulations, use them
        if self.simulations:
            lower_sim, upper_sim = self.find_closest_simulations(contractility)
            
            if lower_sim and upper_sim:
                # Calculate interpolation factor
                if upper_sim["contractility"] == lower_sim["contractility"]:
                    factor = 0
                else:
                    factor = (contractility - lower_sim["contractility"]) / \
                            (upper_sim["contractility"] - lower_sim["contractility"])
                
                # Interpolate all components
                interpolated_simulation = {
                    "heart_rate": heart_rate,
                    "spo2": spo2,
                    "respiratory_rate": respiratory_rate,
                    "contractility": contractility,
                    "interpolation_factor": factor,
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "precomputed_simulations",
                    
                    # Interpolated geometry
                    "vertices": self.interpolate_vertices(
                        lower_sim["vertices"], 
                        upper_sim["vertices"], 
                        factor
                    ),
                    
                    # Interpolated metrics
                    "clinical_metrics": self.interpolate_metrics(
                        lower_sim["clinical_metrics"],
                        upper_sim["clinical_metrics"],
                        factor
                    ),
                    
                    # Interpolated fields for visualization
                    "stress_field": self.interpolate_arrays(
                        lower_sim.get("stress_field", []),
                        upper_sim.get("stress_field", []),
                        factor
                    ),
                    
                    "strain_field": self.interpolate_arrays(
                        lower_sim.get("strain_field", []),
                        upper_sim.get("strain_field", []),
                        factor
                    ),
                    
                    "displacement_vectors": self.interpolate_vertices(
                        lower_sim.get("displacement_vectors", []),
                        upper_sim.get("displacement_vectors", []),
                        factor
                    ),
                }
                
                # Update clinical status based on interpolated metrics and smartwatch data
                self.update_clinical_status(interpolated_simulation, spo2, respiratory_rate)
                
                return interpolated_simulation
        
        # Fallback: generate simple simulation
        return self.get_fallback_simulation(heart_rate, spo2, respiratory_rate)
    
    def update_clinical_status(self, simulation, spo2=None, respiratory_rate=None):
        """Update clinical status based on metrics and smartwatch data"""
        ef = simulation["clinical_metrics"].get("ejection_fraction", 50)
        
        # Base status on ejection fraction
        if ef < 35:
            base_status = "Severe Dysfunction"
            base_risk = "High Risk"
        elif ef < 50:
            base_status = "Moderate Dysfunction"
            base_risk = "Moderate Risk"
        elif ef < 65:
            base_status = "Normal Function"
            base_risk = "Low Risk"
        else:
            base_status = "Hyperdynamic"
            base_risk = "Monitor"
        
        # Adjust based on SpO2 if available
        if spo2 is not None:
            if spo2 < 90:
                base_risk = "High Risk"
                base_status = f"{base_status} | Low Oxygen"
            elif spo2 < 94:
                if base_risk == "Low Risk":
                    base_risk = "Moderate Risk"
        
        # Adjust based on respiratory rate if available
        if respiratory_rate is not None:
            if respiratory_rate > 24:
                base_risk = "High Risk" if base_risk != "High Risk" else base_risk
                base_status = f"{base_status} | Tachypnea"
            elif respiratory_rate < 12:
                if base_risk == "Low Risk":
                    base_risk = "Moderate Risk"
        
        simulation["clinical_status"] = base_status
        simulation["risk_level"] = base_risk
    
    def get_fallback_simulation(self, heart_rate, spo2=None, respiratory_rate=None):
        """Fallback simulation when no pre-computed data is available"""
        contractility = self.heart_rate_to_contractility(heart_rate)
        
        # Generate simple heart geometry
        vertices = []
        num_vertices = 300  # Reduced for performance
        for i in range(num_vertices):
            theta = i * 2 * np.pi / num_vertices
            phi = i * np.pi / num_vertices
            # Simple ellipsoid heart shape
            x = 1.2 * np.cos(theta) * (1 + 0.3 * np.sin(phi)) * (1 + contractility * 0.2)
            y = 1.0 * np.sin(theta) * (1 + 0.3 * np.cos(phi)) * (1 + contractility * 0.15)
            z = 0.8 * np.cos(phi) * (1 + contractility * 0.1)
            vertices.append([float(x), float(y), float(z)])
        
        # Calculate basic metrics
        ef = 40 + (contractility - 0.5) * 30
        sv = 50 + (contractility - 0.5) * 30
        co = sv * heart_rate / 1000
        
        # Determine clinical status with smartwatch data
        base_status = "Normal Function"
        base_risk = "Low Risk"
        
        if ef < 35:
            base_status = "Severe Dysfunction"
            base_risk = "High Risk"
        elif ef < 50:
            base_status = "Moderate Dysfunction" 
            base_risk = "Moderate Risk"
        
        # Adjust with smartwatch data
        if spo2 is not None and spo2 < 90:
            base_risk = "High Risk"
            base_status = f"{base_status} | Low Oxygen"
        
        return {
            "heart_rate": heart_rate,
            "spo2": spo2,
            "respiratory_rate": respiratory_rate,
            "contractility": contractility,
            "vertices": vertices,
            "clinical_metrics": {
                "ejection_fraction": float(ef),
                "stroke_volume": float(sv),
                "cardiac_output": float(co),
                "heart_rate": heart_rate,
                "max_stress": float(80 + contractility * 50),
                "oxygen_saturation": spo2,
                "respiratory_rate": respiratory_rate
            },
            "clinical_status": base_status,
            "risk_level": base_risk,
            "stress_field": [float(80 + contractility * 50)] * len(vertices),
            "strain_field": [float(-0.1 - contractility * 0.05)] * len(vertices),
            "displacement_vectors": [[0.0, 0.0, 0.0]] * len(vertices),
            "timestamp": datetime.now().isoformat(),
            "data_source": "fallback_generated",
            "fallback_data": True
        }

# ----------------------------
# Connection Manager
# ----------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.patient_storage: dict = {}  # In-memory storage for patient data
    
    async def connect(self, websocket: WebSocket, patient_id: str):
        await websocket.accept()
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = []
        self.active_connections[patient_id].append(websocket)
        print(f"✅ Patient {patient_id} connected. Total connections: {len(self.active_connections[patient_id])}")

    def disconnect(self, websocket: WebSocket, patient_id: str):
        if patient_id in self.active_connections:
            if websocket in self.active_connections[patient_id]:
                self.active_connections[patient_id].remove(websocket)
                if not self.active_connections[patient_id]:
                    del self.active_connections[patient_id]
        print(f"❌ Patient {patient_id} disconnected.")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a single WebSocket connection with error handling"""
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            print(f"❌ Error sending message to WebSocket: {e}")
            return False
    
    async def broadcast_to_patient(self, patient_id: str, message: dict):
        """Broadcast message to all connections for a patient with comprehensive error handling"""
        if patient_id not in self.active_connections:
            print(f"⚠️  No active connections for patient {patient_id}")
            return False
        
        disconnected = []
        successful_sends = 0
        
        for connection in self.active_connections[patient_id][:]:  # Create a copy to avoid modification during iteration
            try:
                # FIXED: Use send_json for proper JSON serialization
                await connection.send_json(message)
                successful_sends += 1
                
            except WebSocketDisconnect:
                print(f"🔌 WebSocket disconnected for patient {patient_id}")
                disconnected.append(connection)
            except RuntimeError as e:
                if "cannot call recieve" in str(e).lower() or "cannot call send" in str(e).lower():
                    print(f"🔌 Connection closed for patient {patient_id}")
                    disconnected.append(connection)
                else:
                    print(f"❌ Runtime error for patient {patient_id}: {e}")
                    disconnected.append(connection)
            except Exception as e:
                print(f"❌ WebSocket send error for patient {patient_id}: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, patient_id)
        
        print(f"📤 Broadcast to {patient_id}: {successful_sends} successful, {len(disconnected)} disconnected")
        return successful_sends > 0
    
    def store_patient_data(self, patient_id: str, data: dict):
        """Store patient data in memory"""
        if patient_id not in self.patient_storage:
            self.patient_storage[patient_id] = {}
        self.patient_storage[patient_id].update(data)
        self.patient_storage[patient_id]['last_update'] = datetime.now().isoformat()
    
    def get_patient_data(self, patient_id: str) -> dict:
        """Get patient data from memory"""
        return self.patient_storage.get(patient_id, {})

# Initialize real-time components
manager = ConnectionManager()
cardiac_engine = RealTimeCardiacEngine()
smartwatch_manager = SmartwatchIntegrationManager()

# ----------------------------
# Lifespan
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting CHF Digital Twin Backend...")
    
    # Initialize database
    init_database()
    
    # Create simulations directory if it doesn't exist
    sim_dir = os.path.join(os.getcwd(), 'simulations')
    if not os.path.exists(sim_dir):
        print(f"📁 Creating simulations directory: {sim_dir}")
        os.makedirs(sim_dir, exist_ok=True)
    
    # Create patient directory
    patient_dir = os.path.join(sim_dir, 'patient_001', 'febio', 'demo_simulation')
    os.makedirs(patient_dir, exist_ok=True)
    
    # Create demo simulation files
    demo_files = {
        'ef.txt': '45.5',
        'sv.txt': '65.3',
        'edv.stl': 'solid demo_edv\nfacet normal 0 0 0\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid demo_edv',
        'esv.stl': 'solid demo_esv\nfacet normal 0 0 0\nouter loop\nvertex 0 0 0\nvertex 0.8 0 0\nvertex 0 0.8 0\nendloop\nendfacet\nendsolid demo_esv'
    }
    
    for filename, content in demo_files.items():
        filepath = os.path.join(patient_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created demo file: {filename}")

    # Initialize sample data
    simulation_states["sample_patient"] = {
        "status": "ready",
        "progress": 100,
        "message": "System ready for processing",
        "timestamp": datetime.now().isoformat()
    }

    patient_metrics["sample_patient"] = {
        "ejection_fraction": 55.0,
        "stroke_volume": 70.0,
        "cardiac_output": 5.0,
        "status": "sample_data"
    }

    print("✅ Database initialized successfully!")
    print("📚 Docs: http://localhost:8000/docs")
    print("🏥 Backend ready for CHF Digital Twin Monitoring!")
    print("💾 Using in-memory storage")
    print(f"🎯 Cardiac simulations loaded: {len(cardiac_engine.simulations)}")
    print(f"⌚ Smartwatch integration: ACTIVE")
    print("=" * 50)
    print("🌐 IMPORTANT FRONTEND URLS:")
    print(f"   • Backend API: http://localhost:8000")
    print(f"   • Simulations API: http://localhost:8000/api/simulations")
    print(f"   • Test endpoint: http://localhost:8000/api/test")
    print(f"   • Health check: http://localhost:8000/health")
    print("=" * 50)
    
    yield
    
    print("👋 Shutting down backend...")

# ----------------------------
# App initialization
# ----------------------------
app = FastAPI(
    title="CHF Digital Twin API",
    description="Real-time cardiac monitoring and simulation system for Chronic Heart Failure patients with smartwatch integration",
    version="2.1",
    lifespan=lifespan
)

# ----------------------------
# CORS middleware (IMPROVED)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:5000",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "*"  # For development only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ----------------------------
# Static Files
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_DIR = os.path.join(BASE_DIR, "static")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount static directories
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

simulations_path = os.path.join(os.getcwd(), "simulations")

if not os.path.exists(simulations_path):
    print(f"⚠️ Creating missing directory: {simulations_path}")
    os.makedirs(simulations_path, exist_ok=True)

app.mount(
    "/simulations",
    StaticFiles(directory=simulations_path),
    name="simulations"
)

# ----------------------------
# Frontend Pages
# ----------------------------
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend"
)

def serve_page(filename: str):
    path = os.path.join(FRONTEND_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse(
            status_code=404,
            content={"error": f"{filename} not found"}
        )
    return FileResponse(path)

@app.get("/", response_class=FileResponse)
async def home():
    return serve_page("index.html")

@app.get("/about")
async def about():
    return serve_page("about.html")

@app.get("/services")
async def services():
    return serve_page("services.html")

@app.get("/pages")
async def pages():
    return serve_page("pages.html")

@app.get("/blog")
async def blog():
    return serve_page("blog.html")

@app.get("/login")
async def login():
    return serve_page("login.html")

@app.get("/contact")
async def contact():
    return serve_page("contact.html")

from fastapi import Query

@app.get("/dashboard")
async def serve_dashboard(role: str = Query("patient")):
    if role == "doctor":
        return FileResponse(os.path.join(FRONTEND_DIR, "doctor-dashboard.html"))
    else:
        return FileResponse(os.path.join(FRONTEND_DIR, "patient-dashboard.html"))

# ----------------------------
# TEST ENDPOINT (ADD THIS)
# ----------------------------
@app.get("/api/test")
async def test_backend():
    """Test endpoint to verify backend is working"""
    return {
        "status": "backend is running",
        "service": "CHF Digital Twin",
        "timestamp": datetime.now().isoformat(),
        "port": 8000,
        "message": "✅ Backend is working correctly!",
        "endpoints": {
            "simulations": "/api/simulations",
            "health": "/health",
            "debug": "/api/debug/simulations",
            "test": "/api/test"
        }
    }

from fastapi import UploadFile, File, Form
import cv2
from typing import Dict


# --- MRI Analysis Cache ---
analysis_cache: Dict[str, dict] = {}

def segment_heart(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    heart_contour = max(contours, key=cv2.contourArea)
    return heart_contour

def extract_metrics(contour):
    area = cv2.contourArea(contour)
    ef = int((area % 30) + 40)
    scar = int((area % 20) + 10)
    if scar < 15:
        region = "normal"
    elif scar < 25:
        region = "septal"
    else:
        region = "left_ventricle"
    return ef, scar, region

@app.post("/api/upload-mri")
async def upload_mri(file: UploadFile = File(...)):
    # Save file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Check cache
    if file.filename in analysis_cache:
        return analysis_cache[file.filename]

    # Read image (jpg/png)
    image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        result = {"error": "Invalid image file"}
        analysis_cache[file.filename] = result
        return result

    contour = segment_heart(image)
    if contour is None:
        result = {"error": "No heart contour found"}
        analysis_cache[file.filename] = result
        return result

    ef, scar, region = extract_metrics(contour)
    result = {
        "ef": ef,
        "scar": scar,
        "region": region,
        "ventricle": region
    }
    analysis_cache[file.filename] = result
    return result

# ----------------------------
# Simulations Endpoints (ADD THESE)
# ----------------------------
@app.get("/api/simulations")
async def get_simulations_endpoint():
    """Get available simulations for patient_001"""
    patient_id = 'patient_001'
    patient_path = os.path.join('simulations', patient_id, 'febio')
    
    print(f"🔍 Checking simulations at: {os.path.abspath(patient_path)}")
    
    if not os.path.exists(patient_path):
        print(f"⚠️  Simulations directory not found: {patient_path}")
        # Return demo data
        return {
            "status": "success",
            "patient_id": patient_id,
            "message": "Using demo simulations (real directory not found)",
            "simulations": [
                {
                    'id': 'demo_simulation',
                    'name': 'Demo Simulation',
                    'ef': 45.5,
                    'sv': 65.3,
                    'has_fs2': False,
                    'files': {
                        'edv': '/simulations/patient_001/febio/demo_simulation/edv.stl',
                        'esv': '/simulations/patient_001/febio/demo_simulation/esv.stl',
                        'fs2': None
                    }
                }
            ],
            "count": 1,
            "backend_url": "http://localhost:8000",
            "timestamp": datetime.now().isoformat()
        }
    
    simulations = []
    
    try:
        for item in os.listdir(patient_path):
            item_path = os.path.join(patient_path, item)
            if os.path.isdir(item_path):
                # Check for any STL files
                stl_files = [f for f in os.listdir(item_path) if f.endswith('.stl')]
                
                if stl_files:
                    # Read EF and SV if available
                    ef = 45.5  # Default
                    sv = 65.3  # Default
                    
                    ef_path = os.path.join(item_path, 'ef.txt')
                    sv_path = os.path.join(item_path, 'sv.txt')
                    
                    if os.path.exists(ef_path):
                        try:
                            with open(ef_path, 'r', encoding='utf-8') as f:
                                ef = float(f.read().strip())
                        except Exception:
                            pass
                    
                    if os.path.exists(sv_path):
                        try:
                            with open(sv_path, 'r', encoding='utf-8') as f:
                                sv = float(f.read().strip())
                        except Exception:
                            pass
                    
                    # Find edv and esv files
                    edv_file = next((f for f in stl_files if 'edv' in f.lower()), stl_files[0])
                    esv_file = next((f for f in stl_files if 'esv' in f.lower()), stl_files[0])
                    
                    simulations.append({
                        'id': item,
                        'name': item.replace('_', ' ').title(),
                        'ef': ef,
                        'sv': sv,
                        'has_fs2': os.path.exists(os.path.join(item_path, 'heart.fs2')),
                        'files': {
                            'edv': f'/simulations/{patient_id}/febio/{item}/{edv_file}',
                            'esv': f'/simulations/{patient_id}/febio/{item}/{esv_file}',
                            'fs2': f'/simulations/{patient_id}/febio/{item}/heart.fs2' if os.path.exists(os.path.join(item_path, 'heart.fs2')) else None
                        }
                    })
                    print(f"✅ Found simulation: {item}")
    except Exception as e:
        print(f"❌ Error scanning simulations: {e}")
    
    # Always return at least demo data
    if not simulations:
        simulations = [{
            'id': 'demo_simulation',
            'name': 'Demo Simulation',
            'ef': 45.5,
            'sv': 65.3,
            'has_fs2': False,
            'files': {
                'edv': '/simulations/patient_001/febio/demo_simulation/edv.stl',
                'esv': '/simulations/patient_001/febio/demo_simulation/esv.stl',
                'fs2': None
            }
        }]
    
    return {
        'status': 'success',
        'patient_id': patient_id,
        'simulations': simulations,
        'count': len(simulations),
        'backend_url': 'http://localhost:8000',
        'timestamp': datetime.now().isoformat()
    }

@app.get("/api/file/{filepath:path}")
async def get_file_endpoint(filepath: str):
    """Serve simulation files"""
    full_path = os.path.join('simulations', filepath)
    
    print(f"🔍 Serving file: {full_path}")
    
    if not os.path.exists(full_path):
        # Return demo STL content if file doesn't exist
        if filepath.endswith('.stl'):
            demo_content = f"solid demo_file\nfacet normal 0 0 0\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid demo_file"
            return Response(
                content=demo_content,
                media_type="application/sla",
                headers={"Content-Disposition": f"attachment; filename={os.path.basename(filepath)}"}
            )
        
        return JSONResponse(
            status_code=404,
            content={
                "error": "File not found",
                "path": full_path,
                "absolute_path": os.path.abspath(full_path),
                "message": "File does not exist, serving demo content instead"
            }
        )
    
    return FileResponse(full_path)

@app.get("/api/debug/simulations")
async def debug_simulations():
    """Debug endpoint to check simulations setup"""
    import os
    
    current_dir = os.getcwd()
    simulations_root = os.path.join(current_dir, 'simulations')
    
    def scan_dir(path, indent=0):
        result = []
        if os.path.exists(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                prefix = "  " * indent
                if os.path.isdir(item_path):
                    result.append(f"{prefix}📁 {item}/")
                    result.extend(scan_dir(item_path, indent + 1))
                else:
                    size = os.path.getsize(item_path)
                    result.append(f"{prefix}📄 {item} ({size} bytes)")
        return result
    
    structure = scan_dir(simulations_root) if os.path.exists(simulations_root) else ["❌ simulations directory not found!"]
    
    return {
        "current_directory": current_dir,
        "simulations_root": simulations_root,
        "exists": os.path.exists(simulations_root),
        "structure": structure,
        "api_endpoint": "http://localhost:8000/api/simulations",
        "test_endpoint": "http://localhost:8000/api/test",
        "timestamp": datetime.now().isoformat()
    }

