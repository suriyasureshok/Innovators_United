#!/usr/bin/env python3
"""
SYNAPSE-FI Setup Script
Automates environment setup and validation
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(message):
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}\n")

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Verify Python version is 3.9+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.9+ required (found {version.major}.{version.minor}.{version.micro})")
        return False

def create_venv():
    """Create virtual environment"""
    if Path("venv").exists():
        print("ℹ️  Virtual environment already exists")
        return True
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    activate_cmd = "venv\\Scripts\\activate" if os.name == "nt" else "source venv/bin/activate"
    cmd = f"{activate_cmd} && pip install -r requirements.txt"
    return run_command(cmd, "Installing dependencies")

def create_env_file():
    """Create .env file from template"""
    if Path(".env").exists():
        print("ℹ️  .env file already exists")
        return True
    
    try:
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
        print("⚠️  Please update .env with your configuration!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env: {e}")
        return False

def verify_structure():
    """Verify directory structure"""
    required_dirs = [
        "entity_a", "entity_b", "bridge_hub",
        "dashboard", "shared", "tests", "scripts"
    ]
    
    missing = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        print(f"❌ Missing directories: {', '.join(missing)}")
        return False
    else:
        print("✅ Directory structure verified")
        return True

def main():
    """Main setup flow"""
    print_header("SYNAPSE-FI Environment Setup")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", verify_structure),
        ("Virtual Environment", create_venv),
        ("Environment File", create_env_file),
        # ("Dependencies", install_dependencies),  # Uncomment when venv is activated
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking: {name}")
        results.append((name, check_func()))
    
    print_header("Setup Summary")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        if os.name == "nt":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("3. Update .env with your configuration")
        print("4. Start implementing Entity A (Section 3 of checklist)")
    else:
        print("\n⚠️  Setup incomplete. Please fix the failures above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
