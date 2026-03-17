# Save as: app/utils/advanced_febio_generator.py
import numpy as np
import os

class AdvancedCardiacSimulation:
    def __init__(self):
        self.fluid_particles = []
        self.blood_flow_vectors = []
    
    def create_fsi_febio_model(self, mesh_file, output_feb):
        """Create FEBio model with Fluid-Structure Interaction"""
        
        fsi_template = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="4.0">
<Module type="fluid-FSI"/>

<Control>
    <title>Cardiac FSI Simulation</title>
    <time_steps>200</time_steps>
    <step_size>0.005</step_size>
    <analysis>dynamic</analysis>
    <plot_level>PLOT_MAJOR_ITRS</plot_level>
</Control>

<Globals>
    <Constants>
        <T>0</T>
        <R>0</R>
        <Fc>0</Fc>
    </Constants>
</Globals>

<Material>
    <!-- Myocardium (Solid) -->
    <material id="1" name="myocardium" type="Holzapfel-Ogden">
        <c>0.2</c>
        <k1>2.0</k1>
        <k2>10.0</k2>
        <kappa>0.1</kappa>
        <fibers type="vector">0, 1, 0</fibers>
    </material>
    
    <!-- Active Contraction -->
    <material id="2" name="active_contraction" type="active contraction">
        <T0>120.0</T0>
        <ca0>0.1</ca0>
        <eta>0.1</eta>
        <k>10.0</k>
        <ttype>1</ttype>
    </material>
    
    <!-- Blood (Fluid) -->
    <material id="3" name="blood" type="Newtonian viscous">
        <density>1.06</density>
        <viscosity>0.04</viscosity>
    </material>
</Material>

<Geometry>
    <!-- Solid Domain - Heart Muscle -->
    <Nodes file="{mesh_file}" format="vtk"/>
    <Elements type="solid" mat="1">1</Elements>
    
    <!-- Fluid Domain - Blood Pool -->
    <Elements type="fluid" mat="3">2</Elements>
    
    <!-- Surfaces for FSI -->
    <Surface name="endocardial_surface">
        <!-- This should be the inner surface of ventricles -->
        <tri3 lid="1">1, 2, 3</tri3>
        <!-- Add actual surface elements from your mesh -->
    </Surface>
    
    <Surface name="inlet_surface">
        <!-- Mitral valve area -->
    </Surface>
    
    <Surface name="outlet_surface">
        <!-- Aortic valve area -->
    </Surface>
</Geometry>

<Boundary>
    <!-- Fix heart base -->
    <fix bc="x,y,z">
        <surface>base_surface</surface>
    </fix>
    
    <!-- FSI Interface -->
    <fluid-FSI>
        <surface>endocardial_surface</surface>
    </fluid-FSI>
    
    <!-- Fluid Boundary Conditions -->
    <prescribe name="inlet_flow" bc="q" scale="1.0">
        <surface>inlet_surface</surface>
        <lc>1</lc>
    </prescribe>
    
    <prescribe name="outlet_pressure" bc="p" scale="1.0">
        <surface>outlet_surface</surface>
        <lc>2</lc>
    </prescribe>
</Boundary>

<Loads>
    <!-- Cardiac Cycle -->
    <loadcurve id="1" type="linear">
        <!-- Inlet Flow Curve (ml/s) -->
        <loadpoint>0.0, 0.0</loadpoint>    <!-- Diastole start -->
        <loadpoint>0.1, 200.0</loadpoint>  <!-- Rapid filling -->
        <loadpoint>0.2, 100.0</loadpoint>  <!-- Diastasis -->
        <loadpoint>0.3, 150.0</loadpoint>  <!-- Atrial systole -->
        <loadpoint>0.4, 0.0</loadpoint>    <!-- Systole -->
        <loadpoint>1.0, 0.0</loadpoint>    <!-- Cycle end -->
    </loadcurve>
    
    <loadcurve id="2" type="linear">
        <!-- Outlet Pressure (mmHg) -->
        <loadpoint>0.0, 80.0</loadpoint>   <!-- Diastolic pressure -->
        <loadpoint>0.3, 120.0</loadpoint>  <!-- Systolic pressure -->
        <loadpoint>0.5, 80.0</loadpoint>   <!-- Back to diastolic -->
        <loadpoint>1.0, 80.0</loadpoint>
    </loadcurve>
    
    <!-- Active Contraction -->
    <loadcurve id="3" type="linear">
        <loadpoint>0.0, 0.0</loadpoint>
        <loadpoint>0.2, 1.0</loadpoint>
        <loadpoint>0.4, 0.0</loadpoint>
        <loadpoint>1.0, 0.0</loadpoint>
    </loadcurve>
