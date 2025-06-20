use deltachat_jsonrpc::voice_call::VoiceCallManager;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    println!("Testing Voice Call Manager...");
    
    // Create a new voice call manager
    let manager = VoiceCallManager::new().await?;
    println!("Voice call manager created with node ID: {}", manager.node_id());
    
    // Start listening for calls
    manager.start_listening().await?;
    
    // Simulate starting a call
    let call_id = manager.start_call("test_peer_123".to_string()).await?;
    println!("Started call with ID: {}", call_id);
    
    // Get active calls
    let active_calls = manager.get_active_calls().await;
    println!("Active calls: {:?}", active_calls);
    
    // Get call status
    if let Some(status) = manager.get_call_status(&call_id).await {
        println!("Call status: {:?}", status);
    }
    
    // Simulate an incoming call
    let incoming_call_id = manager.simulate_incoming_call("incoming_peer_456".to_string()).await?;
    println!("Simulated incoming call with ID: {}", incoming_call_id);
    
    // Accept the incoming call
    manager.accept_call(&incoming_call_id).await?;
    println!("Accepted incoming call");
    
    // Get updated active calls
    let active_calls = manager.get_active_calls().await;
    println!("Active calls after accepting: {:?}", active_calls);
    
    // End the first call
    manager.end_call(&call_id).await?;
    println!("Ended first call");
    
    // End the second call
    manager.end_call(&incoming_call_id).await?;
    println!("Ended second call");
    
    // Final check
    let active_calls = manager.get_active_calls().await;
    println!("Final active calls: {:?}", active_calls);
    
    println!("Voice call test completed successfully!");
    Ok(())
}