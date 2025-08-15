#!/usr/bin/env python3
"""
Installation script for Windows ChatGPT MCP Tool
Automates the installation process with dependency checking and validation.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
from typing import List, Optional


class WindowsChatGPTMCPInstaller:
    """Handles installation of the Windows ChatGPT MCP Tool."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def print_header(self):
        """Print installation header."""
        print("=" * 60)
        print("Windows ChatGPT MCP Tool - Installation Script")
        print("=" * 60)
        print()
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        print("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8 or higher is required")
            return False
        
        # Check Windows
        if platform.system() != "Windows":
            self.errors.append("This tool requires Windows operating system")
            return False
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.errors.append("pip is not available")
            return False
        
        print("✓ Prerequisites check passed")
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("\nInstalling Python dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.errors.append("requirements.txt not found")
            return False
        
        try:
            # Upgrade pip first
            print("  Upgrading pip...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            print("  Installing requirements...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            
            print("✓ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install dependencies: {e}")
            return False
    
    def install_package(self) -> bool:
        """Install the package in development mode."""
        print("\nInstalling Windows ChatGPT MCP package...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", str(self.project_root)
            ], check=True)
            
            print("✓ Package installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Failed to install package: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify the installation was successful."""
        print("\nVerifying installation...")
        
        try:
            # Try to import the main module
            import src.mcp_server
            print("✓ Package import successful")
            
            # Run dependency verification
            verify_script = self.project_root / "scripts" / "verify_dependencies.py"
            if verify_script.exists():
                print("  Running dependency verification...")
                result = subprocess.run([
                    sys.executable, str(verify_script)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✓ Dependency verification passed")
                else:
                    self.warnings.append("Some dependency checks failed - see output above")
            
            return True
            
        except ImportError as e:
            self.errors.append(f"Package import failed: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Verification failed: {e}")
            return False
    
    def create_shortcuts(self) -> bool:
        """Create convenient shortcuts and scripts."""
        print("\nCreating shortcuts...")
        
        try:
            # Create a run script
            run_script_content = f"""@echo off
REM Windows ChatGPT MCP Tool Runner
echo Starting Windows ChatGPT MCP Server...
"{sys.executable}" -m src.mcp_server %*
pause
"""
            
            run_script_path = self.project_root / "run_mcp_server.bat"
            with open(run_script_path, 'w') as f:
                f.write(run_script_content)
            
            print(f"✓ Created run script: {run_script_path}")
            return True
            
        except Exception as e:
            self.warnings.append(f"Could not create shortcuts: {e}")
            return True  # Non-critical
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print("\n" + "=" * 60)
        print("INSTALLATION COMPLETE!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Ensure ChatGPT desktop application is installed and running")
        print("2. Configure Claude Desktop or VS Code Claude CLI with MCP settings")
        print("3. Use the example configuration in examples/mcp_config.json")
        print()
        print("To start the MCP server:")
        print(f"  python -m src.mcp_server")
        print("  OR")
        print(f"  Double-click: {self.project_root / 'run_mcp_server.bat'}")
        print()
        print("For troubleshooting, run:")
        print(f"  python {self.project_root / 'scripts' / 'verify_dependencies.py'}")
        print()
    
    def install(self) -> bool:
        """Run the complete installation process."""
        self.print_header()
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Dependencies", self.install_dependencies),
            ("Package", self.install_package),
            ("Verification", self.verify_installation),
            ("Shortcuts", self.create_shortcuts),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"\n✗ {step_name} step failed!")
                if self.errors:
                    print("Errors:")
                    for error in self.errors:
                        print(f"  - {error}")
                return False
        
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        self.print_next_steps()
        return True


def main():
    """Main entry point for installation."""
    installer = WindowsChatGPTMCPInstaller()
    success = installer.install()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()