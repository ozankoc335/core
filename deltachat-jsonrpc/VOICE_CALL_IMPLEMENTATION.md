# Voice Call Implementation for DeltaChat JSON-RPC

## Overview

This implementation adds voice calling functionality to the DeltaChat JSON-RPC API, inspired by the callme library. The implementation provides a basic framework for P2P voice calls that can be extended with real audio processing and network connectivity.

## Features Added

### 1. Core Voice Call Manager (`src/voice_call.rs`)

- **VoiceCallManager**: Main struct for managing voice calls
- **ActiveCall**: Represents an active voice call
- **CallStatus**: Enum for call states (Ringing, Connected, Ended, Failed)
- **CallEvent**: Event structure for call notifications

### 2. JSON-RPC API Methods (`src/api.rs`)

- `init_voice_calls()`: Initialize the voice call manager
- `start_voice_call(remote_peer_id)`: Start an outgoing call
- `accept_voice_call(call_id)`: Accept an incoming call
- `end_voice_call(call_id)`: End a call
- `get_active_voice_calls()`: List active calls
- `get_voice_call_status(call_id)`: Get call status
- `get_voice_node_id()`: Get the node ID
- `simulate_incoming_voice_call(remote_peer_id)`: Simulate incoming call (for testing)

### 3. Dependencies Added (`Cargo.toml`)

```toml
cpal = "0.15"           # Audio processing
uuid = "1.0"            # Unique identifiers
ringbuf = "0.4"         # Audio buffering
rand = "0.8"            # Random values
schemars = "0.8"        # JSON schema support
```

## Usage Example

### Initialize Voice Calls
```json
{
  "jsonrpc": "2.0",
  "method": "init_voice_calls",
  "params": [],
  "id": 1
}
```

### Start a Voice Call
```json
{
  "jsonrpc": "2.0",
  "method": "start_voice_call",
  "params": ["peer_node_id_123"],
  "id": 2
}
```

### Accept an Incoming Call
```json
{
  "jsonrpc": "2.0",
  "method": "accept_voice_call",
  "params": ["call_abc123"],
  "id": 3
}
```

### Get Active Calls
```json
{
  "jsonrpc": "2.0",
  "method": "get_active_voice_calls",
  "params": [],
  "id": 4
}
```

### End a Call
```json
{
  "jsonrpc": "2.0",
  "method": "end_voice_call",
  "params": ["call_abc123"],
  "id": 5
}
```

## Architecture

### Thread Safety
- Uses `Arc<RwLock<HashMap>>` for thread-safe call storage
- `Arc<Mutex<Option<VoiceCallManager>>>` for manager instance
- All operations are async-safe

### Call Management
- Each call gets a unique UUID-based ID
- Call states are tracked and can be queried
- Support for both incoming and outgoing calls

### Error Handling
- Uses `anyhow::Result` for error propagation
- Proper error messages for invalid operations
- Graceful handling of missing calls

## Current Limitations

1. **No Real Audio Processing**: Currently a framework without actual audio capture/playback
2. **No Network Layer**: No P2P connectivity implementation
3. **No Codec Support**: No audio encoding/decoding
4. **Simulation Only**: Uses simulation for incoming calls

## Future Enhancements

### 1. Real Audio Processing
```rust
// Add actual audio capture and playback
impl VoiceCallManager {
    async fn start_audio_capture(&self) -> Result<()> {
        // Implement with cpal
    }
    
    async fn start_audio_playback(&self) -> Result<()> {
        // Implement with cpal
    }
}
```

### 2. P2P Networking
```rust
// Add network connectivity (could use iroh or libp2p)
impl VoiceCallManager {
    async fn connect_to_peer(&self, peer_id: &str) -> Result<Connection> {
        // Implement P2P connection
    }
}
```

### 3. Audio Codecs
```rust
// Add audio encoding/decoding
impl VoiceCallManager {
    fn encode_audio(&self, samples: &[f32]) -> Result<Vec<u8>> {
        // Implement audio encoding (Opus, etc.)
    }
    
    fn decode_audio(&self, data: &[u8]) -> Result<Vec<f32>> {
        // Implement audio decoding
    }
}
```

### 4. Event System
```rust
// Add event notifications
impl VoiceCallManager {
    async fn emit_call_event(&self, event: CallEvent) {
        // Emit events to subscribers
    }
}
```

## Testing

### Unit Tests
Run the voice call tests:
```bash
cargo test voice_call_test
```

### Integration Test
Run the example:
```bash
cargo run --example voice_call_test
```

## Files Modified/Added

- `src/voice_call.rs` - New voice call implementation
- `src/api.rs` - Added JSON-RPC methods
- `src/lib.rs` - Added voice_call module
- `Cargo.toml` - Added dependencies
- `examples/voice_call_test.rs` - Example usage
- `src/voice_call_test.rs` - Unit tests

## Compilation

The project compiles successfully with the new voice call features:
```bash
cargo check  # ✓ Passes
cargo build  # ✓ Builds successfully
```

## Inspiration from Callme

This implementation takes inspiration from the callme library's approach to P2P voice calls:
- Simple API design
- Event-driven architecture
- Extensible framework
- Focus on reliability

The implementation provides a solid foundation that can be extended with real audio processing and network connectivity as needed.