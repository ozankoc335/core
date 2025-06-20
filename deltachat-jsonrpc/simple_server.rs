// Basit JSON-RPC server - voice call özelliklerini test etmek için
use std::collections::HashMap;
use std::sync::Arc;
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

// Basit CallStatus enum
#[derive(Debug, Clone)]
pub enum CallStatus {
    Ringing,
    Connected,
    Ended,
    Failed,
}

impl CallStatus {
    fn to_string(&self) -> &'static str {
        match self {
            CallStatus::Ringing => "Ringing",
            CallStatus::Connected => "Connected", 
            CallStatus::Ended => "Ended",
            CallStatus::Failed => "Failed",
        }
    }
}

// Basit ActiveCall struct
#[derive(Debug)]
pub struct ActiveCall {
    call_id: String,
    remote_peer_id: String,
    is_incoming: bool,
    status: CallStatus,
}

// Thread-safe VoiceCallManager
#[derive(Debug)]
pub struct VoiceCallManager {
    active_calls: Arc<std::sync::Mutex<HashMap<String, ActiveCall>>>,
    node_id: String,
}

impl VoiceCallManager {
    pub fn new() -> Self {
        let node_id = format!("node_{}", rand_u32());
        Self {
            active_calls: Arc::new(std::sync::Mutex::new(HashMap::new())),
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

    pub fn start_call(&self, remote_peer_id: String) -> Result<String, String> {
        let call_id = format!("call_{}", rand_u32());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: false,
            status: CallStatus::Ringing,
        };

        self.active_calls.lock().unwrap().insert(call_id.clone(), active_call);
        println!("Starting call with ID: {}", call_id);
        Ok(call_id)
    }

    pub fn accept_call(&self, call_id: &str) -> Result<(), String> {
        let mut calls = self.active_calls.lock().unwrap();
        if let Some(call) = calls.get_mut(call_id) {
            call.status = CallStatus::Connected;
            println!("Accepted call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id))
        }
    }

    pub fn end_call(&self, call_id: &str) -> Result<(), String> {
        let mut calls = self.active_calls.lock().unwrap();
        if let Some(mut call) = calls.remove(call_id) {
            call.status = CallStatus::Ended;
            println!("Ended call: {}", call_id);
            Ok(())
        } else {
            Err(format!("Call not found: {}", call_id))
        }
    }

    pub fn get_active_calls(&self) -> Vec<String> {
        self.active_calls.lock().unwrap().keys().cloned().collect()
    }

    pub fn get_call_status(&self, call_id: &str) -> Option<CallStatus> {
        self.active_calls.lock().unwrap().get(call_id).map(|call| call.status.clone())
    }

    pub fn simulate_incoming_call(&self, remote_peer_id: String) -> Result<String, String> {
        let call_id = format!("call_{}", rand_u32());
        
        let active_call = ActiveCall {
            call_id: call_id.clone(),
            remote_peer_id,
            is_incoming: true,
            status: CallStatus::Ringing,
        };

        self.active_calls.lock().unwrap().insert(call_id.clone(), active_call);
        println!("Simulated incoming call: {}", call_id);
        Ok(call_id)
    }
}

// Global voice call manager
static mut VOICE_MANAGER: Option<VoiceCallManager> = None;
static INIT: std::sync::Once = std::sync::Once::new();

fn get_voice_manager() -> &'static VoiceCallManager {
    unsafe {
        INIT.call_once(|| {
            VOICE_MANAGER = Some(VoiceCallManager::new());
        });
        VOICE_MANAGER.as_ref().unwrap()
    }
}

// Basit random sayı üretici
fn rand_u32() -> u32 {
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap();
    (now.as_nanos() % u32::MAX as u128) as u32
}

// JSON-RPC request parser
#[derive(Debug)]
struct JsonRpcRequest {
    method: String,
    params: Vec<String>,
    id: i32,
}

fn parse_json_rpc(body: &str) -> Result<JsonRpcRequest, String> {
    // Basit JSON parsing (gerçek projede serde kullanın)
    if let Some(method_start) = body.find("\"method\":") {
        let method_part = &body[method_start + 9..];
        if let Some(method_end) = method_part.find(',') {
            let method = method_part[1..method_end-1].to_string();
            
            let params = if let Some(params_start) = body.find("\"params\":") {
                let params_part = &body[params_start + 9..];
                if let Some(params_end) = params_part.find(']') {
                    let params_str = &params_part[1..params_end];
                    params_str.split(',')
                        .map(|s| s.trim().trim_matches('"').to_string())
                        .filter(|s| !s.is_empty())
                        .collect()
                } else {
                    vec![]
                }
            } else {
                vec![]
            };
            
            let id = if let Some(id_start) = body.find("\"id\":") {
                let id_part = &body[id_start + 5..];
                if let Some(id_end) = id_part.find('}') {
                    id_part[..id_end].trim().parse().unwrap_or(1)
                } else {
                    1
                }
            } else {
                1
            };
            
            Ok(JsonRpcRequest { method, params, id })
        } else {
            Err("Invalid method format".to_string())
        }
    } else {
        Err("Method not found".to_string())
    }
}

// JSON-RPC response formatter
fn format_response(id: i32, result: &str) -> String {
    format!(r#"{{"jsonrpc":"2.0","result":{},"id":{}}}"#, result, id)
}

fn format_error(id: i32, error: &str) -> String {
    format!(r#"{{"jsonrpc":"2.0","error":{{"code":-1,"message":"{}"}},"id":{}}}"#, error, id)
}

// Voice call method handler
fn handle_voice_call_method(method: &str, params: &[String]) -> Result<String, String> {
    let manager = get_voice_manager();
    
    match method {
        "init_voice_calls" => {
            manager.start_listening()?;
            Ok(r#""Voice calls initialized""#.to_string())
        },
        "get_voice_node_id" => {
            Ok(format!(r#""{}""#, manager.node_id()))
        },
        "start_voice_call" => {
            if params.is_empty() {
                return Err("Missing peer_id parameter".to_string());
            }
            let call_id = manager.start_call(params[0].clone())?;
            Ok(format!(r#""{}""#, call_id))
        },
        "accept_voice_call" => {
            if params.is_empty() {
                return Err("Missing call_id parameter".to_string());
            }
            manager.accept_call(&params[0])?;
            Ok(r#""Call accepted""#.to_string())
        },
        "end_voice_call" => {
            if params.is_empty() {
                return Err("Missing call_id parameter".to_string());
            }
            manager.end_call(&params[0])?;
            Ok(r#""Call ended""#.to_string())
        },
        "get_active_voice_calls" => {
            let calls = manager.get_active_calls();
            let calls_json = calls.iter()
                .map(|c| format!(r#""{}""#, c))
                .collect::<Vec<_>>()
                .join(",");
            Ok(format!("[{}]", calls_json))
        },
        "get_voice_call_status" => {
            if params.is_empty() {
                return Err("Missing call_id parameter".to_string());
            }
            if let Some(status) = manager.get_call_status(&params[0]) {
                Ok(format!(r#""{}""#, status.to_string()))
            } else {
                Ok("null".to_string())
            }
        },
        "simulate_incoming_voice_call" => {
            if params.is_empty() {
                return Err("Missing peer_id parameter".to_string());
            }
            let call_id = manager.simulate_incoming_call(params[0].clone())?;
            Ok(format!(r#""{}""#, call_id))
        },
        _ => Err(format!("Unknown method: {}", method))
    }
}

// HTTP request handler
fn handle_client(mut stream: TcpStream) {
    let mut reader = BufReader::new(&stream);
    let mut request_line = String::new();
    reader.read_line(&mut request_line).unwrap();
    
    // Read headers
    let mut content_length = 0;
    loop {
        let mut header = String::new();
        reader.read_line(&mut header).unwrap();
        if header.trim().is_empty() {
            break;
        }
        if header.starts_with("Content-Length:") {
            content_length = header[15..].trim().parse().unwrap_or(0);
        }
    }
    
    // Read body
    let mut body = vec![0; content_length];
    if content_length > 0 {
        std::io::Read::read_exact(&mut reader, &mut body).unwrap();
    }
    let body_str = String::from_utf8_lossy(&body);
    
    println!("Received request: {}", body_str);
    
    // Parse JSON-RPC request
    let response = match parse_json_rpc(&body_str) {
        Ok(req) => {
            match handle_voice_call_method(&req.method, &req.params) {
                Ok(result) => format_response(req.id, &result),
                Err(error) => format_error(req.id, &error),
            }
        },
        Err(error) => format_error(1, &error),
    };
    
    println!("Sending response: {}", response);
    
    // Send HTTP response
    let http_response = format!(
        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nAccess-Control-Allow-Origin: *\r\n\r\n{}",
        response.len(),
        response
    );
    
    stream.write_all(http_response.as_bytes()).unwrap();
    stream.flush().unwrap();
}

fn main() {
    println!("🎤 DeltaChat Voice Call JSON-RPC Server");
    println!("======================================");
    
    let listener = TcpListener::bind("127.0.0.1:3000").unwrap();
    println!("🚀 Server listening on http://127.0.0.1:3000");
    println!("📡 Voice call API endpoints available:");
    println!("   - init_voice_calls");
    println!("   - get_voice_node_id");
    println!("   - start_voice_call");
    println!("   - accept_voice_call");
    println!("   - end_voice_call");
    println!("   - get_active_voice_calls");
    println!("   - get_voice_call_status");
    println!("   - simulate_incoming_voice_call");
    println!("\n💡 Test etmek için: python3 test_jsonrpc_voice.py");
    println!("🛑 Durdurmak için: Ctrl+C\n");
    
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                thread::spawn(|| {
                    handle_client(stream);
                });
            }
            Err(e) => {
                println!("Error: {}", e);
            }
        }
    }
}