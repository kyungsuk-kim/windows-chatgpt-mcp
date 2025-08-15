# Claude Desktop Setup Guide

This guide walks you through configuring the Windows ChatGPT MCP Tool with Claude Desktop on Windows 11.

## Prerequisites

Before starting, ensure you have:

- [ ] Windows ChatGPT MCP Tool installed (see [INSTALL.md](../INSTALL.md))
- [ ] Claude Desktop application installed
- [ ] ChatGPT desktop application installed
- [ ] Python 3.8+ with the MCP tool dependencies

## Step 1: Locate Claude Desktop Configuration

Claude Desktop stores its configuration in a JSON file. The location depends on your installation:

### Standard Installation
```
%APPDATA%\Claude\mcp.json
```

### Alternative Locations
If the above doesn't exist, check:
```
%USERPROFILE%\AppData\Roaming\Claude\mcp.json
%LOCALAPPDATA%\Claude\mcp.json
```

### Finding the Configuration Directory

1. **Open File Explorer**
2. **Navigate to the address bar** and type: `%APPDATA%\Claude`
3. **Press Enter**
4. **Look for `mcp.json`** file

If the directory doesn't exist:
1. **Create the directory**: `%APPDATA%\Claude`
2. **Create an empty `mcp.json` file**

## Step 2: Choose Your Configuration Method

### Method A: Development Installation (Recommended for Development)

Use this if you installed from source or want to modify the tool.

**Configuration File**: `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30"
      }
    }
  }
}
```

**Important**: Replace `C:/path/to/your/windows-chatgpt-mcp` with the actual path to your installation.

### Method B: Pip Installation

Use this if you installed via pip.

**Configuration File**: `%APPDATA%\Claude\mcp.json`

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "windows-chatgpt-mcp",
      "args": [],
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "INFO",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "30",
        "WINDOWS_CHATGPT_MCP_RETRY_COUNT": "3"
      }
    }
  }
}
```

## Step 3: Configure the MCP Server

### Basic Configuration

The minimal configuration requires:
- `command`: The command to run the MCP server
- `args`: Arguments passed to the command
- `cwd`: Working directory (for development installations)

### Advanced Configuration Options

#### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `WINDOWS_CHATGPT_MCP_LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WINDOWS_CHATGPT_MCP_TIMEOUT` | Response timeout (seconds) | `30` | `45`, `60` |
| `WINDOWS_CHATGPT_MCP_RETRY_COUNT` | Number of retries | `3` | `1`, `5` |
| `WINDOWS_CHATGPT_MCP_WINDOW_TITLE` | ChatGPT window title pattern | `ChatGPT` | Custom pattern |

#### Example with All Options

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/Users/YourUsername/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/Users/YourUsername/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "45",
        "WINDOWS_CHATGPT_MCP_RETRY_COUNT": "5",
        "WINDOWS_CHATGPT_MCP_WINDOW_TITLE": "ChatGPT"
      }
    }
  }
}
```

## Step 4: Validate Your Configuration

### Using the Validation Tool

Run the configuration validator:

```cmd
python scripts/validate_config.py
```

This will check:
- JSON syntax
- Required fields
- Path existence
- Environment variable values

### Manual Validation

1. **Check JSON Syntax**:
   ```cmd
   python -m json.tool %APPDATA%\Claude\mcp.json
   ```

2. **Verify Paths**:
   - Ensure the `cwd` path exists
   - Check that Python can find the module

3. **Test MCP Server**:
   ```cmd
   cd C:/path/to/your/windows-chatgpt-mcp
   python -m src.mcp_server --test
   ```

## Step 5: Restart Claude Desktop

1. **Close Claude Desktop** completely
2. **Wait a few seconds**
3. **Restart Claude Desktop**
4. **Check for the MCP server** in the available tools

## Step 6: Test the Integration

### Basic Test

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Type a message** that would benefit from ChatGPT integration
4. **Look for MCP tool availability** in the interface

### Verify MCP Server Connection

In Claude Desktop, you should see:
- MCP server listed in available tools
- No connection errors in the status
- Ability to send messages to ChatGPT

## Troubleshooting

### Common Issues

#### 1. MCP Server Not Listed

**Symptoms**: Windows ChatGPT MCP server doesn't appear in Claude Desktop

**Solutions**:
- Check configuration file location and syntax
- Verify all paths in the configuration
- Restart Claude Desktop
- Check Claude Desktop logs

#### 2. Connection Timeout

**Symptoms**: MCP server appears but times out when used

**Solutions**:
- Increase timeout in environment variables
- Check if ChatGPT application is running
- Verify Windows automation permissions

#### 3. Path Not Found Errors

**Symptoms**: Errors about missing files or directories

**Solutions**:
- Use absolute paths in configuration
- Check that Python and the MCP tool are accessible
- Verify PYTHONPATH is correct

#### 4. Permission Denied

**Symptoms**: Access denied errors when starting MCP server

**Solutions**:
- Run Claude Desktop as administrator
- Check antivirus settings
- Verify file permissions

### Debug Mode

Enable debug logging for detailed troubleshooting:

```json
{
  "mcpServers": {
    "windows-chatgpt": {
      "command": "python",
      "args": ["-m", "src.mcp_server", "--debug"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Log Files

Check log files for detailed error information:
- Claude Desktop logs: Usually in `%APPDATA%\Claude\logs`
- MCP server logs: In the tool's working directory

## Advanced Configuration

### Multiple ChatGPT Instances

If you need to support multiple ChatGPT windows:

```json
{
  "mcpServers": {
    "windows-chatgpt-1": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_WINDOW_TITLE": "ChatGPT - Window 1"
      }
    },
    "windows-chatgpt-2": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src",
        "WINDOWS_CHATGPT_MCP_WINDOW_TITLE": "ChatGPT - Window 2"
      }
    }
  }
}
```

### Custom Server Names

You can customize the server name in Claude Desktop:

```json
{
  "mcpServers": {
    "my-chatgpt-assistant": {
      "command": "python",
      "args": ["-m", "src.mcp_server"],
      "cwd": "C:/path/to/your/windows-chatgpt-mcp",
      "env": {
        "PYTHONPATH": "C:/path/to/your/windows-chatgpt-mcp/src"
      }
    }
  }
}
```

## Next Steps

After successful setup:

1. **Test basic functionality** with simple queries
2. **Explore advanced features** in the main documentation
3. **Configure VS Code** if you also use Claude CLI there
4. **Set up monitoring** for production use

For more information, see:
- [Main README](../README.md)
- [VS Code Setup Guide](VSCODE_SETUP.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)