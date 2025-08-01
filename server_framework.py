#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Server Framework
Basic server implementation for MHF Frontier G
"""

import socket
import threading
import json
import time
import logging
from datetime import datetime
from pathlib import Path

class MHFServer:
    def __init__(self, host='0.0.0.0', port=80):
        self.host = host
        self.port = port
        self.clients = {}
        self.guilds = {}
        self.quests = {}
        self.running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mhf_server.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize data storage
        self.init_data_storage()
    
    def init_data_storage(self):
        """Initialize data storage for the server"""
        self.data_dir = Path("server_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "characters").mkdir(exist_ok=True)
        (self.data_dir / "guilds").mkdir(exist_ok=True)
        (self.data_dir / "quests").mkdir(exist_ok=True)
        (self.data_dir / "items").mkdir(exist_ok=True)
        
        self.logger.info("Data storage initialized")
    
    def start(self):
        """Start the MHF server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            self.logger.info(f"MHF Server started on {self.host}:{self.port}")
            print(f"Monster Hunter Frontier G Server")
            print(f"Listening on {self.host}:{self.port}")
            print(f"Server data directory: {self.data_dir}")
            print("Press Ctrl+C to stop the server")
            
            # Start client handler thread
            client_thread = threading.Thread(target=self.accept_clients)
            client_thread.daemon = True
            client_thread.start()
            
            # Main server loop
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    self.stop()
                    break
                    
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self.stop()
    
    def stop(self):
        """Stop the MHF server"""
        self.running = False
        self.logger.info("Stopping MHF server...")
        
        # Disconnect all clients
        for client_id, client_info in self.clients.items():
            try:
                client_info['socket'].close()
            except:
                pass
        
        # Close server socket
        try:
            self.server_socket.close()
        except:
            pass
        
        self.logger.info("Server stopped")
    
    def accept_clients(self):
        """Accept incoming client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.logger.info(f"New connection from {address}")
                
                # Start client handler
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting client: {e}")
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        client_id = f"{address[0]}:{address[1]}"
        self.clients[client_id] = {
            'socket': client_socket,
            'address': address,
            'connected': datetime.now(),
            'character': None,
            'guild': None
        }
        
        try:
            while self.running:
                # Receive data from client
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # Process the received data
                response = self.process_packet(data, client_id)
                
                # Send response if any
                if response:
                    client_socket.send(response)
                    
        except Exception as e:
            self.logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client connection
            self.disconnect_client(client_id)
    
    def process_packet(self, data, client_id):
        """Process incoming packet data"""
        try:
            # Basic packet structure analysis
            if len(data) < 4:
                return None
            
            # Extract packet header (first 4 bytes)
            header = data[:4]
            packet_type = int.from_bytes(header, byteorder='little')
            
            self.logger.info(f"Received packet type {packet_type} from {client_id}")
            
            # Handle different packet types
            if packet_type == 0x01:  # Login packet
                return self.handle_login(data[4:], client_id)
            elif packet_type == 0x02:  # Character data
                return self.handle_character_data(data[4:], client_id)
            elif packet_type == 0x03:  # Quest data
                return self.handle_quest_data(data[4:], client_id)
            elif packet_type == 0x04:  # Guild data
                return self.handle_guild_data(data[4:], client_id)
            elif packet_type == 0x05:  # Chat packet
                return self.handle_chat_packet(data[4:], client_id)
            else:
                self.logger.warning(f"Unknown packet type: {packet_type}")
                return self.create_error_response("Unknown packet type")
                
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
            return self.create_error_response("Packet processing error")
    
    def handle_login(self, data, client_id):
        """Handle login authentication"""
        self.logger.info(f"Processing login for {client_id}")
        
        # For now, accept all logins
        # In a real implementation, you'd validate credentials
        response = {
            'type': 'login_response',
            'status': 'success',
            'session_id': f"session_{client_id}_{int(time.time())}",
            'server_time': int(time.time())
        }
        
        return self.create_response(0x01, response)
    
    def handle_character_data(self, data, client_id):
        """Handle character data requests"""
        self.logger.info(f"Processing character data for {client_id}")
        
        # Load or create character data
        character_file = self.data_dir / "characters" / f"{client_id}.json"
        
        if character_file.exists():
            with open(character_file, 'r') as f:
                character_data = json.load(f)
        else:
            # Create new character
            character_data = {
                'name': f"Hunter_{client_id}",
                'level': 1,
                'exp': 0,
                'hr': 1,
                'guild_rank': 0,
                'items': [],
                'equipment': {},
                'quests_completed': [],
                'created': datetime.now().isoformat()
            }
            
            # Save character data
            with open(character_file, 'w') as f:
                json.dump(character_data, f, indent=2)
        
        return self.create_response(0x02, character_data)
    
    def handle_quest_data(self, data, client_id):
        """Handle quest-related data"""
        self.logger.info(f"Processing quest data for {client_id}")
        
        # Sample quest data
        quest_data = {
            'available_quests': [
                {'id': 1, 'name': 'Great Jaggi Hunt', 'rank': 1, 'monster': 'Great Jaggi'},
                {'id': 2, 'name': 'Qurupeco Hunt', 'rank': 2, 'monster': 'Qurupeco'},
                {'id': 3, 'name': 'Rathian Hunt', 'rank': 3, 'monster': 'Rathian'}
            ],
            'active_quest': None,
            'quest_history': []
        }
        
        return self.create_response(0x03, quest_data)
    
    def handle_guild_data(self, data, client_id):
        """Handle guild-related data"""
        self.logger.info(f"Processing guild data for {client_id}")
        
        # Sample guild data
        guild_data = {
            'guilds': [
                {'id': 1, 'name': 'Dragon Slayers', 'members': 5, 'rank': 1},
                {'id': 2, 'name': 'Monster Hunters', 'members': 3, 'rank': 2},
                {'id': 3, 'name': 'Frontier Elite', 'members': 8, 'rank': 1}
            ],
            'player_guild': None,
            'guild_halls': [
                {'id': 1, 'name': 'Main Hall', 'capacity': 50},
                {'id': 2, 'name': 'Training Hall', 'capacity': 20},
                {'id': 3, 'name': 'Elite Hall', 'capacity': 10}
            ]
        }
        
        return self.create_response(0x04, guild_data)
    
    def handle_chat_packet(self, data, client_id):
        """Handle chat messages"""
        try:
            message = data.decode('utf-8', errors='ignore')
            self.logger.info(f"Chat from {client_id}: {message}")
            
            # Broadcast to other clients
            self.broadcast_chat(client_id, message)
            
            return self.create_response(0x05, {'status': 'sent'})
        except Exception as e:
            self.logger.error(f"Error handling chat: {e}")
            return self.create_error_response("Chat error")
    
    def broadcast_chat(self, sender_id, message):
        """Broadcast chat message to other clients"""
        chat_data = {
            'sender': sender_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        response = self.create_response(0x05, chat_data)
        
        for client_id, client_info in self.clients.items():
            if client_id != sender_id:
                try:
                    client_info['socket'].send(response)
                except:
                    pass
    
    def create_response(self, packet_type, data):
        """Create a response packet"""
        try:
            # Convert data to JSON
            json_data = json.dumps(data, ensure_ascii=False)
            data_bytes = json_data.encode('utf-8')
            
            # Create packet header
            header = packet_type.to_bytes(4, byteorder='little')
            length = len(data_bytes).to_bytes(4, byteorder='little')
            
            # Combine header and data
            packet = header + length + data_bytes
            
            return packet
        except Exception as e:
            self.logger.error(f"Error creating response: {e}")
            return self.create_error_response("Response creation error")
    
    def create_error_response(self, error_message):
        """Create an error response packet"""
        error_data = {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.create_response(0xFF, error_data)
    
    def disconnect_client(self, client_id):
        """Disconnect a client"""
        if client_id in self.clients:
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            
            del self.clients[client_id]
            self.logger.info(f"Client {client_id} disconnected")
    
    def get_server_status(self):
        """Get current server status"""
        return {
            'running': self.running,
            'clients_connected': len(self.clients),
            'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0,
            'guilds_count': len(self.guilds),
            'quests_active': len(self.quests)
        }

def main():
    """Main server function"""
    print("Monster Hunter Frontier G Server")
    print("=" * 40)
    
    # Create and start server
    server = MHFServer(host='0.0.0.0', port=80)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main() 