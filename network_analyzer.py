#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Network Traffic Analysis Tool
Analyzes captured network packets for protocol understanding
"""

import os
import struct
import binascii
import json
import time
from datetime import datetime
from pathlib import Path

class NetworkAnalyzer:
    def __init__(self):
        self.packets = []
        self.protocol_patterns = {}
        self.server_endpoints = set()
        self.packet_types = {}
        
    def analyze_pcap_file(self, pcap_file):
        """Analyze a PCAP file for Monster Hunter Frontier G traffic"""
        print(f"Analyzing PCAP file: {pcap_file}")
        
        try:
            # This would use pyshark or scapy to read PCAP files
            # For now, we'll create a framework for analysis
            self.load_pcap_data(pcap_file)
            self.identify_protocol_patterns()
            self.analyze_packet_structures()
            self.generate_report()
            
        except Exception as e:
            print(f"Error analyzing PCAP file: {e}")
    
    def load_pcap_data(self, pcap_file):
        """Load packet data from PCAP file"""
        print("Loading packet data...")
        # This would be implemented with pyshark or scapy
        # For now, we'll create sample data structure
        
        # Sample packet structure for demonstration
        sample_packets = [
            {
                'timestamp': time.time(),
                'source_ip': '192.168.1.100',
                'dest_ip': '203.208.60.1',
                'source_port': 12345,
                'dest_port': 80,
                'protocol': 'TCP',
                'data': b'\x01\x02\x03\x04\x05\x06\x07\x08',
                'length': 8
            }
        ]
        
        self.packets = sample_packets
        print(f"Loaded {len(self.packets)} packets")
    
    def identify_protocol_patterns(self):
        """Identify common patterns in the network traffic"""
        print("\nIdentifying protocol patterns...")
        
        # Look for common Monster Hunter patterns
        patterns = {
            'login_packets': rb'\x01\x00\x00\x00',  # Possible login header
            'character_data': rb'\x02\x00\x00\x00',  # Possible character data
            'quest_data': rb'\x03\x00\x00\x00',      # Possible quest data
            'guild_data': rb'\x04\x00\x00\x00',      # Possible guild data
            'chat_packets': rb'\x05\x00\x00\x00',    # Possible chat data
        }
        
        for pattern_name, pattern in patterns.items():
            count = 0
            for packet in self.packets:
                if pattern in packet['data']:
                    count += 1
            
            if count > 0:
                self.protocol_patterns[pattern_name] = count
                print(f"  Found {count} {pattern_name}")
    
    def analyze_packet_structures(self):
        """Analyze the structure of captured packets"""
        print("\nAnalyzing packet structures...")
        
        # Group packets by size
        size_groups = {}
        for packet in self.packets:
            size = packet['length']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(packet)
        
        print("Packet size distribution:")
        for size, packets in sorted(size_groups.items()):
            print(f"  {size} bytes: {len(packets)} packets")
        
        # Analyze common packet structures
        self.analyze_common_headers()
        self.analyze_data_patterns()
    
    def analyze_common_headers(self):
        """Analyze common packet headers"""
        print("\nAnalyzing packet headers...")
        
        # Look for common header patterns
        headers = {}
        for packet in self.packets:
            if len(packet['data']) >= 4:
                header = packet['data'][:4]
                header_hex = binascii.hexlify(header).decode()
                
                if header_hex not in headers:
                    headers[header_hex] = 0
                headers[header_hex] += 1
        
        print("Common packet headers:")
        for header, count in sorted(headers.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {header}: {count} occurrences")
    
    def analyze_data_patterns(self):
        """Analyze patterns in packet data"""
        print("\nAnalyzing data patterns...")
        
        # Look for repeated data patterns
        patterns = {}
        for packet in self.packets:
            data = packet['data']
            
            # Look for 4-byte patterns
            for i in range(len(data) - 3):
                pattern = data[i:i+4]
                pattern_hex = binascii.hexlify(pattern).decode()
                
                if pattern_hex not in patterns:
                    patterns[pattern_hex] = 0
                patterns[pattern_hex] += 1
        
        print("Common 4-byte patterns:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {pattern}: {count} occurrences")
    
    def generate_report(self):
        """Generate a comprehensive network analysis report"""
        report_file = Path("network_analysis_report.txt")
        
        with open(report_file, 'w') as f:
            f.write("Monster Hunter Frontier G - Network Analysis Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Protocol patterns
            f.write("Protocol Patterns Found:\n")
            f.write("-" * 30 + "\n")
            for pattern, count in self.protocol_patterns.items():
                f.write(f"{pattern}: {count} packets\n")
            f.write("\n")
            
            # Server endpoints
            f.write("Server Endpoints:\n")
            f.write("-" * 20 + "\n")
            for endpoint in self.server_endpoints:
                f.write(f"{endpoint}\n")
            f.write("\n")
            
            # Packet statistics
            f.write("Packet Statistics:\n")
            f.write("-" * 20 + "\n")
            total_packets = len(self.packets)
            total_bytes = sum(p['length'] for p in self.packets)
            f.write(f"Total packets: {total_packets}\n")
            f.write(f"Total bytes: {total_bytes:,}\n")
            f.write(f"Average packet size: {total_bytes/total_packets:.1f} bytes\n")
        
        print(f"\nNetwork analysis report saved to: {report_file}")
    
    def create_capture_script(self):
        """Create a script for capturing network traffic"""
        script_content = '''#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Network Capture Script
Captures network traffic during gameplay for analysis
"""

