"""
Tests for conversation management features.

This module tests conversation context tracking, history management, and reset functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from src.windows_automation import WindowsAutomationHandler, WindowInfo, WindowState
from src.config import ConfigManager
from src.exceptions import ChatGPTWindowError, AutomationError


class TestConversationHistoryCapture:
    """Test conversation history capture functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_config = Mock(return_value={
            'response_timeout': 30,
            'polling_interval': 1.0,
            'max_response_length': 50000
        })
        return config_manager
    
    @pytest.fixture
    def mock_window_info(self):
        """Create a mock window info object."""
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
        """Create an automation handler for testing."""
        return WindowsAutomationHandler(mock_config_manager)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_success(self, automation_handler, mock_window_info):
        """Test successful conversation history capture."""
        mock_conversation_text = """
        User: What is Python?
        Assistant: Python is a high-level programming language known for its simplicity and readability.
        User: Can you give me an example?
        Assistant: Sure! Here's a simple Python example:
        print("Hello, World!")
        """
        
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_capture_conversation_area') as mock_capture:
                    mock_capture.return_value = mock_conversation_text
                    
                    history = await automation_handler.get_conversation_history(max_messages=10)
                    
                    assert len(history) > 0
                    assert all(isinstance(msg, dict) for msg in history)
                    assert all('role' in msg and 'content' in msg for msg in history)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_window_not_found(self, automation_handler):
        """Test conversation history capture when ChatGPT window is not found."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = None
            
            history = await automation_handler.get_conversation_history(max_messages=10)
            
            assert history == []
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_focus_failure(self, automation_handler, mock_window_info):
        """Test conversation history capture when window focus fails."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = False
                
                history = await automation_handler.get_conversation_history(max_messages=10)
                
                assert history == []
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_capture_failure(self, automation_handler, mock_window_info):
        """Test conversation history capture when text capture fails."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_capture_conversation_area') as mock_capture:
                    mock_capture.return_value = None
                    
                    history = await automation_handler.get_conversation_history(max_messages=10)
                    
                    assert history == []
    
    def test_parse_conversation_history_empty_text(self, automation_handler):
        """Test parsing empty conversation text."""
        history = automation_handler._parse_conversation_history("", 10)
        assert history == []
    
    def test_parse_conversation_history_simple_conversation(self, automation_handler):
        """Test parsing a simple conversation."""
        conversation_text = """
        What is machine learning?
        Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience.
        Can you explain supervised learning?
        Supervised learning uses labeled training data to learn a mapping function from inputs to outputs.
        """
        
        history = automation_handler._parse_conversation_history(conversation_text, 10)
        
        assert len(history) > 0
        assert all('role' in msg and 'content' in msg for msg in history)
        
        # Check that we have both user and assistant messages
        roles = [msg['role'] for msg in history]
        assert 'user' in roles or 'assistant' in roles
    
    def test_parse_conversation_history_max_messages_limit(self, automation_handler):
        """Test that conversation history respects max_messages limit."""
        # Create a long conversation text
        conversation_text = "\n".join([
            f"Message {i}: This is message number {i}" for i in range(20)
        ])
        
        max_messages = 5
        history = automation_handler._parse_conversation_history(conversation_text, max_messages)
        
        assert len(history) <= max_messages
    
    def test_looks_like_user_message_heuristics(self, automation_handler):
        """Test user message detection heuristics."""
        # Test question patterns
        assert automation_handler._looks_like_user_message("What is Python?")
        assert automation_handler._looks_like_user_message("How do I install Python?")
        assert automation_handler._looks_like_user_message("Can you help me?")
        assert automation_handler._looks_like_user_message("Please explain this concept")
        
        # Test non-user patterns
        assert not automation_handler._looks_like_user_message("Python is a programming language.")
        assert not automation_handler._looks_like_user_message("Here's an example:")


class TestConversationReset:
    """Test conversation reset functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_config = Mock(return_value={})
        return config_manager
    
    @pytest.fixture
    def mock_window_info(self):
        """Create a mock window info object."""
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
        """Create an automation handler for testing."""
        return WindowsAutomationHandler(mock_config_manager)
    
    @patch('src.windows_automation.pyautogui')
    @patch('src.windows_automation.time')
    @pytest.mark.asyncio
    async def test_reset_conversation_success(self, mock_time, mock_pyautogui, 
                                       automation_handler, mock_window_info):
        """Test successful conversation reset."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_verify_conversation_reset') as mock_verify:
                    mock_verify.return_value = True
                    
                    result = await automation_handler.reset_conversation()
                    
                    assert result is True
                    mock_pyautogui.hotkey.assert_called_with('ctrl', 'n')
                    # Verify is called twice - once after first shortcut, once after verification
                    assert mock_verify.call_count >= 1
    
    @patch('src.windows_automation.pyautogui')
    @patch('src.windows_automation.time')
    @pytest.mark.asyncio
    async def test_reset_conversation_fallback_shortcut(self, mock_time, mock_pyautogui,
                                                  automation_handler, mock_window_info):
        """Test conversation reset with fallback keyboard shortcut."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_verify_conversation_reset') as mock_verify:
                    # First call returns False, second returns True
                    mock_verify.side_effect = [False, True]
                    
                    result = await automation_handler.reset_conversation()
                    
                    assert result is True
                    # Should try both shortcuts
                    from unittest.mock import call
                    mock_pyautogui.hotkey.assert_has_calls([
                        call('ctrl', 'n'),
                        call('ctrl', 'shift', 'n')
                    ])
    
    @pytest.mark.asyncio
    async def test_reset_conversation_window_not_found(self, automation_handler):
        """Test conversation reset when ChatGPT window is not found."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = None
            
            result = await automation_handler.reset_conversation()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_reset_conversation_focus_failure(self, automation_handler, mock_window_info):
        """Test conversation reset when window focus fails."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = False
                
                result = await automation_handler.reset_conversation()
                
                assert result is False
    
    @patch('src.windows_automation.pyautogui')
    @patch('src.windows_automation.time')
    @pytest.mark.asyncio
    async def test_reset_conversation_verification_failure(self, mock_time, mock_pyautogui,
                                                    automation_handler, mock_window_info):
        """Test conversation reset when verification fails."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_verify_conversation_reset') as mock_verify:
                    mock_verify.return_value = False
                    
                    result = await automation_handler.reset_conversation()
                    
                    assert result is False
    
    @patch('src.windows_automation.time')
    def test_verify_conversation_reset(self, mock_time, automation_handler):
        """Test conversation reset verification."""
        # This is a simplified test since the actual verification
        # would require more complex UI interaction
        result = automation_handler._verify_conversation_reset()
        
        # Currently always returns True as it's a simplified implementation
        assert result is True
        mock_time.sleep.assert_called_with(0.5)
    
    @patch('src.windows_automation.pyautogui')
    @patch('src.windows_automation.time')
    @pytest.mark.asyncio
    async def test_reset_conversation_exception_handling(self, mock_time, mock_pyautogui,
                                                   automation_handler, mock_window_info):
        """Test conversation reset exception handling."""
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                # Make pyautogui.hotkey raise an exception
                mock_pyautogui.hotkey.side_effect = Exception("Automation error")
                
                result = await automation_handler.reset_conversation()
                
                assert result is False


class TestConversationContextTracking:
    """Test conversation context tracking functionality."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_config = Mock(return_value={})
        return config_manager
    
    @pytest.fixture
    def automation_handler(self, mock_config_manager):
        """Create an automation handler for testing."""
        return WindowsAutomationHandler(mock_config_manager)
    
    def test_capture_conversation_area_delegation(self, automation_handler):
        """Test that _capture_conversation_area delegates to response capture method."""
        mock_window_info = Mock()
        
        with patch.object(automation_handler.response_capture, '_capture_via_selection') as mock_capture:
            mock_capture.return_value = "Captured conversation text"
            
            result = automation_handler._capture_conversation_area(mock_window_info)
            
            assert result == "Captured conversation text"
            mock_capture.assert_called_once_with(mock_window_info)
    
    def test_capture_conversation_area_exception_handling(self, automation_handler):
        """Test exception handling in conversation area capture."""
        mock_window_info = Mock()
        
        with patch.object(automation_handler.response_capture, '_capture_via_selection') as mock_capture:
            mock_capture.side_effect = Exception("Capture failed")
            
            result = automation_handler._capture_conversation_area(mock_window_info)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_conversation_history_integration(self, automation_handler):
        """Test integration between history capture and parsing."""
        mock_window_info = Mock()
        mock_conversation_text = """
        User: Hello
        Assistant: Hi there! How can I help you today?
        User: What's the weather like?
        Assistant: I don't have access to real-time weather data.
        """
        
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                with patch.object(automation_handler, '_capture_conversation_area') as mock_capture:
                    mock_capture.return_value = mock_conversation_text
                    
                    history = await automation_handler.get_conversation_history(max_messages=5)
                    
                    # Verify that we get structured conversation data
                    assert isinstance(history, list)
                    assert len(history) > 0
                    
                    for message in history:
                        assert isinstance(message, dict)
                        assert 'role' in message
                        assert 'content' in message
                        assert message['role'] in ['user', 'assistant']
                        assert isinstance(message['content'], str)
                        assert len(message['content']) > 0


