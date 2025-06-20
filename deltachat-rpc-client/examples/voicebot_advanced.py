#!/usr/bin/env python3
"""Advanced voice call bot example.

This bot extends the echo bot with voice call capabilities using the callme feature.
It can:
- Echo back any message
- Handle voice calls (incoming/outgoing)
- Respond to voice call commands
- Show voice call status
"""

import logging
import sys
import time
from threading import Thread

from deltachat_rpc_client import Bot, DeltaChat, EventType, Rpc, events

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(event):
    if event.kind == EventType.INFO:
        logging.info(event.msg)
    elif event.kind == EventType.WARNING:
        logging.warning(event.msg)


@hooks.on(events.RawEvent(EventType.ERROR))
def log_error(event):
    logging.error(event.msg)


@hooks.on(events.MemberListChanged)
def on_memberlist_changed(event):
    logging.info("member %s was %s", event.member, "added" if event.member_added else "removed")


@hooks.on(events.GroupImageChanged)
def on_group_image_changed(event):
    logging.info("group image %s", "deleted" if event.image_deleted else "changed")


@hooks.on(events.GroupNameChanged)
def on_group_name_changed(event):
    logging.info("group name changed, old name: %s", event.old_name)


# Voice Call Manager Class
class VoiceCallManager:
    def __init__(self, rpc):
        self.rpc = rpc
        self.node_id = None
        self.active_calls = {}
        self.initialized = False
    
    def init_voice_calls(self):
        """Initialize voice call system"""
        try:
            result = self.rpc.init_voice_calls()
            self.initialized = True
            logging.info("✅ Voice calls initialized: %s", result)
            return True
        except Exception as e:
            logging.error("❌ Failed to initialize voice calls: %s", e)
            return False
    
    def get_node_id(self):
        """Get voice call node ID"""
        try:
            self.node_id = self.rpc.get_voice_node_id()
            logging.info("🆔 Voice node ID: %s", self.node_id)
            return self.node_id
        except Exception as e:
            logging.error("❌ Failed to get node ID: %s", e)
            return None
    
    def start_call(self, peer_id):
        """Start outgoing voice call"""
        try:
            call_id = self.rpc.start_voice_call(peer_id)
            self.active_calls[call_id] = {"peer_id": peer_id, "type": "outgoing"}
            logging.info("📞 Started call %s to %s", call_id, peer_id)
            return call_id
        except Exception as e:
            logging.error("❌ Failed to start call: %s", e)
            return None
    
    def accept_call(self, call_id):
        """Accept incoming voice call"""
        try:
            result = self.rpc.accept_voice_call(call_id)
            logging.info("✅ Accepted call %s: %s", call_id, result)
            return True
        except Exception as e:
            logging.error("❌ Failed to accept call: %s", e)
            return False
    
    def end_call(self, call_id):
        """End voice call"""
        try:
            result = self.rpc.end_voice_call(call_id)
            if call_id in self.active_calls:
                del self.active_calls[call_id]
            logging.info("📴 Ended call %s: %s", call_id, result)
            return True
        except Exception as e:
            logging.error("❌ Failed to end call: %s", e)
            return False
    
    def get_active_calls(self):
        """Get list of active calls"""
        try:
            calls = self.rpc.get_active_voice_calls()
            logging.info("📋 Active calls: %s", calls)
            return calls
        except Exception as e:
            logging.error("❌ Failed to get active calls: %s", e)
            return []
    
    def get_call_status(self, call_id):
        """Get call status"""
        try:
            status = self.rpc.get_voice_call_status(call_id)
            logging.info("📊 Call %s status: %s", call_id, status)
            return status
        except Exception as e:
            logging.error("❌ Failed to get call status: %s", e)
            return None
    
    def simulate_incoming_call(self, peer_id):
        """Simulate incoming call for testing"""
        try:
            call_id = self.rpc.simulate_incoming_voice_call(peer_id)
            self.active_calls[call_id] = {"peer_id": peer_id, "type": "incoming"}
            logging.info("📲 Simulated incoming call %s from %s", call_id, peer_id)
            return call_id
        except Exception as e:
            logging.error("❌ Failed to simulate incoming call: %s", e)
            return None


# Global voice call manager
voice_manager = None


@hooks.on(events.NewMessage(func=lambda e: not e.command))
def echo(event):
    """Echo back non-command messages"""
    snapshot = event.message_snapshot
    if snapshot.text or snapshot.file:
        snapshot.chat.send_message(text=snapshot.text, file=snapshot.file)


@hooks.on(events.NewMessage(command="/help"))
def help_command(event):
    """Show help message"""
    snapshot = event.message_snapshot
    help_text = """🤖 VoiceBot Commands:

📝 Basic:
/help - Show this help

🎤 Voice Calls:
/voice_init - Initialize voice calls
/voice_id - Show voice node ID
/voice_call <peer_id> - Start voice call
/voice_accept <call_id> - Accept incoming call
/voice_end <call_id> - End voice call
/voice_status <call_id> - Get call status
/voice_list - List active calls
/voice_test <peer_id> - Simulate incoming call

📞 Example:
/voice_init
/voice_call peer_123
/voice_list
/voice_end call_456

Send me any message and I will echo it back!"""
    
    snapshot.chat.send_text(help_text)


@hooks.on(events.NewMessage(command="/voice_init"))
def voice_init_command(event):
    """Initialize voice call system"""
    global voice_manager
    snapshot = event.message_snapshot
    
    if voice_manager and voice_manager.init_voice_calls():
        node_id = voice_manager.get_node_id()
        snapshot.chat.send_text(f"✅ Voice calls initialized!\n🆔 Node ID: {node_id}")
    else:
        snapshot.chat.send_text("❌ Failed to initialize voice calls")


