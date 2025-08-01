#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Binary Analysis Tool
Analyzes Wii U .app files for network protocol information
"""

import os
import struct
import binascii
import re
from pathlib import Path

class WiiUBinaryAnalyzer:
    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.app_files = []
        self.h3_files = []
        self.find_files()
    
    def find_files(self):
        """Find all .app and .h3 files in the game directory"""
        for file in self.game_dir.glob("*.app"):
            self.app_files.append(file)
        for file in self.game_dir.glob("*.h3"):
            self.h3_files.append(file)
        
        print(f"Found {len(self.app_files)} .app files and {len(self.h3_files)} .h3 files")
    
    def analyze_file(self, file_path):
        """Analyze a single binary file for network-related data"""
        print(f"\nAnalyzing: {file_path.name}")
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Basic file info
            file_size = len(data)
            print(f"  Size: {file_size:,} bytes")
            
            # Look for common patterns
            self.find_strings(data, file_path.name)
            self.find_network_patterns(data, file_path.name)
            self.find_ip_addresses(data, file_path.name)
            self.find_urls(data, file_path.name)
            
        except Exception as e:
            print(f"  Error analyzing {file_path.name}: {e}")
    
    def find_strings(self, data, filename):
        """Extract readable strings from binary data"""
        strings = []
        current_string = ""
        
        for byte in data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += chr(byte)
            else:
                if len(current_string) >= 4:  # Minimum string length
                    strings.append(current_string)
                current_string = ""
        
        # Filter for interesting strings
        interesting_strings = []
        for s in strings:
            if any(keyword in s.lower() for keyword in [
                'http', 'https', 'tcp', 'udp', 'socket', 'connect', 'send', 'recv',
                'login', 'auth', 'session', 'server', 'client', 'packet', 'data',
                'monster', 'hunter', 'guild', 'quest', 'item', 'trade'
            ]):
                interesting_strings.append(s)
        
        if interesting_strings:
            print(f"  Found {len(interesting_strings)} interesting strings:")
            for s in interesting_strings[:10]:  # Limit output
                print(f"    {s}")
    
    def find_network_patterns(self, data, filename):
        """Look for common network-related patterns"""
        patterns = {
            'socket_functions': rb'socket|connect|bind|listen|accept|send|recv',
            'http_patterns': rb'HTTP/[0-9]\.[0-9]|GET |POST |PUT |DELETE ',
            'json_patterns': rb'\{.*\}|\[.*\]',
            'xml_patterns': rb'<\?xml|<[a-zA-Z]+>',
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, data)
            if matches:
                print(f"  Found {len(matches)} {pattern_name} patterns")
    
    def find_ip_addresses(self, data, filename):
        """Extract potential IP addresses"""
        # IPv4 pattern
        ip_pattern = rb'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, data)
        
        if ips:
            print(f"  Found {len(ips)} potential IP addresses:")
            for ip in set(ips[:5]):  # Limit and deduplicate
                print(f"    {ip.decode()}")
    
    def find_urls(self, data, filename):
        """Extract potential URLs"""
        url_pattern = rb'https?://[^\s\x00]+'
        urls = re.findall(url_pattern, data)
        
        if urls:
            print(f"  Found {len(urls)} potential URLs:")
            for url in set(urls[:5]):  # Limit and deduplicate
                print(f"    {url.decode()}")
    
    def analyze_all_files(self):
        """Analyze all found files"""
        print("=== Monster Hunter Frontier G Binary Analysis ===")
        
        # Analyze .app files (main executables and data)
        print("\n--- Analyzing .app files ---")
        for app_file in sorted(self.app_files):
            self.analyze_file(app_file)
        
        # Analyze .h3 files (headers/metadata)
        print("\n--- Analyzing .h3 files ---")
        for h3_file in sorted(self.h3_files):
            self.analyze_file(h3_file)
    
    def create_report(self):
        """Create a comprehensive analysis report"""
        report_file = self.game_dir / "binary_analysis_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("Monster Hunter Frontier G - Binary Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            # File summary
            f.write("File Summary:\n")
            f.write("-" * 20 + "\n")
            for app_file in sorted(self.app_files):
                size = app_file.stat().st_size
                f.write(f"{app_file.name}: {size:,} bytes\n")
            f.write("\n")
            
            # Analysis results will be added here
            f.write("Analysis Results:\n")
            f.write("-" * 20 + "\n")
        
        print(f"\nAnalysis report saved to: {report_file}")

def main():
    # Path to the Monster Hunter Frontier G directory
    game_dir = "Monster Hunter Frontier G"
    
    if not os.path.exists(game_dir):
        print(f"Error: Game directory not found at {game_dir}")
        return
    
    analyzer = WiiUBinaryAnalyzer(game_dir)
    analyzer.analyze_all_files()
    analyzer.create_report()

if __name__ == "__main__":
    main() 