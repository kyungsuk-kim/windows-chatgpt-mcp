#!/usr/bin/env python3
"""
Environment Setup Script for Windows ChatGPT MCP Tool

This script automates the setup of environment variables and configuration
for different deployment scenarios.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any


def setup_development_environment():
    """Set up environment variables for development."""
    env_vars = {
        'WINDOWS_CHATGPT_MCP_LOG_LEVEL': 'DEBUG',
        'WINDOWS_CHATGPT_MCP_DEBUG': '1',
        'WINDOWS_CHATGPT_MCP_TIMEOUT': '60',
        'WINDOWS_CHATGPT_MCP_RETRY_COUNT': '5',
        'WINDOWS_CHATGPT_MCP_PERFORMANCE_MONITORING': '1'
    }
    
    print("Setting up development environment...")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")
    
    print("Development environment configured successfully!")


def setup_production_environment():
    """Set up environment variables for production."""
    env_vars = {
        'WINDOWS_CHATGPT_MCP_LOG_LEVEL': 'WARNING',
        'WINDOWS_CHATGPT_MCP_DEBUG': '0',
        'WINDOWS_CHATGPT_MCP_TIMEOUT': '30',
        'WINDOWS_CHATGPT_MCP_RETRY_COUNT': '2',
        'WINDOWS_CHATGPT_MCP_PERFORMANCE_MONITORING': '0'
    }
    
    print("Setting up production environment...")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")
    
    print("Production environment configured successfully!")


def setup_team_environment():
    """Set up environment variables for team deployment."""
    # Check for team environment variables
    team_path = os.environ.get('TEAM_MCP_PATH')
    if not team_path:
        print("Error: TEAM_MCP_PATH environment variable not set")
        print("Please set: set TEAM_MCP_PATH=C:\\shared\\tools")
        return False
    
    env_vars = {
        'MCP_LOG_LEVEL': os.environ.get('MCP_LOG_LEVEL', 'INFO'),
        'MCP_TIMEOUT': os.environ.get('MCP_TIMEOUT', '30'),
        'MCP_WINDOW_TITLE': os.environ.get('MCP_WINDOW_TITLE', 'ChatGPT'),
        'MCP_DEBUG_MODE': os.environ.get('MCP_DEBUG_MODE', '0')
    }
    
    print("Setting up team environment...")
    print(f"Team MCP Path: {team_path}")
    
    for key, value in env_vars.items():
        print(f"{key}={value}")
    
    print("Team environment configured successfully!")
    return True


def create_config_file(config_type: str, output_path: str):
    """Create a configuration file for the specified type."""
    configs = {
        'development': {
            "mcpServers": {
                "windows-chatgpt-dev": {
                    "command": "python",
                    "args": ["-m", "src.mcp_server", "--debug"],
                    "cwd": "C:/dev/windows-chatgpt-mcp",
                    "env": {
                        "PYTHONPATH": "C:/dev/windows-chatgpt-mcp/src",
                        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG",
                        "WINDOWS_CHATGPT_MCP_DEBUG": "1",
                        "WINDOWS_CHATGPT_MCP_TIMEOUT": "60"
                    }
                }
            }
        },
        'production': {
            "mcpServers": {
                "windows-chatgpt": {
                    "command": "windows-chatgpt-mcp",
                    "args": [],
                    "env": {
                        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "WARNING",
                        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30"
                    }
                }
            }
        },
        'vscode': {
            "claude.mcpServers": {
                "windows-chatgpt": {
                    "command": "python",
                    "args": ["-m", "src.mcp_server"],
                    "cwd": "C:/path/to/windows-chatgpt-mcp",
                    "env": {
                        "PYTHONPATH": "C:/path/to/windows-chatgpt-mcp/src",
                        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
                    }
                }
            },
            "claude.enableMcp": True,
            "claude.mcpTimeout": 30000
        }
    }
    
    if config_type not in configs:
        print(f"Error: Unknown config type '{config_type}'")
        print(f"Available types: {', '.join(configs.keys())}")
        return False
    
    config = configs[config_type]
    
    try:
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration file created: {output_path}")
        return True
    except Exception as e:
        print(f"Error creating config file: {e}")
        return False


def validate_environment():
    """Validate that the environment is properly configured."""
    print("Validating environment configuration...")
    
    # Check Python installation
    try:
        import sys
        print(f"✓ Python {sys.version}")
    except Exception as e:
        print(f"✗ Python check failed: {e}")
        return False
    
    # Check required packages
    required_packages = ['mcp', 'pyautogui', 'pygetwindow', 'pywin32']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} not installed")
            return False
    
    # Check environment variables
    env_vars = [
        'WINDOWS_CHATGPT_MCP_LOG_LEVEL',
        'WINDOWS_CHATGPT_MCP_TIMEOUT'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var}={value}")
        else:
            print(f"ℹ {var} not set (will use default)")
    
    print("Environment validation complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description='Setup Windows ChatGPT MCP Tool environment')
    parser.add_argument('--env', choices=['dev', 'prod', 'team'], 
                       help='Environment type to set up')
    parser.add_argument('--config', choices=['development', 'production', 'vscode'],
                       help='Configuration type to create')
    parser.add_argument('--output', help='Output path for configuration file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate current environment')
    
    args = parser.parse_args()
    
    if args.validate:
        validate_environment()
        return
    
    if args.env:
        if args.env == 'dev':
            setup_development_environment()
        elif args.env == 'prod':
            setup_production_environment()
        elif args.env == 'team':
            setup_team_environment()
    
    if args.config:
        output_path = args.output or f"{args.config}_config.json"
        create_config_file(args.config, output_path)
    
    if not any([args.env, args.config, args.validate]):
        parser.print_help()


if __name__ == '__main__':
    main()