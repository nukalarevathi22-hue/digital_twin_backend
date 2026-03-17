# Save as: app/utils/febio_fsi_generator.py
import os
import numpy as np

class FEBioFSIGenerator:
    def __init__(self):
        self.mesh_data = None
    
    def create_complete_fsi_model(self, solid_mesh_file, fluid_mesh_file, output_feb):
        """Create complete FSI model for heart simulation"""
        
        fsi_model = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="4.0">
<Module type="fluid-FSI"/>

<Control>
    <title>Cardiac FSI Simulation - Digital Twin</title>
    <time_steps>200</time_steps>
    <step_size>0.005</step_size>
    <analysis>dynamic</analysis>
    <plot_level>PLOT_MAJOR_ITRS</plot_level>
    <plot_zero_state>1</plot_zero_state>
    <plot_range>0,1</plot_range>
    <output_level>OUTPUT_MAJOR_ITRS</output_level>
</Control>

<Globals>
    <Constants>
        <T>37</T>
        <R>0</R>
        <Fc>0</Fc>
    </Constants>
</Globals>

<Material>
    <!-- Myocardium Material (Holzapfel-Ogden for anisotropic behavior) -->
    <material id="1" name="myocardium" type="Holzapfel-Ogden">
        <c>0.2</c>
        <k1>2.0</k1>
        <k2>10.0</k2>
        <kappa>0.1</kappa>
        <fibers type="local">
            <fiber type="vector">0, 1, 0</fiber>
        </fibers>
    </material>
    
    <!-- Active Contraction Material -->
    <material id="2" name="active_contraction" type="active contraction">
        <T0>120.0</T0>
        <ca0>0.1</ca0>
        <eta>0.1</eta>
        <k>10.0</k>
        <ttype>1</ttype>
        <lmax>1.2</lmax>
    </material>
    
    <!-- Blood Material (Newtonian Fluid) -->
    <material id="3" name="blood" type="Newtonian viscous">
        <density>1.06</density>
        <viscosity>0.04</viscosity>
    </material>
    
    <!-- Valve Material (Elastic) -->
    <material id="4" name="valve_tissue" type="Mooney-Rivlin">
        <c1>0.5</c1>
        <c2>0.5</c2>
        <k>10.0</k>
    </material>
</Material>

<Geometry>
    <!-- Solid Domain - Heart Muscle -->
    <Nodes file="{solid_mesh_file}" format="vtk"/>
    <Elements type="solid" mat="1">1</Elements>
    
    <!-- Fluid Domain - Blood Pool -->
    <Nodes file="{fluid_mesh_file}" format="vtk"/>
    <Elements type="fluid" mat="3">2</Elements>
    
    <!-- Valve Elements -->
    <Elements type="shell" mat="4">3</Elements>
    
    <!-- Surfaces for Boundary Conditions -->
    <Surface name="endocardial_surface">
        <tri3 lid="1">1, 2, 3</tri3>
        <tri3 lid="2">4, 5, 6</tri3>
        <!-- Add actual surface elements from your mesh -->
    </Surface>
    
    <Surface name="base_surface">
        <tri3 lid="1">7, 8, 9</tri3>
        <!-- Heart base fixation -->
    </Surface>
    
    <Surface name="inlet_surface">
        <!-- Mitral valve inflow area -->
    </Surface>
    
    <Surface name="outlet_surface">
        <!-- Aortic valve outflow area -->
    </Surface>
    
    <Surface name="valve_surface">
        <!-- Valve leaflet surfaces -->
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
    
    <!-- Fluid Inlet Boundary Condition -->
    <prescribe name="inlet_flow" bc="q" scale="1.0">
        <surface>inlet_surface</surface>
        <lc>1</lc>
    </prescribe>
    
    <!-- Fluid Outlet Boundary Condition -->
    <prescribe name="outlet_pressure" bc="p" scale="1.0">
        <surface>outlet_surface</surface>
        <lc>2</lc>
    </prescribe>
    
    <!-- Valve Constraints -->
    <rigid body="1">
        <fixed bc="RX,RY,RZ">1</fixed>
    </rigid>
</Boundary>

