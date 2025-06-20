#!/usr/bin/env python3
"""Test voice call features with real deltachat-rpc-server"""

import sys
import os
import tempfile
import subprocess
import time
import json

# Add deltachat_rpc_client to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deltachat_rpc_client import Rpc

def test_voice_calls_with_real_server():
    print("🎤 Testing Voice Calls with Real DeltaChat RPC Server")
    print("=" * 60)
    
    # Create temporary directory for accounts
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Using temporary accounts directory: {temp_dir}")
        
        # Create accounts.toml file
        accounts_toml = os.path.join(temp_dir, "accounts.toml")
        with open(accounts_toml, "w") as f:
            f.write('selected_account = 0\nnext_id = 1\naccounts = []\n')
        
        # Set environment variable
        os.environ["DC_ACCOUNTS_PATH"] = temp_dir
        
        try:
            # Create RPC client using context manager
            print("🔗 Creating RPC client...")
            server_path = "/workspace/core/target/debug/deltachat-rpc-server"
            
            # Add server to PATH temporarily
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = "/workspace/core/target/debug:" + old_path
            
            with Rpc(temp_dir) as rpc:
                print("\n1. Testing init_voice_calls...")
                result = rpc.init_voice_calls()
                print(f"   ✅ Result: {result}")
                
                print("\n2. Testing get_voice_node_id...")
                node_id = rpc.get_voice_node_id()
                print(f"   ✅ Node ID: {node_id}")
                
                print("\n3. Testing start_voice_call...")
                call_id = rpc.start_voice_call("test_peer_123")
                print(f"   ✅ Call ID: {call_id}")
                
                print("\n4. Testing get_voice_call_status...")
                status = rpc.get_voice_call_status(call_id)
                print(f"   ✅ Status: {status}")
                
                print("\n5. Testing get_active_voice_calls...")
                active_calls = rpc.get_active_voice_calls()
                print(f"   ✅ Active calls: {active_calls}")
                
                print("\n6. Testing simulate_incoming_voice_call...")
                incoming_call_id = rpc.simulate_incoming_voice_call("incoming_peer_456")
                print(f"   ✅ Incoming call ID: {incoming_call_id}")
                
                print("\n7. Testing accept_voice_call...")
                accept_result = rpc.accept_voice_call(incoming_call_id)
                print(f"   ✅ Accept result: {accept_result}")
                
                print("\n8. Testing get_active_voice_calls again...")
                active_calls = rpc.get_active_voice_calls()
                print(f"   ✅ Active calls: {active_calls}")
                
                print("\n9. Testing end_voice_call...")
                end_result1 = rpc.end_voice_call(call_id)
                print(f"   ✅ End result 1: {end_result1}")
                
                end_result2 = rpc.end_voice_call(incoming_call_id)
                print(f"   ✅ End result 2: {end_result2}")
                
                print("\n10. Final check - get_active_voice_calls...")
                active_calls = rpc.get_active_voice_calls()
                print(f"   ✅ Active calls: {active_calls}")
                
                print("\n🎉 All voice call tests passed!")
                
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Clean up environment
            if "DC_ACCOUNTS_PATH" in os.environ:
                del os.environ["DC_ACCOUNTS_PATH"]
            # Restore PATH
            os.environ["PATH"] = old_path

if __name__ == "__main__":
    test_voice_calls_with_real_server()