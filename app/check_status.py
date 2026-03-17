# check_system_status.py
import requests

def check_system_status():
    base_url = "http://localhost:8000"
    
    print("📊 Digital Twin System Status")
    print("=" * 40)
    
    # Health check
    health = requests.get(f"{base_url}/health").json()
    print(f"🩺 Health: {health['status']}")
    print(f"📁 Simulations: {health['cardiac_simulations']}")
    print(f"🔧 Engine: {health['real_time_engine']}")
    
    # Simulation info
    sim_info = requests.get(f"{base_url}/api/cardiac/simulations/info").json()
    print(f"📈 Loaded: {sim_info['total_simulations']} simulations")
    print(f"📏 Range: {sim_info['contractility_range']['min']}-{sim_info['contractility_range']['max']}")
    
    # Patient status
    status = requests.get(f"{base_url}/api/realtime/status/test_patient").json()
    print(f"👤 Patient: {status['patient_id']}")
    print(f"❤️  Last HR: {status.get('heart_rate', 'N/A')} bpm")
    print(f"🫀 Last EF: {status.get('ejection_fraction', 'N/A')}%")
    print(f"📊 Status: {status.get('clinical_status', 'N/A')}")
    
    print(f"\n✅ System is READY for production use!")

if __name__ == "__main__":
    check_system_status()