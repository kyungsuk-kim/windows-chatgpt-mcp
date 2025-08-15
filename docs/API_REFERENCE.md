# Windows ChatGPT MCP Tool - API Reference

This document provides detailed technical documentation for all MCP tools and their APIs.

## Table of Contents

1. [Overview](#overview)
2. [MCP Protocol Compliance](#mcp-protocol-compliance)
3. [Tool Definitions](#tool-definitions)
4. [Error Handling](#error-handling)
5. [Performance Metrics](#performance-metrics)
6. [Configuration API](#configuration-api)
7. [Integration Examples](#integration-examples)

## Overview

The Windows ChatGPT MCP Tool implements the Model Context Protocol (MCP) to provide seamless integration between Claude clients and ChatGPT on Windows systems. The server exposes four primary tools for interaction.

### Server Information

- **Name:** `windows-chatgpt-mcp`
- **Version:** `1.0.0`
- **Protocol:** MCP (Model Context Protocol)
- **Transport:** stdio
- **Platform:** Windows 11/10

### Capabilities

- Tool execution with parameter validation
- Asynchronous operation handling
- Comprehensive error reporting
- Performance monitoring
- Debug information access

## MCP Protocol Compliance

### Supported MCP Methods

| Method | Description | Status |
|--------|-------------|--------|
| `initialize` | Server initialization | ✅ Supported |
| `list_tools` | List available tools | ✅ Supported |
| `call_tool` | Execute a tool | ✅ Supported |
| `get_prompt` | Get prompt templates | ❌ Not implemented |
| `list_resources` | List available resources | ❌ Not implemented |

### Protocol Version

- **Supported Version:** 1.0
- **Minimum Client Version:** 1.0

## Tool Definitions

### 1. send_message

Sends a message to ChatGPT and returns the response.

#### Schema

```json
{
  "name": "send_message",
  "description": "Send a message to ChatGPT and get the response",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The message to send to ChatGPT",
        "minLength": 1,
        "maxLength": 4000
      },
      "timeout": {
        "type": "number",
        "description": "Timeout in seconds for waiting for response",
        "minimum": 5,
        "maximum": 300,
        "default": 30
      }
    },
    "required": ["message"]
  }
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | Yes | - | Message to send to ChatGPT (1-4000 chars) |
| `timeout` | number | No | 30 | Response timeout in seconds (5-300) |

#### Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "ChatGPT's response text"
    }
  ]
}
```

#### Example Usage

**Request:**
```json
{
  "method": "call_tool",
  "params": {
    "name": "send_message",
    "arguments": {
      "message": "What is the capital of France?",
      "timeout": 45
    }
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "The capital of France is Paris. Paris is not only the political capital but also the cultural and economic center of France..."
    }
  ]
}
```

#### Error Conditions

| Error Type | Condition | HTTP Status | Description |
|------------|-----------|-------------|-------------|
| `ValidationError` | Empty message | 400 | Message cannot be empty |
| `ValidationError` | Invalid timeout | 400 | Timeout must be 5-300 seconds |
| `AutomationError` | ChatGPT not found | 503 | ChatGPT application not running |
| `TimeoutError` | Response timeout | 408 | ChatGPT didn't respond in time |

### 2. get_conversation_history

Retrieves the current conversation history from ChatGPT.

#### Schema

```json
{
  "name": "get_conversation_history",
  "description": "Get the current conversation history from ChatGPT",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "number",
        "description": "Maximum number of messages to retrieve",
        "minimum": 1,
        "maximum": 100,
        "default": 10
      }
    }
  }
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | number | No | 10 | Maximum messages to retrieve (1-100) |

#### Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "[\n  {\n    \"role\": \"user\",\n    \"content\": \"Hello\",\n    \"timestamp\": \"2024-01-15T10:30:00Z\"\n  },\n  {\n    \"role\": \"assistant\",\n    \"content\": \"Hi there!\",\n    \"timestamp\": \"2024-01-15T10:30:05Z\"\n  }\n]"
    }
  ]
}
```

#### Conversation History Format

Each message in the history contains:

```typescript
interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string; // ISO 8601 format
  message_id?: string;
}
```

#### Example Usage

**Request:**
```json
{
  "method": "call_tool",
  "params": {
    "name": "get_conversation_history",
    "arguments": {
      "limit": 5
    }
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "[\n  {\n    \"role\": \"user\",\n    \"content\": \"What is machine learning?\",\n    \"timestamp\": \"2024-01-15T10:25:00Z\"\n  },\n  {\n    \"role\": \"assistant\",\n    \"content\": \"Machine learning is a subset of artificial intelligence...\",\n    \"timestamp\": \"2024-01-15T10:25:10Z\"\n  }\n]"
    }
  ]
}
```

### 3. reset_conversation

Resets the current ChatGPT conversation to start fresh.

#### Schema

```json
{
  "name": "reset_conversation",
  "description": "Reset the current ChatGPT conversation",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

#### Parameters

None required.

#### Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "Conversation reset successfully"
    }
  ]
}
```

#### Example Usage

**Request:**
```json
{
  "method": "call_tool",
  "params": {
    "name": "reset_conversation",
    "arguments": {}
  }
}
```

**Response:**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Conversation reset successfully"
    }
  ]
}
```

### 4. get_debug_info

Retrieves debugging information and performance metrics from the server.

#### Schema

```json
{
  "name": "get_debug_info",
  "description": "Get debugging information and performance metrics",
  "inputSchema": {
    "type": "object",
    "properties": {
      "include_metrics": {
        "type": "boolean",
        "description": "Include performance metrics in the response",
        "default": true
      },
      "include_logs": {
        "type": "boolean",
        "description": "Include recent log entries",
        "default": false
      }
    }
  }
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `include_metrics` | boolean | No | true | Include performance data |
| `include_logs` | boolean | No | false | Include recent log entries |

#### Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"server_info\": {\n    \"name\": \"windows-chatgpt-mcp\",\n    \"version\": \"1.0.0\",\n    \"status\": \"running\"\n  },\n  \"performance_metrics\": {...},\n  \"configuration\": {...}\n}"
    }
  ]
}
```

#### Debug Information Structure

```typescript
interface DebugInfo {
  server_info: {
    name: string;
    version: string;
    status: "running" | "error" | "initializing";
    uptime?: number;
  };
  configuration: {
    log_level: string;
    structured_logging: boolean;
    performance_monitoring: boolean;
    log_directory: string;
  };
  performance_metrics?: {
    overall_stats: PerformanceStats;
    operation_stats: {
      [operation: string]: PerformanceStats;
    };
  };
  error_stats: {
    total_errors: number;
    error_types: { [type: string]: number };
    recent_errors: ErrorInfo[];
  };
  logs?: {
    message: string;
    log_file: string;
  };
}

interface PerformanceStats {
  total_calls: number;
  average_duration: number;
  min_duration: number;
  max_duration: number;
  success_rate: number;
  error_rate: number;
}
```

## Error Handling

### Error Response Format

All errors follow the MCP standard error format:

```json
{
  "error": {
    "code": -32000,
    "message": "Error description",
    "data": {
      "type": "ErrorType",
      "details": "Additional error details",
      "field": "parameter_name",
      "value": "invalid_value"
    }
  }
}
```

### Error Types

#### ValidationError (-32602)

Returned when input parameters are invalid.

**Common Causes:**
- Empty or missing required parameters
- Parameters outside valid ranges
- Invalid parameter types

**Example:**
```json
{
  "error": {
    "code": -32602,
    "message": "Message must be a non-empty string",
    "data": {
      "type": "ValidationError",
      "field": "message",
      "value": ""
    }
  }
}
```

#### AutomationError (-32000)

Returned when Windows automation fails.

**Common Causes:**
- ChatGPT application not running
- Window focus issues
- UI interaction failures

**Example:**
```json
{
  "error": {
    "code": -32000,
    "message": "ChatGPT window not found",
    "data": {
      "type": "AutomationError",
      "operation": "find_window",
      "details": "No window found matching ChatGPT patterns"
    }
  }
}
```

#### ConfigurationError (-32001)

Returned when configuration is invalid or missing.

**Example:**
```json
{
  "error": {
    "code": -32001,
    "message": "Invalid configuration setting",
    "data": {
      "type": "ConfigurationError",
      "setting": "window_timeout",
      "value": -1
    }
  }
}
```

#### TimeoutError (-32002)

Returned when operations exceed timeout limits.

**Example:**
```json
{
  "error": {
    "code": -32002,
    "message": "Operation timed out after 30 seconds",
    "data": {
      "type": "TimeoutError",
      "operation": "wait_for_response",
      "timeout": 30
    }
  }
}
```

### Retry Behavior

The server implements automatic retry for certain operations:

| Operation | Max Retries | Retry Conditions |
|-----------|-------------|------------------|
| `send_message` | 2 | Automation failures, temporary UI issues |
| `get_conversation_history` | 2 | Window focus issues |
| `reset_conversation` | 2 | UI interaction failures |

## Performance Metrics

### Tracked Metrics

The server tracks performance metrics for all operations:

- **Total Calls:** Number of times each tool was called
- **Average Duration:** Mean execution time in seconds
- **Min/Max Duration:** Fastest and slowest execution times
- **Success Rate:** Percentage of successful calls
- **Error Rate:** Percentage of failed calls

### Performance Monitoring

Access performance data using the `get_debug_info` tool:

```json
{
  "performance_metrics": {
    "overall_stats": {
      "total_calls": 150,
      "average_duration": 2.3,
      "min_duration": 0.5,
      "max_duration": 15.2,
      "success_rate": 0.96,
      "error_rate": 0.04
    },
    "operation_stats": {
      "send_message": {
        "total_calls": 120,
        "average_duration": 2.8,
        "success_rate": 0.95
      }
    }
  }
}
```

## Configuration API

### Environment Variables

Configure the server using environment variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WINDOWS_CHATGPT_MCP_LOG_LEVEL` | string | `INFO` | Logging level |
| `WINDOWS_CHATGPT_MCP_TIMEOUT` | number | `30` | Default timeout |
| `WINDOWS_CHATGPT_MCP_DEBUG` | boolean | `false` | Debug mode |
| `WINDOWS_CHATGPT_MCP_WINDOW_TITLE` | string | `ChatGPT` | Window pattern |

### Configuration File

Advanced configuration through `src/config.py`:

```python
class Config:
    # Window detection
    WINDOW_TITLE_PATTERNS = ["ChatGPT", "OpenAI ChatGPT"]
    WINDOW_SEARCH_TIMEOUT = 10
    
    # Automation timing
    CLICK_DELAY = 0.1
    TYPE_DELAY = 0.05
    RESPONSE_POLL_INTERVAL = 0.5
    
    # Message handling
    MAX_MESSAGE_LENGTH = 4000
    USE_CLIPBOARD_FOR_LONG_MESSAGES = True
    CLIPBOARD_THRESHOLD = 500
```

## Integration Examples

### Claude Desktop Integration

**mcp.json Configuration:**
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

### VS Code Integration

**settings.json Configuration:**
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

### Programmatic Usage

**Python Client Example:**
```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def use_chatgpt_tool():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server"],
        cwd="C:/path/to/windows-chatgpt-mcp"
    )
    
    async with ClientSession(server_params) as session:
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools.tools]}")
        
        # Send a message
        result = await session.call_tool(
            "send_message",
            {"message": "Hello, ChatGPT!"}
        )
        print(f"Response: {result.content[0].text}")
```

### Custom Client Implementation

**JavaScript/Node.js Example:**
```javascript
const { spawn } = require('child_process');
const { MCPClient } = require('@modelcontextprotocol/client');

async function createChatGPTClient() {
  const serverProcess = spawn('python', ['-m', 'src.mcp_server'], {
    cwd: 'C:/path/to/windows-chatgpt-mcp',
    stdio: ['pipe', 'pipe', 'inherit']
  });
  
  const client = new MCPClient({
    read: serverProcess.stdout,
    write: serverProcess.stdin
  });
  
  await client.initialize();
  return client;
}

// Usage
const client = await createChatGPTClient();
const result = await client.callTool('send_message', {
  message: 'Explain quantum computing'
});
console.log(result.content[0].text);
```

## Rate Limits and Quotas

### Current Limitations

- **Concurrent Requests:** 1 (sequential processing only)
- **Message Length:** 4000 characters maximum
- **Timeout Range:** 5-300 seconds
- **History Limit:** 100 messages maximum

### Recommended Usage Patterns

- **Batch Operations:** Process multiple requests sequentially
- **Long Messages:** Split into smaller chunks if needed
- **Conversation Management:** Reset conversations periodically
- **Error Handling:** Implement retry logic for transient failures

## Versioning and Compatibility

### API Versioning

- **Current Version:** 1.0.0
- **Compatibility:** Backward compatible within major version
- **Deprecation Policy:** 6-month notice for breaking changes

### Client Compatibility

| Client | Minimum Version | Recommended Version |
|--------|----------------|-------------------|
| Claude Desktop | 1.0.0 | Latest |
| VS Code Claude CLI | 1.0.0 | Latest |
| Custom MCP Clients | MCP 1.0 | MCP 1.0+ |

For the most up-to-date API information, refer to the source code in `src/mcp_server.py` and the MCP protocol specification.