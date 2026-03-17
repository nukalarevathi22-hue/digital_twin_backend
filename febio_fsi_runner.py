# febio_fsi_runner.py
import os
import subprocess
import platform
import time
import xml.etree.ElementTree as ET

class FEBioFSIRunner:
    def __init__(self, febio_path=None):
        """Initialize FEBio runner with explicit path"""
        if febio_path:
            self.febio_path = febio_path
        else:
            self.febio_path = self.find_febio()
    
    def find_febio(self):
        """Find FEBio executable"""
        # Your specific installation path
        custom_paths = [
            r"C:\Program Files\FEBioStudio\febio4.exe",
            r"C:\Program Files\FEBioStudio\febio3.exe",
        ]
        
        for path in custom_paths:
            if os.path.exists(path):
                print(f"✅ Found FEBio at: {path}")
                return path
        
        print("❌ FEBio not found in standard locations")
        return None

    def run_fsi_simulation(self, input_file, output_dir="FSI_Results"):
        """Run FSI simulation with correct FEBio syntax"""
        if not self.febio_path:
            print("❌ FEBio path not set")
            return False
        
        if not os.path.exists(input_file):
            print(f"❌ Input file not found: {input_file}")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set output file paths
        log_file = os.path.join(output_dir, "log.txt")
        xplt_file = os.path.join(output_dir, "results.xplt")
        dump_file = os.path.join(output_dir, "dump.txt")
        
        print("🚀 Starting Cardiac FSI Simulation...")
        print(f"   Input: {input_file}")
        print(f"   Output: {output_dir}")
        print("   Simulation Type: Fluid-Structure Interaction")
        print("   Features: Active contraction + Blood flow + Valve motion")
        
        start_time = time.time()
        
        try:
            # FEBio 4.x uses --input, --log, --plot, --dump with double dashes
            cmd = [
                self.febio_path,
                "--input", input_file,
                "--log", log_file,
                "--plot", xplt_file,
                "--dump", dump_file
            ]
            
            print(f"   Command: {' '.join(cmd)}")
            
            # Run FEBio simulation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(input_file) or "."
            )
            
            duration = time.time() - start_time
            
            # Check if simulation was successful
            if result.returncode == 0:
                print(f"✅ FSI Simulation Completed Successfully!")
                print(f"   Duration: {duration:.2f} seconds")
                
                # Check if results were actually generated
                if os.path.exists(xplt_file) and os.path.getsize(xplt_file) > 0:
                    print(f"   Results file: {xplt_file}")
                    return True
                else:
                    print("⚠️  Simulation ran but no results file was created")
                    return False
            else:
                print(f"❌ FEBio Error (return code: {result.returncode})")
                print(f"   Error output: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running simulation: {e}")
            return False

    def extract_results(self, output_dir):
        """Extract and analyze simulation results"""
        print(f"📊 Analyzing results from {output_dir}...")
        
        results = {
            'xplt_file': os.path.join(output_dir, "results.xplt"),
            'log_file': os.path.join(output_dir, "log.txt"),
            'dump_file': os.path.join(output_dir, "dump.txt"),
            'total_steps': 0,
            'solid_iterations': 0,
            'fluid_iterations': 0,
            'completion_time': 0
        }
        
        # Check if results files exist
        if not os.path.exists(results['xplt_file']):
            print("❌ No results file found")
            return None
        
        # Parse log file for simulation statistics
        log_path = results['log_file']
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    log_content = f.read()
                
                # Extract basic statistics from log
                lines = log_content.split('\n')
                for line in lines:
                    if "Number of time steps" in line:
                        try:
                            results['total_steps'] = int(line.split(':')[-1].strip())
                        except:
                            pass
                    elif "Total time" in line:
                        try:
                            results['completion_time'] = float(line.split(':')[-1].strip())
                        except:
                            pass
                            
            except Exception as e:
                print(f"⚠️  Could not parse log file: {e}")
        
        print(f"   Results file: {results['xplt_file']}")
        print(f"   File size: {os.path.getsize(results['xplt_file'])} bytes")
        
        return results

    def check_febio_version(self):
        """Check FEBio version"""
        if not self.febio_path:
            return None
        
        try:
            result = subprocess.run([self.febio_path, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None