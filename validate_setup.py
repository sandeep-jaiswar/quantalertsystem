#!/usr/bin/env python3
"""Validation script to check if the setup is working correctly."""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is acceptable."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor}.{version.micro} is not supported")
        return False

def check_required_directories():
    """Check if required directories exist."""
    required_dirs = ['config', 'models', 'services', 'scripts', 'tests']
    all_exist = True
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ Directory {dir_name} exists")
        else:
            print(f"❌ Directory {dir_name} missing")
            all_exist = False
    
    return all_exist

def check_key_files():
    """Check if key files exist."""
    key_files = [
        'main.py',
        'pyproject.toml', 
        'requirements.txt',
        'config/settings.py',
        'models/market_data.py'
    ]
    all_exist = True
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ File {file_path} exists")
        else:
            print(f"❌ File {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main validation function."""
    print("🔍 Validating Quantitative Alerts System Setup...")
    print("-" * 50)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Required Directories", check_required_directories()),
        ("Key Files", check_key_files())
    ]
    
    all_passed = all(result for _, result in checks)
    
    print("-" * 50)
    if all_passed:
        print("✅ All validation checks passed!")
        return 0
    else:
        print("❌ Some validation checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())