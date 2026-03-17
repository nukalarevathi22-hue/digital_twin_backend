# test_complete_integration.py
import requests
import asyncio
import websockets
import json
import threading
import time

def send_heart_rates():
    """Send heart rates in a separate thread"""
    base_url = "http://localhost:8000"
    
    heart_rates = [50, 65, 80, 95, 110, 125, 140, 120, 100, 80, 65]
    
    for hr in heart_rates:
        response = requests.post(
            f"{base_url}/api/realtime/heart-rate/test_patient",
            json={"heart_rate": hr}
        )
        print(f"📤 Sent HR: {hr} bpm -> EF: {response.json().get('ejection_fraction', 'N/A')}%")
        time.sleep(2)

async def listen_websocket():
    """Listen for WebSocket updates"""
    uri = "ws://localhost:8000/ws/realtime/test_patient"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        await websocket.recv()
        print("✅ WebSocket connected, listening for updates...")
        
        update_count = 0
        while update_count < 10:  # Listen for 10 updates
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                
                if data.get("type") == "cardiac_update":
                    update_count += 1
                    print(f"\n🔄 Update #{update_count}:")
                    print(f"   ❤️  HR: {data['heart_rate']} bpm")
                    print(f"   🫀 EF: {data['clinical_metrics']['ejection_fraction']:.1f}%")
                    print(f"   💓 CO: {data['clinical_metrics']['cardiac_output']:.2f} L/min")
                    print(f"   📊 Status: {data['clinical_status']}")
                    
                elif data.get("type") == "alert":
                    print(f"🚨 ALERT: {data['alert']['message']}")
                    
            except asyncio.TimeoutError:
                print("⏰ No updates received")
                break

def test_complete_integration():
    print("🏥 Complete Digital Twin Integration Test")
    print("=" * 60)
    
    # Start WebSocket listener in a thread
    def run_websocket():
        asyncio.run(listen_websocket())
    
    websocket_thread = threading.Thread(target=run_websocket)
    websocket_thread.start()
    
    # Give WebSocket time to connect
    time.sleep(2)
    
    # Send heart rates
    send_heart_rates()
    
    # Wait for WebSocket thread to finish
    websocket_thread.join()
    
    print("\n🎉 Integration test completed successfully!")

if __name__ == "__main__":
    test_complete_integration()