# Update app/utils/visualization_generator.py
from app.utils.advanced_febio_generator import AdvancedCardiacSimulation


class HeartVisualizationGenerator:
    def __init__(self):
        self.mesh_cache = {}
        self.fluid_simulator = AdvancedCardiacSimulation()
    
    def generate_heart_geometry(self, patient_id: str, frame_count: int = 60):
        """Generate 3D heart geometry with fluid motion"""
        
        # Generate base heart geometry
        vertices, faces = self._create_heart_mesh()
        frames = self._generate_animation_frames(vertices, frame_count)
        
        # Generate fluid flow data
        base_geometry = {
            "chambers": {
                "lv": self._extract_chamber_data("lv", vertices, faces),
                "rv": self._extract_chamber_data("rv", vertices, faces),
                "la": self._extract_chamber_data("la", vertices, faces),
                "ra": self._extract_chamber_data("ra", vertices, faces)
            }
        }
        
        fluid_data = self.fluid_simulator.generate_fluid_flow_data(base_geometry, frame_count)
        
        visualization_data = {
            "metadata": {
                "patient_id": patient_id,
                "frame_count": frame_count,
                "vertex_count": len(vertices),
                "face_count": len(faces),
                "has_fluid_data": True
            },
            "static_geometry": {
                "vertices": vertices,
                "faces": faces,
                "normals": self._calculate_normals(vertices, faces)
            },
            "animation": {
                "frames": frames,
                "displacements": self._generate_displacement_data(vertices, frame_count),
                "stress_data": self._generate_stress_data(vertices, frame_count)
            },
            "fluid_dynamics": fluid_data,
            "chambers": base_geometry["chambers"],
            "valves": self._generate_valve_motion(frame_count)
        }
        
        return visualization_data
    
    def _generate_valve_motion(self, frame_count: int):
        """Generate valve opening/closing animation"""
        valves = {
            "mitral": {"positions": [], "states": []},
            "aortic": {"positions": [], "states": []},
            "tricuspid": {"positions": [], "states": []},
            "pulmonary": {"positions": [], "states": []}
        }
        
        for frame in range(frame_count):
            time = frame / frame_count
            
            # Mitral valve (between LA and LV)
            if time < 0.4:  # Systole - closed
                mitral_state = "closed"
                mitral_pos = 0.0
            else:  # Diastole - open
                mitral_state = "open" 
                mitral_pos = 1.0
            
            # Aortic valve (between LV and aorta)
            if time < 0.4:  # Systole - open
                aortic_state = "open"
                aortic_pos = 1.0
            else:  # Diastole - closed
                aortic_state = "closed"
                aortic_pos = 0.0
            
            valves["mitral"]["states"].append(mitral_state)
            valves["mitral"]["positions"].append(mitral_pos)
            valves["aortic"]["states"].append(aortic_state)
            valves["aortic"]["positions"].append(aortic_pos)
            
            # Similar logic for right heart valves
            valves["tricuspid"]["states"].append("open" if time >= 0.35 else "closed")
            valves["pulmonary"]["states"].append("open" if time < 0.35 else "closed")
        
        return valves