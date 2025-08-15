# VS Code Claude CLI Setup Guide

This guide walks you through configuring the Windows ChatGPT MCP Tool with VS Code Claude CLI extension on Windows 11.

## Prerequisites

Before starting, ensure you have:

- [ ] Windows ChatGPT MCP Tool installed (see [INSTALL.md](../INSTALL.md))
- [ ] VS Code installed
- [ ] Claude CLI extension installed in VS Code
- [ ] ChatGPT desktop application installed
- [ ] Python 3.8+ with the MCP tool dependencies

## Step 1: Install Claude CLI Extension

### From VS Code Marketplace

1. **Open VS Code**
2. **Go to Extensions** (Ctrl+Shift+X)
3. **Search for "Claude CLI"**
4. **Install the official Claude extension**
5. **Reload VS Code** if prompted

### Verify Installation

1. **Open Command Palette** (Ctrl+Shift+P)
2. **Type "Claude"** - you should see Claude-related commands
3. **Check the status bar** for Claude indicators

## Step 2: Choose Your Configuration Method

### Method A: User Settings (Global Configuration)

This applies to all VS Code workspaces.

**File Location**: `%APPDATA%\Code\User\settings.json`

### Method B: Workspace Settings (Project-Specific)

This applies only to the current workspace.

**File Location**: `.vscode/settings.json` in your workspace root

## Step 3: Configure MCP Server

### Basic User Settings Configuration

Open VS Code User Settings:

1. **Open Command Palette** (Ctrl+Shift+P)
2. **Type "Preferences: Open Settings (JSON)"**
3. **Add the MCP configuration**:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 30000
}
```

### Workspace Settings Configuration

Create or edit `.vscode/settings.json` in your workspace:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "${workspaceFolder}/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 45000
}
```

### Pip Installation Configuration

If you installed via pip:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "windows-chatgpt-mcp",
      "args": [],
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 30000
}
```

## Step 4: VS Code Claude Settings

### Essential Claude Settings

| Setting | Description | Default | Recommended |
|---------|-------------|---------|-------------|
| `claude.enableMcp` | Enable MCP support | `false` | `true` |
| `claude.mcpTimeout` | MCP timeout (milliseconds) | `30000` | `30000-60000` |
| `claude.autoStart` | Auto-start MCP servers | `true` | `true` |
| `claude.logLevel` | Claude extension log level | `info` | `info` or `debug` |

### Complete Configuration Example

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/Users/YourUsername/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/Users/YourUsername/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "45",
        "WINDOWS_CHATGPT_MCP_RETRY_COUNT": "3"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 45000,
  "claude.autoStart": true,
  "claude.logLevel": "info",
  "claude.maxTokens": 4096
}
```

## Step 5: Workspace-Specific Setup

### Multi-Root Workspaces

For multi-root workspaces, add to the workspace configuration file:

```json
{
  "folders": [
    {
      "path": "./project1"
    },
    {
      "path": "./project2"
    }
  ],
  "settings": {
    "claude.mcpServers": {
      "windows-chatgpt": {
        "command": "python",
        "args": ["-m", "src.mcp_server"],
        "cwd": "${workspaceFolder:project1}/windows-chatgpt-mcp",
        "env": {
          "PYTHONPATH": "${workspaceFolder:project1}/windows-chatgpt-mcp/src"
        }
      }
    },
    "claude.enableMcp": true
  }
}
```

### Project Templates