@hooks.on(events.NewMessage(command="/voice_id"))
def voice_id_command(event):
    """Get voice node ID"""
    global voice_manager
    snapshot = event.message_snapshot
    
    if voice_manager:
        node_id = voice_manager.get_node_id()
        if node_id:
            snapshot.chat.send_text(f"🆔 Voice Node ID: {node_id}")
        else:
            snapshot.chat.send_text("❌ Failed to get node ID")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_call"))
def voice_call_command(event):
    """Start voice call"""
    global voice_manager
    snapshot = event.message_snapshot
    
    # Parse peer_id from command
    parts = snapshot.text.split()
    if len(parts) < 2:
        snapshot.chat.send_text("❌ Usage: /voice_call <peer_id>")
        return
    
    peer_id = parts[1]
    
    if voice_manager and voice_manager.initialized:
        call_id = voice_manager.start_call(peer_id)
        if call_id:
            snapshot.chat.send_text(f"📞 Started call {call_id} to {peer_id}")
        else:
            snapshot.chat.send_text("❌ Failed to start call")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_accept"))
def voice_accept_command(event):
    """Accept voice call"""
    global voice_manager
    snapshot = event.message_snapshot
    
    # Parse call_id from command
    parts = snapshot.text.split()
    if len(parts) < 2:
        snapshot.chat.send_text("❌ Usage: /voice_accept <call_id>")
        return
    
    call_id = parts[1]
    
    if voice_manager and voice_manager.initialized:
        if voice_manager.accept_call(call_id):
            snapshot.chat.send_text(f"✅ Accepted call {call_id}")
        else:
            snapshot.chat.send_text("❌ Failed to accept call")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_end"))
def voice_end_command(event):
    """End voice call"""
    global voice_manager
    snapshot = event.message_snapshot
    
    # Parse call_id from command
    parts = snapshot.text.split()
    if len(parts) < 2:
        snapshot.chat.send_text("❌ Usage: /voice_end <call_id>")
        return
    
    call_id = parts[1]
    
    if voice_manager and voice_manager.initialized:
        if voice_manager.end_call(call_id):
            snapshot.chat.send_text(f"📴 Ended call {call_id}")
        else:
            snapshot.chat.send_text("❌ Failed to end call")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_status"))
def voice_status_command(event):
    """Get voice call status"""
    global voice_manager
    snapshot = event.message_snapshot
    
    # Parse call_id from command
    parts = snapshot.text.split()
    if len(parts) < 2:
        snapshot.chat.send_text("❌ Usage: /voice_status <call_id>")
        return
    
    call_id = parts[1]
    
    if voice_manager and voice_manager.initialized:
        status = voice_manager.get_call_status(call_id)
        if status:
            snapshot.chat.send_text(f"📊 Call {call_id} status: {status}")
        else:
            snapshot.chat.send_text(f"❌ Call {call_id} not found")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_list"))
def voice_list_command(event):
    """List active voice calls"""
    global voice_manager
    snapshot = event.message_snapshot
    
    if voice_manager and voice_manager.initialized:
        calls = voice_manager.get_active_calls()
        if calls:
            call_list = "\n".join([f"📞 {call_id}" for call_id in calls])
            snapshot.chat.send_text(f"📋 Active calls:\n{call_list}")
        else:
            snapshot.chat.send_text("📋 No active calls")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


@hooks.on(events.NewMessage(command="/voice_test"))
def voice_test_command(event):
    """Simulate incoming call for testing"""
    global voice_manager
    snapshot = event.message_snapshot
    
    # Parse peer_id from command
    parts = snapshot.text.split()
    if len(parts) < 2:
        snapshot.chat.send_text("❌ Usage: /voice_test <peer_id>")
        return
    
    peer_id = parts[1]
    
    if voice_manager and voice_manager.initialized:
        call_id = voice_manager.simulate_incoming_call(peer_id)
        if call_id:
            snapshot.chat.send_text(f"📲 Simulated incoming call {call_id} from {peer_id}")
        else:
            snapshot.chat.send_text("❌ Failed to simulate incoming call")
    else:
        snapshot.chat.send_text("❌ Voice calls not initialized. Use /voice_init first")


def main():
    global voice_manager
    
    with Rpc() as rpc:
        deltachat = DeltaChat(rpc)
        system_info = deltachat.get_system_info()
        logging.info("Running deltachat core %s", system_info.deltachat_core_version)

        # Initialize voice call manager
        voice_manager = VoiceCallManager(rpc)
        logging.info("🎤 VoiceBot initialized with voice call support")

        accounts = deltachat.get_all_accounts()
        account = accounts[0] if accounts else deltachat.add_account()

        bot = Bot(account, hooks)
        if not bot.is_configured():
            configure_thread = Thread(target=bot.configure, kwargs={"email": sys.argv[1], "password": sys.argv[2]})
            configure_thread.start()
        
        logging.info("🤖 VoiceBot starting...")
        logging.info("📞 Voice call commands available:")
        logging.info("   /voice_init - Initialize voice calls")
        logging.info("   /voice_call <peer_id> - Start call")
        logging.info("   /voice_accept <call_id> - Accept call")
        logging.info("   /voice_end <call_id> - End call")
        logging.info("   /voice_list - List active calls")
        logging.info("   /voice_status <call_id> - Get call status")
        logging.info("   /voice_test <peer_id> - Simulate incoming call")
        
        bot.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    if len(sys.argv) < 3:
        print("Usage: python3 voicebot_advanced.py <email> <password>")
        sys.exit(1)
    main()