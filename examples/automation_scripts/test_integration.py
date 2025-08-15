#!/usr/bin/env python3
"""
Integration Testing Script for Windows ChatGPT MCP Tool

This script provides automated testing of the MCP tool integration
with Claude Desktop and VS Code.
"""

import os
import sys
import json
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class MCPIntegrationTester:
    """Handles integration testing of the MCP tool."""
    
    def __init__(self):
        self.test_results = []
        self.mcp_server_process = None
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': time.time()
        })
    
    def test_python_environment(self) -> bool:
        """Test Python environment and dependencies."""
        print("\n=== Testing Python Environment ===")
        
        # Test Python version
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                self.log_test("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}")
            else:
                self.log_test("Python Version", False, f"Python {version.major}.{version.minor}.{version.micro} < 3.8")
                return False
        except Exception as e:
            self.log_test("Python Version", False, str(e))
            return False
        
        # Test required packages
        required_packages = [
            'mcp',
            'pyautogui', 
            'pygetwindow',
            'pywin32'
        ]
        
        all_packages_ok = True
        for package in required_packages:
            try:
                __import__(package)
                self.log_test(f"Package: {package}", True)
            except ImportError as e:
                self.log_test(f"Package: {package}", False, str(e))
                all_packages_ok = False
        
        return all_packages_ok
    
    def test_mcp_server_startup(self) -> bool:
        """Test MCP server startup."""
        print("\n=== Testing MCP Server Startup ===")
        
        try:
            # Start MCP server process
            cmd = [sys.executable, '-m', 'src.mcp_server', '--test']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_test("MCP Server Startup", True, "Server started successfully")
                return True
            else:
                self.log_test("MCP Server Startup", False, f"Exit code: {result.returncode}")
                if result.stderr:
                    print(f"    Error: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            self.log_test("MCP Server Startup", False, "Timeout after 30 seconds")
            return False
        except Exception as e:
            self.log_test("MCP Server Startup", False, str(e))
            return False
    
    def test_chatgpt_detection(self) -> bool:
        """Test ChatGPT window detection."""
        print("\n=== Testing ChatGPT Detection ===")
        
        try:
            import pygetwindow as gw
            
            # Look for ChatGPT windows
            chatgpt_windows = []
            for window in gw.getAllWindows():
                if 'chatgpt' in window.title.lower():
                    chatgpt_windows.append(window.title)
            
            if chatgpt_windows:
                self.log_test("ChatGPT Window Detection", True, f"Found: {', '.join(chatgpt_windows)}")
                return True
            else:
                self.log_test("ChatGPT Window Detection", False, "No ChatGPT windows found")
                print("    Please ensure ChatGPT desktop application is running")
                return False
        
        except Exception as e:
            self.log_test("ChatGPT Window Detection", False, str(e))
            return False
    
    def test_automation_permissions(self) -> bool:
        """Test Windows automation permissions."""
        print("\n=== Testing Automation Permissions ===")
        
        try:
            import pyautogui
            
            # Test basic automation functions
            try:
                pos = pyautogui.position()
                self.log_test("Mouse Position Detection", True, f"Position: {pos}")
            except Exception as e:
                self.log_test("Mouse Position Detection", False, str(e))
                return False
            
            # Test screen capture
            try:
                screenshot = pyautogui.screenshot(region=(0, 0, 100, 100))
                self.log_test("Screen Capture", True, f"Captured {screenshot.size}")
            except Exception as e:
                self.log_test("Screen Capture", False, str(e))
                return False
            
            return True
        
        except Exception as e:
            self.log_test("Automation Permissions", False, str(e))
            return False
    
    def test_configuration_files(self) -> bool:
        """Test configuration file validity."""
        print("\n=== Testing Configuration Files ===")
        
        config_files = [
            'examples/claude_desktop_config.json',
            'examples/vscode_settings.json',
            'examples/development_config.json',
            'examples/production_config.json'
        ]
        
        all_configs_ok = True
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    self.log_test(f"Config: {config_file}", True, "Valid JSON")
                except json.JSONDecodeError as e:
                    self.log_test(f"Config: {config_file}", False, f"Invalid JSON: {e}")
                    all_configs_ok = False
                except Exception as e:
                    self.log_test(f"Config: {config_file}", False, str(e))
                    all_configs_ok = False
            else:
                self.log_test(f"Config: {config_file}", False, "File not found")
                all_configs_ok = False
        
        return all_configs_ok
    
    def test_claude_desktop_integration(self) -> bool:
        """Test Claude Desktop integration."""
        print("\n=== Testing Claude Desktop Integration ===")
        
        claude_config_path = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'mcp.json'
        
        if not claude_config_path.exists():
            self.log_test("Claude Desktop Config", False, "mcp.json not found")
            print(f"    Expected location: {claude_config_path}")
            return False
        
        try:
            with open(claude_config_path, 'r') as f:
                config = json.load(f)
            
            if 'mcpServers' not in config:
                self.log_test("Claude Desktop Config", False, "No mcpServers section")
                return False
            
            # Look for windows-chatgpt server
            chatgpt_servers = [name for name in config['mcpServers'].keys() 
                             if 'chatgpt' in name.lower()]
            
            if chatgpt_servers:
                self.log_test("Claude Desktop Config", True, f"Found servers: {', '.join(chatgpt_servers)}")
                return True
            else:
                self.log_test("Claude Desktop Config", False, "No ChatGPT MCP server configured")
                return False
        
        except Exception as e:
            self.log_test("Claude Desktop Config", False, str(e))
            return False
    
    def test_vscode_integration(self) -> bool:
        """Test VS Code integration."""
        print("\n=== Testing VS Code Integration ===")
        
        # Check user settings
        vscode_settings_path = Path(os.environ.get('APPDATA', '')) / 'Code' / 'User' / 'settings.json'
        workspace_settings_path = Path('.vscode') / 'settings.json'
        
        found_config = False
        
        for settings_path, settings_type in [(vscode_settings_path, "User"), (workspace_settings_path, "Workspace")]:
            if settings_path.exists():
                try:
                    with open(settings_path, 'r') as f:
                        config = json.load(f)
                    
                    if 'claude.mcpServers' in config:
                        chatgpt_servers = [name for name in config['claude.mcpServers'].keys() 
                                         if 'chatgpt' in name.lower()]
                        if chatgpt_servers:
                            self.log_test(f"VS Code {settings_type} Config", True, f"Found servers: {', '.join(chatgpt_servers)}")
                            found_config = True
                        else:
                            self.log_test(f"VS Code {settings_type} Config", False, "No ChatGPT MCP server configured")
                    else:
                        self.log_test(f"VS Code {settings_type} Config", False, "No claude.mcpServers section")
                
                except Exception as e:
                    self.log_test(f"VS Code {settings_type} Config", False, str(e))
            else:
                self.log_test(f"VS Code {settings_type} Config", False, "Settings file not found")
        
        return found_config
    
    async def test_mcp_tools(self) -> bool:
        """Test MCP tools functionality."""
        print("\n=== Testing MCP Tools ===")
        
        # This would require a more complex setup with actual MCP client
        # For now, we'll just test that the server can list tools
        try:
            cmd = [sys.executable, '-c', '''
import asyncio
import sys
sys.path.insert(0, "src")
from mcp_server import WindowsChatGPTMCPServer

async def test():
    server = WindowsChatGPTMCPServer()
    # This is a simplified test - in reality we'd need full MCP protocol
    print("MCP server created successfully")

asyncio.run(test())
''']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_test("MCP Tools", True, "Server initialization successful")
                return True
            else:
                self.log_test("MCP Tools", False, f"Server initialization failed: {result.stderr}")
                return False
        
        except Exception as e:
            self.log_test("MCP Tools", False, str(e))
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'results': self.test_results,
            'timestamp': time.time()
        }
        
        return report
    
    def print_summary(self):
        """Print test summary."""
        report = self.generate_report()
        summary = report['summary']
        
        print(f"\n=== Test Summary ===")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['failed'] > 0:
            print(f"\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests."""
        print("Starting Windows ChatGPT MCP Tool Integration Tests")
        print("=" * 50)
        
        tests = [
            self.test_python_environment,
            self.test_configuration_files,
            self.test_mcp_server_startup,
            self.test_chatgpt_detection,
            self.test_automation_permissions,
            self.test_claude_desktop_integration,
            self.test_vscode_integration,
            self.test_mcp_tools
        ]
        
        all_passed = True
        for test in tests:
            try:
                if asyncio.iscoroutinefunction(test):
                    result = await test()
                else:
                    result = test()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"Test {test.__name__} failed with exception: {e}")
                all_passed = False
        
        self.print_summary()
        return all_passed


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Windows ChatGPT MCP Tool integration')
    parser.add_argument('--report', help='Save test report to file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    tester = MCPIntegrationTester()
    success = await tester.run_all_tests()
    
    if args.report:
        report = tester.generate_report()
        with open(args.report, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nTest report saved to: {args.report}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())