# test_fixed_system.py
import requests
import json

def test_fixed_system():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Fixed Digital Twin System")
    print("=" * 50)
    
    # Test heart rate with JSON body
    test_cases = [
        {"heart_rate": 45, "condition": "Bradycardia"},
        {"heart_rate": 65, "condition": "Normal Resting"},
        {"heart_rate": 85, "condition": "Light Activity"},
        {"heart_rate": 110, "condition": "Tachycardia"},
        {"heart_rate": 130, "condition": "Severe Tachycardia"}
    ]
    
    for case in test_cases:
        print(f"\n❤️  Testing: {case['condition']} (HR: {case['heart_rate']} bpm)")
        
        response = requests.post(
            f"{base_url}/api/realtime/heart-rate/test_patient",
            json={"heart_rate": case["heart_rate"]}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS!")
            print(f"      🫀 EF: {data['ejection_fraction']:.1f}%")
            print(f"      💓 CO: {data['cardiac_output']:.2f} L/min")
            print(f"      📊 Status: {data['clinical_status']}")
            print(f"      🔄 Data: {data['data_source']}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_fixed_system()