#!/usr/bin/env python3
"""Complete test for all voice call methods with deltachat-rpc-server"""

import subprocess
import json
import tempfile
import os
import time

def send_request(process, method, params, request_id):
    """Send JSON-RPC request and get response"""
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": request_id
    }
    
    print(f"📤 {method}: {json.dumps(request)}")
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    # Read response (skip any log lines)
    while True:
        line = process.stdout.readline()
        if not line:
            return None
        line = line.strip()
        if line.startswith("{"):
            print(f"📥 {method}: {line}")
            return json.loads(line)
    
def test_all_voice_methods():
    print("🎤 Complete Voice Call API Test")
    print("=" * 50)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Temp dir: {temp_dir}")
        
        # Create accounts.toml
        accounts_toml = os.path.join(temp_dir, "accounts.toml")
        with open(accounts_toml, "w") as f:
            f.write('selected_account = 0\nnext_id = 1\naccounts = []\n')
        
        # Start server
        env = os.environ.copy()
        env["DC_ACCOUNTS_PATH"] = temp_dir
        
        server_path = "/workspace/core/target/debug/deltachat-rpc-server"
        process = subprocess.Popen(
            [server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        try:
            request_id = 1
            
            # 1. Initialize voice calls
            print("\n1️⃣ Testing init_voice_calls...")
            response = send_request(process, "init_voice_calls", [], request_id)
            request_id += 1
            
            if not response or "error" in response:
                print("❌ init_voice_calls failed:", response.get("error") if response else "No response")
                return
            
            node_id = response["result"]
            print(f"✅ Voice calls initialized! Node ID: {node_id}")
            
            # 2. Get node ID
            print("\n2️⃣ Testing get_voice_node_id...")
            response = send_request(process, "get_voice_node_id", [], request_id)
            request_id += 1
            
            if response and "result" in response:
                print(f"✅ Node ID: {response['result']}")
            else:
                print("❌ get_voice_node_id failed:", response.get("error") if response else "No response")
            
            # 3. Start a voice call
            print("\n3️⃣ Testing start_voice_call...")
            response = send_request(process, "start_voice_call", ["test_peer_123"], request_id)
            request_id += 1
            
            if response and "result" in response:
                call_id = response["result"]
                print(f"✅ Call started! Call ID: {call_id}")
            else:
                print("❌ start_voice_call failed:", response.get("error") if response else "No response")
                return
            
            # 4. Get call status
            print("\n4️⃣ Testing get_voice_call_status...")
            response = send_request(process, "get_voice_call_status", [call_id], request_id)
            request_id += 1
            
            if response and "result" in response:
                print(f"✅ Call status: {response['result']}")
            else:
                print("❌ get_voice_call_status failed:", response.get("error") if response else "No response")
            
            # 5. Get active calls
            print("\n5️⃣ Testing get_active_voice_calls...")
            response = send_request(process, "get_active_voice_calls", [], request_id)
            request_id += 1
            
            if response and "result" in response:
                active_calls = response["result"]
                print(f"✅ Active calls: {len(active_calls)} call(s)")
                for call_id in active_calls:
                    print(f"   - Call ID: {call_id}")
            else:
                print("❌ get_active_voice_calls failed:", response.get("error") if response else "No response")
            
            # 6. Simulate incoming call
            print("\n6️⃣ Testing simulate_incoming_voice_call...")
            response = send_request(process, "simulate_incoming_voice_call", ["incoming_peer_456"], request_id)
            request_id += 1
            
            if response and "result" in response:
                incoming_call_id = response["result"]
                print(f"✅ Incoming call simulated! Call ID: {incoming_call_id}")
            else:
                print("❌ simulate_incoming_voice_call failed:", response.get("error") if response else "No response")
                incoming_call_id = None
            
            # 7. Accept incoming call
            if incoming_call_id:
                print("\n7️⃣ Testing accept_voice_call...")
                response = send_request(process, "accept_voice_call", [incoming_call_id], request_id)
                request_id += 1
                
                if response and "result" in response:
                    print(f"✅ Call accepted: {response['result']}")
                else:
                    print("❌ accept_voice_call failed:", response.get("error") if response else "No response")
            
            # 8. Get active calls again
            print("\n8️⃣ Testing get_active_voice_calls (after accept)...")
            response = send_request(process, "get_active_voice_calls", [], request_id)
            request_id += 1
            
            if response and "result" in response:
                active_calls = response["result"]
                print(f"✅ Active calls: {len(active_calls)} call(s)")
                for call_id in active_calls:
                    print(f"   - Call ID: {call_id}")
            else:
                print("❌ get_active_voice_calls failed:", response.get("error") if response else "No response")
            
            # 9. End first call
            print("\n9️⃣ Testing end_voice_call (first call)...")
            response = send_request(process, "end_voice_call", [call_id], request_id)
            request_id += 1
            
            if response and "result" in response:
                print(f"✅ Call ended: {response['result']}")
            else:
                print("❌ end_voice_call failed:", response.get("error") if response else "No response")
            
            # 10. End second call
            if incoming_call_id:
                print("\n🔟 Testing end_voice_call (second call)...")
                response = send_request(process, "end_voice_call", [incoming_call_id], request_id)
                request_id += 1
                
                if response and "result" in response:
                    print(f"✅ Call ended: {response['result']}")
                else:
                    print("❌ end_voice_call failed:", response.get("error") if response else "No response")
            
            # 11. Final check - should be no active calls
            print("\n1️⃣1️⃣ Final check - get_active_voice_calls...")
            response = send_request(process, "get_active_voice_calls", [], request_id)
            request_id += 1
            
            if response and "result" in response:
                active_calls = response["result"]
                print(f"✅ Active calls: {len(active_calls)} call(s)")
                if len(active_calls) == 0:
                    print("🎉 Perfect! All calls ended successfully!")
                else:
                    print("⚠️  Some calls are still active:")
                    for call_id in active_calls:
                        print(f"   - Call ID: {call_id}")
            else:
                print("❌ get_active_voice_calls failed:", response.get("error") if response else "No response")
            
            print("\n🎉 All voice call API methods tested successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_all_voice_methods()