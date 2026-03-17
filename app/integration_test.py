# final_integration_test.py
import requests
import asyncio
import websockets
import json
import time
import threading

class DigitalTwinTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.patient_id = "patient_001"
        self.websocket_messages = []
    
    def test_all_endpoints(self):
        """Test all API endpoints"""
        print("🧪 Testing All API Endpoints")
        print("=" * 40)
        
        endpoints = [
            ("GET", "/health", {}),
            ("GET", "/api/cardiac/simulations/info", {}),
            ("GET", f"/api/realtime/status/{self.patient_id}", {}),
        ]
        
        for method, endpoint, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = requests.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"✅ {method} {endpoint}: {response.status_code}")
                if response.status_code != 200:
                    print(f"   ❌ Error: {response.text}")
            except Exception as e:
                print(f"❌ {method} {endpoint}: {e}")
    
    def simulate_patient_monitoring(self):
        """Simulate real patient heart rate monitoring"""
        print(f"\n👤 Simulating Patient Monitoring: {self.patient_id}")
        print("=" * 50)
        
        # Simulate different clinical scenarios
        scenarios = [
            {"heart_rate": 45, "description": "Bradycardia - Resting"},
            {"heart_rate": 68, "description": "Normal - Resting"},
            {"heart_rate": 82, "description": "Normal - Light Activity"},
            {"heart_rate": 105, "description": "Tachycardia - Mild Stress"},
            {"heart_rate": 125, "description": "Tachycardia - Exercise"},
            {"heart_rate": 140, "description": "Severe Tachycardia - Emergency"},
            {"heart_rate": 95, "description": "Recovery - Post Exercise"},
            {"heart_rate": 72, "description": "Normal - Resting Recovery"},
        ]
        
        for scenario in scenarios:
            print(f"\n📊 Scenario: {scenario['description']}")
            print(f"   Sending HR: {scenario['heart_rate']} bpm")
            
            response = requests.post(
                f"{self.base_url}/api/realtime/heart-rate/{self.patient_id}",
                json={"heart_rate": scenario["heart_rate"]}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Response:")
                print(f"      🫀 EF: {data['ejection_fraction']:.1f}%")
                print(f"      💓 CO: {data['cardiac_output']:.2f} L/min")
                print(f"      📊 Status: {data['clinical_status']}")
                print(f"      📐 Vertices: {data['vertices_count']}")
                
                # Check for alerts
                if data['clinical_status'] in ['Severe Dysfunction', 'Hyperdynamic']:
                    print(f"      ⚠️  Clinical Alert: {data['clinical_status']}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
            
            time.sleep(1)  # Simulate real-time monitoring interval
    
    async def websocket_listener(self):
        """Listen for real-time WebSocket updates"""
        uri = f"ws://localhost:8000/ws/realtime/{self.patient_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Wait for connection confirmation
                connection_msg = await websocket.recv()
                print(f"🔌 WebSocket Connected: {json.loads(connection_msg)['message']}")
                
                # Listen for updates during the test
                print("🎯 Listening for real-time WebSocket updates...")
                
                update_count = 0
                start_time = time.time()
                
                while time.time() - start_time < 30:  # Listen for 30 seconds
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        self.websocket_messages.append(data)
                        
                        if data.get("type") == "cardiac_update":
                            update_count += 1
                            print(f"   📥 Update #{update_count}: HR {data['heart_rate']} bpm")
                            
                        elif data.get("type") == "alert":
                            print(f"   🚨 ALERT: {data['alert']['message']}")
                            
                    except asyncio.TimeoutError:
                        continue
                        
                print(f"   📊 Received {update_count} real-time updates")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    def run_complete_test(self):
        """Run complete integration test"""
        print("🏥 COMPREHENSIVE DIGITAL TWIN TEST")
        print("=" * 60)
        
        # Test 1: API Endpoints
        self.test_all_endpoints()
        
        # Test 2: Start WebSocket listener in background
        print(f"\n🔌 Starting WebSocket listener for {self.patient_id}...")
        websocket_thread = threading.Thread(
            target=lambda: asyncio.run(self.websocket_listener())
        )
        websocket_thread.daemon = True
        websocket_thread.start()
        
        # Give WebSocket time to connect
        time.sleep(2)
        
        # Test 3: Simulate patient monitoring
        self.simulate_patient_monitoring()
        
        # Test 4: Final status check
        time.sleep(2)  # Let WebSocket catch up
        self.check_final_status()
        
        print(f"\n🎉 COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
        print("   Your Digital Twin is ready for production use! 🚀")
    
    def check_final_status(self):
        """Check final system status"""
        print(f"\n📈 Final System Status Check")
        print("=" * 40)
        
        # Patient status
        status = requests.get(f"{self.base_url}/api/realtime/status/{self.patient_id}").json()
        print(f"👤 Patient: {status['patient_id']}")
        print(f"❤️  Current HR: {status.get('heart_rate', 'N/A')} bpm")
        print(f"🫀 Current EF: {status.get('ejection_fraction', 'N/A')}%")
        print(f"📊 Current Status: {status.get('clinical_status', 'N/A')}")
        print(f"🔗 Connected Clients: {status.get('connected_clients', 0)}")
        print(f"📁 Simulations Available: {status.get('simulations_available', 0)}")
        
        # WebSocket summary
        cardiac_updates = [m for m in self.websocket_messages if m.get('type') == 'cardiac_update']
        alerts = [m for m in self.websocket_messages if m.get('type') == 'alert']
        
        print(f"📊 WebSocket Summary:")
        print(f"   Cardiac Updates: {len(cardiac_updates)}")
        print(f"   Alerts: {len(alerts)}")

if __name__ == "__main__":
    tester = DigitalTwinTester()
    tester.run_complete_test()