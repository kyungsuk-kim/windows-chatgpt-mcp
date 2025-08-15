# Windows ChatGPT MCP Tool

A Model Context Protocol (MCP) server that enables Claude Desktop and VS Code Claude CLI to interact with ChatGPT on Windows 11 systems.

## Overview

This tool provides a bridge between Claude and ChatGPT on Windows, allowing you to leverage ChatGPT functionality within your Claude workflow through the MCP protocol. Get the best of both AI systems by combining Claude's analytical capabilities with ChatGPT's knowledge and conversational abilities.

### Key Features

- 🔗 **Seamless Integration** - Connect Claude with ChatGPT through MCP protocol
- 🪟 **Windows Native** - Optimized for Windows 11/10 with robust automation
- 🛠️ **Multiple Tools** - Send messages, manage conversations, get debug info
- 📊 **Performance Monitoring** - Built-in metrics and logging
- 🔧 **Easy Configuration** - Works with Claude Desktop and VS Code
- 🛡️ **Error Handling** - Comprehensive error recovery and retry logic

## Quick Start

### Prerequisites

- ✅ Windows 11 (or Windows 10 1903+)
- ✅ Python 3.8 or higher
- ✅ ChatGPT desktop application
- ✅ Claude Desktop OR VS Code with Claude CLI extension

### Installation

#### Option 1: Pip Installation (Recommended)

```cmd
pip install windows-chatgpt-mcp
```

#### Option 2: Standalone Executable

1. Download `windows-chatgpt-mcp.exe` from the [releases page](https://github.com/kyungsuk-kim/windows-chatgpt-mcp/releases)
2. Place the executable in your desired directory
3. Run directly without Python installation required

#### Option 3: Development Installation

1. **Clone the repository:**
   ```cmd
   git clone https://github.com/kyungsuk-kim/windows-chatgpt-mcp.git
   cd windows-chatgpt-mcp
   ```

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Install the package:**
   ```cmd
   pip install -e .
   ```

4. **Verify installation:**
   ```cmd
   python -m src.mcp_server --test
   ```

### Configuration

#### For Claude Desktop

Create or edit `%APPDATA%\Claude\mcp.json`:

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

#### For VS Code Claude CLI

Add to your VS Code settings:

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
  }
}
```

## Usage

### Basic Usage

Once configured, you can use ChatGPT through Claude:

```
You: Can you use the ChatGPT tool to ask: "What are the benefits of renewable energy?"

Claude: I'll send that question to ChatGPT for you.

[Uses send_message tool]

ChatGPT Response: Renewable energy offers numerous benefits including...

