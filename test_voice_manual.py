#!/usr/bin/env python3
"""Manual test for voice calls with deltachat-rpc-server"""

import subprocess
import json
import tempfile
import os

def test_voice_manual():
    print("🎤 Manual Voice Call Test")
    print("=" * 40)
    
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
            # Test init_voice_calls
            request = {
                "jsonrpc": "2.0",
                "method": "init_voice_calls",
                "params": [],
                "id": 1
            }
            
            print("📤 Sending:", json.dumps(request))
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # Read response (skip any log lines)
            response_line = ""
            while True:
                line = process.stdout.readline()
                print("📥 Raw line:", repr(line))
                if not line:
                    break
                line = line.strip()
                if line.startswith("{"):
                    response_line = line
                    break
            
            print("📥 JSON Response:", response_line)
            
            if response_line:
                response = json.loads(response_line)
                if "result" in response:
                    print("✅ init_voice_calls successful!")
                    
                    # Test get_voice_node_id
                    request2 = {
                        "jsonrpc": "2.0",
                        "method": "get_voice_node_id",
                        "params": [],
                        "id": 2
                    }
                    
                    print("\n📤 Sending:", json.dumps(request2))
                    process.stdin.write(json.dumps(request2) + "\n")
                    process.stdin.flush()
                    
                    response_line2 = process.stdout.readline()
                    print("📥 Received:", response_line2.strip())
                    
                    if response_line2:
                        response2 = json.loads(response_line2)
                        if "result" in response2:
                            print("✅ get_voice_node_id successful!")
                            print(f"   Node ID: {response2['result']}")
                        else:
                            print("❌ get_voice_node_id failed:", response2.get("error"))
                else:
                    print("❌ init_voice_calls failed:", response.get("error"))
            else:
                print("❌ No response received")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            process.terminate()
            process.wait()

if __name__ == "__main__":
    test_voice_manual()