</Loads>

<Output>
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
        <var type="fluid pressure"/>
        <var type="fluid velocity"/>
        <var type="volume ratio"/>
        <var type="element strain"/>
    </plotfile>
    
    <logfile>
        <node_data data="displacement"/>
        <node_data data="fluid pressure"/>
        <node_data data="fluid velocity"/>
        <element_data data="stress"/>
        <element_data data="strain"/>
    </logfile>
</Output>
</febio_spec>
"""
        
        os.makedirs(os.path.dirname(output_feb), exist_ok=True)
        with open(output_feb, 'w') as f:
            f.write(fsi_template)
        
        print(f"FSI FEBio model created: {output_feb}")
    
    def generate_fluid_flow_data(self, heart_geometry, frame_count=60):
        """Generate synthetic blood flow data for visualization"""
        
        fluid_data = {
            "particles": [],
            "flow_vectors": [],
            "pressure_field": [],
            "velocity_field": []
        }
        
        # Generate blood particles in chambers
        for frame in range(frame_count):
            time = frame / frame_count
            frame_particles = []
            frame_vectors = []
            frame_pressure = []
            frame_velocity = []
            
            # Simulate blood flow through chambers
            for chamber in ["lv", "rv", "la", "ra"]:
                chamber_flow = self._simulate_chamber_flow(chamber, time, heart_geometry)
                frame_particles.extend(chamber_flow["particles"])
                frame_vectors.extend(chamber_flow["vectors"])
                frame_pressure.extend(chamber_flow["pressure"])
                frame_velocity.extend(chamber_flow["velocity"])
            
            fluid_data["particles"].append(frame_particles)
            fluid_data["flow_vectors"].append(frame_vectors)
            fluid_data["pressure_field"].append(frame_pressure)
            fluid_data["velocity_field"].append(frame_velocity)
        
        return fluid_data
    
    def _simulate_chamber_flow(self, chamber, time, geometry):
        """Simulate blood flow in a specific chamber"""
        
        particles = []
        vectors = []
        pressure = []
        velocity = []
        
        # Chamber-specific flow patterns
        if chamber == "lv":
            # Left ventricle - systolic ejection
            if time < 0.4:  # Systole
                flow_direction = [1, 0, 0]  # Toward aorta
                flow_speed = 1.0 - (time / 0.4)  # Decelerating
            else:  # Diastole
                flow_direction = [0, -1, 0]  # Toward apex
                flow_speed = (time - 0.4) / 0.6  # Accelerating
        elif chamber == "rv":
            # Right ventricle - similar but different timing
            if time < 0.35:
                flow_direction = [-1, 0, 0]  # Toward pulmonary artery
                flow_speed = 1.0 - (time / 0.35)
            else:
                flow_direction = [0, -1, 0]
                flow_speed = (time - 0.35) / 0.65
        else:  # Atria
            flow_direction = [0, 1, 0]  # Toward ventricles
            flow_speed = 0.5
        
        # Generate particles in chamber volume
        chamber_vertices = geometry["chambers"][chamber]["vertices"]
        num_particles = min(50, len(chamber_vertices) // 10)
        
        for i in range(num_particles):
            if i < len(chamber_vertices):
                base_pos = chamber_vertices[i]
                
                # Add some randomness
                pos = [
                    base_pos[0] + np.random.normal(0, 0.02),
                    base_pos[1] + np.random.normal(0, 0.02),
                    base_pos[2] + np.random.normal(0, 0.02)
                ]
                
                # Calculate velocity vector
                vel = [d * flow_speed * 0.5 for d in flow_direction]
                
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