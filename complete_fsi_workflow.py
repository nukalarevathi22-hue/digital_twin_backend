# complete_fsi_workflow.py
import os
import subprocess
from febio_fsi_runner import FEBioFSIRunner

def run_complete_fsi_workflow():
    """Complete workflow to run FSI simulation"""
    
    print("🫀 CARDIAC FSI WORKFLOW")
    print("=" * 50)
    
    # 1. Create directories
    os.makedirs("FSI_Results", exist_ok=True)
    
    # 2. Verify FEB file exists
    feb_file = "cardiac_fsi_complete.feb"
    if not os.path.exists(feb_file):
        print(f"❌ FEB file not found: {feb_file}")
        print("Please ensure the FEB file is in the current directory")
        return
    
    # 3. Run simulation
    print("2. Running FSI simulation...")
    
    # Use explicit path
    febio_exe = r"C:\Program Files\FEBioStudio\uninstall.exe"
    
    # Check if FEBio exists
    if not os.path.exists(febio_exe):
        print(f"❌ FEBio not found at: {febio_exe}")
        # Try alternative
        febio_exe = r"C:\Program Files\FEBioStudio\febio3.exe"
        if not os.path.exists(febio_exe):
            print("❌ No FEBio executable found.")
            return
    
    runner = FEBioFSIRunner(febio_path=febio_exe)
    
    # Check FEBio version
    version = runner.check_febio_version()
    if version:
        print(f"   Using {version}")
    
    success = runner.run_fsi_simulation(feb_file, "FSI_Results")
    
    if success:
        # 4. Analyze results
        print("3. Analyzing results...")
        results = runner.extract_results("FSI_Results")
        
        if results:
            print("🎉 FSI SIMULATION COMPLETE!")
            print("📊 Results Summary:")
            for key, value in results.items():
                print(f"   {key}: {value}")
            
            # 5. Generate visualization
            print("4. Generating visualization...")
            generate_visualization(results['xplt_file'])
        else:
            print("❌ No results to analyze")
    else:
        print("❌ Simulation failed.")

def generate_visualization(xplt_file):
    """Generate visualization from FSI results"""
    if os.path.exists(xplt_file):
        print(f"🎨 Creating visualization from {xplt_file}")
        print("✅ Results ready for visualization in FEBio Studio")
        print("   Open FEBio Studio → Post-Processor → Load .xplt file")
        print("   Visualize: Displacement, Fluid Pressure, Velocity Vectors")
    else:
        print("❌ Results file not found for visualization")

if __name__ == "__main__":
    run_complete_fsi_workflow()