Create a template `.vscode/settings.json` for new projects:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "${workspaceFolder}/../windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/../windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 30000
}
```

## Step 6: Validate Configuration

### Using the Validation Tool

```cmd
python scripts/validate_config.py .vscode/settings.json vscode
```

### Manual Validation

1. **Check JSON Syntax**:
   ```cmd
   python -m json.tool .vscode/settings.json
   ```

2. **Verify VS Code Settings**:
   - Open Command Palette (Ctrl+Shift+P)
   - Type "Preferences: Open Settings (JSON)"
   - Check for syntax errors

3. **Test MCP Server**:
   ```cmd
   cd C:/path/to/your/windows-chatgpt-mcp
   python -m src.mcp_server --test
   ```

## Step 7: Restart and Test

### Restart VS Code

1. **Close all VS Code windows**
2. **Reopen VS Code**
3. **Open your workspace/project**

### Verify MCP Server Connection

1. **Open Command Palette** (Ctrl+Shift+P)
2. **Look for Claude commands**
3. **Check the status bar** for MCP server indicators
4. **Open VS Code Developer Tools** (Help → Toggle Developer Tools) to check for errors

### Test Integration

1. **Open a file** in your workspace
2. **Use Claude CLI** features
3. **Try sending a query** that would use ChatGPT
4. **Check for MCP tool availability**

## Step 8: Advanced Configuration

### Environment-Specific Settings

#### Development Environment

```json
{
  "claude.mcpServers": {
    "windows-chatgpt-dev": {
      "command": "python",
      "args": ["-m", "src.mcp_server", "--debug"],
      "cwd": "${workspaceFolder}/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "60"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 60000,
  "claude.logLevel": "debug"
}
```

#### Production Environment

```json
{
  "claude.mcpServers": {
    "windows-chatgpt-prod": {
      "command": "windows-chatgpt-mcp",
      "args": [],
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "WARNING",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30",
        "WINDOWS_CHATGPT_MCP_RETRY_COUNT": "2"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.mcpTimeout": 30000
}
```

### Conditional Configuration

Use VS Code's conditional settings for different scenarios:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "${workspaceFolder}/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "${config:claude.logLevel}"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.logLevel": "info"
}
```

## Troubleshooting

### Common Issues

#### 1. MCP Server Not Starting

**Symptoms**: Claude CLI doesn't show MCP tools

**Solutions**:
- Check VS Code Developer Console for errors
- Verify Python path and module availability
- Test MCP server manually
- Check file permissions

#### 2. Configuration Not Loading

**Symptoms**: Settings don't seem to take effect

**Solutions**:
- Restart VS Code completely
- Check JSON syntax in settings files
- Verify settings file location
- Check for conflicting settings

#### 3. Path Resolution Issues

**Symptoms**: "Module not found" or "Path not found" errors

**Solutions**:
- Use absolute paths instead of relative paths
- Check workspace folder variables
- Verify PYTHONPATH is correct
- Test paths in terminal

#### 4. Permission Errors

**Symptoms**: Access denied when starting MCP server

**Solutions**:
- Run VS Code as administrator
- Check antivirus settings
- Verify file and directory permissions
- Check Windows UAC settings

### Debug Mode

Enable detailed logging:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server", "--verbose", "--debug"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  },
  "claude.enableMcp": true,
  "claude.logLevel": "debug"
}
```

### Log Files and Debugging

1. **VS Code Developer Console**:
   - Help → Toggle Developer Tools
   - Check Console tab for errors

2. **Claude Extension Logs**:
   - Command Palette → "Claude: Show Logs"

3. **MCP Server Logs**:
   - Check the working directory for log files
   - Enable debug mode for detailed output

## Integration with Other Tools

### Git Integration

Add VS Code settings to your `.gitignore` if they contain sensitive paths:

```gitignore
.vscode/settings.json
```

Or create a template:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "${env:WINDOWS_CHATGPT_MCP_PATH}",
      "env": {
        "PYTHONPATH": "${env:WINDOWS_CHATGPT_MCP_PATH}/src"
      }
    }
  },
  "claude.enableMcp": true
}
```

### Docker Integration

For containerized development:

```json
{
  "claude.mcpServers": {
    "windows-chatgpt": {
      "command": "docker",
      "args": ["run", "--rm", "-v", "${workspaceFolder}:/workspace", "windows-chatgpt-mcp"],
      "cwd": "${workspaceFolder}",
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO"
      }
    }
  },
  "claude.enableMcp": true
}
```

## Next Steps

After successful setup:

1. **Test with various file types** in your workspace
2. **Explore Claude CLI features** with ChatGPT integration
3. **Set up team configurations** if working in a team
4. **Configure additional MCP servers** if needed

For more information, see:
- [Main README](../README.md)
- [Claude Desktop Setup Guide](CLAUDE_DESKTOP_SETUP.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)