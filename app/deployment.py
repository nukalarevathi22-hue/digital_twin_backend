# deployment_checklist.py
import requests
import websockets
import asyncio
import json
import time

async def test_websocket_connection():
    """Test WebSocket connection and real-time updates"""
    try:
        uri = "ws://localhost:8000/ws/realtime/checklist_test"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection message
            connection_msg = await websocket.recv()
            connection_data = json.loads(connection_msg)
            
            if (connection_data.get('type') == 'connection_established' and 
                connection_data.get('simulations_loaded', 0) > 0):
                return True
                
    except Exception as e:
        print(f"WebSocket test error: {e}")
        return False
    return False

async def test_real_time_updates():
    """Test that real-time updates work through WebSocket"""
    try:
        uri = "ws://localhost:8000/ws/realtime/checklist_test"
        
        async with websockets.connect(uri) as websocket:
            # Wait for connection message
            await websocket.recv()
            
            # Send heart rate via HTTP
            hr_response = requests.post(
                "http://localhost:8000/api/realtime/heart-rate/checklist_test",
                json={"heart_rate": 75},
                headers={"Content-Type": "application/json"}
            )
            
            if hr_response.status_code != 200:
                return False
            
            # Wait for WebSocket update with timeout
            try:
                update_msg = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                update_data = json.loads(update_msg)
                
                if (update_data.get('type') == 'cardiac_update' and 
                    update_data.get('heart_rate') == 75):
                    return True
                    
            except asyncio.TimeoutError:
                return False
                
    except Exception as e:
        print(f"Real-time update test error: {e}")
        return False
    return False

def test_cors():
    """Test CORS headers properly"""
    try:
        # Test OPTIONS request which should include CORS headers
        response = requests.options(
            "http://localhost:8000/api/realtime/heart-rate/test_cors",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        # Check for CORS headers
        cors_headers = [
            'access-control-allow-origin',
            'access-control-allow-methods', 
            'access-control-allow-headers'
        ]
        
        has_cors = any(header in response.headers for header in cors_headers)
        
        # Also test regular request
        get_response = requests.get("http://localhost:8000/health")
        if 'access-control-allow-origin' in get_response.headers:
            return True
            
        return has_cors
        
    except Exception as e:
        print(f"CORS test error: {e}")
        return False

def production_checklist():
    base_url = "http://localhost:8000"
    
    print("🏥 PRODUCTION DEPLOYMENT CHECKLIST")
    print("=" * 50)
    
    checklist = {
        "API Server Running": False,
        "Cardiac Simulations Loaded": False,
        "WebSocket Endpoint Working": False,
        "Heart Rate Endpoint Working": False,
        "Status Endpoint Working": False,
        "CORS Enabled": False,
        "Error Handling Working": False,
        "Real-time Updates Working": False,
    }
    
    # Check 1: Basic connectivity
    try:
        health = requests.get(f"{base_url}/health")
        if health.status_code == 200:
            checklist["API Server Running"] = True
            print("✅ API Server: Running")
    except Exception as e:
        print(f"❌ API Server: Failed - {e}")
    
    # Check 2: Simulations loaded
    try:
        sim_info = requests.get(f"{base_url}/api/cardiac/simulations/info")
        if sim_info.status_code == 200:
            data = sim_info.json()
            if data.get('total_simulations', 0) > 0:
                checklist["Cardiac Simulations Loaded"] = True
                print(f"✅ Cardiac Simulations: {data.get('total_simulations')} loaded")
            else:
                print("❌ Cardiac Simulations: No simulations loaded")
        else:
            print("❌ Cardiac Simulations: API call failed")
    except Exception as e:
        print(f"❌ Cardiac Simulations: Failed - {e}")
    
    # Check 3: Heart rate endpoint
    try:
        hr_response = requests.post(
            f"{base_url}/api/realtime/heart-rate/test_check",
            json={"heart_rate": 75},
            headers={"Content-Type": "application/json"}
        )
        if hr_response.status_code == 200:
            checklist["Heart Rate Endpoint Working"] = True
            print("✅ Heart Rate Endpoint: Working")
        else:
            print(f"❌ Heart Rate Endpoint: Failed with status {hr_response.status_code}")
    except Exception as e:
        print(f"❌ Heart Rate Endpoint: Failed - {e}")
    
    # Check 4: Status endpoint
    try:
        status_response = requests.get(f"{base_url}/api/realtime/status/test_check")
        if status_response.status_code == 200:
            checklist["Status Endpoint Working"] = True
            print("✅ Status Endpoint: Working")
        else:
            print(f"❌ Status Endpoint: Failed with status {status_response.status_code}")
    except Exception as e:
        print(f"❌ Status Endpoint: Failed - {e}")
    
    # Check 5: CORS
    try:
        cors_result = test_cors()
        checklist["CORS Enabled"] = cors_result
        if cors_result:
            print("✅ CORS: Enabled")
        else:
            print("❌ CORS: Not properly configured")
    except Exception as e:
        print(f"❌ CORS: Failed - {e}")
    
    # Check 6: Error handling
    try:
        error_response = requests.post(
            f"{base_url}/api/realtime/heart-rate/test_check",
            json={"invalid_field": "test"}
        )
        # Should return 422 validation error, not 500
        if error_response.status_code == 422:
            checklist["Error Handling Working"] = True
            print("✅ Error Handling: Working (proper validation errors)")
        else:
            print(f"❌ Error Handling: Expected 422, got {error_response.status_code}")
    except Exception as e:
        print(f"❌ Error Handling: Failed - {e}")
    
    # Check 7: WebSocket endpoint (async)
    try:
        websocket_result = asyncio.run(test_websocket_connection())
        checklist["WebSocket Endpoint Working"] = websocket_result
        if websocket_result:
            print("✅ WebSocket Endpoint: Working")
        else:
            print("❌ WebSocket Endpoint: Failed to connect")
    except Exception as e:
        print(f"❌ WebSocket Endpoint: Failed - {e}")
    
    # Check 8: Real-time updates (async)
    try:
        realtime_result = asyncio.run(test_real_time_updates())
        checklist["Real-time Updates Working"] = realtime_result
        if realtime_result:
            print("✅ Real-time Updates: Working")
        else:
            print("❌ Real-time Updates: Failed to receive updates")
    except Exception as e:
        print(f"❌ Real-time Updates: Failed - {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 FINAL CHECKLIST RESULTS:")
    print("=" * 50)
    
    for item, status in checklist.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {item}")
    
    # Summary
    passed = sum(checklist.values())
    total = len(checklist)
    
    print(f"\n📊 Summary: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Ready for production deployment! 🚀")
        print("\n🚀 Next Steps:")
        print("   1. Deploy to your cloud provider (AWS, Azure, GCP)")
        print("   2. Set up domain and SSL certificate")
        print("   3. Configure load balancing if needed")
        print("   4. Set up monitoring and logging")
        print("   5. Integrate with frontend application")
        print("   6. Connect real smartwatch/device data streams")
    else:
        print("\n⚠️  Some checks failed. Please review before deployment.")
        
        # Provide specific guidance for failed checks
        if not checklist["WebSocket Endpoint Working"]:
            print("\n🔧 WebSocket Fix: Check that uvicorn is running with WebSocket support")
        if not checklist["CORS Enabled"]:
            print("\n🔧 CORS Fix: Ensure CORSMiddleware is properly configured in main.py")
        if not checklist["Real-time Updates Working"]:
            print("\n🔧 Real-time Fix: Verify WebSocket broadcast in heart-rate endpoint")

if __name__ == "__main__":
    production_checklist()