class TestConversationManagementIntegration:
    """Test integration of conversation management features."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_config = Mock(return_value={
            'response_timeout': 30,
            'polling_interval': 1.0,
            'max_response_length': 50000
        })
        return config_manager
    
    @pytest.fixture
    def automation_handler(self, mock_config_manager):
        """Create an automation handler for testing."""
        return WindowsAutomationHandler(mock_config_manager)
    
    @pytest.mark.asyncio
    async def test_conversation_workflow_integration(self, automation_handler):
        """Test the complete conversation management workflow."""
        mock_window_info = Mock()
        
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = True
                
                # Test getting conversation history
                with patch.object(automation_handler, '_capture_conversation_area') as mock_capture:
                    mock_capture.return_value = "User: Hello\nAssistant: Hi there!"
                    
                    history = await automation_handler.get_conversation_history(max_messages=10)
                    assert len(history) > 0
                
                # Test resetting conversation
                with patch.object(automation_handler, '_verify_conversation_reset') as mock_verify:
                    mock_verify.return_value = True
                    
                    with patch('src.windows_automation.pyautogui') as mock_pyautogui:
                        reset_result = await automation_handler.reset_conversation()
                        assert reset_result is True
                        mock_pyautogui.hotkey.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_recovery_in_conversation_management(self, automation_handler):
        """Test error recovery in conversation management operations."""
        # Test that operations gracefully handle various error conditions
        
        # Window not found scenario
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = None
            
            history = await automation_handler.get_conversation_history(max_messages=10)
            assert history == []
            
            reset_result = await automation_handler.reset_conversation()
            assert reset_result is False
        
        # Focus failure scenario
        mock_window_info = Mock()
        with patch.object(automation_handler.window_manager, 'find_chatgpt_window') as mock_find:
            mock_find.return_value = mock_window_info
            
            with patch.object(automation_handler.window_manager, 'focus_window') as mock_focus:
                mock_focus.return_value = False
                
                history = await automation_handler.get_conversation_history(max_messages=10)
                assert history == []
                
                reset_result = await automation_handler.reset_conversation()
                assert reset_result is False