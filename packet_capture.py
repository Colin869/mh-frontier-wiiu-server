#!/usr/bin/env python3
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
        print(f"\n📊 Capture stopped. Total packets: {packet_count}")
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
