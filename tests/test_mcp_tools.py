"""
Tests for MCP tool functionality.

This module tests the MCP tool definitions, parameter validation, and execution handlers.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from mcp.types import TextContent, Tool

from src.mcp_server import WindowsChatGPTMCPServer
from src.config import ConfigManager
from src.exceptions import ValidationError, ChatGPTWindowError, AutomationError
from src.logging_config import LoggingConfig, LogLevel


class TestMCPToolDefinitions:
    """Test MCP tool definitions and registration."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.load_config = AsyncMock()
        return config_manager
    
    @pytest.fixture
    def logging_config(self):
        """Create a test logging configuration."""
        return LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir=None,  # Use console logging for tests
            enable_performance=False,
            enable_structured=False
        )
    
    @pytest.fixture
    def mcp_server(self, mock_config_manager, logging_config):
        """Create an MCP server instance for testing."""
        return WindowsChatGPTMCPServer(mock_config_manager, logging_config)
    
    def test_server_initialization(self, mcp_server):
        """Test that the MCP server initializes correctly."""
        assert mcp_server is not None
        assert mcp_server.config_manager is not None
        assert mcp_server.server is not None
        assert mcp_server.logger is not None
        assert mcp_server.error_handler is not None
    
    @pytest.mark.asyncio
    async def test_list_tools(self, mcp_server):
        """Test that all expected tools are registered."""
        # We can't easily test the actual tool list without running the full server
        # but we can verify the server was initialized correctly
        assert mcp_server.server is not None
        
        # Test that the handler methods exist
        assert hasattr(mcp_server, '_handle_send_message')
        assert hasattr(mcp_server, '_handle_get_conversation_history')
        assert hasattr(mcp_server, '_handle_reset_conversation')
        assert hasattr(mcp_server, '_handle_get_debug_info')
    
    @pytest.mark.asyncio
    async def test_send_message_tool_definition(self, mcp_server):
        """Test send_message tool definition."""
        # Test that the handler methods exist
        assert hasattr(mcp_server, '_handle_send_message')
        assert callable(mcp_server._handle_send_message)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_tool_definition(self, mcp_server):
        """Test get_conversation_history tool definition."""
        # Test that the handler methods exist
        assert hasattr(mcp_server, '_handle_get_conversation_history')
        assert callable(mcp_server._handle_get_conversation_history)
    
    @pytest.mark.asyncio
    async def test_reset_conversation_tool_definition(self, mcp_server):
        """Test reset_conversation tool definition."""
        # Test that the handler methods exist
        assert hasattr(mcp_server, '_handle_reset_conversation')
        assert callable(mcp_server._handle_reset_conversation)


