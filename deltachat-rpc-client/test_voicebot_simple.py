#!/usr/bin/env python3
"""Simple test for voicebot without actual deltachat-rpc-server"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deltachat_rpc_client.rpc import Rpc
import time

# Mock RPC class that connects to our simple server
class MockRpc:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        import requests
        self.requests = requests
    
    def _call_rpc(self, method, params=None):
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
            response = self.requests.post(self.base_url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            result = response.json()
            if "result" in result:
                return result["result"]
            elif "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            else:
                raise Exception("Invalid RPC response")
        except Exception as e:
            raise Exception(f"RPC call failed: {e}")
    
    def __getattr__(self, method_name):
        def rpc_method(*args):
            return self._call_rpc(method_name, list(args))
        return rpc_method

# Import VoiceCallManager from voicebot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'examples'))
from voicebot_advanced import VoiceCallManager

def test_voice_call_manager():
    print("🎤 Testing VoiceCallManager with Simple Server")
    print("=" * 50)
    
    # Create mock RPC
    rpc = MockRpc()
    
    # Create voice call manager
    voice_manager = VoiceCallManager(rpc)
    
    print("\n1. Initializing voice calls...")
    success = voice_manager.init_voice_calls()
    print(f"   Success: {success}")
    
    print("\n2. Getting node ID...")
    node_id = voice_manager.get_node_id()
    print(f"   Node ID: {node_id}")
    
    print("\n3. Starting a call...")
    call_id = voice_manager.start_call("test_peer_123")
    print(f"   Call ID: {call_id}")
    
    print("\n4. Getting call status...")
    if call_id:
        status = voice_manager.get_call_status(call_id)
        print(f"   Status: {status}")
    
    print("\n5. Listing active calls...")
    calls = voice_manager.get_active_calls()
    print(f"   Active calls: {calls}")
    
    print("\n6. Simulating incoming call...")
    incoming_call = voice_manager.simulate_incoming_call("incoming_peer_456")
    print(f"   Incoming call ID: {incoming_call}")
    
    print("\n7. Accepting incoming call...")
    if incoming_call:
        accepted = voice_manager.accept_call(incoming_call)
        print(f"   Accepted: {accepted}")
    
    print("\n8. Listing active calls again...")
    calls = voice_manager.get_active_calls()
    print(f"   Active calls: {calls}")
    
    print("\n9. Ending calls...")
    if call_id:
        ended = voice_manager.end_call(call_id)
        print(f"   Ended call {call_id}: {ended}")
    
    if incoming_call:
        ended = voice_manager.end_call(incoming_call)
        print(f"   Ended call {incoming_call}: {ended}")
    
    print("\n10. Final check - active calls...")
    calls = voice_manager.get_active_calls()
    print(f"   Active calls: {calls}")
    
    print("\n✅ VoiceCallManager test completed!")

if __name__ == "__main__":
    try:
        test_voice_call_manager()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()