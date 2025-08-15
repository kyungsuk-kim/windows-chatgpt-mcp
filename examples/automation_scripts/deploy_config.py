#!/usr/bin/env python3
"""
Configuration Deployment Script for Windows ChatGPT MCP Tool

This script automates the deployment of MCP configuration files to the
appropriate locations for Claude Desktop and VS Code.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigDeployer:
    """Handles deployment of MCP configuration files."""
    
    def __init__(self):
        self.claude_desktop_config_path = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'mcp.json'
        self.vscode_user_settings_path = Path(os.environ.get('APPDATA', '')) / 'Code' / 'User' / 'settings.json'
    
    def backup_existing_config(self, config_path: Path) -> Optional[Path]:
        """Create a backup of existing configuration."""
        if not config_path.exists():
            return None
        
        backup_path = config_path.with_suffix(f'.backup.{int(os.time())}.json')
        try:
            shutil.copy2(config_path, backup_path)
            print(f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return None
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file {config_file}: {e}")
            sys.exit(1)
    
    def merge_configs(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new configuration with existing configuration."""
        merged = existing.copy()
        
        # For MCP servers, merge at the server level
        if 'mcpServers' in new:
            if 'mcpServers' not in merged:
                merged['mcpServers'] = {}
            merged['mcpServers'].update(new['mcpServers'])
        
        # For VS Code settings, merge at the top level
        for key, value in new.items():
            if key != 'mcpServers':
                merged[key] = value
        
        return merged
    
    def deploy_claude_desktop_config(self, config_file: str, merge: bool = True):
        """Deploy configuration to Claude Desktop."""
        print(f"Deploying Claude Desktop configuration from {config_file}")
        
        # Ensure directory exists
        self.claude_desktop_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load new configuration
        new_config = self.load_config(config_file)
        
        # Handle existing configuration
        if self.claude_desktop_config_path.exists() and merge:
            self.backup_existing_config(self.claude_desktop_config_path)
            try:
                with open(self.claude_desktop_config_path, 'r') as f:
                    existing_config = json.load(f)
                final_config = self.merge_configs(existing_config, new_config)
            except Exception as e:
                print(f"Warning: Could not merge with existing config: {e}")
                final_config = new_config
        else:
            if self.claude_desktop_config_path.exists():
                self.backup_existing_config(self.claude_desktop_config_path)
            final_config = new_config
        
        # Write configuration
        try:
            with open(self.claude_desktop_config_path, 'w') as f:
                json.dump(final_config, f, indent=2)
            print(f"✓ Claude Desktop configuration deployed to: {self.claude_desktop_config_path}")
        except Exception as e:
            print(f"✗ Error deploying Claude Desktop configuration: {e}")
            sys.exit(1)
    
    def deploy_vscode_config(self, config_file: str, workspace: bool = False, merge: bool = True):
        """Deploy configuration to VS Code."""
        if workspace:
            config_path = Path('.vscode') / 'settings.json'
            print(f"Deploying VS Code workspace configuration from {config_file}")
        else:
            config_path = self.vscode_user_settings_path
            print(f"Deploying VS Code user configuration from {config_file}")
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load new configuration
        new_config = self.load_config(config_file)
        
        # Handle existing configuration
        if config_path.exists() and merge:
            self.backup_existing_config(config_path)
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
                final_config = self.merge_configs(existing_config, new_config)
            except Exception as e:
                print(f"Warning: Could not merge with existing config: {e}")
                final_config = new_config
        else:
            if config_path.exists():
                self.backup_existing_config(config_path)
            final_config = new_config
        
        # Write configuration
        try:
            with open(config_path, 'w') as f:
                json.dump(final_config, f, indent=2)
            print(f"✓ VS Code configuration deployed to: {config_path}")
        except Exception as e:
            print(f"✗ Error deploying VS Code configuration: {e}")
            sys.exit(1)
    
    def validate_config(self, config_file: str) -> bool:
        """Validate configuration file."""
        print(f"Validating configuration file: {config_file}")
        
        try:
            config = self.load_config(config_file)
        except:
            return False
        
        # Check for required fields
        if 'mcpServers' in config:
            # Claude Desktop format
            for server_name, server_config in config['mcpServers'].items():
                if 'command' not in server_config:
                    print(f"✗ Missing 'command' for server '{server_name}'")
                    return False
                print(f"✓ Server '{server_name}' configuration valid")
        
        elif 'claude.mcpServers' in config:
            # VS Code format
            for server_name, server_config in config['claude.mcpServers'].items():
                if 'command' not in server_config:
                    print(f"✗ Missing 'command' for server '{server_name}'")
                    return False
                print(f"✓ Server '{server_name}' configuration valid")
        
        else:
            print("✗ No MCP server configuration found")
            return False
        
        print("✓ Configuration file is valid")
        return True
    
    def list_deployed_configs(self):
        """List currently deployed configurations."""
        print("Currently deployed configurations:")
        
        if self.claude_desktop_config_path.exists():
            print(f"✓ Claude Desktop: {self.claude_desktop_config_path}")
            try:
                with open(self.claude_desktop_config_path, 'r') as f:
                    config = json.load(f)
                    if 'mcpServers' in config:
                        for server_name in config['mcpServers'].keys():
                            print(f"  - Server: {server_name}")
            except Exception as e:
                print(f"  Warning: Could not read config: {e}")
        else:
            print("✗ Claude Desktop: Not configured")
        
        if self.vscode_user_settings_path.exists():
            print(f"✓ VS Code User: {self.vscode_user_settings_path}")
            try:
                with open(self.vscode_user_settings_path, 'r') as f:
                    config = json.load(f)
                    if 'claude.mcpServers' in config:
                        for server_name in config['claude.mcpServers'].keys():
                            print(f"  - Server: {server_name}")
            except Exception as e:
                print(f"  Warning: Could not read config: {e}")
        else:
            print("✗ VS Code User: Not configured")
        
        workspace_config = Path('.vscode') / 'settings.json'
        if workspace_config.exists():
            print(f"✓ VS Code Workspace: {workspace_config}")
            try:
                with open(workspace_config, 'r') as f:
                    config = json.load(f)
                    if 'claude.mcpServers' in config:
                        for server_name in config['claude.mcpServers'].keys():
                            print(f"  - Server: {server_name}")
            except Exception as e:
                print(f"  Warning: Could not read config: {e}")
        else:
            print("✗ VS Code Workspace: Not configured")


