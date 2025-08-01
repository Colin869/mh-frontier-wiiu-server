#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Game Integration
Analyzes actual game files to extract real protocol information
"""

import os
import re
import struct
import binascii
from pathlib import Path
from collections import defaultdict

class MHFGameIntegration:
    def __init__(self, game_dir="Monster Hunter Frontier G"):
        self.game_dir = Path(game_dir)
        self.protocol_patterns = {}
        self.server_addresses = []
        self.packet_structures = {}
        self.strings_found = []
        
    def analyze_game_files(self):
        """Analyze all game files for network-related information"""
        print("🐉 Monster Hunter Frontier G - Game Integration Analysis")
        print("=" * 60)
        
        if not self.game_dir.exists():
            print(f"✗ Game directory not found: {self.game_dir}")
            return False
        
        print(f"📁 Analyzing game files in: {self.game_dir}")
        
        # Analyze each file type
        self.analyze_app_files()
        self.analyze_h3_files()
        self.analyze_system_files()
        
        # Generate protocol report
        self.generate_protocol_report()
        
        return True
    
    def analyze_app_files(self):
        """Analyze .app files for network patterns"""
        print("\n--- Analyzing .app Files ---")
        
        app_files = list(self.game_dir.glob("*.app"))
        print(f"Found {len(app_files)} .app files")
        
        for app_file in app_files:
            print(f"  Analyzing: {app_file.name}")
            self.analyze_binary_file(app_file, "app")
    
    def analyze_h3_files(self):
        """Analyze .h3 files for headers and metadata"""
        print("\n--- Analyzing .h3 Files ---")
        
        h3_files = list(self.game_dir.glob("*.h3"))
        print(f"Found {len(h3_files)} .h3 files")
        
        for h3_file in h3_files:
            print(f"  Analyzing: {h3_file.name}")
            self.analyze_binary_file(h3_file, "h3")
    
    def analyze_system_files(self):
        """Analyze system files (TMD, TIK, CERT)"""
        print("\n--- Analyzing System Files ---")
        
        system_files = []
        for ext in ['*.tmd', '*.tik', '*.cert']:
            system_files.extend(self.game_dir.glob(ext))
        
        print(f"Found {len(system_files)} system files")
        
        for sys_file in system_files:
            print(f"  Analyzing: {sys_file.name}")
            self.analyze_binary_file(sys_file, "system")
    
    def analyze_binary_file(self, file_path, file_type):
        """Analyze a binary file for network-related patterns"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Look for network-related patterns
            self.find_ip_addresses(data, file_path.name)
            self.find_urls(data, file_path.name)
            self.find_network_strings(data, file_path.name)
            self.find_packet_patterns(data, file_path.name)
            self.find_encryption_patterns(data, file_path.name)
            
        except Exception as e:
            print(f"    Error analyzing {file_path.name}: {e}")
    
    def find_ip_addresses(self, data, filename):
        """Find IP addresses in binary data"""
        # Common MHF server IP patterns
        ip_patterns = [
            rb'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # Standard IP
            rb'frontier\.capcom\.co\.jp',  # Official MHF domain
            rb'mhf\.capcom\.co\.jp',  # Alternative domain
        ]
        
        for pattern in ip_patterns:
            matches = re.findall(pattern, data)
            for match in matches:
                try:
                    ip_str = match.decode('utf-8', errors='ignore')
                    if ip_str not in self.server_addresses:
                        self.server_addresses.append(ip_str)
                        print(f"    Found server address: {ip_str} in {filename}")
                except:
                    pass
    
    def find_urls(self, data, filename):
        """Find URLs in binary data"""
        url_patterns = [
            rb'https?://[^\s\x00]+',
            rb'ws://[^\s\x00]+',
            rb'wss://[^\s\x00]+',
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, data)
            for match in matches:
                try:
                    url_str = match.decode('utf-8', errors='ignore')
                    if url_str not in self.strings_found:
                        self.strings_found.append(url_str)
                        print(f"    Found URL: {url_str} in {filename}")
                except:
                    pass
    
    def find_network_strings(self, data, filename):
        """Find network-related strings"""
        network_keywords = [
            b'login', b'auth', b'session', b'token', b'packet',
            b'socket', b'connect', b'send', b'receive', b'quest',
            b'guild', b'chat', b'character', b'inventory', b'item',
            b'monster', b'hunt', b'reward', b'rank', b'level',
            b'experience', b'equipment', b'weapon', b'armor',
            b'party', b'room', b'lobby', b'hall', b'channel'
        ]
        
        for keyword in network_keywords:
            if keyword in data:
                # Extract surrounding context
                start = max(0, data.find(keyword) - 20)
                end = min(len(data), data.find(keyword) + len(keyword) + 20)
                context = data[start:end]
                
                try:
                    context_str = context.decode('utf-8', errors='ignore')
                    if context_str not in self.strings_found:
                        self.strings_found.append(context_str)
                        print(f"    Found network string: {context_str} in {filename}")
                except:
                    pass
    
    def find_packet_patterns(self, data, filename):
        """Find potential packet structures"""
        # Look for common packet patterns
        packet_patterns = [
            # 4-byte packet type followed by 4-byte length
            rb'....\x00\x00\x00\x04',  # Common packet header
            rb'....\x00\x00\x00\x08',  # Another common size
            rb'....\x00\x00\x00\x10',  # Larger packet
        ]
        
        for pattern in packet_patterns:
            matches = re.findall(pattern, data)
            if matches:
                print(f"    Found potential packet pattern in {filename}")
                self.packet_structures[filename] = len(matches)
    
    def find_encryption_patterns(self, data, filename):
        """Find encryption-related patterns"""
        encryption_patterns = [
            b'AES', b'RSA', b'MD5', b'SHA', b'CRC', b'XOR',
            b'encrypt', b'decrypt', b'hash', b'checksum'
        ]
        
        for pattern in encryption_patterns:
            if pattern in data:
                print(f"    Found encryption pattern: {pattern} in {filename}")
    
    def generate_protocol_report(self):
        """Generate a comprehensive protocol analysis report"""
        print("\n" + "=" * 60)
        print("📊 MONSTER HUNTER FRONTIER G - PROTOCOL ANALYSIS REPORT")
        print("=" * 60)
        
        # Server addresses found
        print(f"\n🌐 Server Addresses Found ({len(self.server_addresses)}):")
        for addr in self.server_addresses:
            print(f"  - {addr}")
        
        # Network strings found
        print(f"\n📡 Network Strings Found ({len(self.strings_found)}):")
        for string in self.strings_found[:20]:  # Show first 20
            print(f"  - {string}")
        
        if len(self.strings_found) > 20:
            print(f"  ... and {len(self.strings_found) - 20} more")
        
        # Packet structures
        print(f"\n📦 Packet Structures Found ({len(self.packet_structures)}):")
        for filename, count in self.packet_structures.items():
            print(f"  - {filename}: {count} potential packets")
        
        # Generate recommendations
        self.generate_recommendations()
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print(f"\n💡 RECOMMENDATIONS:")
        print("=" * 40)
        
        if self.server_addresses:
            print("✅ Found server addresses - Use these for connection testing")
            print("   - Set up packet capture on these addresses")
            print("   - Monitor traffic patterns during login")
        
        if self.strings_found:
            print("✅ Found network strings - Use these for protocol understanding")
            print("   - Analyze string patterns for packet structure")
            print("   - Look for authentication keywords")
        
        if self.packet_structures:
            print("✅ Found packet patterns - Use these for packet analysis")
            print("   - Reverse engineer packet headers")
            print("   - Understand data formats")
        
        print("\n🔧 NEXT STEPS:")
        print("1. Set up Wireshark to capture traffic to found addresses")
        print("2. Use Ghidra/IDA Pro to analyze .app files in detail")
        print("3. Create packet capture scripts for live analysis")
        print("4. Implement packet replay for testing")
        print("5. Build protocol emulator based on findings")
    
    def create_capture_script(self):
        """Create a packet capture script for live analysis"""
        script_content = '''#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Packet Capture Script
Captures live network traffic for protocol analysis
"""

import pyshark
import time
from datetime import datetime

def capture_mhf_traffic():
    """Capture MHF network traffic"""
    print("🐉 Monster Hunter Frontier G - Packet Capture")
    print("=" * 50)
    
    # Create capture interface
    capture = pyshark.LiveCapture(interface='Wi-Fi')  # Adjust interface name
    
    print("📡 Starting packet capture...")
    print("🎮 Start Monster Hunter Frontier G on your Wii U")
    print("📊 Press Ctrl+C to stop capture")
    
    packet_count = 0
    mhf_packets = []
    
    try:
        for packet in capture.sniff_continuously():
            packet_count += 1
            
            # Look for MHF-related traffic
            if hasattr(packet, 'ip'):
                src_ip = packet.ip.src
                dst_ip = packet.ip.dst
                
                # Check if traffic involves MHF servers
                if any(server in src_ip or server in dst_ip for server in [
                    'frontier.capcom.co.jp',
                    'mhf.capcom.co.jp'
                ]):
                    mhf_packets.append({
                        'timestamp': datetime.now(),
                        'src': src_ip,
                        'dst': dst_ip,
                        'protocol': packet.transport_layer,
                        'length': len(packet),
                        'data': str(packet)
                    })
                    
                    print(f"🎯 MHF Packet #{len(mhf_packets)}: {src_ip} -> {dst_ip}")
            
            # Show progress every 100 packets
            if packet_count % 100 == 0:
                print(f"📊 Captured {packet_count} packets, {len(mhf_packets)} MHF packets")
                
    except KeyboardInterrupt:
        print(f"\\n📊 Capture stopped. Total packets: {packet_count}")
        print(f"🎯 MHF packets found: {len(mhf_packets)}")
        
        # Save results
        if mhf_packets:
            self.save_capture_results(mhf_packets)
    
    capture.close()

def save_capture_results(packets):
    """Save capture results to file"""
    filename = f"mhf_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    import json
    with open(filename, 'w') as f:
        json.dump(packets, f, default=str, indent=2)
    
    print(f"💾 Capture results saved to: {filename}")

if __name__ == "__main__":
    capture_mhf_traffic()
'''
        
        with open('packet_capture.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("📝 Created packet_capture.py for live traffic analysis")

def main():
    """Main game integration function"""
    integrator = MHFGameIntegration()
    integrator.analyze_game_files()
    integrator.create_capture_script()

if __name__ == "__main__":
    main() 