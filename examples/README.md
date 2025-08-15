# Windows ChatGPT MCP Tool - Examples and Scripts

This directory contains comprehensive examples, configurations, and automation scripts for the Windows ChatGPT MCP Tool.

## Directory Structure

```
examples/
├── README.md                           # This file
├── automation_scripts/                 # Automation and setup scripts
│   ├── setup_environment.py           # Environment setup automation
│   ├── deploy_config.py               # Configuration deployment
│   └── test_integration.py            # Integration testing
├── deployment_scripts/                 # Team deployment automation
│   ├── deploy_to_team.py              # Team deployment script
│   └── team_config_template.json      # Team configuration template
├── validation_examples/                # Configuration validation
│   ├── validate_claude_config.py      # Claude Desktop config validator
│   └── validate_vscode_config.py      # VS Code config validator
├── claude_desktop_config.json         # Basic Claude Desktop config
├── claude_desktop_config_pip.json     # Claude Desktop config for pip install
├── development_config.json            # Development environment config
├── production_config.json             # Production environment config
├── team_config.json                   # Team shared configuration
├── multi_environment_config.json      # Multiple environments config
├── vscode_settings.json               # Basic VS Code settings
├── vscode_workspace_config.json       # VS Code workspace settings
├── vscode_user_settings.json          # VS Code user settings
└── mcp_config.json                    # Generic MCP configuration
```

## Configuration Examples

### Basic Configurations

#### Claude Desktop Configuration
**File:** `claude_desktop_config.json`

Basic configuration for Claude Desktop with local development setup:

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/Users/YourUsername/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/Users/YourUsername/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Usage:**
1. Copy to `%APPDATA%\Claude\mcp.json`
2. Update paths to match your installation
3. Restart Claude Desktop

#### VS Code Configuration
**File:** `vscode_settings.json`

Basic VS Code settings for MCP integration:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/windows-chatgpt-mcp/src"
      }
    }
  },
  "claude.enableMcp": true
}
```

**Usage:**
1. Add to VS Code user settings or workspace settings
2. Update paths to match your installation
3. Restart VS Code

### Environment-Specific Configurations

#### Development Environment
**File:** `development_config.json`

Configuration optimized for development with debug logging:

- Debug logging enabled
- Extended timeouts
- Performance monitoring
- Verbose error reporting

#### Production Environment
**File:** `production_config.json`

Configuration optimized for production use:

- Minimal logging
- Standard timeouts
- Error-only reporting
- Optimized performance

#### Team Configuration
**File:** `team_config.json`

Shared configuration for team environments:

- Environment variable substitution
- Standardized paths
- Team-specific settings

### Multi-Environment Setup
**File:** `multi_environment_config.json`

Configuration supporting multiple environments simultaneously:

- Development server with debug mode
- Staging server with standard settings
- Production server with minimal logging

## Automation Scripts

### Environment Setup
**Script:** `automation_scripts/setup_environment.py`

Automates environment variable setup and configuration creation.

**Usage:**
```cmd
# Set up development environment
python automation_scripts/setup_environment.py --env dev

# Set up production environment
python automation_scripts/setup_environment.py --env prod

# Create configuration file
python automation_scripts/setup_environment.py --config development --output my_config.json

# Validate environment
python automation_scripts/setup_environment.py --validate
```

**Features:**
- Environment variable management
- Configuration file generation
- Environment validation
- Multiple environment support

### Configuration Deployment
**Script:** `automation_scripts/deploy_config.py`

Automates deployment of configuration files to appropriate locations.

**Usage:**
```cmd
# Deploy to Claude Desktop
python automation_scripts/deploy_config.py config.json --claude

# Deploy to VS Code user settings
python automation_scripts/deploy_config.py config.json --vscode

# Deploy to VS Code workspace
python automation_scripts/deploy_config.py config.json --workspace

# List current configurations
python automation_scripts/deploy_config.py --list

# Validate configuration before deployment
python automation_scripts/deploy_config.py config.json --validate
```

**Features:**
- Automatic backup of existing configurations
- Configuration merging
- Multiple deployment targets
- Validation before deployment

### Integration Testing
**Script:** `automation_scripts/test_integration.py`

Comprehensive integration testing for the MCP tool.

**Usage:**
```cmd
# Run all integration tests
python automation_scripts/test_integration.py

# Save test report
python automation_scripts/test_integration.py --report test_results.json

# Verbose output
python automation_scripts/test_integration.py --verbose
```

**Test Coverage:**
- Python environment validation
- MCP server startup testing
- ChatGPT detection
- Automation permissions
- Configuration file validation
- Claude Desktop integration
- VS Code integration

## Validation Examples

### Claude Desktop Config Validator
**Script:** `validation_examples/validate_claude_config.py`

Validates Claude Desktop MCP configuration files.

**Usage:**
```cmd
# Validate default Claude Desktop config
python validation_examples/validate_claude_config.py

