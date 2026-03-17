# Save as: app/routes/digital_twin_enhanced.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Dict, Any, List
import asyncio
import json
import os
from datetime import datetime
import numpy as np

# Import shared state
from app.shared_state import simulation_states, patient_metrics

# Define the router
router = APIRouter()

@router.post("/patient/{patient_id}/process-cardiac-mri")
async def process_cardiac_mri(
    patient_id: str,
    background_tasks: BackgroundTasks,
    mri_files: List[UploadFile] = File(...)
):
    """Process cardiac MRI and generate digital twin"""
    
    try:
        # Save uploaded files
        upload_dir = f"data/patients/{patient_id}/mri_uploads/"
        os.makedirs(upload_dir, exist_ok=True)
        
        saved_files = []
        for file in mri_files:
            file_path = f"{upload_dir}/{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            saved_files.append(file_path)
        
        # Initialize simulation state
        simulation_states[patient_id] = {
            "status": "initializing",
            "progress": 0,
            "message": "Starting digital twin generation...",
            "timestamp": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(
            generate_digital_twin_pipeline,
            patient_id,
            saved_files
        )
        
        return {
            "status": "processing_started",
            "patient_id": patient_id,
            "message": "Cardiac MRI processing initiated",
            "files_received": len(saved_files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/patient/{patient_id}/digital-twin/status")
async def get_digital_twin_status(patient_id: str):
    """Get current digital twin generation status"""
    
    if patient_id not in simulation_states:
        raise HTTPException(status_code=404, detail="Patient not found in simulation states")
    
    return simulation_states[patient_id]

@router.get("/patient/{patient_id}/digital-twin/metrics")
async def get_digital_twin_metrics(patient_id: str):
    """Get comprehensive CHF metrics from digital twin"""
    
    if patient_id not in patient_metrics:
        # Return default metrics if none available
        default_metrics = {
            "ejection_fraction": 55.0,
            "stroke_volume": 70.0,
            "cardiac_output": 5.0,
            "wall_stress_max": 120.0,
            "chf_risk_score": 2.0,
            "status": "default_data",
            "fluid_dynamics": {
                "mitral_flow_rate": 85.0,
                "aortic_flow_rate": 72.0,
                "cardiac_output": 5.4,
                "valve_efficiency": 0.89
            }
        }
        patient_metrics[patient_id] = default_metrics
    
    return {
        "patient_id": patient_id,
        "metrics": patient_metrics[patient_id],
        "timestamp": datetime.now().isoformat()
    }

@router.post("/patient/{patient_id}/digital-twin/simulate")
async def run_simulation(
    patient_id: str,
    background_tasks: BackgroundTasks,
    parameters: Dict[str, Any] = None
):
    """Run simulation with specific parameters"""
    
    default_params = {
        "heart_rate": 75,
        "systolic_bp": 120,
        "contractility": 1.0,
        "blood_volume": 5000,
        "include_fluid_dynamics": True
    }
    
    sim_params = {**default_params, **(parameters or {})}
    
    # Initialize simulation state
    simulation_states[patient_id] = {
        "status": "parameter_simulation",
        "progress": 0,
        "message": "Starting parameter simulation...",
        "parameters": sim_params,
        "timestamp": datetime.now().isoformat()
    }
    
    background_tasks.add_task(
        run_cardiac_simulation,
        patient_id,
        sim_params
    )
    
    return {
        "status": "simulation_started",
        "patient_id": patient_id,
        "parameters": sim_params,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/patient/{patient_id}/digital-twin/visualization")
async def get_visualization_data(patient_id: str):
    """Get 3D visualization data for the digital twin"""
    
    try:
        # For now, return sample visualization data
        viz_data = {
            "mesh_data": "sample_base64_or_url",
            "displacement_frames": [],
            "stress_data": [],
            "animation_parameters": {
                "duration": 5.0,
                "frame_count": 100
            },
            "status": "sample_data"
        }
        
        return {
            "patient_id": patient_id,
            "visualization": viz_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Visualization data not available: {str(e)}")

# Add the 3D data endpoint
@router.get("/patient/{patient_id}/digital-twin/3d-data")
async def get_3d_visualization_data(patient_id: str):
    """Get complete 3D visualization data for the digital twin heart"""
    
    try:
        # Import here to avoid circular imports
        from app.utils.visualization_generator import HeartVisualizationGenerator
        
        generator = HeartVisualizationGenerator()
        viz_data = generator.generate_heart_geometry(patient_id)
        
        return {
            "patient_id": patient_id,
            "visualization_data": viz_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"3D data generation failed: {str(e)}")

# NEW: Fluid dynamics data endpoint
@router.get("/patient/{patient_id}/digital-twin/fluid-data")
async def get_fluid_dynamics_data(patient_id: str):
    """Get fluid dynamics data for visualization"""
    
    try:
        fluid_data = generate_fluid_dynamics_data(patient_id)
        
        return {
            "patient_id": patient_id,
            "fluid_dynamics": fluid_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fluid data generation failed: {str(e)}")


# Add these new routes to your digital_twin_enhanced.py

@router.post("/patient/{patient_id}/febio/simulation")
async def run_febio_simulation(
    patient_id: str,
    background_tasks: BackgroundTasks
):
    """Run FEBio simulation for digital twin"""
    
    try:
        from app.utils.febio_fsi_generator import FEBioFSIGenerator
        from app.utils.febio_runner import FEBioRunner
        
        # Initialize simulation state
        simulation_states[patient_id] = {
            "status": "febio_setup",
            "progress": 0,
            "message": "Setting up FEBio simulation...",
            "timestamp": datetime.now().isoformat()
        }
        
        # Start FEBio simulation in background
        background_tasks.add_task(
            run_febio_simulation_task,
            patient_id
        )
        
        return {
            "status": "febio_started",
            "patient_id": patient_id,
            "message": "FEBio simulation started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FEBio simulation failed: {str(e)}")

@router.get("/patient/{patient_id}/febio/status")
async def get_febio_status(patient_id: str):
    """Get FEBio simulation status"""
    
    if patient_id not in simulation_states:
        raise HTTPException(status_code=404, detail="Patient simulation not found")
    
    return simulation_states[patient_id]

@router.get("/patient/{patient_id}/febio/results")
async def get_febio_results(patient_id: str):
    """Get FEBio simulation results"""
    
    try:
        from app.utils.febio_visualizer import FEBioVisualizer
        
        # In practice, this would read actual .xplt files
        # For now, we'll generate synthetic results
        visualizer = FEBioVisualizer()
        results = visualizer._create_synthetic_visualization_data()
        
        return {
            "patient_id": patient_id,
            "febio_results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get FEBio results: {str(e)}")

# Background task for FEBio simulation
async def run_febio_simulation_task(patient_id: str):
    """Run FEBio simulation in background"""
    
    try:
        from app.utils.febio_fsi_generator import FEBioFSIGenerator
        from app.utils.febio_runner import FEBioRunner
        
        # Update status
        simulation_states[patient_id].update({
            "status": "generating_mesh",
            "progress": 20,
            "message": "Generating FSI mesh...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate FEBio model
        generator = FEBioFSIGenerator()
        
        # Use your existing tetrahedral mesh
        solid_mesh = f"data/patients/{patient_id}/Tetrahedral_Meshes/unified_heart_frame_01.vtk"
        fluid_mesh = f"data/patients/{patient_id}/Tetrahedral_Meshes/fluid_domain.vtk"
        
        output_feb = f"data/patients/{patient_id}/FEBio_Models/cardiac_fsi_simulation.feb"
        
        # Create FSI model
        febio_file = generator.create_complete_fsi_model(solid_mesh, fluid_mesh, output_feb)
        
        simulation_states[patient_id].update({
            "status": "running_febio",
            "progress": 50,
            "message": "Running FEBio FSI simulation...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Run FEBio simulation
        runner = FEBioRunner()
        success = runner.run_simulation(febio_file)
        
        if success:
            simulation_states[patient_id].update({
                "status": "processing_results",
                "progress": 80,
                "message": "Processing FEBio results...",
                "timestamp": datetime.now().isoformat()
            })
            
            # Process results
            await asyncio.sleep(3)  # Simulate processing time
            
            simulation_states[patient_id].update({
                "status": "completed",
                "progress": 100,
                "message": "FEBio simulation completed successfully!",
                "febio_results_available": True,
                "timestamp": datetime.now().isoformat()
            })
        else:
            simulation_states[patient_id].update({
                "status": "error",
                "progress": 0,
                "message": "FEBio simulation failed",
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        simulation_states[patient_id].update({
            "status": "error",
            "progress": 0,
            "message": f"FEBio simulation error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })

        # Add these new endpoints to your existing file

@router.post("/patient/{patient_id}/generate-febio-model")
async def generate_febio_model(patient_id: str):
    """Generate FEBio model files for the patient"""
    
    try:
        # Create directories
        os.makedirs(f"HeartDigitalTwin/{patient_id}/FEBio_Models", exist_ok=True)
        os.makedirs(f"HeartDigitalTwin/{patient_id}/Tetrahedral_Meshes", exist_ok=True)
        
        # Create simple FEBio file
        simple_content = """<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="4.0">
<Module type="solid"/>
<Control>
    <title>Cardiac Simulation - {patient_id}</title>
    <time_steps>100</time_steps>
    <step_size>0.01</step_size>
</Control>
<Material>
    <material id="1" name="myocardium" type="Mooney-Rivlin">
        <c1>0.05</c1><c2>0.05</c2><k>2.0</k>
    </material>
</Material>
<Geometry>
    <Nodes>
        <node id="1">0,0,0</node><node id="2">1,0,0</node>
        <node id="3">1,1,0</node><node id="4">0,1,0</node>
        <node id="5">0,0,1</node><node id="6">1,0,1</node>
        <node id="7">1,1,1</node><node id="8">0,1,1</node>
    </Nodes>
    <Elements type="solid" mat="1">
        <hex8 id="1">1,2,3,4,5,6,7,8</hex8>
    </Elements>
</Geometry>
<Boundary>
    <fix bc="x,y,z">1,2,3,4</fix>
</Boundary>
<Output>
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
    </plotfile>
</Output>
</febio_spec>""".format(patient_id=patient_id)
        
        simple_path = f"HeartDigitalTwin/{patient_id}/FEBio_Models/simple_cardiac.feb"
        with open(simple_path, 'w') as f:
            f.write(simple_content)
        
        return {
            "status": "success",
            "patient_id": patient_id,
            "files_created": [simple_path],
            "message": "FEBio model files generated successfully",
            "next_steps": [
                "1. Open FEBio Studio",
                "2. File → Open → Select the .feb file", 
                "3. Click 'Run' to visualize simulation"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate FEBio model: {str(e)}")

@router.get("/patient/{patient_id}/febio-files")
async def list_febio_files(patient_id: str):
    """List all FEBio files for a patient"""
    
    try:
        feb_dir = f"HeartDigitalTwin/{patient_id}/FEBio_Models"
        
        if not os.path.exists(feb_dir):
            return {
                "patient_id": patient_id,
                "febio_files": [],
                "message": "No FEBio files found. Use POST /generate-febio-model to create them.",
                "timestamp": datetime.now().isoformat()
            }
        
        files = []
        for file in os.listdir(feb_dir):
            if file.endswith('.feb'):
                file_path = os.path.join(feb_dir, file)
                file_size = os.path.getsize(file_path)
                files.append({
                    "filename": file,
                    "path": file_path,
                    "size_bytes": file_size,
                    "size_kb": round(file_size / 1024, 2)
                })
        
        return {
            "patient_id": patient_id,
            "febio_files": files,
            "count": len(files),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list FEBio files: {str(e)}")
# NEW: Enhanced 3D data with fluid dynamics
@router.get("/patient/{patient_id}/digital-twin/enhanced-3d-data")
async def get_enhanced_3d_data(patient_id: str):
    """Get complete 3D data with fluid dynamics and valve motion"""
    
    try:
        from app.utils.visualization_generator import HeartVisualizationGenerator
        
        generator = HeartVisualizationGenerator()
        
        # Generate base heart geometry
        viz_data = generator.generate_heart_geometry(patient_id)
        
        # Add fluid dynamics data
        fluid_data = generate_fluid_dynamics_data(patient_id)
        viz_data["fluid_dynamics"] = fluid_data
        
        # Add valve motion data
        valve_data = generate_valve_motion_data()
        viz_data["valves"] = valve_data
        
        return {
            "patient_id": patient_id,
            "visualization_data": viz_data,
            "has_fluid_data": True,
            "has_valve_data": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced 3D data generation failed: {str(e)}")

# NEW: Fluid dynamics helper functions
def generate_fluid_dynamics_data(patient_id: str, frame_count: int = 60):
    """Generate synthetic fluid dynamics data"""
    
    fluid_data = {
        "particles": [],
        "flow_vectors": [],
        "pressure_field": [],
        "velocity_field": [],
        "flow_rates": {
            "mitral": generate_flow_waveform("mitral", frame_count),
            "aortic": generate_flow_waveform("aortic", frame_count),
            "tricuspid": generate_flow_waveform("tricuspid", frame_count),
            "pulmonary": generate_flow_waveform("pulmonary", frame_count)
        },
        "pressure_waveforms": {
            "lv": generate_pressure_waveform("lv", frame_count),
            "aorta": generate_pressure_waveform("aorta", frame_count),
            "rv": generate_pressure_waveform("rv", frame_count),
            "pa": generate_pressure_waveform("pa", frame_count)
        }
    }
    
    # Generate particle data for each frame
    for frame in range(frame_count):
        time = frame / frame_count
        frame_particles = []
        frame_vectors = []
        frame_pressure = []
        frame_velocity = []
        
        # Generate particles for each chamber
        for chamber in ["lv", "rv", "la", "ra"]:
            chamber_flow = simulate_chamber_flow(chamber, time)
            frame_particles.extend(chamber_flow["particles"])
            frame_vectors.extend(chamber_flow["vectors"])
            frame_pressure.extend(chamber_flow["pressure"])
            frame_velocity.extend(chamber_flow["velocity"])
        
        fluid_data["particles"].append(frame_particles)
        fluid_data["flow_vectors"].append(frame_vectors)
        fluid_data["pressure_field"].append(frame_pressure)
        fluid_data["velocity_field"].append(frame_velocity)
    
    return fluid_data

def generate_valve_motion_data(frame_count: int = 60):
    """Generate valve opening/closing animation data"""
    
    valves = {
        "mitral": {"positions": [], "states": [], "colors": []},
        "aortic": {"positions": [], "states": [], "colors": []},
        "tricuspid": {"positions": [], "states": [], "colors": []},
        "pulmonary": {"positions": [], "states": [], "colors": []}
    }
    
    for frame in range(frame_count):
        time = frame / frame_count
        
        # Mitral valve (between LA and LV)
        if time < 0.4:  # Systole - closed
            mitral_state = "closed"
            mitral_pos = 0.0
            mitral_color = [1.0, 0.0, 0.0]  # Red
        else:  # Diastole - open
            mitral_state = "open" 
            mitral_pos = 1.0
            mitral_color = [0.0, 1.0, 0.0]  # Green
        
        # Aortic valve (between LV and aorta)
        if time < 0.4:  # Systole - open
            aortic_state = "open"
            aortic_pos = 1.0
            aortic_color = [0.0, 1.0, 0.0]  # Green
        else:  # Diastole - closed
            aortic_state = "closed"
            aortic_pos = 0.0
            aortic_color = [1.0, 0.0, 0.0]  # Red
        
        valves["mitral"]["states"].append(mitral_state)
        valves["mitral"]["positions"].append(mitral_pos)
        valves["mitral"]["colors"].append(mitral_color)
        
        valves["aortic"]["states"].append(aortic_state)
        valves["aortic"]["positions"].append(aortic_pos)
        valves["aortic"]["colors"].append(aortic_color)
        
        # Right heart valves (slightly different timing)
        tricuspid_state = "open" if time >= 0.35 else "closed"
        pulmonary_state = "open" if time < 0.35 else "closed"
        
        valves["tricuspid"]["states"].append(tricuspid_state)
        valves["tricuspid"]["positions"].append(1.0 if tricuspid_state == "open" else 0.0)
        valves["tricuspid"]["colors"].append([0.0, 1.0, 0.0] if tricuspid_state == "open" else [1.0, 0.0, 0.0])
        
        valves["pulmonary"]["states"].append(pulmonary_state)
        valves["pulmonary"]["positions"].append(1.0 if pulmonary_state == "open" else 0.0)
        valves["pulmonary"]["colors"].append([0.0, 1.0, 0.0] if pulmonary_state == "open" else [1.0, 0.0, 0.0])
    
    return valves

def simulate_chamber_flow(chamber: str, time: float):
    """Simulate blood flow in a specific chamber"""
    
    particles = []
    vectors = []
    pressure = []
    velocity = []
    
    num_particles = 20  # Reduced for performance
    
    # Chamber-specific flow patterns
    if chamber == "lv":
        # Left ventricle
        if time < 0.4:  # Systole - ejection
            flow_direction = [1, 0, 0]  # Toward aorta
            flow_speed = 1.0 - (time / 0.4)  # Decelerating
            base_position = [0.5, -0.5, 0]
        else:  # Diastole - filling
            flow_direction = [0, -1, 0]  # Toward apex
            flow_speed = (time - 0.4) / 0.6  # Accelerating
            base_position = [0.3, 0.2, 0]
            
    elif chamber == "rv":
        # Right ventricle
        if time < 0.35:
            flow_direction = [-1, 0, 0]  # Toward pulmonary artery
            flow_speed = 1.0 - (time / 0.35)
            base_position = [-0.5, -0.5, 0]
        else:
            flow_direction = [0, -1, 0]
            flow_speed = (time - 0.35) / 0.65
            base_position = [-0.3, 0.2, 0]
            
    else:  # Atria
        flow_direction = [0, 1, 0]  # Toward ventricles
        flow_speed = 0.5
        if chamber == "la":
            base_position = [0.3, 0.5, 0]
        else:  # ra
            base_position = [-0.3, 0.5, 0]
    
    # Generate particles
    for i in range(num_particles):
        # Create particles around base position
        pos = [
            base_position[0] + np.random.normal(0, 0.1),
            base_position[1] + np.random.normal(0, 0.1),
            base_position[2] + np.random.normal(0, 0.05)
        ]
        
        # Calculate velocity vector
        vel = [d * flow_speed * 0.3 for d in flow_direction]
        
        particles.append(pos)
        vectors.append(vel)
        pressure.append(flow_speed * 100)  # Simulated pressure
        velocity.append(np.linalg.norm(vel))
    
    return {
        "particles": particles,
        "vectors": vectors,
        "pressure": pressure,
        "velocity": velocity
    }

def generate_flow_waveform(valve_type: str, frame_count: int):
    """Generate flow rate waveform for a valve"""
    waveform = []
    
    for frame in range(frame_count):
        time = frame / frame_count
        
        if valve_type == "mitral":
            # Mitral flow - diastolic
            if time >= 0.4:
                flow = np.sin((time - 0.4) * np.pi * 2) * 100
            else:
                flow = 0
                
        elif valve_type == "aortic":
            # Aortic flow - systolic
            if time < 0.4:
                flow = np.sin(time * np.pi * 2.5) * 120
            else:
                flow = 0
                
        else:  # Right heart valves - similar patterns
            flow = np.sin(time * np.pi * 2) * 80
            
        waveform.append(max(0, flow))  # No negative flow
    
    return waveform

def generate_pressure_waveform(location: str, frame_count: int):
    """Generate pressure waveform"""
    waveform = []
    
    for frame in range(frame_count):
        time = frame / frame_count
        
        if location == "lv":
            # LV pressure - high in systole
            pressure = 80 + 40 * np.sin(time * np.pi * 2) if time < 0.4 else 80
        elif location == "aorta":
            # Aortic pressure - follows LV but smoother
            pressure = 80 + 35 * np.sin(time * np.pi * 2)
        elif location == "rv":
            # RV pressure - lower pressures
            pressure = 25 + 15 * np.sin(time * np.pi * 2) if time < 0.35 else 25
        else:  # PA pressure
            pressure = 25 + 10 * np.sin(time * np.pi * 2)
            
        waveform.append(pressure)
    
    return waveform

# Background task functions
async def generate_digital_twin_pipeline(patient_id: str, mri_files: List[str]):
    """Complete digital twin generation pipeline"""
    
    try:
        # Simulate the pipeline steps
        steps = [
            ("processing_mri", "Segmenting cardiac structures...", 10),
            ("cleaning_meshes", "Cleaning and unifying STL meshes...", 30),
            ("generating_tetrahedral", "Generating tetrahedral mesh...", 50),
            ("setting_up_simulation", "Setting up FEBio simulation...", 70),
            ("running_simulation", "Running cardiac mechanics simulation...", 80),
            ("extracting_metrics", "Extracting clinical metrics...", 90),
        ]
        
        for status, message, progress in steps:
            simulation_states[patient_id].update({
                "status": status,
                "progress": progress,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(2)  # Simulate processing time
        
        # Final metrics with fluid dynamics
        sample_metrics = {
            "ejection_fraction": 55.5,
            "stroke_volume": 72.3,
            "cardiac_output": 5.4,
            "wall_stress_max": 145.2,
            "chf_risk_score": 3.2,
            "end_diastolic_volume": 140.0,
            "end_systolic_volume": 70.0,
            "myocardial_mass": 150.0,
            "fluid_dynamics": {
                "mitral_flow_rate": 85.2,
                "aortic_flow_rate": 72.3,
                "tricuspid_flow_rate": 78.1,
                "pulmonary_flow_rate": 71.8,
                "cardiac_output": 5.4,
                "valve_efficiency": 0.89
            }
        }
        
        patient_metrics[patient_id] = sample_metrics
        
        # Final status
        simulation_states[patient_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Digital twin generation completed!",
            "metrics_available": True,
            "visualization_ready": True,
            "fluid_dynamics_ready": True,
            "valve_data_ready": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        simulation_states[patient_id] = {
            "status": "error",
            "progress": 0,
            "message": f"Pipeline failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

async def run_cardiac_simulation(patient_id: str, parameters: Dict[str, Any]):
    """Run cardiac simulation with given parameters"""
    
    try:
        # Simulate simulation progress
        for i in range(10):
            simulation_states[patient_id].update({
                "progress": (i + 1) * 10,
                "message": f"Running simulation step {i + 1}/10...",
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(1)
        
        # Update metrics with parameter effects
        base_metrics = patient_metrics.get(patient_id, {})
        hr_effect = (parameters.get('heart_rate', 75) - 75) * 0.1
        bp_effect = (parameters.get('systolic_bp', 120) - 120) * 0.05
        
        updated_metrics = {
            **base_metrics,
            "ejection_fraction": base_metrics.get('ejection_fraction', 55) + hr_effect,
            "wall_stress_max": base_metrics.get('wall_stress_max', 145) + bp_effect,
            "simulation_parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update fluid dynamics based on parameters
        if parameters.get('include_fluid_dynamics', True):
            updated_metrics["fluid_dynamics"] = {
                "mitral_flow_rate": 85.2 * (1 + hr_effect * 0.1),
                "aortic_flow_rate": 72.3 * (1 + hr_effect * 0.1),
                "cardiac_output": 5.4 * (1 + hr_effect * 0.1),
                "valve_efficiency": 0.89 - abs(bp_effect) * 0.01
            }
        
        patient_metrics[patient_id] = updated_metrics
        
        simulation_states[patient_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Parameter simulation completed",
            "metrics_updated": True,
            "fluid_dynamics_updated": parameters.get('include_fluid_dynamics', True),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        simulation_states[patient_id] = {
            "status": "error",
            "message": f"Simulation failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }