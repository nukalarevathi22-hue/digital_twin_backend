# Save as: upgrade_existing_febio.py
import xml.etree.ElementTree as ET

def upgrade_to_fsi(existing_feb_file, output_feb_file):
    """Upgrade existing FEBio file to include FSI"""
    
    print(f"🔄 Upgrading {existing_feb_file} to include FSI...")
    
    # Parse existing file
    tree = ET.parse(existing_feb_file)
    root = tree.getroot()
    
    # Change module to fluid-FSI
    module_elem = root.find('Module')
    if module_elem is not None:
        module_elem.set('type', 'fluid-FSI')
    
    # Add fluid material
    material_elem = root.find('Material')
    if material_elem is not None:
        fluid_material = ET.SubElement(material_elem, 'material')
        fluid_material.set('id', '2')
        fluid_material.set('name', 'blood')
        fluid_material.set('type', 'Newtonian viscous')
        
        density = ET.SubElement(fluid_material, 'density')
        density.text = '1.06'
        viscosity = ET.SubElement(fluid_material, 'viscosity')
        viscosity.text = '0.04'
    
    # Add fluid elements section
    geometry_elem = root.find('Geometry')
    if geometry_elem is not None:
        # Find solid elements and duplicate for fluid
        solid_elems = geometry_elem.find('Elements[@type="solid"]')
        if solid_elems is not None:
            fluid_elems = ET.SubElement(geometry_elem, 'Elements')
            fluid_elems.set('type', 'fluid')
            fluid_elems.set('mat', '2')
            fluid_elems.text = solid_elems.text
    
    # Add FSI boundary conditions
    boundary_elem = root.find('Boundary')
    if boundary_elem is not None:
        fsi_bc = ET.SubElement(boundary_elem, 'fluid-FSI')
        surface = ET.SubElement(fsi_bc, 'surface')
        surface.text = '1'  # Use your surface ID
    
    # Add fluid output variables
    output_elem = root.find('Output')
    if output_elem is not None:
        plotfile = output_elem.find('plotfile')
        if plotfile is not None:
            fluid_vars = ['fluid pressure', 'fluid velocity', 'fluid flux']
            for var in fluid_vars:
                var_elem = ET.SubElement(plotfile, 'var')
                var_elem.set('type', var)
    
    # Save upgraded file
    tree.write(output_feb_file, encoding='ISO-8859-1', xml_declaration=True)
    print(f"✅ Upgraded file saved: {output_feb_file}")

# Usage
upgrade_to_fsi(
    "your_existing_simulation.feb", 
    "upgraded_fsi_simulation.feb"
)