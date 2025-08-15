#!/usr/bin/env python3
"""
Configuration validation tool for Windows ChatGPT MCP Tool
Validates MCP configuration files for Claude Desktop and VS Code.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class ConfigValidator:
    """Validates MCP configuration files."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
    
    def validate_json_syntax(self, config_path: Path) -> bool:
        """Validate JSON syntax of configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                json.load(f)
            self.info.append(f"✓ JSON syntax is valid: {config_path}")
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"✗ JSON syntax error in {config_path}: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"✗ Configuration file not found: {config_path}")
            return False
        except Exception as e:
            self.errors.append(f"✗ Error reading {config_path}: {e}")
            return False
    
    def validate_mcp_structure(self, config: Dict[str, Any], config_type: str) -> bool:
        """Validate MCP configuration structure."""
        valid = True
        
        if config_type == "claude_desktop":
            if "mcpServers" not in config:
                self.errors.append("✗ Missing 'mcpServers' section in Claude Desktop config")
                return False
            
            servers = config["mcpServers"]
            if not isinstance(servers, dict):
                self.errors.append("✗ 'mcpServers' must be an object")
                return False
            
            for server_name, server_config in servers.items():
                if not self.validate_server_config(server_name, server_config):
                    valid = False
        
        elif config_type == "vscode":
            if "claude.mcpServers" in config:
                servers = config["claude.mcpServers"]
                for server_name, server_config in servers.items():
                    if not self.validate_server_config(server_name, server_config):
                        valid = False
            elif "settings" in config and "claude.mcpServers" in config["settings"]:
                servers = config["settings"]["claude.mcpServers"]
                for server_name, server_config in servers.items():
                    if not self.validate_server_config(server_name, server_config):
                        valid = False
            else:
                self.warnings.append("⚠ No MCP servers configuration found")
        
        return valid
    
    def validate_server_config(self, server_name: str, config: Dict[str, Any]) -> bool:
        """Validate individual server configuration."""
        valid = True
        
        # Check required fields
        if "command" not in config:
            self.errors.append(f"✗ Server '{server_name}': Missing 'command' field")
            valid = False
        
        # Validate command
        if "command" in config:
            command = config["command"]
            if command == "python":
                self.info.append(f"✓ Server '{server_name}': Using Python command")
            elif command == "windows-chatgpt-mcp":
                self.info.append(f"✓ Server '{server_name}': Using pip-installed command")
            else:
                self.warnings.append(f"⚠ Server '{server_name}': Unusual command '{command}'")
        
        # Validate args
        if "args" in config:
            args = config["args"]
            if not isinstance(args, list):
                self.errors.append(f"✗ Server '{server_name}': 'args' must be a list")
                valid = False
            elif "-m" in args and "src.mcp_server" in args:
                self.info.append(f"✓ Server '{server_name}': Correct module args")
        
        # Validate cwd (current working directory)
        if "cwd" in config:
            cwd = config["cwd"]
            if not isinstance(cwd, str):
                self.errors.append(f"✗ Server '{server_name}': 'cwd' must be a string")
                valid = False
            else:
                # Check if path exists (with variable substitution awareness)
                if not cwd.startswith("${") and not os.path.exists(cwd):
                    self.warnings.append(f"⚠ Server '{server_name}': Directory '{cwd}' does not exist")
                else:
                    self.info.append(f"✓ Server '{server_name}': Working directory specified")
        
        # Validate environment variables
        if "env" in config:
            env = config["env"]
            if not isinstance(env, dict):
                self.errors.append(f"✗ Server '{server_name}': 'env' must be an object")
                valid = False
            else:
                self.validate_environment_variables(server_name, env)
        
        return valid
    
    def validate_environment_variables(self, server_name: str, env: Dict[str, str]) -> None:
        """Validate environment variables."""
        expected_vars = [
            "PYTHONPATH",
            "WINDOWS_CHATGPT_MCP_LOG_LEVEL",
            "WINDOWS_CHATGPT_MCP_TIMEOUT",
            "WINDOWS_CHATGPT_MCP_RETRY_COUNT"
        ]
        
        for var_name, var_value in env.items():
            if var_name in expected_vars:
                self.info.append(f"✓ Server '{server_name}': Environment variable '{var_name}' set")
                
                # Validate specific variables
                if var_name == "WINDOWS_CHATGPT_MCP_LOG_LEVEL":
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
                    if var_value not in valid_levels:
                        self.warnings.append(f"⚠ Server '{server_name}': Invalid log level '{var_value}'")
                
                elif var_name == "WINDOWS_CHATGPT_MCP_TIMEOUT":
                    try:
                        timeout = int(var_value)
                        if timeout <= 0:
                            self.warnings.append(f"⚠ Server '{server_name}': Timeout should be positive")
                    except ValueError:
                        self.warnings.append(f"⚠ Server '{server_name}': Timeout should be a number")
            else:
                self.info.append(f"✓ Server '{server_name}': Custom environment variable '{var_name}'")
    
    def validate_file(self, config_path: Path, config_type: str) -> bool:
        """Validate a configuration file."""
        print(f"\nValidating {config_type} configuration: {config_path}")
        print("-" * 50)
        
        # Check JSON syntax
        if not self.validate_json_syntax(config_path):
            return False
        
        # Load and validate structure
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            return self.validate_mcp_structure(config, config_type)
        
        except Exception as e:
            self.errors.append(f"✗ Error validating {config_path}: {e}")
            return False
    
    def print_results(self) -> None:
        """Print validation results."""
        if self.info:
            print("\nINFO:")
            for msg in self.info:
                print(f"  {msg}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\nERRORS:")
            for msg in self.errors:
                print(f"  {msg}")
    
    def get_claude_desktop_config_path(self) -> Optional[Path]:
        """Get the Claude Desktop configuration file path."""
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_path = Path(appdata) / "Claude" / "mcp.json"
            return config_path
        return None


def validate_example_configs():
    """Validate all example configuration files."""
    validator = ConfigValidator()
    project_root = Path(__file__).parent.parent
    examples_dir = project_root / "examples"
    
    example_configs = [
        ("mcp_config.json", "claude_desktop"),
        ("claude_desktop_config.json", "claude_desktop"),
        ("claude_desktop_config_pip.json", "claude_desktop"),
        ("vscode_settings.json", "vscode"),
        ("vscode_workspace_settings.json", "vscode"),
    ]
    
    all_valid = True
    
    print("Windows ChatGPT MCP Tool - Configuration Validator")
    print("=" * 60)
    
    for config_file, config_type in example_configs:
        config_path = examples_dir / config_file
        if config_path.exists():
            if not validator.validate_file(config_path, config_type):
                all_valid = False
        else:
            validator.warnings.append(f"⚠ Example config not found: {config_file}")
    
    return validator, all_valid


def validate_user_config():
    """Validate user's actual configuration files."""
    validator = ConfigValidator()
    
    # Check Claude Desktop config
    claude_config_path = validator.get_claude_desktop_config_path()
    if claude_config_path and claude_config_path.exists():
        validator.validate_file(claude_config_path, "claude_desktop")
    else:
        validator.warnings.append("⚠ Claude Desktop configuration not found")
    
    return validator


def main():
    """Main entry point for configuration validation."""
    if len(sys.argv) > 1:
        # Validate specific file
        config_path = Path(sys.argv[1])
        config_type = sys.argv[2] if len(sys.argv) > 2 else "claude_desktop"
        
        validator = ConfigValidator()
        success = validator.validate_file(config_path, config_type)
        validator.print_results()
        
        sys.exit(0 if success else 1)
    
    else:
        # Validate example configs
        example_validator, examples_valid = validate_example_configs()
        
        # Validate user config
        user_validator = validate_user_config()
        
        # Print combined results
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        example_validator.print_results()
        user_validator.print_results()
        
        overall_success = examples_valid and not user_validator.errors
        print(f"\nOVERALL STATUS: {'✓ PASSED' if overall_success else '✗ FAILED'}")
        
        if not overall_success:
            print("\nTo fix configuration issues:")
            print("1. Check JSON syntax in configuration files")
            print("2. Verify file paths exist and are accessible")
            print("3. Review example configurations in examples/ directory")
            print("4. Ensure Python and package paths are correct")
        
        sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()