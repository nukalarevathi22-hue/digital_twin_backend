# save as: convert_simple.py
import pyvista as pv
import json
import numpy as np

# Your file path
input_file = r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\slicer_digital_twin\heart_tetrahedral_ascii.vtk"
output_file = "heart_threejs.json"

print(f"Converting: {input_file}")

# 1. Read the VTK file
mesh = pv.read(input_file)
print(f"✓ Loaded: {mesh.n_points} points, {mesh.n_cells} cells")

# 2. Extract surface (if tetrahedral volume mesh)
if mesh.n_cells > 0 and hasattr(mesh, 'extract_surface'):
    mesh = mesh.extract_surface()
    print(f"✓ Extracted surface: {mesh.n_cells} faces")

# 3. Ensure all triangles
if not mesh.is_all_triangles:
    mesh = mesh.triangulate()
    print(f"✓ Triangulated")

# 4. Get vertices and faces
vertices = mesh.points.astype(np.float32)  # Convert to float32
faces = mesh.faces.reshape(-1, 4)[:, 1:4]  # Remove first column (number of vertices)

print(f"✓ Final: {len(vertices)} vertices, {len(faces)} triangles")

# 5. Create Three.js JSON structure
threejs_data = {
    "metadata": {
        "version": 4.5,
        "type": "BufferGeometry",
        "generator": "VTK to Three.js Converter"
    },
    "type": "BufferGeometry",
    "data": {
        "attributes": {
            "position": {
                "itemSize": 3,
                "type": "Float32Array",
                "array": vertices.flatten().tolist()
            }
        },
        "index": {
            "type": "Uint16Array", 
            "array": faces.flatten().tolist()
        }
    }
}

# 6. Save to JSON file
with open(output_file, 'w') as f:
    json.dump(threejs_data, f, indent=2)

print(f"✓ Saved to: {output_file}")
print("Done! Now load 'heart_threejs.json' in Three.js")