// En basit voice call test - sadece std kütüphanesi
use std::collections::HashMap;

// Basit CallStatus enum
#[derive(Debug, Clone)]
pub enum CallStatus {
    Ringing,
    Connected,
    Ended,
    Failed,
}

// Basit ActiveCall struct
#[derive(Debug)]
pub struct ActiveCall {
    call_id: String,
    remote_peer_id: String,
    is_incoming: bool,
    status: CallStatus,
}

// Basit VoiceCallManager
#[derive(Debug)]
pub struct VoiceCallManager {
    active_calls: HashMap<String, ActiveCall>,
    node_id: String,
}

impl VoiceCallManager {
    pub fn new() -> Self {
        let node_id = format!("node_{}", rand_u32());
        Self {
            active_calls: HashMap::new(),
            node_id,
        }
    }

    pub fn node_id(&self) -> &str {
        &self.node_id
    }

    pub fn start_listening(&self) -> Result<(), String> {
        println!("Voice call manager started listening for incoming calls");
        Ok(())
    }

    pub fn start_call(&mut self, remote_peer_id: String) -> Result<String, String> {
        let call_id = format!("call_{}", rand_u32());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: false,
            status: CallStatus::Ringing,
        };

        self.active_calls.insert(call_id.clone(), active_call);
        println!("Starting call with ID: {}", call_id);
        Ok(call_id)
    }

    pub fn accept_call(&mut self, call_id: &str) -> Result<(), String> {
        if let Some(call) = self.active_calls.get_mut(call_id) {
            call.status = CallStatus::Connected;
            println!("Accepted call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id))
        }
    }

    pub fn end_call(&mut self, call_id: &str) -> Result<(), String> {
        if let Some(mut call) = self.active_calls.remove(call_id) {
            call.status = CallStatus::Ended;
            println!("Ended call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id))
        }
    }

    pub fn get_active_calls(&self) -> Vec<String> {
        self.active_calls.keys().cloned().collect()
    }

    pub fn get_call_status(&self, call_id: &str) -> Option<CallStatus> {
        self.active_calls.get(call_id).map(|call| call.status.clone())
    }

    pub fn simulate_incoming_call(&mut self, remote_peer_id: String) -> Result<String, String> {
        let call_id = format!("call_{}", rand_u32());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: true,
            status: CallStatus::Ringing,
        };

        self.active_calls.insert(call_id.clone(), active_call);
        println!("Simulated incoming call: {}", call_id);
        Ok(call_id)
    }
}

// Basit random sayı üretici
fn rand_u32() -> u32 {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (now.as_nanos() % u32::MAX as u128) as u32
}

fn main() -> Result<(), String> {
    println!("🎤 Voice Call Manager Test Başlıyor...");
    
    // Voice call manager oluştur
    let mut manager = VoiceCallManager::new();
    println!("✅ Voice call manager oluşturuldu, Node ID: {}", manager.node_id());
    
    // Dinlemeye başla
    manager.start_listening()?;
    
    // Giden arama başlat
    let call_id = manager.start_call("test_peer_123".to_string())?;
    println!("📞 Giden arama başlatıldı: {}", call_id);
    
    // Aktif aramaları listele
    let active_calls = manager.get_active_calls();
    println!("📋 Aktif aramalar: {:?}", active_calls);
    
    // Arama durumunu kontrol et
    if let Some(status) = manager.get_call_status(&call_id) {
        println!("📊 Arama durumu: {:?}", status);
    }
    
    // Gelen arama simüle et
    let incoming_call_id = manager.simulate_incoming_call("incoming_peer_456".to_string())?;
    println!("📲 Gelen arama simüle edildi: {}", incoming_call_id);
    
    // Gelen aramayı kabul et
    manager.accept_call(&incoming_call_id)?;
    println!("✅ Gelen arama kabul edildi");
    
    // Güncellenmiş aktif aramaları listele
    let active_calls = manager.get_active_calls();
    println!("📋 Kabul sonrası aktif aramalar: {:?}", active_calls);
    
    // İlk aramayı sonlandır
    manager.end_call(&call_id)?;
    println!("❌ İlk arama sonlandırıldı");
    
    // İkinci aramayı sonlandır
    manager.end_call(&incoming_call_id)?;
    println!("❌ İkinci arama sonlandırıldı");
    
    // Son kontrol
    let active_calls = manager.get_active_calls();
    println!("📋 Son durum - aktif aramalar: {:?}", active_calls);
    
    println!("🎉 Voice call test başarıyla tamamlandı!");
    
    // JSON-RPC API örnekleri göster
    println!("\n📡 JSON-RPC API Kullanım Örnekleri:");
    println!("1. Voice call manager başlat:");
    println!(r#"   {{"jsonrpc": "2.0", "method": "init_voice_calls", "params": [], "id": 1}}"#);
    
    println!("2. Arama başlat:");
    println!(r#"   {{"jsonrpc": "2.0", "method": "start_voice_call", "params": ["peer_123"], "id": 2}}"#);
    
    println!("3. Aramayı kabul et:");
    println!(r#"   {{"jsonrpc": "2.0", "method": "accept_voice_call", "params": ["call_abc"], "id": 3}}"#);
    
    println!("4. Aktif aramaları listele:");
    println!(r#"   {{"jsonrpc": "2.0", "method": "get_active_voice_calls", "params": [], "id": 4}}"#);
    
    println!("5. Aramayı sonlandır:");
    println!(r#"   {{"jsonrpc": "2.0", "method": "end_voice_call", "params": ["call_abc"], "id": 5}}"#);
    
    Ok(())
}