# test_fixed_endpoints.py
import requests
import json

def test_fixed_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Fixed Endpoints")
    print("=" * 40)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/api/cardiac/simulations/info", "Simulations info"),
        ("POST", "/api/realtime/heart-rate/test_patient", "Heart rate endpoint"),
        ("GET", "/api/realtime/status/test_patient", "Patient status"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"\n🔍 {description}")
        print(f"   {method} {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            elif method == "POST":
                response = requests.post(
                    f"{base_url}{endpoint}", 
                    json={"heart_rate": 75},
                    timeout=10
                )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS!")
                if endpoint == "/api/realtime/heart-rate/test_patient":
                    print(f"      EF: {data.get('ejection_fraction')}%")
                    print(f"      CO: {data.get('cardiac_output')} L/min")
                    print(f"      Status: {data.get('clinical_status')}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_fixed_endpoints()