def main():
    parser = argparse.ArgumentParser(description='Deploy Windows ChatGPT MCP Tool configurations')
    parser.add_argument('config_file', nargs='?', help='Configuration file to deploy')
    parser.add_argument('--claude', action='store_true', help='Deploy to Claude Desktop')
    parser.add_argument('--vscode', action='store_true', help='Deploy to VS Code user settings')
    parser.add_argument('--workspace', action='store_true', help='Deploy to VS Code workspace settings')
    parser.add_argument('--no-merge', action='store_true', help='Replace existing config instead of merging')
    parser.add_argument('--validate', action='store_true', help='Validate configuration file only')
    parser.add_argument('--list', action='store_true', help='List currently deployed configurations')
    
    args = parser.parse_args()
    
    deployer = ConfigDeployer()
    
    if args.list:
        deployer.list_deployed_configs()
        return
    
    if not args.config_file:
        if not args.list:
            parser.print_help()
        return
    
    if args.validate:
        if deployer.validate_config(args.config_file):
            print("Configuration file is valid!")
        else:
            print("Configuration file validation failed!")
            sys.exit(1)
        return
    
    merge = not args.no_merge
    
    if args.claude:
        deployer.deploy_claude_desktop_config(args.config_file, merge)
    
    if args.vscode:
        deployer.deploy_vscode_config(args.config_file, workspace=False, merge=merge)
    
    if args.workspace:
        deployer.deploy_vscode_config(args.config_file, workspace=True, merge=merge)
    
    if not any([args.claude, args.vscode, args.workspace]):
        print("No deployment target specified. Use --claude, --vscode, or --workspace")
        parser.print_help()


if __name__ == '__main__':
    main()