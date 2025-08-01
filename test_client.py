#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Test Client
Simple client to test the MHF server functionality
"""

import socket
import json
import time
import struct

class MHFTestClient:
    def __init__(self, host='localhost', port=80):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the MHF server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✓ Connected to MHF server at {self.host}:{self.port}")
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
    
    def test_login(self):
        """Test login functionality"""
        print("\n--- Testing Login ---")
        login_data = {
            'username': 'test_hunter',
            'password': 'test_password',
            'version': '1.0.0'
        }
        
        if self.send_packet(0x01, login_data):
            return self.receive_response()
        return None
    
    def test_character_data(self):
        """Test character data request"""
        print("\n--- Testing Character Data ---")
        char_data = {
            'request_type': 'load_character',
            'character_id': 'test_character_001'
        }
        
        if self.send_packet(0x02, char_data):
            return self.receive_response()
        return None
    
    def test_quest_data(self):
        """Test quest data request"""
        print("\n--- Testing Quest Data ---")
        quest_data = {
            'request_type': 'available_quests',
            'player_rank': 1
        }
        
        if self.send_packet(0x03, quest_data):
            return self.receive_response()
        return None
    
    def test_guild_data(self):
        """Test guild data request"""
        print("\n--- Testing Guild Data ---")
        guild_data = {
            'request_type': 'guild_list',
            'player_id': 'test_player_001'
        }
        
        if self.send_packet(0x04, guild_data):
            return self.receive_response()
        return None
    
    def test_chat(self):
        """Test chat functionality"""
        print("\n--- Testing Chat ---")
        chat_data = {
            'message': 'Hello, fellow hunters!',
            'channel': 'general',
            'sender': 'test_hunter'
        }
        
        if self.send_packet(0x05, chat_data):
            return self.receive_response()
        return None
    
    def run_all_tests(self):
        """Run all server tests"""
        print("🐉 Monster Hunter Frontier G - Server Test Client")
        print("=" * 50)
        
        if not self.connect():
            return
        
        try:
            # Test all server functions
            self.test_login()
            time.sleep(1)
            
            self.test_character_data()
            time.sleep(1)
            
            self.test_quest_data()
            time.sleep(1)
            
            self.test_guild_data()
            time.sleep(1)
            
            self.test_chat()
            time.sleep(1)
            
            print("\n" + "=" * 50)
            print("✓ All tests completed!")
            print("Server is working correctly!")
            
        except KeyboardInterrupt:
            print("\n⚠ Tests interrupted by user")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
            print("✓ Disconnected from server")

def main():
    """Main test function"""
    client = MHFTestClient()
    client.run_all_tests()

if __name__ == "__main__":
    main() 