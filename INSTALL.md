# Windows ChatGPT MCP Tool - Installation Guide

This guide provides comprehensive instructions for installing and configuring the Windows ChatGPT MCP Tool on Windows 11 systems.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Installation Methods](#installation-methods)
4. [Post-Installation Verification](#post-installation-verification)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

## System Requirements

### Operating System
- **Windows 11** (recommended)
- **Windows 10** (version 1903 or later, may have limited support)

### Software Requirements
- **Python 3.8 or higher**
  - Download from [python.org](https://www.python.org/downloads/)
  - Ensure "Add Python to PATH" is checked during installation
- **ChatGPT Desktop Application**
  - Download from the official ChatGPT website
  - Must be installed and accessible
- **Claude Desktop** or **VS Code with Claude CLI**
  - For Claude Desktop: Download from Anthropic
  - For VS Code: Install Claude CLI extension

### Hardware Requirements
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 500MB free space
- **Display**: 1920x1080 or higher resolution recommended

## Pre-Installation Checklist

Before installing, ensure you have:

- [ ] Windows 11 or compatible Windows 10 version
- [ ] Python 3.8+ installed with pip
- [ ] ChatGPT desktop application installed
- [ ] Administrator privileges (for some installation steps)
- [ ] Stable internet connection
- [ ] Antivirus software configured to allow Python automation

### Verify Python Installation

Open Command Prompt or PowerShell and run:

```cmd
python --version
pip --version
```

You should see Python 3.8+ and pip version information.

## Installation Methods

### Method 1: Automated Installation (Recommended)

1. **Download or Clone the Repository**
   ```cmd
   git clone https://github.com/example/windows-chatgpt-mcp.git
   cd windows-chatgpt-mcp
   ```

2. **Run the Installation Script**
   ```cmd
   python scripts/install.py
   ```

   The script will:
   - Check system prerequisites
   - Install Python dependencies
   - Install the package
   - Verify the installation
   - Create convenient shortcuts

3. **Follow the on-screen instructions** for any additional setup steps.

### Method 2: Manual Installation

1. **Download the Repository**
   ```cmd
   git clone https://github.com/example/windows-chatgpt-mcp.git
   cd windows-chatgpt-mcp
   ```

2. **Install Dependencies**
   ```cmd
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install the Package**
   ```cmd
   pip install -e .
   ```

4. **Verify Installation**
   ```cmd
   python scripts/verify_dependencies.py
   ```

### Method 3: PyPI Installation (When Available)

```cmd
pip install windows-chatgpt-mcp
```

## Post-Installation Verification

### 1. Run Dependency Verification

```cmd
python scripts/verify_dependencies.py
```

This will check:
- Python version compatibility
- Required packages installation
- ChatGPT application detection
- Windows automation permissions

### 2. Test Basic Functionality

```cmd
python -m src.mcp_server --test
```

### 3. Check Package Import

```cmd
python -c "import src.mcp_server; print('Installation successful!')"
```

## Configuration

### 1. ChatGPT Application Setup

1. **Install ChatGPT Desktop App**
   - Download from the official ChatGPT website
   - Complete the installation process
   - Sign in to your ChatGPT account

2. **Configure ChatGPT Settings**
   - Ensure the application is set to start with Windows (optional)
   - Configure any accessibility settings if needed

### 2. Claude Desktop Configuration

1. **Locate Claude Desktop Configuration**
   - Configuration file is typically at: `%APPDATA%\Claude\mcp.json`

2. **Add MCP Server Configuration**
   ```json
   {
     "mcpServers": {
       "windows-chatgpt": {
         "command": "python",
         "args": ["-m", "src.mcp_server"],
         "cwd": "C:\\path\\to\\windows-chatgpt-mcp",
         "env": {
           "PYTHONPATH": "C:\\path\\to\\windows-chatgpt-mcp\\src"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the new configuration.

### 3. VS Code Claude CLI Configuration

1. **Install Claude CLI Extension** in VS Code

2. **Configure MCP Settings** in VS Code settings or workspace configuration:
   ```json
   {
     "claude.mcpServers": {
       "windows-chatgpt": {
         "command": "python",
         "args": ["-m", "src.mcp_server"],
         "cwd": "C:\\path\\to\\windows-chatgpt-mcp"
       }
     }
   }
   ```

## Troubleshooting

### Common Issues and Solutions

#### 1. Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
- Reinstall Python with "Add Python to PATH" checked
- Or use full path: `C:\Python39\python.exe`

#### 2. Permission Denied Errors
**Error**: Permission denied when installing packages

**Solution**:
- Run Command Prompt as Administrator
- Or use: `pip install --user -r requirements.txt`

#### 3. ChatGPT Not Detected
**Error**: ChatGPT application not found

**Solution**:
- Ensure ChatGPT desktop app is installed
- Check if it's running in the background
- Verify the application window title matches expected patterns

#### 4. GUI Automation Blocked
**Error**: GUI automation not working

**Solution**:
- Check Windows privacy settings for app permissions
- Disable antivirus real-time protection temporarily during testing
- Ensure no other automation tools are conflicting

#### 5. MCP Connection Issues
**Error**: Claude cannot connect to MCP server

**Solution**:
- Verify the MCP server is running: `python -m src.mcp_server`
- Check configuration file paths and syntax
- Restart Claude Desktop/VS Code after configuration changes

### Advanced Troubleshooting

#### Enable Debug Logging

1. Set environment variable:
   ```cmd
   set WINDOWS_CHATGPT_MCP_DEBUG=1
   ```

2. Run with verbose output:
   ```cmd
   python -m src.mcp_server --verbose
   ```

#### Check System Compatibility

```cmd
python scripts/verify_dependencies.py --detailed
```

#### Reset Configuration

1. Remove existing configuration files
2. Re-run the installation script
3. Reconfigure Claude Desktop/VS Code

### Getting Help

If you encounter issues not covered here:

1. **Check the logs** in the application output
2. **Run the dependency verification** script
3. **Review the troubleshooting section** in README.md
4. **Create an issue** on the project repository with:
   - Your Windows version
   - Python version
   - Complete error messages
   - Steps to reproduce the issue

## Security Considerations

### Antivirus Configuration

Some antivirus software may flag GUI automation as suspicious. You may need to:

1. Add Python and the project directory to antivirus exclusions
2. Allow GUI automation in security settings
3. Temporarily disable real-time protection during installation

### Firewall Settings

The MCP server may need firewall permissions for local communication. Allow Python applications through Windows Firewall if prompted.

### Privacy

This tool:
- Does not store conversation data persistently
- Only accesses ChatGPT through GUI automation
- Communicates locally with Claude applications
- Does not send data to external servers

## Next Steps

After successful installation:

1. **Test the integration** with a simple Claude query
2. **Review the usage documentation** in README.md
3. **Explore example configurations** in the examples/ directory
4. **Consider creating backups** of your configuration files

For detailed usage instructions, see the main [README.md](README.md) file.