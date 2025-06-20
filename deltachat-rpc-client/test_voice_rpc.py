#!/usr/bin/env python3
"""Test voice call features with deltachat-rpc-client"""

import json
import requests
import sys

# Test voice call features using direct HTTP requests to our simple server
def test_voice_calls():
    base_url = "http://localhost:3000"
    
    def call_rpc(method, params=None):
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(base_url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    print("🎤 Testing Voice Call Features")
    print("=" * 40)
    
    # Test 1: Initialize voice calls
    print("\n1. Initializing voice calls...")
    result = call_rpc("init_voice_calls")
    print(f"   Result: {result}")
    
    # Test 2: Get node ID
    print("\n2. Getting voice node ID...")
    result = call_rpc("get_voice_node_id")
    print(f"   Result: {result}")
    
    # Test 3: Start a call
    print("\n3. Starting voice call...")
    result = call_rpc("start_voice_call", ["peer_test_123"])
    print(f"   Result: {result}")
    call_id = result.get("result", "").strip('"') if "result" in result else None
    
    # Test 4: Get active calls
    print("\n4. Getting active calls...")
    result = call_rpc("get_active_voice_calls")
    print(f"   Result: {result}")
    
    # Test 5: Get call status
    if call_id:
        print(f"\n5. Getting call status for {call_id}...")
        result = call_rpc("get_voice_call_status", [call_id])
        print(f"   Result: {result}")
    
    # Test 6: Simulate incoming call
    print("\n6. Simulating incoming call...")
    result = call_rpc("simulate_incoming_voice_call", ["peer_incoming_456"])
    print(f"   Result: {result}")
    incoming_call_id = result.get("result", "").strip('"') if "result" in result else None
    
    # Test 7: Accept incoming call
    if incoming_call_id:
        print(f"\n7. Accepting incoming call {incoming_call_id}...")
        result = call_rpc("accept_voice_call", [incoming_call_id])
        print(f"   Result: {result}")
    
    # Test 8: List all active calls
    print("\n8. Listing all active calls...")
    result = call_rpc("get_active_voice_calls")
    print(f"   Result: {result}")
    
    # Test 9: End calls
    if call_id:
        print(f"\n9. Ending call {call_id}...")
        result = call_rpc("end_voice_call", [call_id])
        print(f"   Result: {result}")
    
    if incoming_call_id:
        print(f"\n10. Ending incoming call {incoming_call_id}...")
        result = call_rpc("end_voice_call", [incoming_call_id])
        print(f"   Result: {result}")
    
    # Test 10: Final check - should be no active calls
    print("\n11. Final check - active calls...")
    result = call_rpc("get_active_voice_calls")
    print(f"   Result: {result}")
    
    print("\n✅ Voice call test completed!")

if __name__ == "__main__":
    try:
        test_voice_calls()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")