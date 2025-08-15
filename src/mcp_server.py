"""
MCP Server Core - Main MCP protocol handler

This module implements the core MCP server functionality for Windows ChatGPT integration.
It handles MCP protocol communication, request routing, and server lifecycle management.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Sequence
from dataclasses import dataclass
import json

from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .config import ConfigManager
from .windows_automation import WindowsAutomationHandler
from .error_handler import ErrorHandler, handle_mcp_tool_error, with_error_handling, RetryConfig
from .exceptions import ValidationError, ConfigurationError, AutomationError
from .logging_config import (
    setup_logging, get_logger, LoggingConfig, LogLevel,
    log_performance, log_operation, log_mcp_request, log_mcp_response
)


@dataclass
class MCPRequest:
    """Data model for MCP requests"""
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


class WindowsChatGPTMCPServer:
    """
    Main MCP server class for Windows ChatGPT integration.
    
    Handles MCP protocol communication, request routing, and server lifecycle management.
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, 
                 logging_config: Optional[LoggingConfig] = None):
        """
        Initialize the MCP server.
        
        Args:
            config_manager: Configuration manager instance. If None, creates a default one.
            logging_config: Logging configuration. If None, creates a default one.
        """
        self.config_manager = config_manager or ConfigManager()
        self.automation_handler = None
        self.server = Server("windows-chatgpt-mcp")
        
        # Set up comprehensive logging
        if logging_config is None:
            logging_config = LoggingConfig(
                log_level=LogLevel.INFO,
                log_dir="logs",
                enable_performance=True,
                enable_structured=True
            )
        
        self.logging_manager = setup_logging(logging_config)
        self.logger = get_logger(__name__)
        self.error_handler = ErrorHandler(self.logger)
        
        # Log system information
        self.logging_manager.log_system_info()
        
        # Register MCP tools
        self._register_tools()
        
    def _register_tools(self) -> None:
        """Register available MCP tools with the server."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools for the MCP client."""
            return [
                Tool(
                    name="send_message",
                    description="Send a message to ChatGPT and get the response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message to send to ChatGPT"
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Timeout in seconds for waiting for response (optional)",
                                "default": 30
                            }
                        },
                        "required": ["message"]
                    }
                ),
                Tool(
                    name="get_conversation_history",
                    description="Get the current conversation history from ChatGPT",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of messages to retrieve (optional)",
                                "default": 10
                            }
                        }
                    }
                ),
                Tool(
                    name="reset_conversation",
                    description="Reset the current ChatGPT conversation",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_debug_info",
                    description="Get debugging information and performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "include_metrics": {
                                "type": "boolean",
                                "description": "Include performance metrics in the response",
                                "default": True
                            },
                            "include_logs": {
                                "type": "boolean", 
                                "description": "Include recent log entries",
                                "default": False
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool execution requests."""
            start_time = time.time()
            
            # Log the incoming request
            log_mcp_request({
                "method": "call_tool",
                "params": {"name": name, "arguments": arguments}
            })
            
            try:
                if name == "send_message":
                    result = await self._handle_send_message(arguments)
                elif name == "get_conversation_history":
                    result = await self._handle_get_conversation_history(arguments)
                elif name == "reset_conversation":
                    result = await self._handle_reset_conversation(arguments)
                elif name == "get_debug_info":
                    result = await self._handle_get_debug_info(arguments)
                else:
                    raise ValidationError(f"Unknown tool: {name}", field="tool_name", value=name)
                
                # Log successful response
                duration = time.time() - start_time
                log_mcp_response({"result": "success"}, duration)
                
                return result
                    
            except Exception as e:
                # Log error response
                duration = time.time() - start_time
                log_mcp_response({"error": str(e)}, duration)
                
                return await handle_mcp_tool_error(e, name)
    
    @with_error_handling("send_message", retry_config=RetryConfig(max_attempts=2))
    @log_performance("send_message", include_args=True)
    async def _handle_send_message(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle send_message tool requests.
        
        Args:
            arguments: Tool arguments containing message and optional timeout
            
        Returns:
            List of TextContent with the ChatGPT response
        """
        message = arguments.get("message", "")
        timeout = arguments.get("timeout", 30)
        
        # Validate input
        if not message or not isinstance(message, str):
            raise ValidationError("Message must be a non-empty string", field="message", value=message)
        
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValidationError("Timeout must be a positive number", field="timeout", value=timeout)
        
        # Initialize automation handler if not already done
        if not self.automation_handler:
            self.automation_handler = WindowsAutomationHandler(self.config_manager)
        
        # Send message and get response
        response = await self.automation_handler.send_message_and_get_response(
            message, timeout
        )
        
        return [TextContent(
            type="text",
            text=response
        )]
    
    @with_error_handling("get_conversation_history", retry_config=RetryConfig(max_attempts=2))
    @log_performance("get_conversation_history", include_args=True)
    async def _handle_get_conversation_history(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle get_conversation_history tool requests.
        
        Args:
            arguments: Tool arguments containing optional limit
            
        Returns:
            List of TextContent with conversation history
        """
        limit = arguments.get("limit", 10)
        
        # Validate input
        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError("Limit must be a positive integer", field="limit", value=limit)
        
        # Initialize automation handler if not already done
        if not self.automation_handler:
            self.automation_handler = WindowsAutomationHandler(self.config_manager)
        
        # Get conversation history
        history = await self.automation_handler.get_conversation_history(limit)
        
        return [TextContent(
            type="text",
            text=json.dumps(history, indent=2)
        )]
    
    @with_error_handling("reset_conversation", retry_config=RetryConfig(max_attempts=2))
    @log_performance("reset_conversation", include_args=True)
    async def _handle_reset_conversation(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle reset_conversation tool requests.
        
        Args:
            arguments: Tool arguments (empty for this tool)
            
        Returns:
            List of TextContent with reset confirmation
        """
        # Initialize automation handler if not already done
        if not self.automation_handler:
            self.automation_handler = WindowsAutomationHandler(self.config_manager)
        
        # Reset conversation
        success = await self.automation_handler.reset_conversation()
        
        if success:
            return [TextContent(
                type="text",
                text="Conversation reset successfully"
            )]
        else:
            raise AutomationError("Failed to reset conversation", "reset_conversation")
    
    @log_performance("get_debug_info")
    async def _handle_get_debug_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """
        Handle get_debug_info tool requests.
        
        Args:
            arguments: Tool arguments containing options for debug info
            
        Returns:
            List of TextContent with debug information
        """
        include_metrics = arguments.get("include_metrics", True)
        include_logs = arguments.get("include_logs", False)
        
        debug_info = {
            "server_info": {
                "name": "windows-chatgpt-mcp",
                "version": "1.0.0",
                "status": "running"
            },
            "configuration": {
                "log_level": self.logging_manager.config.log_level.name,
                "structured_logging": self.logging_manager.config.enable_structured,
                "performance_monitoring": self.logging_manager.config.enable_performance,
                "log_directory": self.logging_manager.config.log_dir
            }
        }
        
        if include_metrics:
            performance_monitor = self.logging_manager.get_performance_monitor()
            debug_info["performance_metrics"] = {
                "overall_stats": performance_monitor.get_statistics(),
                "operation_stats": {
                    "send_message": performance_monitor.get_statistics("send_message"),
                    "get_conversation_history": performance_monitor.get_statistics("get_conversation_history"),
                    "reset_conversation": performance_monitor.get_statistics("reset_conversation")
                }
            }
        
        if include_logs:
            # Note: In a real implementation, you might want to read recent log entries
            # from the log file. For now, we'll just indicate that logs are available.
            debug_info["logs"] = {
                "message": "Logs are available in the configured log directory",
                "log_file": f"{self.logging_manager.config.log_dir}/windows_chatgpt_mcp.log" if self.logging_manager.config.log_dir else "console only"
            }
        
        # Add error handler statistics
        debug_info["error_stats"] = self.error_handler.get_error_stats()
        
        return [TextContent(
            type="text",
            text=json.dumps(debug_info, indent=2, default=str)
        )]
    
    @with_error_handling("initialize_server")
    @log_performance("initialize_server")
    async def initialize_server(self) -> None:
        """
        Initialize the MCP server and prepare for handling requests.
        
        This method sets up the server configuration and prepares the automation handler.
        """
        self.logger.info("Initializing Windows ChatGPT MCP Server...")
        
        # Load configuration
        await self.config_manager.load_config()
        self.logger.info("Configuration loaded successfully")
        
        # Initialize automation handler
        self.automation_handler = WindowsAutomationHandler(self.config_manager)
        self.logger.info("Windows automation handler initialized")
        
        self.logger.info("MCP Server initialization complete")
    
    @log_performance("run_server")
    async def run_server(self) -> None:
        """
        Run the MCP server using stdio transport.
        
        This method starts the server and handles the main server loop.
        """
        with log_operation("run_mcp_server", self.logger):
            await self.initialize_server()
            
            self.logger.info("Starting MCP server with stdio transport...")
            
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="windows-chatgpt-mcp",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities()
                    )
                )
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the MCP server.
        
        This method cleans up resources and closes connections.
        """
        with log_operation("shutdown_mcp_server", self.logger):
            # Clean up automation handler
            if self.automation_handler:
                await self.automation_handler.cleanup()
            
            # Log performance statistics before shutdown
            performance_monitor = self.logging_manager.get_performance_monitor()
            stats = performance_monitor.get_statistics()
            self.logger.info("Server performance statistics", extra=stats)
            
            # Clean up logging resources
            self.logging_manager.cleanup()
            
            self.logger.info("MCP server shutdown complete")


async def main():
    """Main entry point for the MCP server."""
    server = WindowsChatGPTMCPServer()
    
    try:
        await server.run_server()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, shutting down...")
    except Exception as e:
        print(f"Server error: {str(e)}")
    finally:
        await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())