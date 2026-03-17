# test_api.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test a single endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Endpoint: {endpoint}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS (Status: {response.status_code})")
            
            # Pretty print the response
            if 'data' in data:
                print(f"📊 Response summary:")
                if 'simulation_data' in data['data']:
                    sim_data = data['data']['simulation_data']
                    if 'displacement' in sim_data:
                        disp = sim_data['displacement']
                        print(f"   • Displacement: {disp.get('min_value', 0):.2f} - {disp.get('max_value', 0):.2f} mm")
                if 'clinical_insights' in data['data']:
                    insights = data['data']['clinical_insights']
                    print(f"   • Risk Level: {data['data'].get('risk_assessment', {}).get('risk_level', 'N/A')}")
            else:
                print(json.dumps(data, indent=2))
                
        else:
            print(f"❌ FAILED (Status: {response.status_code})")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_all_endpoints():
    """Test all major endpoints"""
    print("🚀 Starting API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Test basic endpoints
    test_endpoint("/", "Root endpoint")
    test_endpoint("/health", "Health check")
    
    # Test digital twin endpoints
    test_endpoint("/api/patient/patient_001/digital-twin", "Digital Twin State")
    test_endpoint("/api/patient/patient_001/digital-twin/visualization", "Visualization Data")
    test_endpoint("/api/patient/patient_001/digital-twin/raw-data", "Raw Simulation Data")
    test_endpoint("/api/patient/patient_001/digital-twin/visualization?time_step=0.05", "Visualization with time step")
    
    # Test simulation endpoints
    test_endpoint("/api/patient/patient_001/simulations", "Patient Simulations")
    test_endpoint("/api/patient/patient_001/simulation-status", "Simulation Status")
    test_endpoint("/api/simulation/Model_heart", "Specific Simulation")
    
    # Test alerts (if any)
    test_endpoint("/api/patient/patient_001/alerts", "Patient Alerts")

def test_with_error_handling():
    """Test with various error scenarios"""
    print(f"\n{'='*60}")
    print("Testing Error Scenarios")
    print(f"{'='*60}")
    
    # Test non-existent patient
    test_endpoint("/api/patient/non_existent_patient/digital-twin", "Non-existent Patient")
    
    # Test invalid endpoint
    test_endpoint("/api/invalid-endpoint", "Invalid Endpoint")

if __name__ == "__main__":
    test_all_endpoints()
    test_with_error_handling()