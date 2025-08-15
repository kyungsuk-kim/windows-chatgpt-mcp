# Windows ChatGPT MCP Tool - User Guide

This comprehensive guide covers everything you need to know about using the Windows ChatGPT MCP Tool effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Available Tools](#available-tools)
4. [Common Usage Scenarios](#common-usage-scenarios)
5. [Advanced Features](#advanced-features)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

Before using the Windows ChatGPT MCP Tool, ensure you have:

- ✅ Windows 11 (or Windows 10 1903+)
- ✅ Python 3.8 or higher
- ✅ ChatGPT desktop application installed and running
- ✅ Claude Desktop OR VS Code with Claude CLI extension
- ✅ Windows ChatGPT MCP Tool installed

### Quick Setup Verification

1. **Verify ChatGPT is running:**
   - Open ChatGPT desktop application
   - Ensure it's logged in and ready to use

2. **Test MCP server:**
   ```cmd
   python -m src.mcp_server --test
   ```

3. **Check Claude integration:**
   - Open Claude Desktop or VS Code
   - Look for "windows-chatgpt" in available tools

## Basic Usage

### Sending Messages to ChatGPT

The primary function is sending messages to ChatGPT through Claude:

**In Claude Desktop:**
```
Can you use the ChatGPT tool to ask: "What are the benefits of renewable energy?"
```

**In VS Code Claude CLI:**
```
@chatgpt What are the benefits of renewable energy?
```

### Getting Responses

The tool automatically:
1. Focuses the ChatGPT window
2. Sends your message
3. Waits for ChatGPT's response
4. Captures and returns the response to Claude

## Available Tools

### 1. send_message

**Purpose:** Send a message to ChatGPT and get the response

**Parameters:**
- `message` (required): The message to send to ChatGPT
- `timeout` (optional): Timeout in seconds (default: 30)

**Example Usage:**
```
Use the send_message tool with:
- message: "Explain quantum computing in simple terms"
- timeout: 45
```

**Response:** Returns ChatGPT's complete response as text

### 2. get_conversation_history

**Purpose:** Retrieve the current conversation history from ChatGPT

**Parameters:**
- `limit` (optional): Maximum number of messages to retrieve (default: 10)

**Example Usage:**
```
Use get_conversation_history to see the last 5 messages
```

**Response:** Returns JSON-formatted conversation history

### 3. reset_conversation

**Purpose:** Start a new conversation in ChatGPT

**Parameters:** None

**Example Usage:**
```
Use reset_conversation to start fresh
```

**Response:** Confirmation that the conversation was reset

### 4. get_debug_info

**Purpose:** Get debugging information and performance metrics

**Parameters:**
- `include_metrics` (optional): Include performance data (default: true)
- `include_logs` (optional): Include recent log entries (default: false)

**Example Usage:**
```
Use get_debug_info to check server status
```

**Response:** Detailed server and performance information

## Common Usage Scenarios

### Scenario 1: Research and Analysis

**Use Case:** You want ChatGPT to research a topic while working in Claude

**Steps:**
1. Ask Claude to use ChatGPT for research
2. Review ChatGPT's response
3. Ask Claude to analyze or summarize the information

**Example:**
```
Claude: Use ChatGPT to research the latest developments in AI safety, then summarize the key points for me.
```

### Scenario 2: Code Review and Debugging

**Use Case:** Get a second opinion on code from ChatGPT

**Steps:**
1. Share your code with Claude
2. Ask Claude to get ChatGPT's perspective
3. Compare both AI responses

**Example:**
```
Claude: Here's my Python function [code]. Can you ask ChatGPT to review it for potential issues?
```

### Scenario 3: Creative Writing Collaboration

**Use Case:** Collaborate between Claude and ChatGPT on creative projects

**Steps:**
1. Start a story or idea with Claude
2. Ask ChatGPT to continue or provide alternatives
3. Iterate between both AIs

**Example:**
```
Claude: I started this story: [story beginning]. Ask ChatGPT to write the next paragraph, then we'll continue together.
```

### Scenario 4: Technical Problem Solving

**Use Case:** Get multiple perspectives on technical challenges

**Steps:**
1. Describe your problem to Claude
2. Get ChatGPT's solution approach
3. Compare and combine solutions

**Example:**
```
Claude: I'm having trouble with [technical issue]. Can you ask ChatGPT for their approach, then we'll compare solutions?
```

### Scenario 5: Learning and Education

**Use Case:** Use both AIs for comprehensive learning

**Steps:**
1. Ask ChatGPT to explain a concept
2. Ask Claude to provide additional context or examples
3. Create a comprehensive understanding

**Example:**
```
Claude: Ask ChatGPT to explain machine learning algorithms, then help me create a study plan based on their explanation.
```

## Advanced Features

### Conversation Management

**Starting Fresh:**
```
Use reset_conversation before starting a new topic
```

**Tracking History:**
```
Use get_conversation_history to review what's been discussed
```

### Performance Monitoring

**Check Server Health:**
```
Use get_debug_info to monitor performance and identify issues
```

**Optimize Response Times:**
- Use appropriate timeout values
- Monitor performance metrics
- Reset conversations when they become too long

### Error Handling

The tool automatically handles:
- ChatGPT window not found
- Network timeouts
- UI interaction failures
- Response parsing errors

**Manual Recovery:**
1. Ensure ChatGPT is running and visible
2. Check that ChatGPT is ready for input
3. Try resetting the conversation
4. Restart the MCP server if needed

### Customization Options

**Environment Variables:**
```cmd
# Adjust timeout settings
set WINDOWS_CHATGPT_MCP_TIMEOUT=60

# Change log level
set WINDOWS_CHATGPT_MCP_LOG_LEVEL=DEBUG

# Enable debug mode
set WINDOWS_CHATGPT_MCP_DEBUG=1
```

**Configuration File:**
Edit `src/config.py` for advanced customization:
- Window detection patterns
- Automation timing
- Response parsing rules

## Best Practices

### Message Composition

**✅ Do:**
- Be clear and specific in your requests
- Use proper grammar and punctuation
- Break complex requests into smaller parts
- Specify timeout for long operations

**❌ Don't:**
- Send extremely long messages (>2000 characters)
- Use special characters that might interfere with automation
- Send rapid successive messages
- Ignore error messages

### Performance Optimization

**For Better Speed:**
- Keep ChatGPT window visible and unobstructed
- Close unnecessary applications
- Use shorter messages when possible
- Reset conversations periodically

**For Better Reliability:**
- Ensure stable system performance
- Keep ChatGPT updated
- Monitor system resources
- Use appropriate timeout values

### Security Considerations

**Data Privacy:**
- Be aware that messages pass through ChatGPT
- Don't send sensitive personal information
- Consider data retention policies
- Use appropriate privacy settings in ChatGPT

**System Security:**
- Run with minimal required privileges
- Keep all software updated
- Monitor for unusual behavior
- Use antivirus exclusions carefully

### Workflow Integration

**With Claude Desktop:**
- Use natural language to request ChatGPT interactions
- Combine responses from both AIs effectively
- Save important conversations
- Use Claude's analysis capabilities on ChatGPT responses

**With VS Code:**
- Integrate into development workflows
- Use for code review and debugging
- Combine with other VS Code extensions
- Save useful responses as code comments

## Troubleshooting

### Common Issues and Solutions

**Issue: "ChatGPT window not found"**
- Solution: Ensure ChatGPT is running and visible
- Check window title matches expected pattern
- Try clicking on ChatGPT window to focus it

**Issue: "Timeout waiting for response"**
- Solution: Increase timeout value
- Check if ChatGPT is processing a complex request
- Ensure ChatGPT isn't showing error messages

**Issue: "Empty or partial response"**
- Solution: Wait for ChatGPT to finish responding
- Check if response area is visible
- Try scrolling in ChatGPT to see full response

**Issue: "Permission denied for automation"**
- Solution: Run as administrator
- Check Windows privacy settings
- Add Python to antivirus exclusions

### Getting Help

**Debug Information:**
```
Use get_debug_info with include_logs: true to get detailed diagnostics
```

**Log Files:**
Check `logs/windows_chatgpt_mcp.log` for detailed error information

**Community Support:**
- GitHub Issues for bug reports
- Documentation for setup help
- Community discussions for usage tips

### Performance Monitoring

**Regular Health Checks:**
```
Use get_debug_info regularly to monitor:
- Response times
- Error rates
- Memory usage
- Success rates
```

**Optimization Tips:**
- Monitor performance metrics
- Adjust timeout values based on usage patterns
- Reset conversations when they become slow
- Keep system resources available

## Conclusion

The Windows ChatGPT MCP Tool provides a powerful bridge between Claude and ChatGPT, enabling you to leverage the strengths of both AI systems. By following this guide and best practices, you can create efficient workflows that combine the capabilities of both platforms.

Remember to:
- Start with simple use cases and gradually explore advanced features
- Monitor performance and adjust settings as needed
- Keep both ChatGPT and the MCP tool updated
- Refer to troubleshooting guides when issues arise

For additional help, consult the [Setup Guide](SETUP_GUIDE.md), [Troubleshooting Guide](../TROUBLESHOOTING.md), and [API Documentation](API_REFERENCE.md).