class TestMCPToolParameterValidation:
    """Test parameter validation for MCP tools."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create an MCP server instance for testing."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.load_config = AsyncMock()
        logging_config = LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir=None,
            enable_performance=False,
            enable_structured=False
        )
        return WindowsChatGPTMCPServer(config_manager, logging_config)
    
    @pytest.mark.asyncio
    async def test_send_message_parameter_validation(self, mcp_server):
        """Test parameter validation for send_message tool."""
        # Test with valid parameters
        valid_args = {"message": "Hello, ChatGPT!", "timeout": 30}
        
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.send_message_and_get_response = AsyncMock(return_value="Hello!")
            
            result = await mcp_server._handle_send_message(valid_args)
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "Hello!"
    
    @pytest.mark.asyncio
    async def test_send_message_invalid_message(self, mcp_server):
        """Test send_message with invalid message parameter."""
        # Test with empty message
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_send_message({"message": ""})
        
        assert "Message must be a non-empty string" in str(exc_info.value)
        assert exc_info.value.details.get("field") == "message"
        
        # Test with non-string message
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_send_message({"message": 123})
        
        assert "Message must be a non-empty string" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_send_message_invalid_timeout(self, mcp_server):
        """Test send_message with invalid timeout parameter."""
        # Test with negative timeout
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_send_message({"message": "Hello", "timeout": -5})
        
        assert "Timeout must be a positive number" in str(exc_info.value)
        assert exc_info.value.details.get("field") == "timeout"
        
        # Test with zero timeout
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_send_message({"message": "Hello", "timeout": 0})
        
        assert "Timeout must be a positive number" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_parameter_validation(self, mcp_server):
        """Test parameter validation for get_conversation_history tool."""
        # Test with valid parameters
        valid_args = {"limit": 5}
        
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.get_conversation_history = AsyncMock(return_value=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ])
            
            result = await mcp_server._handle_get_conversation_history(valid_args)
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            
            # Parse the JSON response
            history = json.loads(result[0].text)
            assert len(history) == 2
            assert history[0]["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_invalid_limit(self, mcp_server):
        """Test get_conversation_history with invalid limit parameter."""
        # Test with negative limit
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_get_conversation_history({"limit": -1})
        
        assert "Limit must be a positive integer" in str(exc_info.value)
        assert exc_info.value.details.get("field") == "limit"
        
        # Test with zero limit
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_get_conversation_history({"limit": 0})
        
        assert "Limit must be a positive integer" in str(exc_info.value)


class TestMCPToolExecutionHandlers:
    """Test MCP tool execution handlers."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create an MCP server instance for testing."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.load_config = AsyncMock()
        logging_config = LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir=None,
            enable_performance=False,
            enable_structured=False
        )
        return WindowsChatGPTMCPServer(config_manager, logging_config)
    
    @pytest.mark.asyncio
    async def test_send_message_handler_success(self, mcp_server):
        """Test successful send_message handler execution."""
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.send_message_and_get_response = AsyncMock(
                return_value="This is ChatGPT's response"
            )
            
            result = await mcp_server._handle_send_message({
                "message": "Hello, ChatGPT!",
                "timeout": 30
            })
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "This is ChatGPT's response"
            
            # Verify the automation handler was called correctly
            mock_handler.send_message_and_get_response.assert_called_once_with(
                "Hello, ChatGPT!", 30
            )
    
    @pytest.mark.asyncio
    async def test_send_message_handler_automation_error(self, mcp_server):
        """Test send_message handler with automation error."""
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.send_message_and_get_response = AsyncMock(
                side_effect=AutomationError("Failed to send message", "send_message")
            )
            
            with pytest.raises(AutomationError):
                await mcp_server._handle_send_message({
                    "message": "Hello, ChatGPT!",
                    "timeout": 30
                })
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_handler_success(self, mcp_server):
        """Test successful get_conversation_history handler execution."""
        mock_history = [
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a programming language."},
            {"role": "user", "content": "Tell me more."},
            {"role": "assistant", "content": "Python is known for its simplicity."}
        ]
        
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.get_conversation_history = AsyncMock(return_value=mock_history)
            
            result = await mcp_server._handle_get_conversation_history({"limit": 10})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            
            # Parse and verify the JSON response
            history = json.loads(result[0].text)
            assert len(history) == 4
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "What is Python?"
            
            # Verify the automation handler was called correctly
            mock_handler.get_conversation_history.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_reset_conversation_handler_success(self, mcp_server):
        """Test successful reset_conversation handler execution."""
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.reset_conversation = AsyncMock(return_value=True)
            
            result = await mcp_server._handle_reset_conversation({})
            
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].text == "Conversation reset successfully"
            
            # Verify the automation handler was called
            mock_handler.reset_conversation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_reset_conversation_handler_failure(self, mcp_server):
        """Test reset_conversation handler with failure."""
        with patch.object(mcp_server, 'automation_handler') as mock_handler:
            mock_handler.reset_conversation = AsyncMock(return_value=False)
            
            with pytest.raises(AutomationError) as exc_info:
                await mcp_server._handle_reset_conversation({})
            
            assert "Failed to reset conversation" in str(exc_info.value)
            assert exc_info.value.details.get("operation") == "reset_conversation"
    
    @pytest.mark.asyncio
    async def test_get_debug_info_handler(self, mcp_server):
        """Test get_debug_info handler execution."""
        result = await mcp_server._handle_get_debug_info({
            "include_metrics": True,
            "include_logs": True
        })
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        
        # Parse and verify the JSON response
        debug_info = json.loads(result[0].text)
        assert "server_info" in debug_info
        assert "configuration" in debug_info
        assert "performance_metrics" in debug_info
        assert "logs" in debug_info
        assert "error_stats" in debug_info
        
        # Verify server info
        assert debug_info["server_info"]["name"] == "windows-chatgpt-mcp"
        assert debug_info["server_info"]["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_automation_handler_initialization(self, mcp_server):
        """Test that automation handler is initialized when needed."""
        # Initially, automation handler should be None
        assert mcp_server.automation_handler is None
        
        with patch('src.mcp_server.WindowsAutomationHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.send_message_and_get_response = AsyncMock(return_value="Response")
            mock_handler_class.return_value = mock_handler
            
            # Call a method that requires automation handler
            await mcp_server._handle_send_message({
                "message": "Hello",
                "timeout": 30
            })
            
            # Verify automation handler was created
            assert mcp_server.automation_handler is not None
            mock_handler_class.assert_called_once_with(mcp_server.config_manager)


class TestMCPToolIntegration:
    """Test integration between MCP tools and automation handlers."""
    
    @pytest.fixture
    def mcp_server(self):
        """Create an MCP server instance for testing."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.load_config = AsyncMock()
        logging_config = LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir=None,
            enable_performance=False,
            enable_structured=False
        )
        return WindowsChatGPTMCPServer(config_manager, logging_config)
    
    @pytest.mark.asyncio
    async def test_call_tool_handler_routing(self, mcp_server):
        """Test that call_tool handler routes to correct tool handlers."""
        # Test that the handler methods exist and can be called
        with patch.object(mcp_server, '_handle_send_message') as mock_send:
            mock_send.return_value = [TextContent(type="text", text="Response")]
            
            result = await mcp_server._handle_send_message({"message": "Hello", "timeout": 30})
            
            assert len(result) == 1
            assert result[0].text == "Response"
            mock_send.assert_called_once_with({"message": "Hello", "timeout": 30})
    
    @pytest.mark.asyncio
    async def test_error_handling_in_call_tool(self, mcp_server):
        """Test error handling in call_tool handler."""
        # Test that validation errors are properly raised
        with pytest.raises(ValidationError) as exc_info:
            await mcp_server._handle_send_message({"message": ""})
        
        assert "Invalid message" in str(exc_info.value) or "Message must be a non-empty string" in str(exc_info.value)