Claude: Based on ChatGPT's response, I can also add that...
```

### Available Tools

| Tool | Description | Usage |
|------|-------------|-------|
| `send_message` | Send a message to ChatGPT | Ask Claude to send any question or request |
| `get_conversation_history` | Get recent ChatGPT messages | "Show me the last 5 ChatGPT messages" |
| `reset_conversation` | Start fresh in ChatGPT | "Reset the ChatGPT conversation" |
| `get_debug_info` | Server diagnostics | "Get debug info from the ChatGPT tool" |

### Common Use Cases

- **Research & Analysis** - Get multiple AI perspectives on complex topics
- **Code Review** - Have both AIs review your code for comprehensive feedback
- **Creative Writing** - Collaborate between AIs for enhanced creativity
- **Problem Solving** - Combine analytical approaches from both systems
- **Learning** - Use both AIs for comprehensive educational content

## Documentation

- 📖 **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage instructions
- 🔧 **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed installation and configuration
- 📚 **[API Reference](docs/API_REFERENCE.md)** - Technical API documentation
- ❓ **[FAQ](docs/FAQ.md)** - Frequently asked questions
- 🎯 **[Usage Scenarios](docs/USAGE_SCENARIOS.md)** - Real-world examples
- 🔍 **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

## Configuration Examples

### Development Setup

```json
{
  "mcpServers": {
    "chatgpt-dev": {
      "command": "python",
      "args": ["-m", "src.mcp_server", "--debug"],
      "cwd": "C:/dev/windows-chatgpt-mcp",
      "env": {
        "WINDOWS_CHATGPT_MCP_LOG_LEVEL": "DEBUG",
        "WINDOWS_CHATGPT_MCP_TIMEOUT": "60"
      }
    }
  }
}
```

### Production Setup

```json
{
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
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WINDOWS_CHATGPT_MCP_LOG_LEVEL` | `INFO` | Logging verbosity |
| `WINDOWS_CHATGPT_MCP_TIMEOUT` | `30` | Response timeout (seconds) |
| `WINDOWS_CHATGPT_MCP_DEBUG` | `false` | Enable debug mode |
| `WINDOWS_CHATGPT_MCP_WINDOW_TITLE` | `ChatGPT` | Window detection pattern |

## Troubleshooting

### Common Issues

**ChatGPT not found:**
- Ensure ChatGPT desktop app is running and visible
- Check window title matches expected pattern

**Permission denied:**
- Run as administrator
- Check Windows privacy settings for app control

**Timeout errors:**
- Increase timeout value in configuration
- Ensure stable internet connection

**For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

## Performance

The tool includes comprehensive performance monitoring:

- Response time tracking
- Success/failure rates
- Error categorization
- Resource usage monitoring

Access performance data using the `get_debug_info` tool.

## Security

- Messages are processed locally through ChatGPT desktop app
- No data is stored permanently by the MCP server
- Follows Windows security best practices
- Configurable logging levels to protect sensitive information

## Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for detailed information.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `python run_tests.py`
5. Submit a pull request

### Development Setup

```cmd
# Clone your fork
git clone https://github.com/yourusername/windows-chatgpt-mcp.git
cd windows-chatgpt-mcp

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

For detailed contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

### Getting Help

- 📖 **Documentation** - Comprehensive guides in the [docs/](docs/) directory
- 🐛 **Bug Reports** - Report issues on [GitHub Issues](https://github.com/example/windows-chatgpt-mcp/issues)
- 💬 **Discussions** - Ask questions in [GitHub Discussions](https://github.com/example/windows-chatgpt-mcp/discussions)
- 🔍 **Troubleshooting** - Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

### Community

- **GitHub Repository**: [windows-chatgpt-mcp](https://github.com/example/windows-chatgpt-mcp)
- **Issue Tracker**: [Report bugs and request features](https://github.com/example/windows-chatgpt-mcp/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/example/windows-chatgpt-mcp/discussions)

### Professional Support

For enterprise support, custom integrations, or consulting services, please contact the maintainers through GitHub.

## Distribution

### Available Packages

The Windows ChatGPT MCP Tool is distributed in multiple formats:

- **Wheel Package**: `windows_chatgpt_mcp-1.0.0-py3-none-any.whl` - Standard Python package
- **Source Distribution**: `windows_chatgpt_mcp-1.0.0.tar.gz` - Source code archive
- **Standalone Executable**: `windows-chatgpt-mcp.exe` - No Python installation required

### Building from Source

To build your own distribution packages:

```cmd
# Build all packages
python build_dist.py

# Build only wheel package
python build_dist.py --wheel-only

# Build only standalone executable
python build_dist.py --exe-only
```

For detailed build instructions, see [DISTRIBUTION.md](DISTRIBUTION.md).

## Roadmap

### Version 1.1 (Planned)
- [ ] Image and file attachment support
- [ ] Enhanced error recovery mechanisms
- [ ] Performance optimizations

### Version 1.2 (Future)
- [ ] Multiple ChatGPT account support
- [ ] Enhanced conversation management
- [ ] Additional automation features
- [ ] Configuration GUI

### Long-term Goals
- [ ] Cross-platform support (macOS, Linux)
- [ ] Plugin system for extensibility
- [ ] Advanced AI workflow automation

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the Model Context Protocol (MCP) standard
- Uses Windows automation libraries for ChatGPT integration
- Inspired by the macOS ChatGPT MCP tool

---

**Ready to get started?** Follow the [Setup Guide](docs/SETUP_GUIDE.md) for detailed installation instructions.