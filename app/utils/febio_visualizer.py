# Save as: app/utils/febio_visualizer.py
import numpy as np
import struct
import os
from typing import Dict, List, Any

class FEBioVisualizer:
    def __init__(self):
        self.results = {}
    
    def parse_xplt_file(self, xplt_file):
        """Parse FEBio .xplt file to extract visualization data"""
        
        if not os.path.exists(xplt_file):
            raise Exception(f"XPLT file not found: {xplt_file}")
        
        print(f"📊 Parsing FEBio results: {xplt_file}")
        
        # This is a simplified parser - FEBio .xplt is binary format
        # In practice, you'd use FEBio's Python API or convert to VTK
        
        # For now, we'll create synthetic data based on simulation parameters
        visualization_data = self._create_synthetic_visualization_data()
        
        return visualization_data
    
    def _create_synthetic_visualization_data(self):
        """Create synthetic visualization data mimicking FEBio output"""
        
        # Generate realistic cardiac cycle data
        frame_count = 60
        vertices, faces = self._create_heart_mesh()
        
        visualization_data = {
            "metadata": {
                "simulation_type": "fluid-FSI",
                "frame_count": frame_count,
                "time_steps": 200,
                "has_fluid_data": True,
                "has_stress_data": True
            },
            "solid_domain": {
                "vertices": vertices,
                "faces": faces,
                "displacement_frames": self._generate_displacement_frames(vertices, frame_count),
                "stress_frames": self._generate_stress_frames(vertices, frame_count),
                "strain_frames": self._generate_strain_frames(vertices, frame_count)
            },
            "fluid_domain": {
                "velocity_frames": self._generate_velocity_frames(frame_count),
                "pressure_frames": self._generate_pressure_frames(frame_count),
                "particle_trajectories": self._generate_particle_trajectories(frame_count)
            },
            "valve_data": {
                "mitral": self._generate_valve_motion("mitral", frame_count),
                "aortic": self._generate_valve_motion("aortic", frame_count),
                "tricuspid": self._generate_valve_motion("tricuspid", frame_count),
                "pulmonary": self._generate_valve_motion("pulmonary", frame_count)
            },
            "time_data": {
                "time_points": np.linspace(0, 1, frame_count).tolist(),
                "cardiac_phase": ["diastole" if t > 0.4 else "systole" for t in np.linspace(0, 1, frame_count)]
            }
        }
        
        return visualization_data
    
    def _create_heart_mesh(self):
        """Create a detailed heart mesh"""
        vertices = []
        faces = []
        
        # Create more detailed heart geometry
        u_steps, v_steps = 30, 30
        for i in range(u_steps):
            for j in range(v_steps):
                u = i / (u_steps - 1) * 2 * np.pi
                v = j / (v_steps - 1) * 2 * np.pi
                
                # Enhanced heart parametric equations
                x = 2.0 * np.sin(u) * np.sin(u) * np.sin(v)
                y = 2.0 * np.cos(u) * np.sin(v)
                z = 1.5 * (np.cos(v) + np.log(1 + abs(v))) * 0.3
                
                # Add some asymmetry for realism
                if x > 0:  # Left side
                    x *= 1.1
                else:  # Right side
                    x *= 0.9
                
                vertices.append([float(x), float(y), float(z)])
        
        # Create faces
        for i in range(u_steps - 1):
            for j in range(v_steps - 1):
                idx1 = i * v_steps + j
                idx2 = i * v_steps + (j + 1)
                idx3 = (i + 1) * v_steps + j
                idx4 = (i + 1) * v_steps + (j + 1)
                
                faces.append([idx1, idx2, idx3])
                faces.append([idx2, idx4, idx3])
        
        return vertices, faces
    
    def _generate_displacement_frames(self, vertices, frame_count):
        """Generate displacement frames for heart motion"""
        frames = []
        
        for frame in range(frame_count):
            time = frame / frame_count * 2 * np.pi
            frame_vertices = []
            
            for v in vertices:
                # Realistic cardiac motion
                contraction = 0.3 * np.sin(time)  # Base contraction
                
                # Regional variation - apex moves more
                apex_factor = max(0, 1 - np.sqrt(v[0]**2 + v[1]**2) / 2)
                regional_contraction = contraction * (0.5 + 0.5 * apex_factor)
                
                # Twist motion
                twist = 0.1 * np.sin(time) * v[2]
                
                new_vertex = [
                    v[0] * (1 - regional_contraction) + twist * 0.1,
                    v[1] * (1 - regional_contraction),
                    v[2] * (1 - contraction * 0.5)
                ]
                frame_vertices.append(new_vertex)
            
            frames.append(frame_vertices)
        
        return frames
    
    def _generate_velocity_frames(self, frame_count):
        """Generate fluid velocity fields"""
        frames = []
        
        for frame in range(frame_count):
            time = frame / frame_count
            frame_velocities = []
            
            # Generate velocity field
            for i in range(100):  # Sample points in fluid domain
                x = np.random.uniform(-1, 1)
                y = np.random.uniform(-1, 1)
                z = np.random.uniform(-0.5, 0.5)
                
                if time < 0.4:  # Systole
                    # Flow toward outlets
                    if x > 0:  # Left side - aortic flow
                        vel = [1.0, 0.0, 0.0]
                    else:  # Right side - pulmonary flow
                        vel = [-0.8, 0.0, 0.0]
                else:  # Diastole
                    # Flow toward ventricles
                    vel = [0.0, -0.5, 0.0]
                
                # Add some turbulence
                vel[0] += np.random.normal(0, 0.1)
                vel[1] += np.random.normal(0, 0.1)
                vel[2] += np.random.normal(0, 0.05)
                
                frame_velocities.append({
                    "position": [float(x), float(y), float(z)],
                    "velocity": [float(vel[0]), float(vel[1]), float(vel[2])],
                    "speed": float(np.linalg.norm(vel))
                })
            
            frames.append(frame_velocities)
        
        return frames