# test_websocket.py
import asyncio
import websockets
import json
import time

async def test_websocket_connection():
    """Test WebSocket connection and real-time updates"""
    uri = "ws://localhost:8000/ws/realtime/test_patient"
    
    try:
        print("🔌 Testing WebSocket connection...")
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection message
            connection_msg = await websocket.recv()
            connection_data = json.loads(connection_msg)
            
            print(f"✅ {connection_data.get('message')}")
            print(f"✅ Simulations loaded: {connection_data.get('simulations_loaded')}")
            
            # Test ping-pong
            print("🔄 Testing ping-pong...")
            ping_msg = json.dumps({"type": "ping"})
            await websocket.send(ping_msg)
            
            pong_response = await websocket.recv()
            pong_data = json.loads(pong_response)
            
            if pong_data.get("type") == "pong":
                print("✅ Ping-pong working: pong")
            else:
                print("❌ Ping-pong failed")
                return False
            
            # Test heart rate update
            print("🎯 Testing real-time updates...")
            
            # Send heart rate via HTTP POST
            import requests
            heart_rate_response = requests.post(
                "http://localhost:8000/api/realtime/heart-rate/test_patient",
                json={"heart_rate": 75},
                headers={"Content-Type": "application/json"}
            )
            
            if heart_rate_response.status_code == 200:
                print("✅ Heart rate sent successfully")
            else:
                print(f"❌ Heart rate send failed: {heart_rate_response.text}")
                return False
            
            # Wait for WebSocket update
            print("⏳ Waiting for WebSocket update...")
            try:
                update_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                update_data = json.loads(update_msg)
                
                if update_data.get("type") == "cardiac_update":
                    print("✅ Real-time update received successfully!")
                    print(f"   Heart Rate: {update_data.get('heart_rate')} bpm")
                    print(f"   Clinical Status: {update_data.get('clinical_status')}")
                    print(f"   Ejection Fraction: {update_data.get('clinical_metrics', {}).get('ejection_fraction')}%")
                else:
                    print(f"❌ Unexpected message type: {update_data.get('type')}")
                    return False
                    
            except asyncio.TimeoutError:
                print("❌ No WebSocket update received within timeout")
                return False
            
            # Keep connection alive for a bit to test stability
            print("🔒 Testing connection stability...")
            await asyncio.sleep(3)
            
            print("🎉 All WebSocket tests passed!")
            return True
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except Exception as e:
        print(f"💥 WebSocket test failed: {e}")
        return False

async def test_multiple_connections():
    """Test multiple simultaneous WebSocket connections"""
    print("\n🧪 Testing multiple connections...")
    
    async def connect_client(client_id):
        try:
            uri = f"ws://localhost:8000/ws/realtime/patient_{client_id}"
            async with websockets.connect(uri) as websocket:
                # Wait for connection message
                await websocket.recv()
                print(f"✅ Client {client_id} connected")
                
                # Keep connection alive
                await asyncio.sleep(2)
                return True
        except Exception as e:
            print(f"❌ Client {client_id} failed: {e}")
            return False
    
    # Test 3 simultaneous connections
    tasks = [connect_client(i) for i in range(3)]
    results = await asyncio.gather(*tasks)
    
    successful = sum(results)
    print(f"📊 Multiple connection test: {successful}/3 successful")
    return successful == 3

if __name__ == "__main__":
    # Run the tests
    print("🏥 Starting CHF Digital Twin WebSocket Tests...\n")
    
    # Test single connection
    single_test = asyncio.run(test_websocket_connection())
    
    if single_test:
        # Test multiple connections
        multi_test = asyncio.run(test_multiple_connections())
        
        if single_test and multi_test:
            print("\n🎉 ALL TESTS PASSED! WebSocket system is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the WebSocket implementation.")
    else:
        print("\n💥 WebSocket tests failed. Server may need debugging.")