#!/usr/bin/env python3
"""
Dependency verification script for Windows ChatGPT MCP Tool
Checks if all required dependencies and system requirements are met.
"""

import sys
import os
import platform
import subprocess
import importlib
from typing import List, Tuple, Dict, Any


class DependencyVerifier:
    """Verifies system and Python dependencies for the Windows ChatGPT MCP Tool."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.success_messages: List[str] = []
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        min_version = (3, 8)
        current_version = sys.version_info[:2]
        
        if current_version >= min_version:
            self.success_messages.append(f"✓ Python {sys.version.split()[0]} meets minimum requirement (3.8+)")
            return True
        else:
            self.errors.append(f"✗ Python {current_version[0]}.{current_version[1]} is too old. Minimum required: 3.8")
            return False
    
    def check_operating_system(self) -> bool:
        """Check if running on supported Windows version."""
        if platform.system() != "Windows":
            self.errors.append("✗ This tool requires Windows operating system")
            return False
        
        # Check Windows version
        version = platform.version()
        release = platform.release()
        
        if release in ["10", "11"]:
            self.success_messages.append(f"✓ Windows {release} is supported")
            return True
        else:
            self.warnings.append(f"⚠ Windows {release} may not be fully supported. Recommended: Windows 10 or 11")
            return True
    
    def check_python_packages(self) -> bool:
        """Check if required Python packages are installed."""
        required_packages = [
            ("mcp", "1.0.0"),
            ("pyautogui", "0.9.54"),
            ("pygetwindow", "0.0.9"),
            ("pywin32", "306"),
            ("typing_extensions", "4.0.0"),
            ("dataclasses_json", "0.6.0"),
            ("pyperclip", "1.8.2"),
            ("psutil", "5.9.0"),
        ]
        
        all_packages_ok = True
        
        for package_name, min_version in required_packages:
            try:
                # Handle package name variations
                import_name = package_name
                if package_name == "pygetwindow":
                    import_name = "pygetwindow"
                elif package_name == "dataclasses_json":
                    import_name = "dataclasses_json"
                elif package_name == "typing_extensions":
                    import_name = "typing_extensions"
                
                module = importlib.import_module(import_name)
                
                # Try to get version
                version = getattr(module, '__version__', 'unknown')
                if version == 'unknown':
                    # Try alternative version attributes
                    version = getattr(module, 'version', 'unknown')
                    if version == 'unknown' and hasattr(module, 'VERSION'):
                        version = getattr(module, 'VERSION', 'unknown')
                
                self.success_messages.append(f"✓ {package_name} ({version}) is installed")
                
            except ImportError:
                self.errors.append(f"✗ {package_name} is not installed")
                all_packages_ok = False
            except Exception as e:
                self.warnings.append(f"⚠ Could not verify {package_name} version: {e}")
        
        return all_packages_ok
    
    def check_chatgpt_installation(self) -> bool:
        """Check if ChatGPT desktop application might be installed."""
        # Common installation paths for ChatGPT
        possible_paths = [
            os.path.expanduser("~/AppData/Local/ChatGPT/ChatGPT.exe"),
            os.path.expanduser("~/AppData/Roaming/ChatGPT/ChatGPT.exe"),
            "C:/Program Files/ChatGPT/ChatGPT.exe",
            "C:/Program Files (x86)/ChatGPT/ChatGPT.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.success_messages.append(f"✓ ChatGPT found at: {path}")
                return True
        
        self.warnings.append("⚠ ChatGPT desktop application not found in common locations")
        self.warnings.append("  Please ensure ChatGPT desktop app is installed and accessible")
        return False
    
    def check_permissions(self) -> bool:
        """Check if script has necessary permissions for automation."""
        try:
            import pyautogui
            # Test basic automation capability
            pyautogui.FAILSAFE = True
            self.success_messages.append("✓ GUI automation permissions appear to be working")
            return True
        except Exception as e:
            self.errors.append(f"✗ GUI automation test failed: {e}")
            return False
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all dependency checks and return results."""
        print("Windows ChatGPT MCP Tool - Dependency Verification")
        print("=" * 50)
        
        checks = [
            ("Python Version", self.check_python_version),
            ("Operating System", self.check_operating_system),
            ("Python Packages", self.check_python_packages),
            ("ChatGPT Installation", self.check_chatgpt_installation),
            ("Automation Permissions", self.check_permissions),
        ]
        
        results = {}
        overall_success = True
        
        for check_name, check_func in checks:
            print(f"\nChecking {check_name}...")
            try:
                result = check_func()
                results[check_name] = result
                if not result:
                    overall_success = False
            except Exception as e:
                self.errors.append(f"✗ {check_name} check failed: {e}")
                results[check_name] = False
                overall_success = False
        
        # Print results
        print("\n" + "=" * 50)
        print("VERIFICATION RESULTS")
        print("=" * 50)
        
        if self.success_messages:
            print("\nSUCCESS:")
            for msg in self.success_messages:
                print(f"  {msg}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\nERRORS:")
            for msg in self.errors:
                print(f"  {msg}")
        
        print(f"\nOVERALL STATUS: {'✓ PASSED' if overall_success else '✗ FAILED'}")
        
        if not overall_success:
            print("\nTo fix issues:")
            print("1. Install missing Python packages: pip install -r requirements.txt")
            print("2. Ensure ChatGPT desktop app is installed")
            print("3. Check Windows permissions for GUI automation")
        
        return {
            "success": overall_success,
            "results": results,
            "errors": self.errors,
            "warnings": self.warnings,
            "success_messages": self.success_messages
        }


def main():
    """Main entry point for dependency verification."""
    verifier = DependencyVerifier()
    results = verifier.run_all_checks()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()