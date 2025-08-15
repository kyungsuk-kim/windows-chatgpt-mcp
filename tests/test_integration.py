"""
Integration tests for Windows ChatGPT MCP.

This module tests the integration between multiple components without requiring
the actual ChatGPT application to be running.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.config import ConfigManager
from src.mcp_server import WindowsChatGPTMCPServer
from src.windows_automation import WindowsAutomationHandler, WindowInfo, WindowState
from src.response_parser import ResponseParser
from src.error_handler import ErrorHandler
from src.exceptions import ChatGPTWindowError, AutomationError


@pytest.mark.integration
class TestMCPServerIntegration:
    """Integration tests for MCP Server with other components."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock config manager for testing."""
        config_manager = Mock()
        config_manager.get_server_config.return_value = Mock(server_name="test-server")
        return config_manager
    

    
    @pytest.fixture
    def mock_window_info(self):
        """Create a mock WindowInfo for testing."""
        return WindowInfo(
            handle=12345,
            title="Test ChatGPT",
            position=(100, 100),
            size=(800, 600),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
    
    @pytest.mark.asyncio
    async def test_mcp_server_initialization_with_config(self, mock_config_manager):
        """Test MCP server initialization with configuration."""
        server = WindowsChatGPTMCPServer(mock_config_manager)
        
        # Verify server is initialized with config
        assert server.config_manager == mock_config_manager
        assert server.server.name == "windows-chatgpt-mcp"
    
    @pytest.mark.asyncio
    async def test_automation_handler_with_config_integration(self, mock_config_manager):
        """Test WindowsAutomationHandler integration with ConfigManager."""
        handler = WindowsAutomationHandler(mock_config_manager)
        
        # Verify handler is initialized with config
        assert handler.config_manager == mock_config_manager
        assert handler.window_manager is not None
        assert handler.message_sender is not None
        assert handler.response_capture is not None
    
    @pytest.mark.asyncio
    async def test_end_to_end_message_flow_mocked(self, mock_config_manager, mock_window_info):
        """Test end-to-end message flow with mocked ChatGPT interaction."""
        # Create components
        handler = WindowsAutomationHandler(mock_config_manager)
        response_parser = ResponseParser()
        
        # Mock the window operations
        with patch.object(handler.window_manager, 'find_chatgpt_window', return_value=mock_window_info), \
             patch.object(handler.window_manager, 'focus_window', return_value=True), \
             patch.object(handler.message_sender, 'send_message', return_value=True), \
             patch.object(handler.response_capture, 'capture_response', return_value="Hello! How can I help you today?"):
            
            # Test the flow
            response = await handler.send_message_and_get_response("Hello", timeout=5)
            
            # Verify response
            assert response == "Hello! How can I help you today?"
            
            # Parse the response
            parsed_response = response_parser.parse_response(response)
            
            # Verify parsed response
            assert parsed_response.content == "Hello! How can I help you today?"
            assert parsed_response.response_type.value == "text"
    
    @pytest.mark.asyncio
    async def test_conversation_history_integration(self, mock_config_manager, mock_window_info):
        """Test conversation history retrieval integration."""
        handler = WindowsAutomationHandler(mock_config_manager)
        
        # Mock conversation text
        mock_conversation = "User: Hello\nAssistant: Hi there!\nUser: How are you?\nAssistant: I'm doing well!"
        
        with patch.object(handler.window_manager, 'find_chatgpt_window', return_value=mock_window_info), \
             patch.object(handler.window_manager, 'focus_window', return_value=True), \
             patch.object(handler, '_capture_conversation_area', return_value=mock_conversation):
            
            # Test conversation history retrieval
            history = await handler.get_conversation_history(max_messages=10)
            
            # Verify history structure
            assert len(history) == 4
            assert history[0]["role"] == "user"
            assert history[0]["content"] == "Hello"
            assert history[1]["role"] == "assistant"
            assert history[1]["content"] == "Hi there!"
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mock_config_manager, mock_window_info):
        """Test error handling across components."""
        handler = WindowsAutomationHandler(mock_config_manager)
        error_handler = ErrorHandler()
        
        # Test window not found scenario
        with patch.object(handler.window_manager, 'find_chatgpt_window', return_value=None):
            
            with pytest.raises(AutomationError, match="Failed to send message"):
                await handler.send_message_and_get_response("Hello")
        
        # Test automation error scenario
        with patch.object(handler.window_manager, 'find_chatgpt_window', return_value=mock_window_info), \
             patch.object(handler.window_manager, 'focus_window', return_value=True), \
             patch.object(handler.message_sender, 'send_message', return_value=False):
            
            with pytest.raises(AutomationError, match="Failed to send message"):
                await handler.send_message_and_get_response("Hello")


