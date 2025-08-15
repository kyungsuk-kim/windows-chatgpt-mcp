#!/usr/bin/env python3
"""
Claude Desktop Configuration Validator

This script validates Claude Desktop MCP configuration files for the
Windows ChatGPT MCP Tool.
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple


class ClaudeConfigValidator:
    """Validates Claude Desktop MCP configuration."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message: str):
        """Add validation error."""
        self.errors.append(message)
        print(f"✗ ERROR: {message}")
    
    def add_warning(self, message: str):
        """Add validation warning."""
        self.warnings.append(message)
        print(f"⚠ WARNING: {message}")
    
    def add_success(self, message: str):
        """Add success message."""
        print(f"✓ {message}")
    
    def validate_json_structure(self, config: Dict[str, Any]) -> bool:
        """Validate basic JSON structure."""
        print("Validating JSON structure...")
        
        if not isinstance(config, dict):
            self.add_error("Configuration must be a JSON object")
            return False
        
        if 'mcpServers' not in config:
            self.add_error("Missing required 'mcpServers' section")
            return False
        
        if not isinstance(config['mcpServers'], dict):
            self.add_error("'mcpServers' must be an object")
            return False
        
        self.add_success("JSON structure is valid")
        return True
    
    def validate_server_config(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Validate individual server configuration."""
        print(f"Validating server '{server_name}'...")
        
        valid = True
        
        # Required fields
        required_fields = ['command']
        for field in required_fields:
            if field not in server_config:
                self.add_error(f"Server '{server_name}' missing required field '{field}'")
                valid = False
        
        # Validate command
        if 'command' in server_config:
            command = server_config['command']
            if not isinstance(command, str):
                self.add_error(f"Server '{server_name}' command must be a string")
                valid = False
            elif command in ['python', 'python.exe']:
                # Check if Python is in PATH
                if not self.check_python_availability():
                    self.add_warning(f"Server '{server_name}' uses 'python' command but Python may not be in PATH")
            elif command == 'windows-chatgpt-mcp':
                self.add_warning(f"Server '{server_name}' uses package command - ensure package is installed")
            elif not Path(command).exists():
                self.add_warning(f"Server '{server_name}' command path may not exist: {command}")
        
        # Validate args
        if 'args' in server_config:
            args = server_config['args']
            if not isinstance(args, list):
                self.add_error(f"Server '{server_name}' args must be an array")
                valid = False
            else:
                for i, arg in enumerate(args):
                    if not isinstance(arg, str):
                        self.add_error(f"Server '{server_name}' args[{i}] must be a string")
                        valid = False
        
        # Validate cwd
        if 'cwd' in server_config:
            cwd = server_config['cwd']
            if not isinstance(cwd, str):
                self.add_error(f"Server '{server_name}' cwd must be a string")
                valid = False
            elif not cwd.startswith('${') and not Path(cwd).exists():
                self.add_warning(f"Server '{server_name}' cwd directory may not exist: {cwd}")
        
        # Validate env
        if 'env' in server_config:
            env = server_config['env']
            if not isinstance(env, dict):
                self.add_error(f"Server '{server_name}' env must be an object")
                valid = False
            else:
                self.validate_environment_variables(server_name, env)
        
        if valid:
            self.add_success(f"Server '{server_name}' configuration is valid")
        
        return valid
    
    def validate_environment_variables(self, server_name: str, env: Dict[str, str]):
        """Validate environment variables."""
        known_vars = {
            'PYTHONPATH': 'Python module search path',
            'WINDOWS_CHATGPT_MCP_LOG_LEVEL': 'Logging level (DEBUG, INFO, WARNING, ERROR)',
            'WINDOWS_CHATGPT_MCP_TIMEOUT': 'Response timeout in seconds',
            'WINDOWS_CHATGPT_MCP_DEBUG': 'Debug mode (0 or 1)',
            'WINDOWS_CHATGPT_MCP_RETRY_COUNT': 'Number of retry attempts',
            'WINDOWS_CHATGPT_MCP_WINDOW_TITLE': 'ChatGPT window title pattern'
        }
        
        for var_name, var_value in env.items():
            if not isinstance(var_value, str):
                self.add_error(f"Server '{server_name}' env variable '{var_name}' must be a string")
                continue
            
            if var_name == 'WINDOWS_CHATGPT_MCP_LOG_LEVEL':
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
                if var_value not in valid_levels:
                    self.add_warning(f"Server '{server_name}' log level '{var_value}' not in {valid_levels}")
            
            elif var_name == 'WINDOWS_CHATGPT_MCP_TIMEOUT':
                try:
                    timeout = int(var_value)
                    if timeout <= 0:
                        self.add_warning(f"Server '{server_name}' timeout should be positive: {timeout}")
                    elif timeout > 300:
                        self.add_warning(f"Server '{server_name}' timeout is very high: {timeout}")
                except ValueError:
                    self.add_error(f"Server '{server_name}' timeout must be a number: {var_value}")
            
            elif var_name == 'WINDOWS_CHATGPT_MCP_DEBUG':
                if var_value not in ['0', '1', 'true', 'false']:
                    self.add_warning(f"Server '{server_name}' debug value should be 0/1 or true/false: {var_value}")
            
            elif var_name == 'PYTHONPATH':
                paths = var_value.split(os.pathsep)
                for path in paths:
                    if not path.startswith('${') and not Path(path).exists():
                        self.add_warning(f"Server '{server_name}' PYTHONPATH directory may not exist: {path}")
            
            elif var_name not in known_vars:
                self.add_warning(f"Server '{server_name}' unknown environment variable: {var_name}")
    
    def check_python_availability(self) -> bool:
        """Check if Python is available in PATH."""
        import subprocess
        try:
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def validate_chatgpt_server_presence(self, config: Dict[str, Any]) -> bool:
        """Check if there's a ChatGPT MCP server configured."""
        print("Checking for ChatGPT MCP server...")
        
        chatgpt_servers = []
        for server_name in config.get('mcpServers', {}).keys():
            if 'chatgpt' in server_name.lower():
                chatgpt_servers.append(server_name)
        
        if not chatgpt_servers:
            self.add_warning("No ChatGPT MCP server found in configuration")
            return False
        
        self.add_success(f"Found ChatGPT MCP servers: {', '.join(chatgpt_servers)}")
        return True
    
    def validate_file(self, config_file: str) -> bool:
        """Validate configuration file."""
        print(f"Validating Claude Desktop configuration: {config_file}")
        print("=" * 50)
        
        # Check file exists
        if not Path(config_file).exists():
            self.add_error(f"Configuration file not found: {config_file}")
            return False
        
        # Load and parse JSON
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.add_error(f"Invalid JSON: {e}")
            return False
        except Exception as e:
            self.add_error(f"Error reading file: {e}")
            return False
        
        # Validate structure
        if not self.validate_json_structure(config):
            return False
        
        # Validate each server
        all_servers_valid = True
        for server_name, server_config in config['mcpServers'].items():
            if not self.validate_server_config(server_name, server_config):
                all_servers_valid = False
        
        # Check for ChatGPT server
        self.validate_chatgpt_server_presence(config)
        
        return all_servers_valid and len(self.errors) == 0
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        
        if not self.errors and not self.warnings:
            print("✓ Configuration is valid with no issues!")
        else:
            if self.errors:
                print(f"✗ {len(self.errors)} error(s) found:")
                for error in self.errors:
                    print(f"  - {error}")
            
            if self.warnings:
                print(f"⚠ {len(self.warnings)} warning(s) found:")
                for warning in self.warnings:
                    print(f"  - {warning}")
        
        return len(self.errors) == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate Claude Desktop MCP configuration')
    parser.add_argument('config_file', nargs='?', 
                       default=str(Path(os.environ.get('APPDATA', '')) / 'Claude' / 'mcp.json'),
                       help='Configuration file to validate')
    parser.add_argument('--strict', action='store_true', 
                       help='Treat warnings as errors')
    
    args = parser.parse_args()
    
    validator = ClaudeConfigValidator()
    is_valid = validator.validate_file(args.config_file)
    
    if args.strict and validator.warnings:
        is_valid = False
    
    success = validator.print_summary()
    
    if args.strict and validator.warnings:
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()