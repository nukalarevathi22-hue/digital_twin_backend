# Save as: create_febio_file.py
import os
import numpy as np

def create_simple_febio_file():
    """Create a basic but working FEBio file"""
    
    # Create directory structure
    os.makedirs("HeartDigitalTwin/Patient_001/FEBio_Models", exist_ok=True)
    os.makedirs("HeartDigitalTwin/Patient_001/Tetrahedral_Meshes", exist_ok=True)
    
    # Simple FEBio template
    feb_content = """<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="4.0">
<Module type="solid"/>

<Control>
    <title>Cardiac Digital Twin Simulation</title>
    <time_steps>100</time_steps>
    <step_size>0.01</step_size>
    <analysis>static</analysis>
    <plot_level>PLOT_MAJOR_ITRS</plot_level>
</Control>

<Material>
    <material id="1" name="myocardium" type="Mooney-Rivlin">
        <c1>0.05</c1>
        <c2>0.05</c2>
        <k>2.0</k>
    </material>
</Material>

<Geometry>
    <!-- Simple heart-shaped geometry -->
    <Nodes>
        <node id="1">0.0, 0.0, 0.0</node>
        <node id="2">1.0, 0.0, 0.0</node>
        <node id="3">0.5, 1.0, 0.0</node>
        <node id="4">0.0, 0.0, 1.0</node>
        <node id="5">1.0, 0.0, 1.0</node>
        <node id="6">0.5, 1.0, 1.0</node>
        <node id="7">0.5, 0.5, 0.5</node>
    </Nodes>
    
    <Elements type="solid" mat="1">
        <tet4 id="1">1, 2, 3, 7</tet4>
        <tet4 id="2">4, 5, 6, 7</tet4>
        <tet4 id="3">1, 4, 7, 2</tet4>
        <tet4 id="4">2, 5, 7, 3</tet4>
        <tet4 id="5">3, 6, 7, 1</tet4>
    </Elements>
    
    <Surface name="fixed_surface">
        <tri3 id="1">1, 2, 3</tri3>
    </Surface>
    
    <Surface name="pressure_surface">
        <tri3 id="1">4, 5, 6</tri3>
    </Surface>
</Geometry>

<Boundary>
    <fix bc="x,y,z">
        <surface>fixed_surface</surface>
    </fix>
</Boundary>

<Loads>
    <loadcurve id="1" type="linear">
        <loadpoint>0,0</loadpoint>
        <loadpoint>1,1</loadpoint>
    </loadcurve>
    
    <pressure type="linear">
        <surface>pressure_surface</surface>
        <scale>10.0</scale>
        <lc>1</lc>
    </pressure>
</Loads>

<Output>
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
        <var type="strain"/>
    </plotfile>
    
    <logfile>
        <node_data data="displacement"/>
        <element_data data="stress"/>
    </logfile>
</Output>

<Step>
    <analysis>static</analysis>
    <time_steps>100</time_steps>
    <step_size>0.01</step_size>
</Step>
</febio_spec>"""
    
    # Save the file
    output_path = "HeartDigitalTwin/Patient_001/FEBio_Models/cardiac_simulation.feb"
    with open(output_path, 'w') as f:
        f.write(feb_content)
    
    print(f"✅ Created FEBio file: {output_path}")
    print(f"📁 File size: {os.path.getsize(output_path)} bytes")
    
    return output_path

def create_advanced_fsi_febio_file():
    """Create a more advanced FSI FEBio file"""
    
    advanced_content = """<?xml version="1.0" encoding="ISO-8859-1"?>
<febio_spec version="4.0">
<Module type="fluid-FSI"/>

<Control>
    <title>Cardiac FSI Simulation - Digital Twin</title>
    <time_steps>50</time_steps>
    <step_size>0.02</step_size>
    <analysis>dynamic</analysis>
    <plot_level>PLOT_MAJOR_ITRS</plot_level>
</Control>

<Material>
    <!-- Heart muscle -->
    <material id="1" name="myocardium" type="Mooney-Rivlin">
        <c1>0.1</c1>
        <c2>0.1</c2>
        <k>5.0</k>
    </material>
    
    <!-- Blood -->
    <material id="2" name="blood" type="Newtonian viscous">
        <density>1.06</density>
        <viscosity>0.04</viscosity>
    </material>
</Material>

<Geometry>
    <!-- Simple heart geometry with 8 nodes -->
    <Nodes>
        <node id="1">0, 0, 0</node>
        <node id="2">2, 0, 0</node>
        <node id="3">2, 2, 0</node>
        <node id="4">0, 2, 0</node>
        <node id="5">0, 0, 2</node>
        <node id="6">2, 0, 2</node>
        <node id="7">2, 2, 2</node>
        <node id="8">0, 2, 2</node>
    </Nodes>
    
    <!-- Solid elements for heart wall -->
    <Elements type="solid" mat="1">
        <hex8 id="1">1, 2, 3, 4, 5, 6, 7, 8</hex8>
    </Elements>
    
    <!-- Fluid elements for blood -->
    <Elements type="fluid" mat="2">
        <hex8 id="2">1, 2, 3, 4, 5, 6, 7, 8</hex8>
    </Elements>
    
    <Surface name="base">
        <quad4 id="1">1, 2, 3, 4</quad4>
    </Surface>
    
    <Surface name="endocardium">
        <quad4 id="1">5, 6, 7, 8</quad4>
    </Surface>
</Geometry>

<Boundary>
    <fix bc="x,y,z">
        <surface>base</surface>
    </fix>
    
    <fluid-FSI>
        <surface>endocardium</surface>
    </fluid-FSI>
</Boundary>

<Loads>
    <loadcurve id="1" type="linear">
        <loadpoint>0,0</loadpoint>
        <loadpoint>1,1</loadpoint>
    </loadcurve>
</Loads>

<Output>
    <plotfile type="febio">
        <var type="displacement"/>
        <var type="stress"/>
        <var type="fluid pressure"/>
        <var type="fluid velocity"/>
    </plotfile>
</Output>
</febio_spec>"""
    
    output_path =r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\digital_twin_backend\simulation.feb"
    with open(output_path, 'w') as f:
        f.write(advanced_content)
    
    print(f"✅ Created FSI FEBio file: {output_path}")
    return output_path

if __name__ == "__main__":
    print("🫀 Creating FEBio files for Cardiac Digital Twin...")
    
    # Create simple file first
    simple_file = create_simple_febio_file()
    
    # Create advanced FSI file
    advanced_file = create_advanced_fsi_febio_file()
    
    print("\n🎉 FEBio files created successfully!")
    print("Next steps:")
    print("1. Open FEBio Studio")
    print("2. File → Open → Select the .feb file")
    print("3. Click 'Run' to see the simulation")