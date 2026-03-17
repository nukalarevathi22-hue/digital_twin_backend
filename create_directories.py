# Save as: create_directories.py
import os

def create_required_directories():
    """Create all required directories for the application"""
    
    directories = [
        "data/patients",
        "dashboard",
        "app/routes",
        "app/utils",
        "HeartDigitalTwin/Patient_001/FEBio_Models",
        "HeartDigitalTwin/Patient_001/Tetrahedral_Meshes",
        "HeartDigitalTwin/Patient_001/Simulation_Results"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    # Create a simple dashboard index.html
    with open("dashboard/index.html", "w") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>CHF Digital Twin Dashboard</title>
</head>
<body>
    <h1>CHF Digital Twin Dashboard</h1>
    <p>Backend is running! Check the API docs at <a href="/docs">/docs</a></p>
</body>
</html>
        """)
    
    print("✅ Created basic dashboard file")

if __name__ == "__main__":
    create_required_directories()