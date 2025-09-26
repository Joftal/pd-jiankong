#!/usr/bin/env python3
"""
GitHub Actions Build Script
Cross-platform build script for PD-Signal application
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def log_info(message):
    """Output info log"""
    print(f"[INFO] {message}")

def log_error(message):
    """Output error log"""
    print(f"[ERROR] {message}")

def log_success(message):
    """Output success log"""
    print(f"[SUCCESS] {message}")

def run_command(cmd, description=""):
    """Run command and handle errors"""
    try:
        log_info(f"Running command: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if description:
            log_success(description)
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Command failed: {cmd}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_dependencies():
    """Check dependencies"""
    log_info("Checking dependencies...")
    
    # Check Python version
    python_version = sys.version_info
    log_info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        log_error("Python 3.8 or higher required")
        return False
    
    # Check required packages
    required_packages = ['flet', 'requests', 'plyer', 'pyinstaller']
    for package in required_packages:
        try:
            __import__(package)
            log_success(f"Package {package} is installed")
        except ImportError:
            log_error(f"Package {package} is not installed")
            return False
    
    return True

def clean_build_dirs():
    """Clean build directories"""
    log_info("Cleaning build directories...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            log_success(f"Deleted directory: {dir_name}")
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        log_success(f"Deleted file: {spec_file}")

def build_executable():
    """Build executable"""
    log_info("Starting executable build...")
    
    # Get current platform
    current_platform = platform.system().lower()
    log_info(f"Current platform: {current_platform}")
    
    # Build PyInstaller command
    cmd_parts = [
        "pyinstaller",
        "--onefile",  # Single file mode
        "--windowed",  # No console window
        "--name", "PD-Signal",
        "--distpath", "dist/PD-Signal",
        "--workpath", "build",
        "--specpath", ".",
        "main.py"
    ]
    
    # Add platform-specific options
    if current_platform == "windows":
        cmd_parts.extend([
            "--add-data", "usersetting.json;.",
            "--add-data", "sql;sql"
        ])
    else:  # macOS and Linux
        cmd_parts.extend([
            "--add-data", "usersetting.json:.",
            "--add-data", "sql:sql"
        ])
    
    cmd = " ".join(cmd_parts)
    
    if not run_command(cmd, "PyInstaller build completed"):
        return False
    
    # Check build result
    if current_platform == "windows":
        exe_path = "dist/PD-Signal/PD-Signal.exe"
    else:
        exe_path = "dist/PD-Signal/PD-Signal"
    
    if not os.path.exists(exe_path):
        log_error(f"Executable not found: {exe_path}")
        return False
    
    log_success(f"Executable created: {exe_path}")
    
    # Show file size
    file_size = os.path.getsize(exe_path)
    log_info(f"File size: {file_size / (1024*1024):.2f} MB")
    
    return True

def create_additional_files():
    """Create additional files"""
    log_info("Creating additional files...")
    
    # Create startup script for Windows
    if platform.system().lower() == "windows":
        bat_content = """@echo off
echo Starting PD-Signal...
PD-Signal.exe
pause
"""
        with open("dist/启动PD-Signal.bat", "w", encoding="utf-8") as f:
            f.write(bat_content)
        log_success("Created startup script: 启动PD-Signal.bat")
        
        # Create debug script
        debug_content = """@echo off
echo Starting PD-Signal in debug mode...
PD-Signal.exe --debug
pause
"""
        with open("dist/调试模式.bat", "w", encoding="utf-8") as f:
            f.write(debug_content)
        log_success("Created debug script: 调试模式.bat")
    
    # Create readme
    readme_content = """# PD-Signal Usage Instructions

## Features
- Multi-streamer monitoring support
- Real-time live/offline notifications
- Windows system notifications
- Persistent data storage
- Modern GUI interface
- Auto-save configuration

## Usage
1. Run PD-Signal.exe to start the program
2. Add streamer IDs to monitor in the interface
3. Set monitoring interval
4. Click "Start Monitoring" button

## Notes
- First use requires setting Cookie
- Recommend reasonable monitoring interval (30+ seconds)
- Program auto-saves configuration

## Troubleshooting
If program fails to run properly, try:
1. Check network connection
2. Update Cookie
3. Use debug mode for detailed error info
"""
    
    with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    log_success("Created readme: 使用说明.txt")
    
    return True

def main():
    """Main function"""
    log_info("Starting GitHub Actions build process...")
    
    try:
        # Check dependencies
        if not check_dependencies():
            log_error("Dependency check failed")
            sys.exit(1)
        
        # Clean build directories
        clean_build_dirs()
        
        # Build executable
        if not build_executable():
            log_error("Executable build failed")
            sys.exit(1)
        
        # Create additional files
        if not create_additional_files():
            log_error("Additional files creation failed")
            sys.exit(1)
        
        log_success("Build process completed!")
        
    except Exception as e:
        log_error(f"Error during build process: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()