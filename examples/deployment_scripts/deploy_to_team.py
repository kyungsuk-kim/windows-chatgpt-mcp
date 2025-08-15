#!/usr/bin/env python3
"""
Team Deployment Script for Windows ChatGPT MCP Tool

This script automates deployment of the MCP tool across team environments
with standardized configurations and validation.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse


class TeamDeployer:
    """Handles team deployment of the Windows ChatGPT MCP Tool."""
    
    def __init__(self, team_config: Dict[str, Any]):
        self.team_config = team_config
        self.deployment_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log deployment message."""
        log_entry = f"[{level}] {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)
    
    def validate_team_config(self) -> bool:
        """Validate team configuration."""
        self.log("Validating team configuration...")
        
        required_fields = ['team_name', 'shared_path', 'python_path', 'environments']
        for field in required_fields:
            if field not in self.team_config:
                self.log(f"Missing required field: {field}", "ERROR")
                return False
        
        # Validate shared path
        shared_path = Path(self.team_config['shared_path'])
        if not shared_path.exists():
            self.log(f"Shared path does not exist: {shared_path}", "ERROR")
            return False
        
        # Validate Python path
        python_path = Path(self.team_config['python_path'])
        if not python_path.exists():
            self.log(f"Python path does not exist: {python_path}", "ERROR")
            return False
        
        self.log("Team configuration is valid")
        return True
    
    def setup_shared_installation(self) -> bool:
        """Set up shared installation of the MCP tool."""
        self.log("Setting up shared installation...")
        
        shared_path = Path(self.team_config['shared_path'])
        mcp_path = shared_path / 'windows-chatgpt-mcp'
        
        # Create directory structure
        try:
            mcp_path.mkdir(parents=True, exist_ok=True)
            (mcp_path / 'src').mkdir(exist_ok=True)
            (mcp_path / 'logs').mkdir(exist_ok=True)
            (mcp_path / 'config').mkdir(exist_ok=True)
        except Exception as e:
            self.log(f"Failed to create directory structure: {e}", "ERROR")
            return False
        
        # Copy source files
        try:
            source_dir = Path('src')
            if source_dir.exists():
                shutil.copytree(source_dir, mcp_path / 'src', dirs_exist_ok=True)
                self.log("Source files copied successfully")
            else:
                self.log("Source directory not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"Failed to copy source files: {e}", "ERROR")
            return False
        
        # Copy requirements
        try:
            if Path('requirements.txt').exists():
                shutil.copy2('requirements.txt', mcp_path / 'requirements.txt')
                self.log("Requirements file copied")
        except Exception as e:
            self.log(f"Failed to copy requirements: {e}", "WARNING")
        
        # Install dependencies
        try:
            python_path = self.team_config['python_path']
            cmd = [str(python_path), '-m', 'pip', 'install', '-r', str(mcp_path / 'requirements.txt')]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Dependencies installed successfully")
            else:
                self.log(f"Failed to install dependencies: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Failed to install dependencies: {e}", "ERROR")
            return False
        
        return True
    
    def create_environment_configs(self) -> bool:
        """Create configuration files for each environment."""
        self.log("Creating environment configurations...")
        
        shared_path = Path(self.team_config['shared_path'])
        mcp_path = shared_path / 'windows-chatgpt-mcp'
        config_dir = mcp_path / 'config'
        
        for env_name, env_config in self.team_config['environments'].items():
            self.log(f"Creating configuration for environment: {env_name}")
            
            # Create Claude Desktop config
            claude_config = {
                "mcpServers": {
                    f"windows-chatgpt-{env_name}": {
                        "command": str(self.team_config['python_path']),
                        "args": ["-m", "src.mcp_server"],
                        "cwd": str(mcp_path),
                        "env": {
                            "PYTHONPATH": str(mcp_path / 'src'),
                            **env_config.get('env_vars', {})
                        }
                    }
                }
            }
            
            claude_config_file = config_dir / f'claude_desktop_{env_name}.json'
            try:
                with open(claude_config_file, 'w') as f:
                    json.dump(claude_config, f, indent=2)
                self.log(f"Created Claude Desktop config: {claude_config_file}")
            except Exception as e:
                self.log(f"Failed to create Claude config for {env_name}: {e}", "ERROR")
                return False
            
            # Create VS Code config
            vscode_config = {
                "claude.mcpServers": {
                    f"windows-chatgpt-{env_name}": {
                        "command": str(self.team_config['python_path']),
                        "args": ["-m", "src.mcp_server"],
                        "cwd": str(mcp_path),
                        "env": {
                            "PYTHONPATH": str(mcp_path / 'src'),
                            **env_config.get('env_vars', {})
                        }
                    }
                },
                "claude.enableMcp": True,
                "claude.mcpTimeout": env_config.get('timeout', 30000)
            }
            
            vscode_config_file = config_dir / f'vscode_{env_name}.json'
            try:
                with open(vscode_config_file, 'w') as f:
                    json.dump(vscode_config, f, indent=2)
                self.log(f"Created VS Code config: {vscode_config_file}")
            except Exception as e:
                self.log(f"Failed to create VS Code config for {env_name}: {e}", "ERROR")
                return False
        
        return True
    
    def create_deployment_scripts(self) -> bool:
        """Create deployment scripts for team members."""
        self.log("Creating deployment scripts...")
        
        shared_path = Path(self.team_config['shared_path'])
        mcp_path = shared_path / 'windows-chatgpt-mcp'
        scripts_dir = mcp_path / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Create environment setup script
        setup_script = f'''@echo off
REM Team Environment Setup Script for {self.team_config['team_name']}
REM Generated automatically - do not edit manually

echo Setting up {self.team_config['team_name']} MCP environment...

REM Set team environment variables
set TEAM_MCP_PATH={shared_path}
set TEAM_PYTHON_PATH={self.team_config['python_path']}

REM Set default MCP environment variables
set MCP_LOG_LEVEL=INFO
set MCP_TIMEOUT=30
set MCP_WINDOW_TITLE=ChatGPT
set MCP_DEBUG_MODE=0

echo Environment variables set successfully!
echo.
echo Available configurations:
'''
        
        for env_name in self.team_config['environments'].keys():
            setup_script += f'echo   - {env_name}: Use config\\claude_desktop_{env_name}.json or config\\vscode_{env_name}.json\n'
        
        setup_script += '''
echo.
echo To deploy a configuration:
echo   For Claude Desktop: copy config\\claude_desktop_ENV.json %APPDATA%\\Claude\\mcp.json
echo   For VS Code: merge config\\vscode_ENV.json with your VS Code settings
echo.
pause
'''
        
        setup_script_file = scripts_dir / 'setup_team_environment.bat'
        try:
            with open(setup_script_file, 'w') as f:
                f.write(setup_script)
            self.log(f"Created setup script: {setup_script_file}")
        except Exception as e:
            self.log(f"Failed to create setup script: {e}", "ERROR")
            return False
        
        # Create Python deployment helper
        deploy_helper = f'''#!/usr/bin/env python3
"""
Team Deployment Helper for {self.team_config['team_name']}
Generated automatically - do not edit manually
"""

import os
import sys
import json
import shutil
from pathlib import Path

TEAM_CONFIG = {json.dumps(self.team_config, indent=2)}

def deploy_claude_config(env_name):
    """Deploy Claude Desktop configuration."""
    config_file = Path(__file__).parent.parent / 'config' / f'claude_desktop_{{env_name}}.json'
    target_file = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'mcp.json'
    
    if not config_file.exists():
        print(f"Configuration file not found: {{config_file}}")
        return False
    
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config_file, target_file)
        print(f"Deployed Claude Desktop configuration for {{env_name}}")
        return True
    except Exception as e:
        print(f"Failed to deploy configuration: {{e}}")
        return False

def list_environments():
    """List available environments."""
    print("Available environments:")
    for env_name, env_config in TEAM_CONFIG['environments'].items():
        print(f"  - {{env_name}}: {{env_config.get('description', 'No description')}}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Deploy team MCP configurations')
    parser.add_argument('--env', help='Environment to deploy')
    parser.add_argument('--claude', action='store_true', help='Deploy to Claude Desktop')
    parser.add_argument('--list', action='store_true', help='List available environments')
    
    args = parser.parse_args()
    
    if args.list:
        list_environments()
        return
    
    if args.env and args.claude:
        deploy_claude_config(args.env)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
'''
        
        deploy_helper_file = scripts_dir / 'deploy_helper.py'
        try:
            with open(deploy_helper_file, 'w') as f:
                f.write(deploy_helper)
            self.log(f"Created deployment helper: {deploy_helper_file}")
        except Exception as e:
            self.log(f"Failed to create deployment helper: {e}", "ERROR")
            return False
        
        return True
    
    def create_documentation(self) -> bool:
        """Create team-specific documentation."""
        self.log("Creating team documentation...")
        
        shared_path = Path(self.team_config['shared_path'])
        mcp_path = shared_path / 'windows-chatgpt-mcp'
        docs_dir = mcp_path / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        team_readme = f'''# {self.team_config['team_name']} - Windows ChatGPT MCP Tool

This is the team deployment of the Windows ChatGPT MCP Tool for {self.team_config['team_name']}.

## Quick Start

1. **Set up environment variables:**
   ```cmd
   scripts\\setup_team_environment.bat
   ```

2. **Deploy configuration:**
   ```cmd
   python scripts\\deploy_helper.py --env ENVIRONMENT --claude
   ```

## Available Environments

'''
        
        for env_name, env_config in self.team_config['environments'].items():
            team_readme += f'''### {env_name}

- **Description:** {env_config.get('description', 'No description')}
- **Log Level:** {env_config.get('env_vars', {}).get('WINDOWS_CHATGPT_MCP_LOG_LEVEL', 'INFO')}
- **Timeout:** {env_config.get('timeout', 30000)}ms

**Configuration Files:**
- Claude Desktop: `config/claude_desktop_{env_name}.json`
- VS Code: `config/vscode_{env_name}.json`

'''
        
        team_readme += f'''## Team Configuration

- **Shared Path:** `{self.team_config['shared_path']}`
- **Python Path:** `{self.team_config['python_path']}`
- **Team Contact:** {self.team_config.get('contact', 'Not specified')}

## Support

For team-specific support, contact: {self.team_config.get('contact', 'team administrator')}

For general tool support, see the main documentation.
'''
        
        readme_file = mcp_path / 'README_TEAM.md'
        try:
            with open(readme_file, 'w') as f:
                f.write(team_readme)
            self.log(f"Created team documentation: {readme_file}")
        except Exception as e:
            self.log(f"Failed to create documentation: {e}", "ERROR")
            return False
        
        return True
    
    def validate_deployment(self) -> bool:
        """Validate the deployment."""
        self.log("Validating deployment...")
        
        shared_path = Path(self.team_config['shared_path'])
        mcp_path = shared_path / 'windows-chatgpt-mcp'
        
        # Check required files exist
        required_files = [
            'src/mcp_server.py',
            'requirements.txt',
            'README_TEAM.md',
            'scripts/setup_team_environment.bat',
            'scripts/deploy_helper.py'
        ]
        
        for file_path in required_files:
            full_path = mcp_path / file_path
            if not full_path.exists():
                self.log(f"Missing required file: {full_path}", "ERROR")
                return False
        
        # Check configuration files
        for env_name in self.team_config['environments'].keys():
            claude_config = mcp_path / 'config' / f'claude_desktop_{env_name}.json'
            vscode_config = mcp_path / 'config' / f'vscode_{env_name}.json'
            
            if not claude_config.exists():
                self.log(f"Missing Claude config for {env_name}: {claude_config}", "ERROR")
                return False
            
            if not vscode_config.exists():
                self.log(f"Missing VS Code config for {env_name}: {vscode_config}", "ERROR")
                return False
        
        self.log("Deployment validation successful")
        return True
    
    def deploy(self) -> bool:
        """Execute full deployment."""
        self.log(f"Starting team deployment for {self.team_config['team_name']}")
        
        steps = [
            self.validate_team_config,
            self.setup_shared_installation,
            self.create_environment_configs,
            self.create_deployment_scripts,
            self.create_documentation,
            self.validate_deployment
        ]
        
        for step in steps:
            if not step():
                self.log("Deployment failed", "ERROR")
                return False
        
        self.log("Team deployment completed successfully!")
        return True
    
    def save_deployment_log(self, log_file: str):
        """Save deployment log to file."""
        try:
            with open(log_file, 'w') as f:
                f.write(f"Team Deployment Log for {self.team_config['team_name']}\\n")
                f.write("=" * 50 + "\\n\\n")
                for entry in self.deployment_log:
                    f.write(entry + "\\n")
            print(f"Deployment log saved to: {log_file}")
        except Exception as e:
            print(f"Failed to save deployment log: {e}")


def load_team_config(config_file: str) -> Dict[str, Any]:
    """Load team configuration from file."""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load team configuration: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Deploy Windows ChatGPT MCP Tool for team')
    parser.add_argument('config_file', help='Team configuration file')
    parser.add_argument('--log', help='Save deployment log to file')
    parser.add_argument('--validate-only', action='store_true', help='Only validate configuration')
    
    args = parser.parse_args()
    
    # Load team configuration
    team_config = load_team_config(args.config_file)
    
    # Create deployer
    deployer = TeamDeployer(team_config)
    
    if args.validate_only:
        success = deployer.validate_team_config()
    else:
        success = deployer.deploy()
    
    # Save log if requested
    if args.log:
        deployer.save_deployment_log(args.log)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()