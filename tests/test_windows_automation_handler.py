"""
Unit tests for WindowsAutomationHandler class.

This module tests the main automation handler that coordinates all ChatGPT interactions.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from src.windows_automation import (
    WindowsAutomationHandler, WindowManager, MessageSender, ResponseCapture,
    WindowInfo, WindowState
)
from src.config import ConfigManager
from src.exceptions import (
    ChatGPTWindowError, AutomationError, ResponseTimeoutError
)


class TestWindowsAutomationHandler:
    """Test cases for WindowsAutomationHandler class."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock()
        # Don't mock get_config since it doesn't exist - the handler will use empty dict
        return config_manager
    
    @pytest.fixture
    def mock_window_info(self):
        """Create a mock WindowInfo object."""
        return WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(100, 100),
            size=(800, 600),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
    
    @pytest.fixture
    def automation_handler(self, mock_config_manager):
        """Create a WindowsAutomationHandler with mocked dependencies."""
        with patch('src.windows_automation.WindowManager') as mock_window_manager_class, \
             patch('src.windows_automation.MessageSender') as mock_message_sender_class, \
             patch('src.windows_automation.ResponseCapture') as mock_response_capture_class:
            
            handler = WindowsAutomationHandler(mock_config_manager)
            
            # Replace the actual instances with mocks for testing
            handler.window_manager = Mock(spec=WindowManager)
            handler.message_sender = Mock(spec=MessageSender)
            handler.response_capture = Mock(spec=ResponseCapture)
            
            return handler
    
    def test_initialization(self, automation_handler, mock_config_manager):
        """Test WindowsAutomationHandler initialization."""
        assert automation_handler.config_manager == mock_config_manager
        assert automation_handler.window_manager is not None
        assert automation_handler.message_sender is not None
        assert automation_handler.response_capture is not None
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_success(self, automation_handler, mock_window_info):
        """Test successful message sending and response capture."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = True
        automation_handler.message_sender.send_message.return_value = True
        automation_handler.response_capture.capture_response.return_value = "Hello! How can I help you?"
        
        # Test the method
        result = await automation_handler.send_message_and_get_response("Hello", timeout=10)
        
        # Verify calls
        automation_handler.window_manager.find_chatgpt_window.assert_called_once()
        automation_handler.window_manager.focus_window.assert_called_once_with(mock_window_info)
        automation_handler.message_sender.send_message.assert_called_once_with("Hello")
        automation_handler.response_capture.capture_response.assert_called_once_with(timeout=10)
        
        # Verify result
        assert result == "Hello! How can I help you?"
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_window_not_found(self, automation_handler):
        """Test message sending when ChatGPT window is not found."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = None
        
        # Test the method - should raise exception
        with pytest.raises(ChatGPTWindowError, match="ChatGPT window not found"):
            await automation_handler.send_message_and_get_response("Hello")
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_focus_failed(self, automation_handler, mock_window_info):
        """Test message sending when window focus fails."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = False
        
        # Test the method - should raise exception
        with pytest.raises(ChatGPTWindowError, match="Failed to focus ChatGPT window"):
            await automation_handler.send_message_and_get_response("Hello")
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_send_failed(self, automation_handler, mock_window_info):
        """Test message sending when message sending fails."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = True
        automation_handler.message_sender.send_message.return_value = False
        
        # Test the method - should raise exception
        with pytest.raises(AutomationError, match="Failed to send message"):
            await automation_handler.send_message_and_get_response("Hello")
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_no_response(self, automation_handler, mock_window_info):
        """Test message sending when no response is captured."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = True
        automation_handler.message_sender.send_message.return_value = True
        automation_handler.response_capture.capture_response.return_value = None
        
        # Test the method - should raise exception
        with pytest.raises(ResponseTimeoutError, match="No response received"):
            await automation_handler.send_message_and_get_response("Hello")
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_success(self, automation_handler, mock_window_info):
        """Test successful conversation history retrieval."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = True
        
        expected_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        with patch.object(automation_handler, '_capture_conversation_area', return_value="User: Hello\nAssistant: Hi there!"):
            result = await automation_handler.get_conversation_history(max_messages=5)
        
        # Verify calls
        automation_handler.window_manager.find_chatgpt_window.assert_called_once()
        automation_handler.window_manager.focus_window.assert_called_once_with(mock_window_info)
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(msg, dict) for msg in result)
        assert all('role' in msg and 'content' in msg for msg in result)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_window_not_found(self, automation_handler):
        """Test conversation history when window not found."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = None
        
        # Test the method
        result = await automation_handler.get_conversation_history()
        
        # Should return empty list
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_focus_failed(self, automation_handler, mock_window_info):
        """Test conversation history when window focus fails."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = False
        
        # Test the method
        result = await automation_handler.get_conversation_history()
        
        # Should return empty list
        assert result == []
    
    @pytest.mark.asyncio
    async def test_reset_conversation_success(self, automation_handler, mock_window_info):
        """Test successful conversation reset."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = True
        
        with patch('src.windows_automation.pyautogui') as mock_pyautogui, \
             patch.object(automation_handler, '_verify_conversation_reset', return_value=True):
            
            result = await automation_handler.reset_conversation()
        
        # Verify calls
        automation_handler.window_manager.find_chatgpt_window.assert_called_once()
        automation_handler.window_manager.focus_window.assert_called_once_with(mock_window_info)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_reset_conversation_window_not_found(self, automation_handler):
        """Test conversation reset when window not found."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = None
        
        # Test the method
        result = await automation_handler.reset_conversation()
        
        # Should return False
        assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_conversation_focus_failed(self, automation_handler, mock_window_info):
        """Test conversation reset when window focus fails."""
        # Setup mocks
        automation_handler.window_manager.find_chatgpt_window.return_value = mock_window_info
        automation_handler.window_manager.focus_window.return_value = False
        
        # Test the method
        result = await automation_handler.reset_conversation()
        
        # Should return False
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup(self, automation_handler):
        """Test cleanup method."""
        # Test the method - should not raise any exceptions
        await automation_handler.cleanup()
        
        # Cleanup should complete successfully
        assert True  # If we get here, cleanup worked
    
    def test_capture_conversation_area_placeholder(self, mock_config_manager, mock_window_info):
        """Test _capture_conversation_area placeholder implementation."""
        # Create handler and mock the response capture component
        handler = WindowsAutomationHandler(mock_config_manager)
        
        # Mock the response_capture component's method to avoid real screen interaction
        with patch.object(handler.response_capture, '_capture_via_selection', return_value=None):
            result = handler._capture_conversation_area(mock_window_info)
        
        # Should return None when no text is captured
        assert result is None
    
    def test_parse_conversation_history_empty(self, mock_config_manager):
        """Test parsing empty conversation history."""
        handler = WindowsAutomationHandler(mock_config_manager)
        result = handler._parse_conversation_history("", 10)
        
        assert result == []
    
    def test_parse_conversation_history_simple(self, mock_config_manager):
        """Test parsing simple conversation history."""
        handler = WindowsAutomationHandler(mock_config_manager)
        conversation_text = "User: Hello\nAssistant: Hi there!\nUser: How are you?\nAssistant: I'm doing well!"
        
        result = handler._parse_conversation_history(conversation_text, 10)
        
        assert len(result) == 4
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "Hello"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Hi there!"
    
    def test_parse_conversation_history_max_messages(self, mock_config_manager):
        """Test parsing conversation history with max message limit."""
        handler = WindowsAutomationHandler(mock_config_manager)
        conversation_text = "User: Hello\nAssistant: Hi!\nUser: How are you?\nAssistant: Good!\nUser: Great!"
        
        result = handler._parse_conversation_history(conversation_text, 3)
        
        # Should return only the last 3 messages
        assert len(result) == 3
    
    def test_looks_like_user_message_positive_cases(self, mock_config_manager):
        """Test _looks_like_user_message with positive cases."""
        handler = WindowsAutomationHandler(mock_config_manager)
        user_messages = [
            "How are you?",
            "Can you help me?",
            "Please explain this",
            "What is Python?",
            "Why does this happen?",
            "When should I use this?",
            "Where can I find more info?",
            "User: Hello there"
        ]
        
        for message in user_messages:
            result = handler._looks_like_user_message(message)
            assert result is True, f"Should detect '{message}' as user message"
    
    def test_looks_like_user_message_negative_cases(self, mock_config_manager):
        """Test _looks_like_user_message with negative cases."""
        handler = WindowsAutomationHandler(mock_config_manager)
        non_user_messages = [
            "I can help you with that.",
            "Here's the explanation.",
            "This is a statement.",
            "Assistant: Hello there"
        ]
        
        for message in non_user_messages:
            result = handler._looks_like_user_message(message)
            assert result is False, f"Should not detect '{message}' as user message"
    
    def test_verify_conversation_reset_placeholder(self, mock_config_manager):
        """Test _verify_conversation_reset placeholder implementation."""
        handler = WindowsAutomationHandler(mock_config_manager)
        result = handler._verify_conversation_reset()
        
        # Placeholder implementation should return True
        assert result is True