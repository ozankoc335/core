#!/usr/bin/env python3
"""
Test script for callme integration in deltachat-jsonrpc
"""

import json
import requests
import subprocess
import time
import sys
import os

def test_callme_integration():
    """Test callme P2P voice call integration"""
    
    print("🎯 Testing Callme Integration in DeltaChat-JSONRPC")
    print("=" * 60)
    
    # Start simple server
    print("📡 Starting simple JSON-RPC server...")
    server_process = subprocess.Popen([
        "cargo", "run", "--bin", "simple_server"
    ], cwd="/workspace/core/deltachat-jsonrpc", 
       stdout=subprocess.PIPE, 
       stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test basic voice call initialization
        print("\n1️⃣ Testing voice call initialization...")
        response = requests.post("http://localhost:3030", json={
            "jsonrpc": "2.0",
            "method": "init_voice_calls",
            "id": 1
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Voice calls initialized: {result}")
            node_id = result.get('result')
        else:
            print(f"❌ Failed to initialize voice calls: {response.text}")
            return False
        
        # Test getting callme node ID
        print("\n2️⃣ Testing callme node ID retrieval...")
        response = requests.post("http://localhost:3030", json={
            "jsonrpc": "2.0",
            "method": "get_callme_node_id",
            "id": 2
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Callme node ID: {result}")
            callme_node_id = result.get('result')
        else:
            print(f"❌ Failed to get callme node ID: {response.text}")
            return False
        
        # Test starting a callme P2P call
        if callme_node_id:
            print("\n3️⃣ Testing callme P2P call start...")
            response = requests.post("http://localhost:3030", json={
                "jsonrpc": "2.0",
                "method": "start_callme_call",
                "params": {"peer_node_id": callme_node_id},
                "id": 3
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Callme call started: {result}")
                call_id = result.get('result')
            else:
                print(f"❌ Failed to start callme call: {response.text}")
                return False
        
        # Test getting active callme calls
        print("\n4️⃣ Testing active callme calls...")
        response = requests.post("http://localhost:3030", json={
            "jsonrpc": "2.0",
            "method": "get_active_callme_calls",
            "id": 4
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Active callme calls: {result}")
        else:
            print(f"❌ Failed to get active callme calls: {response.text}")
            return False
        
        # Test getting callme call status
        if call_id:
            print("\n5️⃣ Testing callme call status...")
            response = requests.post("http://localhost:3030", json={
                "jsonrpc": "2.0",
                "method": "get_callme_call_status",
                "params": {"call_id": call_id},
                "id": 5
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Callme call status: {result}")
            else:
                print(f"❌ Failed to get callme call status: {response.text}")
                return False
        
        # Test ending callme call
        if call_id:
            print("\n6️⃣ Testing callme call end...")
            response = requests.post("http://localhost:3030", json={
                "jsonrpc": "2.0",
                "method": "end_callme_call",
                "params": {"call_id": call_id},
                "id": 6
            })
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Callme call ended: {result}")
            else:
                print(f"❌ Failed to end callme call: {response.text}")
                return False
        
        print("\n🎉 All callme integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
        
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    success = test_callme_integration()
    sys.exit(0 if success else 1)