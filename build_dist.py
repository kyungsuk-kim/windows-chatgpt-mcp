#!/usr/bin/env python3
"""
Build script for creating distributable packages of Windows ChatGPT MCP Tool
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                print(f"Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing file: {path}")
                path.unlink()

def build_wheel_package():
    """Build pip-installable wheel package"""
    print("\n=== Building Wheel Package ===")
    
    # Install build dependencies
    if not run_command([sys.executable, '-m', 'pip', 'install', 'build', 'wheel']):
        return False
    
    # Build the package
    if not run_command([sys.executable, '-m', 'build']):
        return False
    
    print("✓ Wheel package built successfully")
    return True

def build_standalone_executable():
    """Build standalone executable using PyInstaller"""
    print("\n=== Building Standalone Executable ===")
    
    # Install PyInstaller
    if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller']):
        return False
    
    # Create PyInstaller spec file if it doesn't exist
    spec_file = 'windows-chatgpt-mcp.spec'
    if not os.path.exists(spec_file):
        create_pyinstaller_spec()
    
    # Build executable
    if not run_command([sys.executable, '-m', 'PyInstaller', spec_file]):
        return False
    
    print("✓ Standalone executable built successfully")
    return True

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/mcp_server.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/config', 'config'),
        ('examples', 'examples'),
        ('README.md', '.'),
        ('INSTALL.md', '.'),
        ('TROUBLESHOOTING.md', '.'),
    ],
    hiddenimports=[
        'win32gui',
        'win32con',
        'win32api',
        'pyautogui',
        'pygetwindow',
        'mcp',
        'asyncio',
        'json',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='windows-chatgpt-mcp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('windows-chatgpt-mcp.spec', 'w') as f:
        f.write(spec_content)
    print("✓ PyInstaller spec file created")

def create_distribution_info():
    """Create distribution information files"""
    print("\n=== Creating Distribution Information ===")
    
    # Create version file
    version_content = '''"""Version information for Windows ChatGPT MCP Tool"""

__version__ = "1.0.0"
__author__ = "Windows ChatGPT MCP Tool Developer"
__email__ = "developer@example.com"
__description__ = "MCP tool for Windows 11 that enables Claude to interact with ChatGPT desktop application"
'''
    
    os.makedirs('src/windows_chatgpt_mcp', exist_ok=True)
    with open('src/windows_chatgpt_mcp/__version__.py', 'w') as f:
        f.write(version_content)
    
    # Create MANIFEST.in for including additional files
    manifest_content = '''include README.md
include INSTALL.md
include TROUBLESHOOTING.md
include LICENSE
include requirements.txt
recursive-include src/config *.json
recursive-include examples *.json *.py *.md
recursive-include docs *.md
recursive-include scripts *.py
'''
    
    with open('MANIFEST.in', 'w') as f:
        f.write(manifest_content)
    
    print("✓ Distribution information files created")

def create_license():
    """Create MIT license file"""
    license_content = '''MIT License

Copyright (c) 2024 Windows ChatGPT MCP Tool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    
    with open('LICENSE', 'w') as f:
        f.write(license_content)
    print("✓ LICENSE file created")

def main():
    """Main build process"""
    print("Windows ChatGPT MCP Tool - Distribution Builder")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create distribution files
    create_distribution_info()
    create_license()
    
    # Build packages
    success = True
    
    if '--wheel-only' not in sys.argv:
        success &= build_wheel_package()
    
    if '--exe-only' not in sys.argv:
        success &= build_standalone_executable()
    
    if success:
        print("\n✓ All packages built successfully!")
        print("\nDistribution files created:")
        if os.path.exists('dist'):
            for file in os.listdir('dist'):
                print(f"  - dist/{file}")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()