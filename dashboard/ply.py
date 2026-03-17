import json
import numpy as np
from plyfile import PlyData

# Load PLY file
ply = PlyData.read(r"C:\Users\Polagoni Sowmya\OneDrive\Desktop\digital_twin_backend\simulation.ply")  # Change name to your actual file

# Extract vertices
vertices = np.array([(v[0], v[1], v[2]) for v in ply['vertex']])

# ✅ Convert NumPy float32 to Python float
vertices_list = vertices.astype(float).tolist()

# Create JSON object
data_json = {
    "nodes": vertices_list
}

# ✅ Save JSON in a serializable format
with open("heart_model.json", "w") as f:
    json.dump(data_json, f)

print("✅ heart_model.json generated successfully!")
