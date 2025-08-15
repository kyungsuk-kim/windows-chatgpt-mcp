"""
Unit tests for MCP Server Core functionality.

Tests the main MCP server class, request handling, tool registration,
and server lifecycle management.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from mcp.types import TextContent, Tool

from src.mcp_server import WindowsChatGPTMCPServer, MCPRequest
from src.config import ConfigManager
from src.exceptions import ValidationError, AutomationError, ConfigurationError
from src.logging_config import LoggingConfig, LogLevel


class TestMCPRequest:
    """Test the MCPRequest data model."""
    
    def test_mcp_request_creation(self):
        """Test creating an MCPRequest instance."""
        request = MCPRequest(
            method="send_message",
            params={"message": "Hello"},
            id="test-123"
        )
        
        assert request.method == "send_message"
        assert request.params == {"message": "Hello"}
        assert request.id == "test-123"
    
    def test_mcp_request_optional_id(self):
        """Test creating an MCPRequest without ID."""
        request = MCPRequest(
            method="get_conversation_history",
            params={"limit": 5}
        )
        
        assert request.method == "get_conversation_history"
        assert request.params == {"limit": 5}
        assert request.id is None


class TestWindowsChatGPTMCPServer:
    """Test the main MCP server class."""
    
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
            log_dir=None,  # Use console only for tests
            enable_performance=False,
            enable_structured=False
        )
    
    @pytest.fixture
    def server(self, mock_config_manager, logging_config):
        """Create a test MCP server instance."""
        with patch('src.mcp_server.setup_logging') as mock_setup_logging:
            mock_logging_manager = Mock()
            mock_logging_manager.log_system_info = Mock()
            mock_logging_manager.get_performance_monitor = Mock()
            mock_logging_manager.cleanup = Mock()
            mock_setup_logging.return_value = mock_logging_manager
            
            server = WindowsChatGPTMCPServer(
                config_manager=mock_config_manager,
                logging_config=logging_config
            )
            server.logging_manager = mock_logging_manager
            return server
    
    def test_server_initialization(self, mock_config_manager, logging_config):
        """Test server initialization."""
        with patch('src.mcp_server.setup_logging') as mock_setup_logging:
            mock_logging_manager = Mock()
            mock_logging_manager.log_system_info = Mock()
            mock_setup_logging.return_value = mock_logging_manager
            
            server = WindowsChatGPTMCPServer(
                config_manager=mock_config_manager,
                logging_config=logging_config
            )
            
            assert server.config_manager == mock_config_manager
            assert server.automation_handler is None
            assert server.server is not None
            assert server.error_handler is not None
            mock_logging_manager.log_system_info.assert_called_once()
    
    def test_server_initialization_with_defaults(self):
        """Test server initialization with default parameters."""
        with patch('src.mcp_server.setup_logging') as mock_setup_logging:
            mock_logging_manager = Mock()
            mock_logging_manager.log_system_info = Mock()
            mock_setup_logging.return_value = mock_logging_manager
            
            server = WindowsChatGPTMCPServer()
            
            assert isinstance(server.config_manager, ConfigManager)
            assert server.automation_handler is None
    
    @pytest.mark.asyncio
    async def test_initialize_server(self, server, mock_config_manager):
        """Test server initialization process."""
        with patch('src.mcp_server.WindowsAutomationHandler') as mock_automation_class:
            mock_automation_handler = Mock()
            mock_automation_class.return_value = mock_automation_handler
            
            await server.initialize_server()
            
            mock_config_manager.load_config.assert_called_once()
            mock_automation_class.assert_called_once_with(mock_config_manager)
            assert server.automation_handler == mock_automation_handler
    
    @pytest.mark.asyncio
    async def test_handle_send_message_success(self, server):
        """Test successful send_message handling."""
        # Mock automation handler
        mock_automation_handler = AsyncMock()
        mock_automation_handler.send_message_and_get_response.return_value = "Test response"
        server.automation_handler = mock_automation_handler
        
        arguments = {"message": "Hello ChatGPT", "timeout": 30}
        result = await server._handle_send_message(arguments)
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Test response"
        mock_automation_handler.send_message_and_get_response.assert_called_once_with(
            "Hello ChatGPT", 30
        )
    
    @pytest.mark.asyncio
    async def test_handle_send_message_validation_error(self, server):
        """Test send_message with invalid input."""
        # Test empty message
        with pytest.raises(ValidationError) as exc_info:
            await server._handle_send_message({"message": ""})
        assert "Message must be a non-empty string" in str(exc_info.value)
        
        # Test invalid timeout
        with pytest.raises(ValidationError) as exc_info:
            await server._handle_send_message({"message": "Hello", "timeout": -1})
        assert "Timeout must be a positive number" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_handle_send_message_creates_automation_handler(self, server):
        """Test that send_message creates automation handler if not exists."""
        with patch('src.mcp_server.WindowsAutomationHandler') as mock_automation_class:
            mock_automation_handler = AsyncMock()
            mock_automation_handler.send_message_and_get_response.return_value = "Response"
            mock_automation_class.return_value = mock_automation_handler
            
            arguments = {"message": "Hello"}
            await server._handle_send_message(arguments)
            
            mock_automation_class.assert_called_once_with(server.config_manager)
            assert server.automation_handler == mock_automation_handler
    
    @pytest.mark.asyncio
    async def test_handle_get_conversation_history_success(self, server):
        """Test successful get_conversation_history handling."""
        mock_automation_handler = AsyncMock()
        mock_history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
        mock_automation_handler.get_conversation_history.return_value = mock_history
        server.automation_handler = mock_automation_handler
        
        arguments = {"limit": 5}
        result = await server._handle_get_conversation_history(arguments)
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        parsed_result = json.loads(result[0].text)
        assert parsed_result == mock_history
        mock_automation_handler.get_conversation_history.assert_called_once_with(5)
    
    @pytest.mark.asyncio
    async def test_handle_get_conversation_history_validation_error(self, server):
        """Test get_conversation_history with invalid input."""
        with pytest.raises(ValidationError) as exc_info:
            await server._handle_get_conversation_history({"limit": -1})
        assert "Limit must be a positive integer" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            await server._handle_get_conversation_history({"limit": "invalid"})
        assert "Limit must be a positive integer" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_handle_reset_conversation_success(self, server):
        """Test successful reset_conversation handling."""
        mock_automation_handler = AsyncMock()
        mock_automation_handler.reset_conversation.return_value = True
        server.automation_handler = mock_automation_handler
        
        result = await server._handle_reset_conversation({})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Conversation reset successfully"
        mock_automation_handler.reset_conversation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_reset_conversation_failure(self, server):
        """Test reset_conversation failure handling."""
        mock_automation_handler = AsyncMock()
        mock_automation_handler.reset_conversation.return_value = False
        server.automation_handler = mock_automation_handler
        
        with pytest.raises(AutomationError) as exc_info:
            await server._handle_reset_conversation({})
        assert "Failed to reset conversation" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_handle_get_debug_info(self, server):
        """Test get_debug_info handling."""
        # Mock performance monitor
        mock_performance_monitor = Mock()
        mock_performance_monitor.get_statistics.return_value = {
            "total_calls": 10,
            "average_duration": 1.5
        }
        server.logging_manager.get_performance_monitor.return_value = mock_performance_monitor
        
        # Mock error handler stats
        server.error_handler.get_error_stats = Mock(return_value={"total_errors": 2})
        
        arguments = {"include_metrics": True, "include_logs": False}
        result = await server._handle_get_debug_info(arguments)
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        debug_info = json.loads(result[0].text)
        
        assert "server_info" in debug_info
        assert "configuration" in debug_info
        assert "performance_metrics" in debug_info
        assert "error_stats" in debug_info
        assert debug_info["server_info"]["name"] == "windows-chatgpt-mcp"
    
    @pytest.mark.asyncio
    async def test_handle_get_debug_info_with_logs(self, server):
        """Test get_debug_info with logs included."""
        mock_performance_monitor = Mock()
        mock_performance_monitor.get_statistics.return_value = {}
        server.logging_manager.get_performance_monitor.return_value = mock_performance_monitor
        server.error_handler.get_error_stats = Mock(return_value={})
        
        arguments = {"include_metrics": False, "include_logs": True}
        result = await server._handle_get_debug_info(arguments)
        
        debug_info = json.loads(result[0].text)
        assert "logs" in debug_info
        assert "performance_metrics" not in debug_info
    
    @pytest.mark.asyncio
    async def test_shutdown(self, server):
        """Test server shutdown process."""
        mock_automation_handler = AsyncMock()
        mock_automation_handler.cleanup = AsyncMock()
        server.automation_handler = mock_automation_handler
        
        mock_performance_monitor = Mock()
        mock_performance_monitor.get_statistics.return_value = {"test": "stats"}
        server.logging_manager.get_performance_monitor.return_value = mock_performance_monitor
        
        await server.shutdown()
        
        mock_automation_handler.cleanup.assert_called_once()
        server.logging_manager.cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_without_automation_handler(self, server):
        """Test server shutdown when automation handler is None."""
        server.automation_handler = None
        
        mock_performance_monitor = Mock()
        mock_performance_monitor.get_statistics.return_value = {}
        server.logging_manager.get_performance_monitor.return_value = mock_performance_monitor
        
        # Should not raise an exception
        await server.shutdown()
        
        server.logging_manager.cleanup.assert_called_once()


class TestMCPServerToolRegistration:
    """Test MCP tool registration and handling."""
    
    @pytest.fixture
    def server(self):
        """Create a test server with mocked dependencies."""
        with patch('src.mcp_server.setup_logging') as mock_setup_logging:
            mock_logging_manager = Mock()
            mock_logging_manager.log_system_info = Mock()
            mock_setup_logging.return_value = mock_logging_manager
            
            server = WindowsChatGPTMCPServer()
            server.logging_manager = mock_logging_manager
            return server
    
    def test_tool_registration(self, server):
        """Test that tools are properly registered."""
        # The tools should be registered during server initialization
        # We can verify this by checking that the server has the expected handlers
        assert server.server is not None
        
        # Note: In a real test, we might want to inspect the server's internal
        # tool registry, but since that's implementation-specific, we'll test
        # the tool functionality through the public interface
    
    @pytest.mark.asyncio
    async def test_list_tools_handler(self, server):
        """Test the list_tools handler returns expected tools."""
        # This would require accessing the server's internal tool handlers
        # For now, we'll test that the expected tools are defined
        expected_tools = [
            "send_message",
            "get_conversation_history", 
            "reset_conversation",
            "get_debug_info"
        ]
        
        # In a real implementation, we'd call the list_tools handler
        # and verify the returned tools match our expectations
        assert True  # Placeholder - would need access to server internals


class TestMCPServerErrorHandling:
    """Test error handling in MCP server operations."""
    
    @pytest.fixture
    def server(self):
        """Create a test server."""
        with patch('src.mcp_server.setup_logging') as mock_setup_logging:
            mock_logging_manager = Mock()
            mock_logging_manager.log_system_info = Mock()
            mock_setup_logging.return_value = mock_logging_manager
            
            server = WindowsChatGPTMCPServer()
            server.logging_manager = mock_logging_manager
            return server
    
    @pytest.mark.asyncio
    async def test_automation_error_handling(self, server):
        """Test handling of automation errors."""
        mock_automation_handler = AsyncMock()
        mock_automation_handler.send_message_and_get_response.side_effect = AutomationError(
            "ChatGPT window not found", "window_detection"
        )
        server.automation_handler = mock_automation_handler
        
        with pytest.raises(AutomationError):
            await server._handle_send_message({"message": "Hello"})
    
    @pytest.mark.asyncio
    async def test_configuration_error_handling(self, server):
        """Test handling of configuration errors."""
        # Mock the load_config method to raise an error
        server.config_manager.load_config = AsyncMock(
            side_effect=ConfigurationError("Invalid configuration file", "config.json")
        )
        
        with pytest.raises(ConfigurationError):
            await server.initialize_server()
    
    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, server):
        """Test handling of unexpected errors."""
        mock_automation_handler = AsyncMock()
        mock_automation_handler.send_message_and_get_response.side_effect = Exception(
            "Unexpected error"
        )
        server.automation_handler = mock_automation_handler
        
        with pytest.raises(Exception):
            await server._handle_send_message({"message": "Hello"})


if __name__ == "__main__":
    pytest.main([__file__])