import pyshark
import time
import datetime

def capture_mhf_traffic(interface='Wi-Fi', duration=300):
    """Capture network traffic for Monster Hunter Frontier G"""
    print(f"Starting capture on interface: {interface}")
    print(f"Duration: {duration} seconds")
    
    # Create capture object
    capture = pyshark.LiveCapture(interface=interface)
    
    # Start capture
    start_time = time.time()
    packets = []
    
    try:
        for packet in capture.sniff_continuously():
            # Filter for potential MHF traffic
            if hasattr(packet, 'ip'):
                # Look for traffic to/from known MHF servers
                if any(ip in str(packet.ip) for ip in ['203.208.60', '203.208.61']):
                    packets.append({
                        'timestamp': packet.sniff_timestamp,
                        'source': packet.ip.src,
                        'dest': packet.ip.dst,
                        'protocol': packet.transport_layer,
                        'length': int(packet.length),
                        'data': packet.get_raw_packet()
                    })
                    print(f"Captured packet: {packet.ip.src} -> {packet.ip.dst}")
            
            # Check if duration exceeded
            if time.time() - start_time > duration:
                break
                
    except KeyboardInterrupt:
        print("\\nCapture stopped by user")
    
    # Save captured data
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"mhf_capture_{timestamp}.pcap"
    
    # Save packets to file
    with open(filename, 'wb') as f:
        for packet in packets:
            f.write(packet['data'])
    
    print(f"Capture saved to: {filename}")
    print(f"Total packets captured: {len(packets)}")
    
    return filename

if __name__ == "__main__":
    # Start capture
    capture_file = capture_mhf_traffic(duration=600)  # 10 minutes
    print(f"Capture completed: {capture_file}")
'''
        
        with open("capture_traffic.py", 'w') as f:
            f.write(script_content)
        
        print("Created capture script: capture_traffic.py")

def main():
    analyzer = NetworkAnalyzer()
    
    # Check if we have any PCAP files to analyze
    pcap_files = list(Path('.').glob('*.pcap'))
    
    if pcap_files:
        print(f"Found {len(pcap_files)} PCAP files to analyze:")
        for pcap_file in pcap_files:
            print(f"  {pcap_file}")
            analyzer.analyze_pcap_file(pcap_file)
    else:
        print("No PCAP files found. Creating capture script...")
        analyzer.create_capture_script()
        print("\nTo capture network traffic:")
        print("1. Install pyshark: pip install pyshark")
        print("2. Run: python capture_traffic.py")
        print("3. Play Monster Hunter Frontier G while capturing")
        print("4. Run this script again to analyze the captured data")

if __name__ == "__main__":
    main() 