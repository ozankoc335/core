#[cfg(test)]
mod tests {
    use super::voice_call::*;

    #[tokio::test]
    async fn test_voice_call_manager_creation() {
        let manager = VoiceCallManager::new().await.unwrap();
        assert!(!manager.node_id().is_empty());
        assert!(manager.node_id().starts_with("node_"));
    }

    #[tokio::test]
    async fn test_start_call() {
        let manager = VoiceCallManager::new().await.unwrap();
        let call_id = manager.start_call("test_peer".to_string()).await.unwrap();
        
        assert!(!call_id.is_empty());
        assert!(call_id.starts_with("call_"));
        
        let active_calls = manager.get_active_calls().await;
        assert_eq!(active_calls.len(), 1);
        assert_eq!(active_calls[0], call_id);
    }

    #[tokio::test]
    async fn test_call_status() {
        let manager = VoiceCallManager::new().await.unwrap();
        let call_id = manager.start_call("test_peer".to_string()).await.unwrap();
        
        let status = manager.get_call_status(&call_id).await;
        assert!(status.is_some());
        assert!(matches!(status.unwrap(), CallStatus::Ringing));
    }

    #[tokio::test]
    async fn test_accept_call() {
        let manager = VoiceCallManager::new().await.unwrap();
        let call_id = manager.simulate_incoming_call("test_peer".to_string()).await.unwrap();
        
        manager.accept_call(&call_id).await.unwrap();
        
        let status = manager.get_call_status(&call_id).await;
        assert!(status.is_some());
        assert!(matches!(status.unwrap(), CallStatus::Connected));
    }

    #[tokio::test]
    async fn test_end_call() {
        let manager = VoiceCallManager::new().await.unwrap();
        let call_id = manager.start_call("test_peer".to_string()).await.unwrap();
        
        manager.end_call(&call_id).await.unwrap();
        
        let active_calls = manager.get_active_calls().await;
        assert_eq!(active_calls.len(), 0);
        
        let status = manager.get_call_status(&call_id).await;
        assert!(status.is_none());
    }

    #[tokio::test]
    async fn test_multiple_calls() {
        let manager = VoiceCallManager::new().await.unwrap();
        
        let call1 = manager.start_call("peer1".to_string()).await.unwrap();
        let call2 = manager.simulate_incoming_call("peer2".to_string()).await.unwrap();
        
        let active_calls = manager.get_active_calls().await;
        assert_eq!(active_calls.len(), 2);
        
        manager.end_call(&call1).await.unwrap();
        let active_calls = manager.get_active_calls().await;
        assert_eq!(active_calls.len(), 1);
        
        manager.end_call(&call2).await.unwrap();
        let active_calls = manager.get_active_calls().await;
        assert_eq!(active_calls.len(), 0);
    }
}