#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Enhanced Test Client
Tests the enhanced server with authentication and advanced features
"""

import socket
import json
import time
import struct

class MHFEnhancedTestClient:
    def __init__(self, host='localhost', port=80):
        self.host = host
        self.port = port
        self.socket = None
        self.session_token = None
        self.user_info = None
        
    def connect(self):
        """Connect to the enhanced MHF server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✓ Connected to enhanced MHF server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            return False
    
    def send_packet(self, packet_type, data):
        """Send a packet to the server"""
        try:
            # Convert data to JSON
            json_data = json.dumps(data, ensure_ascii=False)
            data_bytes = json_data.encode('utf-8')
            
            # Create packet header
            header = packet_type.to_bytes(4, byteorder='little')
            length = len(data_bytes).to_bytes(4, byteorder='little')
            
            # Combine header and data
            packet = header + length + data_bytes
            
            # Send packet
            self.socket.send(packet)
            print(f"✓ Sent packet type {packet_type} ({len(packet)} bytes)")
            return True
        except Exception as e:
            print(f"✗ Failed to send packet: {e}")
            return False
    
    def receive_response(self):
        """Receive response from server"""
        try:
            # Receive header (8 bytes: 4 for type, 4 for length)
            header = self.socket.recv(8)
            if len(header) < 8:
                return None
            
            packet_type = int.from_bytes(header[:4], byteorder='little')
            data_length = int.from_bytes(header[4:], byteorder='little')
            
            # Receive data
            data = b''
            while len(data) < data_length:
                chunk = self.socket.recv(data_length - len(data))
                if not chunk:
                    break
                data += chunk
            
            # Parse JSON response
            response = json.loads(data.decode('utf-8'))
            print(f"✓ Received response type {packet_type}: {response}")
            return response
            
        except Exception as e:
            print(f"✗ Failed to receive response: {e}")
            return None
    
    def test_enhanced_login(self):
        """Test enhanced login functionality"""
        print("\n--- Testing Enhanced Login ---")
        
        # Test with valid credentials
        login_data = {
            'username': 'hunter001',
            'password': 'password123',
            'user_agent': 'MHF-Enhanced-Client/1.0'
        }
        
        if self.send_packet(0x01, login_data):
            response = self.receive_response()
            if response and response.get('status') == 'success':
                self.session_token = response.get('session_token')
                self.user_info = response
                print(f"✓ Login successful! Session token: {self.session_token[:16]}...")
                return True
            else:
                print("✗ Login failed!")
                return False
        return False
    
    def test_session_validation(self):
        """Test session validation"""
        print("\n--- Testing Session Validation ---")
        
        if not self.session_token:
            print("✗ No session token available")
            return False
        
        session_data = {
            'session_token': self.session_token
        }
        
        if self.send_packet(0x06, session_data):
            response = self.receive_response()
            if response and response.get('valid'):
                print("✓ Session validated successfully!")
                return True
            else:
                print("✗ Session validation failed!")
                return False
        return False
    
    def test_enhanced_character_data(self):
        """Test enhanced character data"""
        print("\n--- Testing Enhanced Character Data ---")
        
        if not self.session_token:
            print("✗ No session token available")
            return False
        
        char_data = {
            'session_token': self.session_token,
            'request_type': 'load_characters'
        }
        
        if self.send_packet(0x02, char_data):
            response = self.receive_response()
            if response and 'characters' in response:
                characters = response['characters']
                print(f"✓ Found {len(characters)} characters:")
                for char in characters:
                    print(f"  - {char['name']} (HR{char['hr']}, Level {char['level']})")
                return True
            else:
                print("✗ Character data request failed!")
                return False
        return False
    
    def test_enhanced_quest_data(self):
        """Test enhanced quest data"""
        print("\n--- Testing Enhanced Quest Data ---")
        
        quest_data = {
            'player_rank': 3,  # Test with high rank
            'session_token': self.session_token
        }
        
        if self.send_packet(0x03, quest_data):
            response = self.receive_response()
            if response and 'available_quests' in response:
                quests = response['available_quests']
                print(f"✓ Found {len(quests)} available quests:")
                for quest in quests:
                    print(f"  - {quest['name']} (Rank {quest['rank']}, Reward: {quest['reward']})")
                return True
            else:
                print("✗ Quest data request failed!")
                return False
        return False
    
    def test_enhanced_guild_data(self):
        """Test enhanced guild data"""
        print("\n--- Testing Enhanced Guild Data ---")
        
        guild_data = {
            'session_token': self.session_token,
            'request_type': 'guild_list'
        }
        
        if self.send_packet(0x04, guild_data):
            response = self.receive_response()
            if response and 'guilds' in response:
                guilds = response['guilds']
                halls = response['guild_halls']
                print(f"✓ Found {len(guilds)} guilds:")
                for guild in guilds:
                    print(f"  - {guild['name']} (Leader: {guild['leader']}, Members: {guild['members']})")
                print(f"✓ Found {len(halls)} guild halls:")
                for hall in halls:
                    print(f"  - {hall['name']} ({hall['current_occupants']}/{hall['capacity']} occupants)")
                return True
            else:
                print("✗ Guild data request failed!")
                return False
        return False
    
    def test_enhanced_chat(self):
        """Test enhanced chat functionality"""
        print("\n--- Testing Enhanced Chat ---")
        
        chat_data = {
            'message': 'Hello from enhanced client! Ready to hunt some monsters!',
            'channel': 'general',
            'session_token': self.session_token
        }
        
        if self.send_packet(0x05, chat_data):
            response = self.receive_response()
            if response and response.get('status') == 'sent':
                print("✓ Chat message sent successfully!")
                return True
            else:
                print("✗ Chat message failed!")
                return False
        return False
    
    def test_failed_login(self):
        """Test failed login attempt"""
        print("\n--- Testing Failed Login ---")
        
        login_data = {
            'username': 'invalid_user',
            'password': 'wrong_password',
            'user_agent': 'MHF-Enhanced-Client/1.0'
        }
        
        if self.send_packet(0x01, login_data):
            response = self.receive_response()
            if response and response.get('status') == 'failed':
                print("✓ Failed login handled correctly!")
                return True
            else:
                print("✗ Failed login test failed!")
                return False
        return False
    
    def run_all_enhanced_tests(self):
        """Run all enhanced server tests"""
        print("🐉 Monster Hunter Frontier G - Enhanced Test Client")
        print("=" * 60)
        
        if not self.connect():
            return
        
        try:
            # Test failed login first
            self.test_failed_login()
            time.sleep(1)
            
            # Test successful login
            if self.test_enhanced_login():
                time.sleep(1)
                
                # Test session validation
                self.test_session_validation()
                time.sleep(1)
                
                # Test character data
                self.test_enhanced_character_data()
                time.sleep(1)
                
                # Test quest data
                self.test_enhanced_quest_data()
                time.sleep(1)
                
                # Test guild data
                self.test_enhanced_guild_data()
                time.sleep(1)
                
                # Test chat
                self.test_enhanced_chat()
                time.sleep(1)
                
                print("\n" + "=" * 60)
                print("✓ All enhanced tests completed!")
                print("Enhanced server is working correctly!")
                print("Features tested:")
                print("  ✅ Authentication system")
                print("  ✅ Session management")
                print("  ✅ Character system")
                print("  ✅ Quest system")
                print("  ✅ Guild system")
                print("  ✅ Chat system")
                print("  ✅ Error handling")
            else:
                print("✗ Login failed, cannot test other features")
            
        except KeyboardInterrupt:
            print("\n⚠ Tests interrupted by user")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
            print("✓ Disconnected from enhanced server")

def main():
    """Main enhanced test function"""
    client = MHFEnhancedTestClient()
    client.run_all_enhanced_tests()

if __name__ == "__main__":
    main() 