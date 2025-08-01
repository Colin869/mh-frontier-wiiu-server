#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Live Packet Capture System
Captures and analyzes real MHF network traffic using Scapy
"""

import time
import json
import struct
from datetime import datetime
from scapy.all import *
from collections import defaultdict
import threading
import queue
import os

class MHFLiveCapture:
    def __init__(self):
        """Initialize the MHF live capture system"""
        self.captured_packets = []
        self.packet_queue = queue.Queue()
        self.is_capturing = False
        self.interface = None
        self.filter = None
        
        # MHF-specific patterns
        self.mhf_servers = [
            'frontier.capcom.co.jp',
            'mhf.capcom.co.jp',
            '203.208.60.1',  # Known MHF server IP
            '203.208.60.2',
            '203.208.60.3'
        ]
        
        # Packet analysis results
        self.packet_types = defaultdict(int)
        self.connection_pairs = defaultdict(int)
        self.protocol_stats = defaultdict(int)
        
    def start_capture(self, interface=None, filter_string=None):
        """Start live packet capture"""
        print("🐉 Monster Hunter Frontier G - Live Packet Capture")
        print("=" * 60)
        
        # Set interface
        if interface:
            self.interface = interface
        else:
            # Auto-detect interface
            self.interface = self.detect_interface()
        
        # Set filter
        if filter_string:
            self.filter = filter_string
        else:
            # Default MHF filter
            self.filter = "host 203.208.60.1 or host 203.208.60.2 or host 203.208.60.3"
        
        print(f"📡 Interface: {self.interface}")
        print(f"🔍 Filter: {self.filter}")
        print("🎮 Start Monster Hunter Frontier G on your Wii U")
        print("📊 Press Ctrl+C to stop capture")
        
        self.is_capturing = True
        
        try:
            # Start capture in background thread
            capture_thread = threading.Thread(target=self._capture_packets)
            capture_thread.daemon = True
            capture_thread.start()
            
            # Start analysis thread
            analysis_thread = threading.Thread(target=self._analyze_packets)
            analysis_thread.daemon = True
            analysis_thread.start()
            
            # Main loop
            while self.is_capturing:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop_capture()
    
    def detect_interface(self):
        """Auto-detect the best network interface"""
        interfaces = get_if_list()
        
        # Prefer wireless interfaces for Wii U
        preferred = ['Wi-Fi', 'wlan0', 'wlan1', 'wireless']
        
        for pref in preferred:
            for iface in interfaces:
                if pref.lower() in iface.lower():
                    return iface
        
        # Fallback to first interface
        return interfaces[0] if interfaces else 'eth0'
    
    def _capture_packets(self):
        """Background packet capture thread"""
        try:
            sniff(
                iface=self.interface,
                filter=self.filter,
                prn=self._packet_callback,
                store=0,
                stop_filter=lambda x: not self.is_capturing
            )
        except Exception as e:
            print(f"Capture error: {e}")
    
    def _packet_callback(self, packet):
        """Callback for each captured packet"""
        try:
            # Basic packet info
            packet_info = {
                'timestamp': datetime.now().isoformat(),
                'length': len(packet),
                'protocol': packet.proto if hasattr(packet, 'proto') else 'Unknown'
            }
            
            # Extract IP information
            if IP in packet:
                packet_info['src_ip'] = packet[IP].src
                packet_info['dst_ip'] = packet[IP].dst
                packet_info['ttl'] = packet[IP].ttl
                
                # Check if it's MHF traffic
                if self._is_mhf_traffic(packet[IP].src, packet[IP].dst):
                    packet_info['is_mhf'] = True
                    print(f"🎯 MHF Packet: {packet[IP].src} -> {packet[IP].dst} ({len(packet)} bytes)")
                else:
                    packet_info['is_mhf'] = False
            
            # Extract TCP information
            if TCP in packet:
                packet_info['src_port'] = packet[TCP].sport
                packet_info['dst_port'] = packet[TCP].dport
                packet_info['flags'] = packet[TCP].flags
                
                # Extract payload
                if packet[TCP].payload:
                    payload = bytes(packet[TCP].payload)
                    packet_info['payload'] = payload.hex()
                    packet_info['payload_length'] = len(payload)
                    
                    # Analyze payload for MHF patterns
                    mhf_analysis = self._analyze_mhf_payload(payload)
                    if mhf_analysis:
                        packet_info['mhf_analysis'] = mhf_analysis
            
            # Extract UDP information
            elif UDP in packet:
                packet_info['src_port'] = packet[UDP].sport
                packet_info['dst_port'] = packet[UDP].dport
                
                if packet[UDP].payload:
                    payload = bytes(packet[UDP].payload)
                    packet_info['payload'] = payload.hex()
                    packet_info['payload_length'] = len(payload)
            
            # Add to queue for analysis
            self.packet_queue.put(packet_info)
            
        except Exception as e:
            print(f"Packet callback error: {e}")
    
    def _is_mhf_traffic(self, src_ip, dst_ip):
        """Check if traffic is MHF-related"""
        # Check against known MHF servers
        for server in self.mhf_servers:
            if server in src_ip or server in dst_ip:
                return True
        
        # Check for common MHF ports
        mhf_ports = [80, 443, 8080, 9000, 10000]
        # This would need to be enhanced with actual port analysis
        
        return False
    
    def _analyze_mhf_payload(self, payload):
        """Analyze payload for MHF-specific patterns"""
        analysis = {}
        
        try:
            # Look for packet headers (4-byte type + 4-byte length)
            if len(payload) >= 8:
                # Try to parse as MHF packet header
                try:
                    packet_type, data_length = struct.unpack('<II', payload[:8])
                    analysis['packet_type'] = f"0x{packet_type:08X}"
                    analysis['data_length'] = data_length
                    analysis['header_valid'] = True
                except:
                    analysis['header_valid'] = False
            
            # Look for JSON patterns
            try:
                json_start = payload.find(b'{')
                json_end = payload.rfind(b'}')
                if json_start != -1 and json_end != -1:
                    json_data = payload[json_start:json_end+1]
                    parsed_json = json.loads(json_data.decode('utf-8', errors='ignore'))
                    analysis['json_data'] = parsed_json
            except:
                pass
            
            # Look for encryption patterns
            if b'AES' in payload or b'RSA' in payload or b'MD5' in payload:
                analysis['encryption_detected'] = True
            
            # Look for game-specific strings
            game_strings = [b'login', b'auth', b'quest', b'guild', b'character', b'monster']
            for game_string in game_strings:
                if game_string in payload:
                    analysis['game_strings'] = analysis.get('game_strings', []) + [game_string.decode()]
            
            return analysis if analysis else None
            
        except Exception as e:
            return None
    
    def _analyze_packets(self):
        """Background packet analysis thread"""
        while self.is_capturing:
            try:
                # Get packet from queue
                packet_info = self.packet_queue.get(timeout=1)
                
                # Store packet
                self.captured_packets.append(packet_info)
                
                # Update statistics
                self._update_statistics(packet_info)
                
                # Analyze MHF packets in detail
                if packet_info.get('is_mhf', False):
                    self._detailed_mhf_analysis(packet_info)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Analysis error: {e}")
    
    def _update_statistics(self, packet_info):
        """Update packet statistics"""
        # Protocol statistics
        self.protocol_stats[packet_info['protocol']] += 1
        
        # Connection pairs
        if 'src_ip' in packet_info and 'dst_ip' in packet_info:
            pair = f"{packet_info['src_ip']} -> {packet_info['dst_ip']}"
            self.connection_pairs[pair] += 1
        
        # Packet types (if MHF analysis available)
        if 'mhf_analysis' in packet_info:
            packet_type = packet_info['mhf_analysis'].get('packet_type', 'Unknown')
            self.packet_types[packet_type] += 1
    
    def _detailed_mhf_analysis(self, packet_info):
        """Perform detailed analysis of MHF packets"""
        if 'mhf_analysis' not in packet_info:
            return
        
        analysis = packet_info['mhf_analysis']
        
        print(f"\n🔍 MHF Packet Analysis:")
        print(f"  Type: {analysis.get('packet_type', 'Unknown')}")
        print(f"  Length: {analysis.get('data_length', 'Unknown')}")
        
        if 'json_data' in analysis:
            print(f"  JSON Data: {analysis['json_data']}")
        
        if 'game_strings' in analysis:
            print(f"  Game Strings: {analysis['game_strings']}")
        
        if analysis.get('encryption_detected'):
            print(f"  Encryption: Detected")
    
    def stop_capture(self):
        """Stop packet capture"""
        print("\n🛑 Stopping packet capture...")
        self.is_capturing = False
        
        # Wait a moment for threads to finish
        time.sleep(2)
        
        # Generate report
        self.generate_capture_report()
    
    def generate_capture_report(self):
        """Generate comprehensive capture report"""
        print("\n" + "=" * 60)
        print("📊 MONSTER HUNTER FRONTIER G - CAPTURE REPORT")
        print("=" * 60)
        
        total_packets = len(self.captured_packets)
        mhf_packets = len([p for p in self.captured_packets if p.get('is_mhf', False)])
        
        print(f"\n📦 Total Packets Captured: {total_packets}")
        print(f"🎯 MHF Packets: {mhf_packets}")
        print(f"📈 MHF Percentage: {(mhf_packets/total_packets*100):.1f}%" if total_packets > 0 else "0%")
        
        # Protocol statistics
        print(f"\n🌐 Protocol Statistics:")
        for protocol, count in self.protocol_stats.items():
            print(f"  {protocol}: {count}")
        
        # Connection pairs
        print(f"\n🔗 Top Connection Pairs:")
        sorted_pairs = sorted(self.connection_pairs.items(), key=lambda x: x[1], reverse=True)
        for pair, count in sorted_pairs[:5]:
            print(f"  {pair}: {count} packets")
        
        # MHF packet types
        if self.packet_types:
            print(f"\n📋 MHF Packet Types:")
            for packet_type, count in self.packet_types.items():
                print(f"  {packet_type}: {count}")
        
        # Save results
        self.save_capture_results()
    
    def save_capture_results(self):
        """Save capture results to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mhf_capture_{timestamp}.json"
        
        # Prepare data for saving
        save_data = {
            'capture_info': {
                'timestamp': datetime.now().isoformat(),
                'interface': self.interface,
                'filter': self.filter,
                'total_packets': len(self.captured_packets),
                'mhf_packets': len([p for p in self.captured_packets if p.get('is_mhf', False)])
            },
            'statistics': {
                'protocol_stats': dict(self.protocol_stats),
                'connection_pairs': dict(self.connection_pairs),
                'packet_types': dict(self.packet_types)
            },
            'packets': self.captured_packets
        }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"\n💾 Capture results saved to: {filename}")
        print(f"📁 File size: {os.path.getsize(filename)} bytes")

def main():
    """Main capture function"""
    print("🐉 Monster Hunter Frontier G - Live Packet Capture")
    print("=" * 60)
    
    # Create capture system
    capture = MHFLiveCapture()
    
    # Start capture
    try:
        capture.start_capture()
    except KeyboardInterrupt:
        print("\n⚠ Capture interrupted by user")
    finally:
        capture.stop_capture()

if __name__ == "__main__":
    main() 