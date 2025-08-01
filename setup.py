#!/usr/bin/env python3
"""
Monster Hunter Frontier G - Development Environment Setup
Installs all necessary tools and prepares the analysis environment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def install_python_packages():
    """Install required Python packages"""
    packages = [
        "pyshark",
        "scapy", 
        "requests",
        "pandas",
        "numpy",
        "flask",
        "flask-socketio",
        "python-dateutil",
        "pytest",
        "black",
        "flake8"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "analysis_results",
        "captured_traffic", 
        "server_data",
        "logs",
        "tools"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    return True

def download_tools():
    """Download additional tools if needed"""
    print("\nChecking for additional tools...")
    
    # Check if Wireshark is installed
    try:
        subprocess.run(["wireshark", "--version"], capture_output=True, check=True)
        print("✓ Wireshark is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Wireshark not found. Please install Wireshark for network analysis:")
        print("  Download from: https://www.wireshark.org/download.html")
    
    # Check if Ghidra is available
    ghidra_path = Path("tools/ghidra")
    if not ghidra_path.exists():
        print("⚠ Ghidra not found. For binary analysis, download Ghidra:")
        print("  Download from: https://ghidra-sre.org/")
        print("  Extract to: tools/ghidra")
    
    return True

def create_config_files():
    """Create configuration files"""
    configs = {
        "config.ini": """[Server]
host = 0.0.0.0
port = 80
max_clients = 100

[Database]
type = sqlite
path = server_data/mhf.db

[Logging]
level = INFO
file = logs/server.log

[Analysis]
capture_interface = Wi-Fi
capture_duration = 300
""",
        "analysis_config.json": """{
    "game_files_path": "../Monster Hunter Frontier G",
    "capture_interface": "Wi-Fi",
    "server_endpoints": [
        "203.208.60.1",
        "203.208.61.1"
    ],
    "packet_patterns": {
        "login": "\\x01\\x00\\x00\\x00",
        "character": "\\x02\\x00\\x00\\x00",
        "quest": "\\x03\\x00\\x00\\x00",
        "guild": "\\x04\\x00\\x00\\x00",
        "chat": "\\x05\\x00\\x00\\x00"
    }
}"""
    }
    
    for filename, content in configs.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✓ Created config file: {filename}")
    
    return True

def create_quick_start_guide():
    """Create a quick start guide"""
    guide_content = """# Monster Hunter Frontier G - Quick Start Guide

## Getting Started

### 1. Binary Analysis
```bash
python binary_analyzer.py
```
This will analyze the game files for network protocol information.

### 2. Network Traffic Capture
```bash
python network_analyzer.py
```
This will create a capture script for network traffic analysis.

### 3. Start Server
```bash
python server_framework.py
```
This starts a basic MHF server for testing.

## File Structure
- `Monster Hunter Frontier G/` - Game files
- `analysis_results/` - Analysis output
- `captured_traffic/` - Network captures
- `server_data/` - Server data storage
- `logs/` - Log files

## Next Steps
1. Run binary analysis to understand the protocol
2. Capture network traffic during gameplay
3. Cross-reference binary and network analysis
4. Implement server features based on findings

## Tools Needed
- Wireshark (for network capture)
- Ghidra (for binary analysis)
- Python 3.8+ (already installed)

## Community Resources
- MHF Discord servers
- GBAtemp forums
- GitHub repositories for existing projects
"""
    
    with open("QUICK_START.md", 'w') as f:
        f.write(guide_content)
    
    print("✓ Created quick start guide: QUICK_START.md")
    return True

def main():
    """Main setup function"""
    print("Monster Hunter Frontier G - Development Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install Python packages
    if not install_python_packages():
        print("\n✗ Failed to install Python packages")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n✗ Failed to create directories")
        sys.exit(1)
    
    # Download tools
    if not download_tools():
        print("\n⚠ Some tools may need manual installation")
    
    # Create config files
    if not create_config_files():
        print("\n✗ Failed to create config files")
        sys.exit(1)
    
    # Create quick start guide
    if not create_quick_start_guide():
        print("\n✗ Failed to create quick start guide")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Read QUICK_START.md for usage instructions")
    print("2. Run: python binary_analyzer.py")
    print("3. Install Wireshark for network analysis")
    print("4. Start analyzing the Monster Hunter Frontier G files!")
    print("\nHappy hunting!")

if __name__ == "__main__":
    main() 