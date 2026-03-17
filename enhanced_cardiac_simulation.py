# Save as: 8_enhanced_cardiac_simulation.py
def create_advanced_febio_model(mesh_file, output_feb):
    """
    Creates FEBio file with realistic heart motion and fluid dynamics
    """
    
    advanced_template = f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="3.0">
<Module type="solid"/>

<Control>
    <title>Cardiac Cycle Simulation</title>
    <time_steps>200</time_steps>
    <step_size>0.005</step_size>
    <max_refs>50</max_refs>
    <dtol>0.001</dtol>
    <etol>0.01</etol>
    <rtol>0.001</rtol>
    <lstol>0.9</lstol>
    <analysis>static</analysis>
    <time_stepper>
        <dtmin>0.001</dtmin>
        <dtmax>0.01</dtmax>
        <max_retries>5</max_retries>
        <opt_iter>10</opt_iter>
    </time_stepper>
</Control>

<Material>
    <!-- Hyperelastic Myocardium with Fiber Orientation -->
    <material id="1" name="myocardium" type="Holzapfel-Ogden">
        <c>0.2</c>
        <k1>2.0</k1>
        <k2>10.0</k2>
        <kappa>0.1</kappa>
        <fibers type="vector">0, 1, 0</fibers>
    </material>
    
    <!-- Active Cardiac Muscle Contraction -->
    <material id="2" name="active_contraction" type="active contraction">
        <T0>120.0</T0>
        <ca0>0.1</ca0>
        <eta>0.1</eta>
        <k>10.0</k>
        <ttype>1</ttype>
        <lmax>1.2</lmax>
    </material>
</Material>

<Geometry>
    <Nodes file="{mesh_file}" format="vtk"/>
    <Elements type="solid" mat="1">1</Elements>
    
    <!-- Define Surfaces for Boundary Conditions -->
    <Surface name="lv_endocardium">
        <!-- You need to define the surface elements for LV -->
        <tri3 lid="1">1, 2, 3</tri3>
        <!-- Add all surface elements from your mesh -->
    </Surface>
    
    <Surface name="rv_endocardium">
        <!-- RV surface elements -->
    </Surface>
    
    <Surface name="base_surface">
        <!-- Heart base for fixation -->
    </Surface>
</Geometry>

<Boundary>
    <!-- Fix the base of the heart -->
    <fix name="fixed_base" bc="x,y,z">
        <surface>base_surface</surface>
    </fix>
    
    <!-- Left Ventricle Pressure (Cardiac Cycle) -->
    <prescribe name="lv_pressure" bc="p" scale="1.0">
        <surface>lv_endocardium</surface>
        <lc>1</lc>
    </prescribe>
    
    <!-- Right Ventricle Pressure -->
    <prescribe name="rv_pressure" bc="p" scale="1.0">
        <surface>rv_endocardium</surface>
        <lc>2</lc>
    </prescribe>
</Boundary>

<Loads>
    <!-- Complete Cardiac Cycle Pressure Curve (mmHg) -->
    <loadcurve id="1" type="linear" extend="constant">
        <!-- LV Pressure: 0-1 second cardiac cycle -->
        <loadpoint>0.0, 8.0</loadpoint>    <!-- Early diastole -->
        <loadpoint>0.1, 10.0</loadpoint>   <!-- Late diastole -->
        <loadpoint>0.2, 12.0</loadpoint>   <!-- Atrial systole -->
        <loadpoint>0.3, 120.0</loadpoint>  <!-- Peak systole -->
        <loadpoint>0.4, 100.0</loadpoint>  <!-- Late systole -->
        <loadpoint>0.5, 8.0</loadpoint>    <!-- Early diastole -->
        <loadpoint>1.0, 8.0</loadpoint>    <!-- End cycle -->
    </loadcurve>
    
    <loadcurve id="2" type="linear" extend="constant">
        <!-- RV Pressure -->
        <loadpoint>0.0, 4.0</loadpoint>
        <loadpoint>0.3, 25.0</loadpoint>
        <loadpoint>0.5, 4.0</loadpoint>
        <loadpoint>1.0, 4.0</loadpoint>
    </loadcurve>
    
    <!-- Active Contraction Timing -->
    <loadcurve id="3" type="linear">
        <!-- Muscle activation (0=relaxed, 1=fully contracted) -->
        <loadpoint>0.0, 0.0</loadpoint>
        <loadpoint>0.15, 0.0</loadpoint>
        <loadpoint>0.2, 1.0</loadpoint>
        <loadpoint>0.4, 0.0</loadpoint>
        <loadpoint>1.0, 0.0</loadpoint>
    </loadcurve>
</Loads>

<Output>
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/> 
        <var type="strain"/>
        <var type="pressure"/>
        <var type="volume"/>
        <var type="element strain"/>
        <var type="element stress"/>
    </plotfile>
    
    <logfile>
        <node_data data="displacement"/>
        <node_data data="pressure"/>
        <element_data data="stress"/>
        <element_data data="strain"/>
        <surface_data data="pressure" surface="lv_endocardium"/>
        <surface_data data="pressure" surface="rv_endocardium"/>
    </logfile>
</Output>
</febio_spec>
"""
    
    with open(output_feb, 'w') as f:
        f.write(advanced_template)
    
    print(f"Advanced FEBio model created: {output_feb}")

# Create enhanced simulation
mesh_file = r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\3d slicer-digital_twin\heart_tetrahedral_ascii.vtk"
output_feb = r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\3d slicer-digital_twin\heart_simulation.feb"

create_advanced_febio_model(mesh_file, output_feb)