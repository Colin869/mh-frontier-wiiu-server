#!/usr/bin/env python3
"""
GitHub Repository Setup Script
Helps initialize the Monster Hunter Frontier G server project on GitHub
"""

import os
import subprocess
import sys
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

def check_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✓ Git is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Git is not installed. Please install Git first:")
        print("  Download from: https://git-scm.com/downloads")
        return False

def initialize_git_repo():
    """Initialize Git repository"""
    if not run_command("git init", "Initializing Git repository"):
        return False
    
    if not run_command("git add .", "Adding files to Git"):
        return False
    
    if not run_command('git commit -m "Initial commit: Monster Hunter Frontier G Server Project"', "Creating initial commit"):
        return False
    
    return True

def create_github_repo_instructions():
    """Provide instructions for creating GitHub repository"""
    print("\n" + "=" * 60)
    print("📋 GitHub Repository Setup Instructions")
    print("=" * 60)
    
    print("\n1. Go to GitHub.com and sign in to your account")
    print("2. Click the '+' icon in the top right and select 'New repository'")
    print("3. Repository settings:")
    print("   - Repository name: mhf-frontier-server")
    print("   - Description: Monster Hunter Frontier G Server - Reverse engineering project")
    print("   - Make it Public (recommended for community projects)")
    print("   - Don't initialize with README (we already have one)")
    print("   - Don't add .gitignore (we already have one)")
    print("   - Don't add license (we already have one)")
    print("4. Click 'Create repository'")
    
    print("\n5. After creating the repository, GitHub will show you commands.")
    print("   Use these commands to connect your local repo:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/mhf-frontier-server.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\n6. Replace 'YOUR_USERNAME' with your actual GitHub username")
    
    return True

def create_github_workflow():
    """Create GitHub Actions workflow for CI/CD"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = """name: Python CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Run linting
      run: |
        pip install flake8 black
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check .
    
    - name: Check code formatting
      run: |
        black --check .
"""
    
    workflow_file = workflow_dir / "ci.yml"
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    print(f"✓ Created GitHub Actions workflow: {workflow_file}")
    return True

def create_issue_templates():
    """Create GitHub issue templates"""
    issue_dir = Path(".github/ISSUE_TEMPLATE")
    issue_dir.mkdir(parents=True, exist_ok=True)
    
    # Bug report template
    bug_template = """---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: ['bug']
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error '...'

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, macOS, Ubuntu]
 - Python Version: [e.g. 3.8.0]
 - Game Version: [e.g. Monster Hunter Frontier G JP]

**Additional context**
Add any other context about the problem here.
"""
    
    # Feature request template
    feature_template = """---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: ['enhancement']
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
"""
    
    # Analysis findings template
    analysis_template = """---
name: Analysis findings
about: Share your reverse engineering findings
title: '[ANALYSIS] '
labels: ['analysis', 'documentation']
assignees: ''
---

**What did you analyze?**
- [ ] Binary files (.app files)
- [ ] Network traffic (PCAP files)
- [ ] Game behavior
- [ ] Other: _____

**Key findings**
Describe your main discoveries:

**Technical details**
- File(s) analyzed: _____
- Tools used: _____
- Patterns found: _____

**Evidence**
Include any relevant code snippets, packet captures, or screenshots.

**Next steps**
What should be done with this information?
"""
    
    templates = {
        "bug_report.md": bug_template,
        "feature_request.md": feature_template,
        "analysis_findings.md": analysis_template
    }
    
    for filename, content in templates.items():
        template_file = issue_dir / filename
        with open(template_file, 'w') as f:
            f.write(content)
        print(f"✓ Created issue template: {template_file}")
    
    return True

def create_project_structure():
    """Create additional project directories"""
    directories = [
        "analysis",
        "server", 
        "docs",
        "tests",
        "tools",
        "examples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create placeholder files
    placeholders = {
        "analysis/__init__.py": "",
        "server/__init__.py": "",
        "tests/__init__.py": "",
        "docs/protocol.md": "# Monster Hunter Frontier G Protocol Documentation\n\nThis document will contain the reverse engineered protocol specifications.",
        "examples/basic_client.py": "# Basic MHF Client Example\n\nThis is a basic example of how to connect to the MHF server.",
        "tools/__init__.py": ""
    }
    
    for filepath, content in placeholders.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✓ Created placeholder file: {filepath}")
    
    return True

def main():
    """Main setup function"""
    print("🐉 Monster Hunter Frontier G - GitHub Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_git_installed():
        sys.exit(1)
    
    # Create project structure
    if not create_project_structure():
        print("\n✗ Failed to create project structure")
        sys.exit(1)
    
    # Create GitHub workflow
    if not create_github_workflow():
        print("\n⚠ Failed to create GitHub workflow")
    
    # Create issue templates
    if not create_issue_templates():
        print("\n⚠ Failed to create issue templates")
    
    # Initialize Git repository
    if not initialize_git_repo():
        print("\n✗ Failed to initialize Git repository")
        sys.exit(1)
    
    # Provide GitHub setup instructions
    create_github_repo_instructions()
    
    print("\n" + "=" * 60)
    print("✓ GitHub setup completed!")
    print("\nNext steps:")
    print("1. Follow the GitHub repository setup instructions above")
    print("2. Push your code to GitHub")
    print("3. Enable GitHub Issues and Discussions")
    print("4. Share your repository with the community!")
    print("\nHappy hunting! 🐉⚔️")

if __name__ == "__main__":
    main() 