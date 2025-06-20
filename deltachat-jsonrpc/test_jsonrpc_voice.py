#!/usr/bin/env python3
"""
DeltaChat JSON-RPC Voice Call Test
Bu script deltachat-jsonrpc server'ına voice call komutları gönderir
"""

import json
import requests
import time

# JSON-RPC server URL (deltachat-jsonrpc çalışıyor olmalı)
SERVER_URL = "http://localhost:3000"

def send_jsonrpc_request(method, params=None, id_val=1):
    """JSON-RPC request gönder"""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or [],
        "id": id_val
    }
    
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {e}"}

def test_voice_calls():
    """Voice call özelliklerini test et"""
    print("🎤 DeltaChat JSON-RPC Voice Call Test")
    print("=" * 50)
    
    # 1. Voice call manager'ı başlat
    print("1. Voice call manager başlatılıyor...")
    result = send_jsonrpc_request("init_voice_calls")
    print(f"   Sonuç: {result}")
    
    if "error" in result:
        print("❌ Voice call manager başlatılamadı!")
        return
    
    # 2. Node ID'yi al
    print("\n2. Node ID alınıyor...")
    result = send_jsonrpc_request("get_voice_node_id")
    print(f"   Node ID: {result.get('result', 'N/A')}")
    
    # 3. Giden arama başlat
    print("\n3. Giden arama başlatılıyor...")
    result = send_jsonrpc_request("start_voice_call", ["test_peer_123"])
    call_id = result.get("result")
    print(f"   Call ID: {call_id}")
    
    # 4. Aktif aramaları listele
    print("\n4. Aktif aramalar listeleniyor...")
    result = send_jsonrpc_request("get_active_voice_calls")
    print(f"   Aktif aramalar: {result.get('result', [])}")
    
    # 5. Arama durumunu kontrol et
    if call_id:
        print(f"\n5. Arama durumu kontrol ediliyor (Call ID: {call_id})...")
        result = send_jsonrpc_request("get_voice_call_status", [call_id])
        print(f"   Durum: {result.get('result')}")
    
    # 6. Gelen arama simüle et
    print("\n6. Gelen arama simüle ediliyor...")
    result = send_jsonrpc_request("simulate_incoming_voice_call", ["incoming_peer_456"])
    incoming_call_id = result.get("result")
    print(f"   Incoming Call ID: {incoming_call_id}")
    
    # 7. Gelen aramayı kabul et
    if incoming_call_id:
        print(f"\n7. Gelen arama kabul ediliyor (Call ID: {incoming_call_id})...")
        result = send_jsonrpc_request("accept_voice_call", [incoming_call_id])
        print(f"   Sonuç: {result}")
    
    # 8. Güncellenmiş aktif aramaları listele
    print("\n8. Güncellenmiş aktif aramalar...")
    result = send_jsonrpc_request("get_active_voice_calls")
    print(f"   Aktif aramalar: {result.get('result', [])}")
    
    # 9. Aramaları sonlandır
    if call_id:
        print(f"\n9. İlk arama sonlandırılıyor (Call ID: {call_id})...")
        result = send_jsonrpc_request("end_voice_call", [call_id])
        print(f"   Sonuç: {result}")
    
    if incoming_call_id:
        print(f"\n10. İkinci arama sonlandırılıyor (Call ID: {incoming_call_id})...")
        result = send_jsonrpc_request("end_voice_call", [incoming_call_id])
        print(f"    Sonuç: {result}")
    
    # 11. Son durum kontrolü
    print("\n11. Son durum kontrolü...")
    result = send_jsonrpc_request("get_active_voice_calls")
    print(f"    Aktif aramalar: {result.get('result', [])}")
    
    print("\n🎉 Voice call test tamamlandı!")

def show_usage():
    """Kullanım örneklerini göster"""
    print("\n📡 JSON-RPC Voice Call API Kullanım Örnekleri:")
    print("-" * 50)
    
    examples = [
        ("Voice call manager başlat", "init_voice_calls", []),
        ("Node ID al", "get_voice_node_id", []),
        ("Arama başlat", "start_voice_call", ["peer_id_123"]),
        ("Aramayı kabul et", "accept_voice_call", ["call_abc123"]),
        ("Aramayı sonlandır", "end_voice_call", ["call_abc123"]),
        ("Aktif aramaları listele", "get_active_voice_calls", []),
        ("Arama durumunu al", "get_voice_call_status", ["call_abc123"]),
        ("Gelen arama simüle et", "simulate_incoming_voice_call", ["peer_id_456"])
    ]
    
    for desc, method, params in examples:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        print(f"\n{desc}:")
        print(f"  {json.dumps(payload, indent=2)}")

if __name__ == "__main__":
    print("DeltaChat JSON-RPC Voice Call Test Script")
    print("Bu script deltachat-jsonrpc server'ının çalışıyor olmasını gerektirir.")
    print(f"Server URL: {SERVER_URL}")
    print("\nServer'ı başlatmak için:")
    print("  cd /workspace/core/deltachat-jsonrpc")
    print("  cargo run")
    print("\nVeya sadece örnekleri görmek için 'examples' yazın:")
    
    user_input = input("\nDevam etmek için Enter'a basın (veya 'examples' yazın): ").strip()
    
    if user_input.lower() == 'examples':
        show_usage()
    else:
        test_voice_calls()
        show_usage()