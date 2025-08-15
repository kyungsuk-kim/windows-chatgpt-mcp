# Complete Setup Guide - Windows ChatGPT MCP Tool

This comprehensive guide covers setting up the Windows ChatGPT MCP Tool with both Claude Desktop and VS Code Claude CLI.

## Quick Start Checklist

- [ ] Windows 11 (or Windows 10 1903+)
- [ ] Python 3.8+ installed
- [ ] ChatGPT desktop application installed
- [ ] Windows ChatGPT MCP Tool installed
- [ ] Claude Desktop OR VS Code with Claude CLI extension

## Installation Overview

### 1. System Preparation

```cmd
# Verify Python installation
python --version
pip --version

# Check Windows version
winver
```

### 2. Install the MCP Tool

#### Option A: Automated Installation
```cmd
git clone https://github.com/example/windows-chatgpt-mcp.git
cd windows-chatgpt-mcp
python scripts/install.py
```

#### Option B: Manual Installation
```cmd
pip install -r requirements.txt
pip install -e .
```

#### Option C: PyPI Installation (when available)
```cmd
pip install windows-chatgpt-mcp
```

### 3. Verify Installation

```cmd
python scripts/verify_dependencies.py
```

## Configuration Quick Reference

### Claude Desktop Configuration

**File**: `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### VS Code Configuration

**File**: `.vscode/settings.json` or User Settings

```json
{
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
  "claude.enableMcp": true,
  "claude.mcpTimeout": 30000
}
```

## Detailed Setup Instructions

### For Claude Desktop Users

👉 **[Follow the detailed Claude Desktop setup guide](CLAUDE_DESKTOP_SETUP.md)**

Key steps:
1. Locate configuration file at `%APPDATA%\Claude\mcp.json`
2. Add MCP server configuration
3. Restart Claude Desktop
4. Test integration

### For VS Code Users

👉 **[Follow the detailed VS Code setup guide](VSCODE_SETUP.md)**

Key steps:
1. Install Claude CLI extension
2. Configure MCP server in settings
3. Restart VS Code
4. Test integration

## Configuration Templates

### Development Setup

For active development and debugging:

```json
{
  "mcpServers": {
    "windows-chatgpt-dev": {
      "command": "python",
      "args": ["-m", "src.mcp_server", "--debug"],
      "cwd": "C:/dev/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/dev/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "60"
      }
    }
  }
}
```

### Production Setup

For stable, production use:

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "windows-chatgpt-mcp",
      "args": [],
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "WARNING",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30",
        "WINDOWS_CHATGPT_MCP_RETRY_COUNT": "2"
      }
    }
  }
}
```

## Environment Variables Reference

| Variable | Description | Default | Values |
|----------|-------------|---------|--------|
| `WINDOWS_CHATGPT_MCP_LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WINDOWS_CHATGPT_MCP_TIMEOUT` | Response timeout (seconds) | `30` | `10-120` |
| `WINDOWS_CHATGPT_MCP_RETRY_COUNT` | Number of retries | `3` | `1-10` |
| `WINDOWS_CHATGPT_MCP_WINDOW_TITLE` | ChatGPT window pattern | `ChatGPT` | Custom regex |
| `WINDOWS_CHATGPT_MCP_DEBUG` | Enable debug mode | `false` | `true`, `false` |

## Validation and Testing

### Automated Validation

```cmd
# Validate all configurations
python scripts/validate_config.py

# Validate specific file
python scripts/validate_config.py %APPDATA%\Claude\mcp.json claude_desktop
python scripts/validate_config.py .vscode/settings.json vscode
```

### Manual Testing

```cmd
# Test MCP server directly
python -m src.mcp_server --test

# Test with verbose output
python -m src.mcp_server --verbose --debug
```

### Integration Testing

1. **Start ChatGPT** desktop application
2. **Open Claude Desktop** or **VS Code**
3. **Send a test message** through Claude
4. **Verify response** from ChatGPT

## Common Configuration Patterns

### Multiple Environments

```json
{
  "mcpServers": {
    "chatgpt-dev": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/dev/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/dev/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG"
      }
    },
    "chatgpt-prod": {
      "command": "windows-chatgpt-mcp",
      "args": [],
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

### Team Configuration

Create a shared configuration template:

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "${env:TEAM_MCP_PATH}/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "${env:TEAM_MCP_PATH}/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "${env:MCP_LOG_LEVEL}"
      }
    }
  }
}
```

Team members set environment variables:
```cmd
set TEAM_MCP_PATH=C:\shared\tools
set MCP_LOG_LEVEL=INFO
```

## Troubleshooting Quick Fixes

### Issue: MCP Server Not Found

```cmd
# Check if Python can find the module
python -c "import src.mcp_server; print('OK')"

# Check paths
echo %PYTHONPATH%
```

### Issue: ChatGPT Not Detected

```cmd
# List all windows
python -c "import pygetwindow as gw; [print(w.title) for w in gw.getAllWindows() if 'chat' in w.title.lower()]"
```

### Issue: Permission Denied

```cmd
# Run as administrator
# Check antivirus exclusions
# Verify file permissions
```

### Issue: Configuration Not Loading

```cmd
# Validate JSON syntax
python -m json.tool %APPDATA%\Claude\mcp.json

# Check file location
dir %APPDATA%\Claude\
```

## Performance Optimization

### Reduce Startup Time

```json
{
  "env": {
    "WINDOWS_CHATGPT_MCP_CACHE_WINDOWS": "true",
    "WINDOWS_CHATGPT_MCP_FAST_START": "true"
  }
}
```

### Optimize for Large Messages

```json
{
  "env": {
    "WINDOWS_CHATGPT_MCP_USE_CLIPBOARD": "true",
    "WINDOWS_CHATGPT_MCP_CHUNK_SIZE": "1000"
  }
}
```

## Security Considerations

### Secure Configuration

- Use absolute paths to prevent path injection
- Set appropriate log levels to avoid sensitive data logging
- Consider running with limited user privileges
- Add antivirus exclusions carefully

### Example Secure Configuration

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "C:/Python39/python.exe",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/Program Files/WindowsChatGPTMCP",
      "env": {
        "PYTHONPATH": "C:/Program Files/WindowsChatGPTMCP/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

## Backup and Recovery

### Backup Configuration

```cmd
# Backup Claude Desktop config
copy "%APPDATA%\Claude\mcp.json" "mcp_backup_%date%.json"

# Backup VS Code settings
copy ".vscode\settings.json" "vscode_backup_%date%.json"
```

### Recovery

```cmd
# Restore from backup
copy "mcp_backup_YYYY-MM-DD.json" "%APPDATA%\Claude\mcp.json"
```

## Next Steps

After successful setup:

1. **Read the usage documentation** in the main README
2. **Explore advanced features** and customization options
3. **Set up monitoring** for production environments
4. **Join the community** for support and updates

## Getting Help

- **Documentation**: [README.md](../README.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- **Issues**: GitHub Issues page
- **Community**: Project discussions

## Quick Reference Commands

```cmd
# Installation
python scripts/install.py

# Validation
python scripts/validate_config.py

# Testing
python -m src.mcp_server --test

# Debug mode
python -m src.mcp_server --debug --verbose

# Dependency check
python scripts/verify_dependencies.py
```