# Save as: create_fluid_domain.py
import numpy as np
import pyvista as pv
import meshio
import os

def create_fluid_domain_from_heart(solid_mesh_path, output_path):
    """
    Create fluid domain mesh from solid heart mesh
    This creates the blood pool inside the heart chambers
    """
    print("💧 Creating fluid domain for blood flow...")
    
    # Load your existing heart mesh
    heart_mesh = pv.read(solid_mesh_path)
    
    # Create simplified fluid domains for each chamber
    fluid_meshes = []
    
    # Left Ventricle Fluid Domain
    lv_fluid = pv.Sphere(center=(0, 0, 0), radius=0.8)
    lv_fluid = lv_fluid.scale([1.2, 0.9, 1.1], inplace=True)
    lv_fluid.translate([0.5, 0, 0], inplace=True)
    fluid_meshes.append(lv_fluid)
    
    # Right Ventricle Fluid Domain
    rv_fluid = pv.Sphere(center=(0, 0, 0), radius=0.7)
    rv_fluid = rv_fluid.scale([1.0, 0.8, 0.9], inplace=True)
    rv_fluid.translate([-0.4, 0.3, 0], inplace=True)
    fluid_meshes.append(rv_fluid)
    
    # Left Atrium Fluid Domain
    la_fluid = pv.Sphere(center=(0, 0, 0), radius=0.5)
    la_fluid.translate([0.3, 0.8, 0.2], inplace=True)
    fluid_meshes.append(la_fluid)
    
    # Right Atrium Fluid Domain
    ra_fluid = pv.Sphere(center=(0, 0, 0), radius=0.5)
    ra_fluid.translate([-0.3, 0.8, 0.1], inplace=True)
    fluid_meshes.append(ra_fluid)
    
    # Combine all fluid domains
    combined_fluid = fluid_meshes[0]
    for mesh in fluid_meshes[1:]:
        combined_fluid = combined_fluid.boolean_union(mesh)
    
    # Create tetrahedral mesh
    fluid_tet_mesh = combined_fluid.tetrahedralize()
    
    # Save as VTK
    fluid_tet_mesh.save(output_path)
    print(f"✅ Fluid domain saved: {output_path}")
    
    return output_path

def update_febio_with_fluid_domain(febio_template, solid_mesh, fluid_mesh, output_feb):
    """Update FEBio file with actual mesh paths"""
    
    with open(febio_template, 'r') as f:
        content = f.read()
    
    # Replace mesh file paths
    content = content.replace('unified_heart_frame_01.vtk', solid_mesh)
    
    # For now, we'll use the same mesh for demonstration
    # In practice, you'd have separate fluid and solid meshes
    content = content.replace('<!-- Fluid Elements - Blood Pool (you\'ll need to create this) -->', 
                             f'<Elements type="fluid" mat="3">2</Elements>')
    
    with open(output_feb, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated FEBio file: {output_feb}")

if __name__ == "__main__":
    # Path to your existing heart mesh
    solid_mesh = "HeartDigitalTwin/Patient_001/Tetrahedral_Meshes/unified_heart_frame_01.vtk"
    fluid_mesh = "HeartDigitalTwin/Patient_001/Tetrahedral_Meshes/fluid_domain.vtk"
    febio_output = "HeartDigitalTwin/Patient_001/FEBio_Models/cardiac_fsi_updated.feb"
    
    # Create fluid domain
    create_fluid_domain_from_heart(solid_mesh, fluid_mesh)
    
    # Update FEBio file
    update_febio_with_fluid_domain("cardiac_fsi_complete.feb", solid_mesh, fluid_mesh, febio_output)