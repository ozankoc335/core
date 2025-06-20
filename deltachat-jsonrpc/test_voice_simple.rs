// Basit voice call test - minimal dependencies ile
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

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
    active_calls: Arc<RwLock<HashMap<String, ActiveCall>>>,
    node_id: String,
}

impl VoiceCallManager {
    pub async fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let node_id = format!("node_{}", rand::random::<u32>());
        Ok(Self {
            active_calls: Arc::new(RwLock::new(HashMap::new())),
            node_id,
        })
    }

    pub fn node_id(&self) -> &str {
        &self.node_id
    }

    pub async fn start_listening(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!("Voice call manager started listening for incoming calls");
        Ok(())
    }

    pub async fn start_call(&self, remote_peer_id: String) -> Result<String, Box<dyn std::error::Error>> {
        let call_id = format!("call_{}", rand::random::<u32>());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: false,
            status: CallStatus::Ringing,
        };

        self.active_calls.write().await.insert(call_id.clone(), active_call);
        println!("Starting call with ID: {}", call_id);
        Ok(call_id)
    }

    pub async fn accept_call(&self, call_id: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut calls = self.active_calls.write().await;
        if let Some(call) = calls.get_mut(call_id) {
            call.status = CallStatus::Connected;
            println!("Accepted call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id).into())
        }
    }

    pub async fn end_call(&self, call_id: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut calls = self.active_calls.write().await;
        if let Some(mut call) = calls.remove(call_id) {
            call.status = CallStatus::Ended;
            println!("Ended call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id).into())
        }
    }

    pub async fn get_active_calls(&self) -> Vec<String> {
        self.active_calls.read().await.keys().cloned().collect()
    }

    pub async fn get_call_status(&self, call_id: &str) -> Option<CallStatus> {
        self.active_calls.read().await.get(call_id).map(|call| call.status.clone())
    }

    pub async fn simulate_incoming_call(&self, remote_peer_id: String) -> Result<String, Box<dyn std::error::Error>> {
        let call_id = format!("call_{}", rand::random::<u32>());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: true,
            status: CallStatus::Ringing,
        };

        self.active_calls.write().await.insert(call_id.clone(), active_call);
        println!("Simulated incoming call: {}", call_id);
        Ok(call_id)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🎤 Voice Call Manager Test Başlıyor...");
    
    // Voice call manager oluştur
    let manager = VoiceCallManager::new().await?;
    println!("✅ Voice call manager oluşturuldu, Node ID: {}", manager.node_id());
    
    // Dinlemeye başla
    manager.start_listening().await?;
    
    // Giden arama başlat
    let call_id = manager.start_call("test_peer_123".to_string()).await?;
    println!("📞 Giden arama başlatıldı: {}", call_id);
    
    // Aktif aramaları listele
    let active_calls = manager.get_active_calls().await;
    println!("📋 Aktif aramalar: {:?}", active_calls);
    
    // Arama durumunu kontrol et
    if let Some(status) = manager.get_call_status(&call_id).await {
        println!("📊 Arama durumu: {:?}", status);
    }
    
    // Gelen arama simüle et
    let incoming_call_id = manager.simulate_incoming_call("incoming_peer_456".to_string()).await?;
    println!("📲 Gelen arama simüle edildi: {}", incoming_call_id);
    
    // Gelen aramayı kabul et
    manager.accept_call(&incoming_call_id).await?;
    println!("✅ Gelen arama kabul edildi");
    
    // Güncellenmiş aktif aramaları listele
    let active_calls = manager.get_active_calls().await;
    println!("📋 Kabul sonrası aktif aramalar: {:?}", active_calls);
    
    // İlk aramayı sonlandır
    manager.end_call(&call_id).await?;
    println!("❌ İlk arama sonlandırıldı");
    
    // İkinci aramayı sonlandır
    manager.end_call(&incoming_call_id).await?;
    println!("❌ İkinci arama sonlandırıldı");
    
    // Son kontrol
    let active_calls = manager.get_active_calls().await;
    println!("📋 Son durum - aktif aramalar: {:?}", active_calls);
    
    println!("🎉 Voice call test başarıyla tamamlandı!");
    Ok(())
}