# Validate specific file
python validation_examples/validate_claude_config.py path/to/mcp.json

# Strict validation (warnings as errors)
python validation_examples/validate_claude_config.py --strict
```

**Validation Checks:**
- JSON syntax validation
- Required field verification
- Path existence checking
- Environment variable validation
- Python availability testing

### VS Code Config Validator
**Script:** `validation_examples/validate_vscode_config.py`

Validates VS Code settings for MCP integration.

**Usage:**
```cmd
# Validate user settings
python validation_examples/validate_vscode_config.py --user

# Validate workspace settings
python validation_examples/validate_vscode_config.py --workspace

# Validate specific file
python validation_examples/validate_vscode_config.py path/to/settings.json
```

**Validation Checks:**
- VS Code settings structure
- MCP server configuration
- Claude-specific settings
- Environment variable validation

## Team Deployment

### Team Deployment Script
**Script:** `deployment_scripts/deploy_to_team.py`

Automates deployment across team environments with standardized configurations.

**Usage:**
```cmd
# Deploy using team configuration
python deployment_scripts/deploy_to_team.py team_config.json

# Validate team configuration only
python deployment_scripts/deploy_to_team.py team_config.json --validate-only

# Save deployment log
python deployment_scripts/deploy_to_team.py team_config.json --log deployment.log
```

**Features:**
- Shared installation setup
- Environment-specific configurations
- Automated script generation
- Team documentation creation
- Deployment validation

### Team Configuration Template
**File:** `deployment_scripts/team_config_template.json`

Template for team deployment configuration:

```json
{
  "team_name": "Development Team",
  "shared_path": "C:/shared/tools",
  "python_path": "C:/Python39/python.exe",
  "contact": "devops@company.com",
  "environments": {
    "development": { ... },
    "staging": { ... },
    "production": { ... }
  }
}
```

## Quick Start Guide

### 1. Choose Your Configuration

**For Individual Use:**
- `claude_desktop_config.json` - Basic Claude Desktop setup
- `vscode_settings.json` - Basic VS Code setup

**For Development:**
- `development_config.json` - Debug-enabled configuration

**For Production:**
- `production_config.json` - Optimized for production

**For Teams:**
- `team_config.json` - Shared team configuration

### 2. Validate Configuration

```cmd
# Validate Claude Desktop config
python validation_examples/validate_claude_config.py your_config.json

# Validate VS Code config
python validation_examples/validate_vscode_config.py your_config.json
```

### 3. Deploy Configuration

```cmd
# Deploy to Claude Desktop
python automation_scripts/deploy_config.py your_config.json --claude

# Deploy to VS Code
python automation_scripts/deploy_config.py your_config.json --vscode
```

### 4. Test Integration

```cmd
# Run integration tests
python automation_scripts/test_integration.py
```

## Environment Variables Reference

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `WINDOWS_CHATGPT_MCP_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WINDOWS_CHATGPT_MCP_TIMEOUT` | Response timeout (seconds) | `30` | `30`, `60`, `120` |
| `WINDOWS_CHATGPT_MCP_DEBUG` | Debug mode | `0` | `0`, `1` |
| `WINDOWS_CHATGPT_MCP_RETRY_COUNT` | Retry attempts | `3` | `1`, `3`, `5` |
| `WINDOWS_CHATGPT_MCP_WINDOW_TITLE` | Window detection pattern | `ChatGPT` | `ChatGPT`, `OpenAI` |

## Troubleshooting

### Common Issues

**Configuration not loading:**
1. Validate JSON syntax
2. Check file paths
3. Verify permissions

**MCP server not starting:**
1. Check Python installation
2. Verify dependencies
3. Review log files

**ChatGPT not detected:**
1. Ensure ChatGPT is running
2. Check window title patterns
3. Verify automation permissions

### Getting Help

1. **Run diagnostics:**
   ```cmd
   python automation_scripts/test_integration.py
   ```

2. **Validate configuration:**
   ```cmd
   python validation_examples/validate_claude_config.py
   ```

3. **Check logs:**
   - Review MCP server logs
   - Check Claude Desktop logs
   - Examine VS Code output

## Contributing

To contribute new examples or scripts:

1. Follow existing naming conventions
2. Include comprehensive documentation
3. Add validation and error handling
4. Test across different environments
5. Update this README

## Support

For support with examples and configurations:

- Check the main [documentation](../docs/)
- Review [troubleshooting guide](../TROUBLESHOOTING.md)
- Create GitHub issues for bugs
- Use discussions for questions

---

**Need help getting started?** Try the [Quick Start Guide](#quick-start-guide) or run the integration tests to validate your setup.