<Loads>
    <!-- Cardiac Cycle Load Curves -->
    
    <!-- Inlet Flow Waveform (ml/s) -->
    <loadcurve id="1" type="linear" extend="repeat">
        <loadpoint>0.00, 0.0</loadpoint>    <!-- Cycle start -->
        <loadpoint>0.05, 50.0</loadpoint>   <!-- Early filling -->
        <loadpoint>0.10, 200.0</loadpoint>  <!-- Peak E-wave -->
        <loadpoint>0.20, 80.0</loadpoint>   <!-- Diastasis -->
        <loadpoint>0.25, 150.0</loadpoint>  <!-- A-wave -->
        <loadpoint>0.30, 0.0</loadpoint>    <!-- End diastole -->
        <loadpoint>0.40, 0.0</loadpoint>    <!-- Systole -->
        <loadpoint>1.00, 0.0</loadpoint>    <!-- Cycle end -->
    </loadcurve>
    
    <!-- Outlet Pressure Waveform (mmHg) -->
    <loadcurve id="2" type="linear" extend="repeat">
        <loadpoint>0.00, 80.0</loadpoint>   <!-- Diastolic -->
        <loadpoint>0.10, 85.0</loadpoint>   <!-- Early systole -->
        <loadpoint>0.20, 120.0</loadpoint>  <!-- Peak systole -->
        <loadpoint>0.30, 110.0</loadpoint>  <!-- Late systole -->
        <loadpoint>0.40, 80.0</loadpoint>   <!-- Back to diastolic -->
        <loadpoint>1.00, 80.0</loadpoint>   <!-- Cycle end -->
    </loadcurve>
    
    <!-- Active Contraction Timing -->
    <loadcurve id="3" type="linear" extend="repeat">
        <loadpoint>0.00, 0.0</loadpoint>    <!-- Relaxed -->
        <loadpoint>0.15, 0.0</loadpoint>    <!-- Start contraction -->
        <loadpoint>0.20, 1.0</loadpoint>    <!-- Peak contraction -->
        <loadpoint>0.35, 0.5</loadpoint>    <!-- Relaxing -->
        <loadpoint>0.40, 0.0</loadpoint>    <!-- Fully relaxed -->
        <loadpoint>1.00, 0.0</loadpoint>    <!-- Cycle end -->
    </loadcurve>
    
    <!-- Valve Motion Control -->
    <loadcurve id="4" type="linear" extend="repeat">
        <!-- Mitral valve closure timing -->
        <loadpoint>0.00, 1.0</loadpoint>    <!-- Open -->
        <loadpoint>0.35, 1.0</loadpoint>    <!-- Start closing -->
        <loadpoint>0.40, 0.0</loadpoint>    <!-- Closed -->
        <loadpoint>0.80, 0.0</loadpoint>    <!-- Start opening -->
        <loadpoint>0.85, 1.0</loadpoint>    <!-- Open -->
        <loadpoint>1.00, 1.0</loadpoint>    <!-- Cycle end -->
    </loadcurve>
</Loads>

<Output>
    <!-- Detailed plot file for visualization -->
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
        <var type="strain"/>
        <var type="fluid pressure"/>
        <var type="fluid velocity"/>
        <var type="fluid flux"/>
        <var type="volume ratio"/>
        <var type="element strain"/>
        <var type="element stress"/>
        <var type="contact pressure"/>
    </plotfile>
    
    <!-- Log file for data extraction -->
    <logfile>
        <node_data data="displacement"/>
        <node_data data="fluid pressure"/>
        <node_data data="fluid velocity"/>
        <element_data data="stress"/>
        <element_data data="strain"/>
        <surface_data data="fluid pressure" surface="endocardial_surface"/>
        <surface_data data="fluid velocity" surface="outlet_surface"/>
    </logfile>
    
    <!-- Additional output for visualization -->
    <output>
        <data type="fluid velocity" file="fluid_velocity.txt"/>
        <data type="displacement" file="displacement.txt"/>
        <data type="stress" file="stress.txt"/>
    </output>
</Output>

<Step>
    <analysis>dynamic</analysis>
    <time_steps>200</time_steps>
    <step_size>0.005</step_size>
    <max_refs>15</max_refs>
    <max_ups>10</max_ups>
    <dtol>0.001</dtol>
    <etol>0.01</etol>
    <rtol>0.001</rtol>
    <lstol>0.9</lstol>
    <time_stepper>
        <dtmin>0.001</dtmin>
        <dtmax>0.01</dtmax>
        <max_retries>5</max_retries>
        <opt_iter>10</opt_iter>
        <aggressiveness>1</aggressiveness>
    </time_stepper>
</Step>
</febio_spec>
"""
        
        os.makedirs(os.path.dirname(output_feb), exist_ok=True)
        with open(output_feb, 'w') as f:
            f.write(fsi_model)
        
        print(f"✅ FSI FEBio model created: {output_feb}")
        return output_feb

    def generate_fluid_mesh(self, solid_mesh_file, output_fluid_mesh):
        """Generate fluid domain mesh from solid mesh"""
        # This creates a simplified fluid mesh inside the heart
        # In practice, you'd use mesh generation software
        pass