# test_http.py
import requests
import json

def test_http_endpoints():
    """Test HTTP endpoints"""
    base_url = "http://localhost:8000"
    
    print("🌐 Testing HTTP endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test simulations info
    try:
        response = requests.get(f"{base_url}/api/cardiac/simulations/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Simulations info: {data.get('total_simulations')} simulations loaded")
        else:
            print(f"❌ Simulations info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Simulations info error: {e}")
    
    # Test heart rate endpoint
    try:
        response = requests.post(
            f"{base_url}/api/realtime/heart-rate/test_patient_http",
            json={"heart_rate": 85},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Heart rate endpoint working - Status: {data.get('clinical_status')}")
        else:
            print(f"❌ Heart rate endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Heart rate endpoint error: {e}")

if __name__ == "__main__":
    test_http_endpoints()