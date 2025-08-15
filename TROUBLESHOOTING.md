# Windows ChatGPT MCP Tool - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Windows ChatGPT MCP Tool.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Configuration Issues](#configuration-issues)
4. [Runtime Issues](#runtime-issues)
5. [Performance Issues](#performance-issues)
6. [Advanced Troubleshooting](#advanced-troubleshooting)
7. [Getting Support](#getting-support)

## Quick Diagnostics

### Run the Diagnostic Script

First, run the built-in diagnostic tool:

```cmd
python scripts/verify_dependencies.py
```

This will check:
- System requirements
- Python dependencies
- ChatGPT installation
- Automation permissions

### Check MCP Server Status

Test if the MCP server starts correctly:

```cmd
python -m src.mcp_server --test
```

## Installation Issues

### Issue: Python Not Found

**Symptoms:**
- `'python' is not recognized as an internal or external command`
- Installation script fails to run

**Solutions:**

1. **Verify Python Installation:**
   ```cmd
   where python
   python --version
   ```

2. **Add Python to PATH:**
   - Reinstall Python with "Add Python to PATH" checked
   - Or manually add Python to system PATH

3. **Use Full Python Path:**
   ```cmd
   C:\Python39\python.exe scripts/install.py
   ```

### Issue: Permission Denied During Installation

**Symptoms:**
- `PermissionError: [Errno 13] Permission denied`
- Package installation fails

**Solutions:**

1. **Run as Administrator:**
   - Right-click Command Prompt → "Run as administrator"
   - Re-run installation

2. **Use User Installation:**
   ```cmd
   pip install --user -r requirements.txt
   ```

3. **Check Antivirus:**
   - Temporarily disable real-time protection
   - Add Python directory to exclusions

### Issue: Package Installation Fails

**Symptoms:**
- `pip install` commands fail
- Missing dependencies errors

**Solutions:**

1. **Update pip:**
   ```cmd
   python -m pip install --upgrade pip
   ```

2. **Clear pip cache:**
   ```cmd
   pip cache purge
   ```

3. **Install packages individually:**
   ```cmd
   pip install mcp
   pip install pyautogui
   pip install pygetwindow
   pip install pywin32
   ```

4. **Use alternative package sources:**
   ```cmd
   pip install -i https://pypi.org/simple/ -r requirements.txt
   ```

## Configuration Issues

### Issue: Claude Desktop Cannot Find MCP Server

**Symptoms:**
- MCP server not listed in Claude Desktop
- Connection timeout errors

**Solutions:**

1. **Check Configuration File Location:**
   - Claude Desktop: `%APPDATA%\Claude\mcp.json`
   - Verify file exists and has correct syntax

2. **Validate JSON Syntax:**
   ```cmd
   python -m json.tool %APPDATA%\Claude\mcp.json
   ```

3. **Check File Paths:**
   - Ensure all paths in configuration use forward slashes or escaped backslashes
   - Verify Python executable path is correct

4. **Example Working Configuration:**
   ```json
   {
     "mcpServers": {
       "windows-chatgpt": {
         "command": "python",
         "args": ["-m", "src.mcp_server"],
         "cwd": "C:/path/to/windows-chatgpt-mcp",
         "env": {
           "PYTHONPATH": "C:/path/to/windows-chatgpt-mcp/src"
         }
       }
     }
   }
   ```

### Issue: VS Code Claude CLI Configuration Problems

**Symptoms:**
- MCP server not available in VS Code
- Extension errors

**Solutions:**

1. **Check Extension Installation:**
   - Verify Claude CLI extension is installed and enabled
   - Update to latest version

2. **Review Settings:**
   - Open VS Code settings (Ctrl+,)
   - Search for "claude"
   - Verify MCP server configuration

3. **Workspace vs User Settings:**
   - Try configuring in both workspace and user settings
   - Workspace settings take precedence

## Runtime Issues

### Issue: ChatGPT Application Not Found

**Symptoms:**
- "ChatGPT window not found" errors
- Automation fails to locate ChatGPT

**Solutions:**

1. **Verify ChatGPT is Running:**
   - Start ChatGPT desktop application
   - Ensure it's not minimized to system tray

2. **Check Window Title:**
   - The tool looks for windows containing "ChatGPT"
   - Verify the window title matches expected patterns

3. **Update Window Detection:**
   - Edit `src/config.py` to add custom window titles
   - Add debug logging to see detected windows

4. **Manual Window Detection Test:**
   ```python
   import pygetwindow as gw
   windows = gw.getAllWindows()
   for window in windows:
       if "chatgpt" in window.title.lower():
           print(f"Found: {window.title}")
   ```

### Issue: GUI Automation Not Working

**Symptoms:**
- Mouse/keyboard automation fails
- "Access denied" errors for GUI operations

**Solutions:**

1. **Check Windows Privacy Settings:**
   - Settings → Privacy & Security → App permissions
   - Allow apps to control other apps

2. **Disable Antivirus Interference:**
   - Add Python to antivirus exclusions
   - Temporarily disable real-time protection

3. **Run with Administrator Privileges:**
   - Right-click Command Prompt → "Run as administrator"
   - Start MCP server from elevated prompt

4. **Test Basic Automation:**
   ```python
   import pyautogui
   pyautogui.FAILSAFE = True
   print(pyautogui.position())  # Should print mouse position
   ```

### Issue: Message Sending Fails

**Symptoms:**
- Messages not appearing in ChatGPT
- Timeout errors during message sending

**Solutions:**

1. **Check ChatGPT Interface:**
   - Ensure ChatGPT is ready for input
   - No modal dialogs or loading screens

2. **Adjust Timing Settings:**
   - Increase delays in configuration
   - Edit `src/config.py` timing parameters

3. **Test Manual Input:**
   - Try typing manually in ChatGPT
   - Verify input field is accessible

4. **Use Clipboard Method:**
   - Enable clipboard-based input in configuration
   - May be more reliable for long messages

### Issue: Response Capture Problems

**Symptoms:**
- Empty responses returned
- Partial or corrupted response text

**Solutions:**

1. **Increase Response Timeout:**
   - Edit configuration to wait longer for responses
   - ChatGPT may need more time for complex queries

2. **Check Response Area:**
   - Verify ChatGPT response area is visible
   - Scroll to ensure latest response is in view

3. **Test Response Detection:**
   ```python
   import pyautogui
   import time
   time.sleep(5)  # Switch to ChatGPT window
   screenshot = pyautogui.screenshot()
   screenshot.save("debug_screenshot.png")
   ```

## Performance Issues

### Issue: Slow Response Times

**Symptoms:**
- Long delays between request and response
- Timeouts during operation

**Solutions:**

1. **Optimize Timing Settings:**
   - Reduce unnecessary delays
   - Tune automation timing parameters

2. **Check System Resources:**
   - Monitor CPU and memory usage
   - Close unnecessary applications

3. **Update Dependencies:**
   ```cmd
   pip install --upgrade pyautogui pygetwindow
   ```

### Issue: High CPU Usage

**Symptoms:**
- Python process consuming high CPU
- System becomes sluggish

**Solutions:**

1. **Add Sleep Delays:**
   - Increase delays between automation steps
   - Reduce polling frequency

2. **Optimize Window Detection:**
   - Cache window handles
   - Reduce frequency of window searches

3. **Profile Performance:**
   ```cmd
   python -m cProfile -o profile.stats -m src.mcp_server
   ```

## Advanced Troubleshooting

### Enable Debug Logging

1. **Set Environment Variables:**
   ```cmd
   set WINDOWS_CHATGPT_MCP_DEBUG=1
   set WINDOWS_CHATGPT_MCP_LOG_LEVEL=DEBUG
   ```

2. **Run with Verbose Output:**
   ```cmd
   python -m src.mcp_server --verbose --debug
   ```

3. **Check Log Files:**
   - Logs are typically in `logs/` directory
   - Review for error messages and timing information

### Network and Firewall Issues

1. **Check Firewall Settings:**
   - Allow Python through Windows Firewall
   - Check for corporate firewall restrictions

2. **Test Local Connections:**
   ```cmd
   netstat -an | findstr :8080
   ```

3. **Verify MCP Protocol:**
   - Test with minimal MCP client
   - Check protocol version compatibility

### System-Specific Issues

#### Windows 11 Specific

1. **Check Windows 11 Security Features:**
   - Windows Defender Application Guard
   - Core isolation settings

2. **Verify Compatibility Mode:**
   - Right-click Python executable
   - Properties → Compatibility → Run in compatibility mode

#### Multiple Monitor Setups

1. **Screen Coordinate Issues:**
   - Test on primary monitor only
   - Adjust coordinate calculations for multi-monitor

2. **DPI Scaling Problems:**
   - Check Windows display scaling settings
   - May need DPI-aware automation settings

### Memory and Resource Issues

1. **Monitor Memory Usage:**
   ```cmd
   tasklist | findstr python
   ```

2. **Check for Memory Leaks:**
   - Run for extended periods
   - Monitor memory growth over time

3. **Optimize Resource Usage:**
   - Implement proper cleanup in automation code
   - Use context managers for resources

## Getting Support

### Before Requesting Support

1. **Run Full Diagnostics:**
   ```cmd
   python scripts/verify_dependencies.py --detailed
   ```

2. **Collect System Information:**
   ```cmd
   systeminfo > system_info.txt
   python --version > python_info.txt
   pip list > pip_packages.txt
   ```

3. **Gather Error Logs:**
   - Enable debug logging
   - Reproduce the issue
   - Collect all log output

### Creating a Support Request

Include the following information:

1. **System Details:**
   - Windows version and build
   - Python version
   - Package versions

2. **Problem Description:**
   - Exact error messages
   - Steps to reproduce
   - Expected vs actual behavior

3. **Configuration:**
   - MCP configuration files
   - Any custom settings

4. **Diagnostic Output:**
   - Results from verify_dependencies.py
   - Debug logs
   - Screenshots if relevant

### Community Resources

- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** Check README.md for updates
- **Examples:** Review example configurations

### Emergency Workarounds

If you need immediate functionality:

1. **Use Manual Mode:**
   - Disable automation temporarily
   - Use copy-paste workflow

2. **Alternative Tools:**
   - Consider other MCP servers
   - Use direct ChatGPT web interface

3. **Rollback:**
   - Revert to previous working version
   - Restore backup configurations

Remember to test any workarounds thoroughly before relying on them in production environments.