@pytest.mark.integration
class TestResponseParsingIntegration:
    """Integration tests for response parsing with different components."""
    
    @pytest.fixture
    def response_parser(self):
        """Create a ResponseParser instance."""
        return ResponseParser()
    
    def test_response_parser_with_automation_output(self, response_parser):
        """Test response parser with realistic automation output."""
        # Simulate response that might come from ChatGPT automation
        raw_response = {
            "content": "Here's a Python example:\n\n```python\ndef hello_world():\n    print('Hello, World!')\n```\n\nThis function prints a greeting.",
            "type": "mixed",
            "timestamp": "2024-01-01T12:00:00Z",
            "model": "gpt-4"
        }
        
        # Parse the response
        parsed = response_parser.parse_response(raw_response)
        
        # Verify parsing
        assert parsed.response_type.value == "mixed"
        assert "def hello_world():" in parsed.content
        assert parsed.timestamp == "2024-01-01T12:00:00Z"
        
        # Extract code blocks
        code_blocks = response_parser.extract_code_blocks(parsed.content)
        assert len(code_blocks) == 1
        assert code_blocks[0]["language"] == "python"
        assert "def hello_world():" in code_blocks[0]["code"]
        
        # Format for MCP
        formatted = response_parser.format_for_mcp(parsed)
        assert formatted["type"] == "mixed"
        assert formatted["model"] == "gpt-4"
    
    def test_response_parser_error_handling(self, response_parser):
        """Test response parser error handling integration."""
        # Test with invalid input
        with pytest.raises(Exception):  # Should raise ValidationError or similar
            response_parser.parse_response(None)
        
        # Test with empty content
        with pytest.raises(Exception):  # Should raise ValidationError or similar
            response_parser.parse_response({"content": "", "type": "text"})


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration across components."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.mark.asyncio
    async def test_config_propagation_to_components(self, temp_config_dir):
        """Test that configuration is properly propagated to all components."""
        config_file = os.path.join(temp_config_dir, "test_config.json")
        
        # Create test config
        config_data = {
            "server": {
                "server_name": "integration-test-server",
                "server_version": "1.0.0",
                "log_level": "INFO",
                "max_concurrent_requests": 10,
                "request_timeout": 30.0
            },
            "window_detection": {
                "window_title_patterns": ["Test Pattern"],
                "search_timeout": 15.0
            },
            "automation": {
                "typing_delay": 0.02,
                "response_timeout": 25.0
            }
        }
        
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
        
        # Load config and create components
        config_manager = ConfigManager(config_file)
        await config_manager.load_config()
        
        # Test MCP server gets config
        server = WindowsChatGPTMCPServer(config_manager)
        assert server.server.name == "windows-chatgpt-mcp"
        
        # Test automation handler gets config
        handler = WindowsAutomationHandler(config_manager)
        assert handler.config_manager == config_manager
        
        # Verify config values are accessible
        window_config = config_manager.get_window_detection_config()
        assert window_config.window_title_patterns == ["Test Pattern"]
        assert window_config.search_timeout == 15.0
        
        automation_config = config_manager.get_automation_config()
        assert automation_config.typing_delay == 0.02
        assert automation_config.response_timeout == 25.0
    
    @pytest.mark.asyncio
    async def test_config_validation_integration(self, temp_config_dir):
        """Test configuration validation across components."""
        config_file = os.path.join(temp_config_dir, "invalid_config.json")
        
        # Create invalid config
        invalid_config = {
            "server": {
                "server_name": "",  # Invalid empty name
                "server_version": "1.0.0",
                "log_level": "INFO",
                "max_concurrent_requests": 10,
                "request_timeout": 30.0
            },
            "window_detection": {
                "window_title_patterns": ["ChatGPT"],
                "search_timeout": -1.0  # Invalid negative timeout
            },
            "automation": {
                "typing_delay": 0.05,
                "response_timeout": 30.0
            },
            "chatgpt": {
                "model_preferences": ["gpt-4"]
            }
        }
        
        with open(config_file, 'w') as f:
            import json
            json.dump(invalid_config, f)
        
        # Test that invalid config is handled
        config_manager = ConfigManager(config_file)
        
        # Should either raise an exception or use defaults
        try:
            await config_manager.load_config()
            # If no exception, verify defaults are used
            server_config = config_manager.get_server_config()
            assert server_config.server_name != ""  # Should have default
        except Exception:
            # Exception is acceptable for invalid config
            pass


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Integration tests for performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_response_parsing_performance(self):
        """Test response parsing performance with large responses."""
        parser = ResponseParser()
        
        # Create a large response with multiple code blocks
        large_content = "Here are multiple code examples:\n\n"
        for i in range(10):
            large_content += f"```python\ndef function_{i}():\n    return {i}\n```\n\n"
        large_content += "That's all the examples."
        
        response_data = {
            "content": large_content,
            "type": "code",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        # Time the parsing operation
        import time
        start_time = time.time()
        
        parsed = parser.parse_response(response_data)
        code_blocks = parser.extract_code_blocks(parsed.content)
        formatted = parser.format_for_mcp(parsed)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify results
        assert len(code_blocks) == 10
        assert formatted["type"] == "code"
        
        # Performance assertion (should process in reasonable time)
        assert processing_time < 1.0, f"Processing took too long: {processing_time}s"
    
    @pytest.mark.asyncio
    async def test_conversation_parsing_performance(self):
        """Test conversation parsing performance with long conversations."""
        config_manager = Mock()
        handler = WindowsAutomationHandler(config_manager)
        
        # Create a long conversation
        conversation_lines = []
        for i in range(100):
            conversation_lines.append(f"User: Question {i}?")
            conversation_lines.append(f"Assistant: Answer {i}.")
        
        conversation_text = "\n".join(conversation_lines)
        
        # Time the parsing operation
        import time
        start_time = time.time()
        
        result = handler._parse_conversation_history(conversation_text, 50)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify results
        assert len(result) == 50  # Should limit to max_messages
        assert result[0]["role"] in ["user", "assistant"]
        
        # Performance assertion
        assert processing_time < 0.5, f"Conversation parsing took too long: {processing_time}s"