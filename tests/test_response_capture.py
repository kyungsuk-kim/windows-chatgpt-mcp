"""
Unit tests for the ResponseCapture class in windows_automation module.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, List, Dict

from src.windows_automation import (
    ResponseCapture, 
    WindowManager, 
    WindowInfo, 
    WindowState, 
    ChatGPTWindowError
)


class TestResponseCapture:
    """Test cases for ResponseCapture class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_window_manager = Mock(spec=WindowManager)
        self.response_capture = ResponseCapture(self.mock_window_manager)
        
        # Mock window info for testing
        self.mock_window_info = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(100, 100),
            size=(800, 600),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
    
    def test_capture_response_success(self):
        """Test successful response capture."""
        # Setup mocks
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        
        raw_response = "This is a test response from ChatGPT."
        cleaned_response = "This is a test response from ChatGPT."
        
        with patch.object(self.response_capture, '_wait_for_response', return_value=raw_response), \
             patch.object(self.response_capture, '_parse_and_clean_response', return_value=cleaned_response):
            
            result = self.response_capture.capture_response()
            
            assert result == cleaned_response
    
    def test_capture_response_window_not_found(self):
        """Test response capture when ChatGPT window is not found."""
        self.mock_window_manager.find_chatgpt_window.return_value = None
        
        result = self.response_capture.capture_response()
        
        assert result is None
    
    def test_capture_response_timeout(self):
        """Test response capture with timeout."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        
        with patch.object(self.response_capture, '_wait_for_response', return_value=None):
            result = self.response_capture.capture_response(timeout=5.0)
            
            assert result is None
    
    def test_capture_response_custom_timeout(self):
        """Test response capture with custom timeout."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        
        with patch.object(self.response_capture, '_wait_for_response') as mock_wait:
            mock_wait.return_value = "Test response"
            
            self.response_capture.capture_response(timeout=10.0)
            
            # Verify custom timeout was passed
            mock_wait.assert_called_once_with(self.mock_window_info, 10.0)
    
    @patch('src.windows_automation.time.time')
    @patch('src.windows_automation.time.sleep')
    def test_wait_for_response_success(self, mock_sleep, mock_time):
        """Test successful response waiting."""
        # Mock time progression
        mock_time.side_effect = [0, 1, 2, 3]  # Simulate time passing
        
        self.mock_window_manager.focus_window.return_value = True
        
        with patch.object(self.response_capture, '_capture_response_area') as mock_capture, \
             patch.object(self.response_capture, '_is_response_complete') as mock_complete:
            
            mock_capture.side_effect = [None, "Incomplete response", "Complete response"]
            mock_complete.side_effect = [False, True]
            
            result = self.response_capture._wait_for_response(self.mock_window_info, 30.0)
            
            assert result == "Complete response"
    
    @patch('src.windows_automation.time.time')
    @patch('src.windows_automation.time.sleep')
    def test_wait_for_response_timeout(self, mock_sleep, mock_time):
        """Test response waiting with timeout."""
        # Mock time progression that exceeds timeout
        mock_time.side_effect = [0, 35]  # Simulate timeout
        
        self.mock_window_manager.focus_window.return_value = True
        
        with patch.object(self.response_capture, '_capture_response_area', return_value=None):
            result = self.response_capture._wait_for_response(self.mock_window_info, 30.0)
            
            assert result is None
    
    def test_capture_response_area_success(self):
        """Test successful response area capture."""
        with patch.object(self.response_capture, '_capture_via_selection', return_value="Test response"):
            result = self.response_capture._capture_response_area(self.mock_window_info)
            
            assert result == "Test response"
    
    def test_capture_response_area_failure(self):
        """Test response area capture failure."""
        with patch.object(self.response_capture, '_capture_via_selection', return_value=None):
            result = self.response_capture._capture_response_area(self.mock_window_info)
            
            assert result is None
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('src.windows_automation.pyautogui.click')
    @patch('src.windows_automation.pyautogui.hotkey')
    @patch('src.windows_automation.time.sleep')
    def test_capture_via_selection_success(self, mock_sleep, mock_hotkey, mock_click, 
                                         mock_copy, mock_paste):
        """Test successful text capture via selection."""
        original_clipboard = "original content"
        captured_text = "Captured ChatGPT response"
        
        mock_paste.side_effect = [original_clipboard, captured_text]
        
        with patch.object(self.response_capture, '_find_response_area', return_value=(400, 300)):
            result = self.response_capture._capture_via_selection(self.mock_window_info)
            
            assert result == captured_text
            mock_click.assert_called_once_with(400, 300)
            assert mock_hotkey.call_count == 2  # ctrl+a and ctrl+c
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    def test_capture_via_selection_no_response_area(self, mock_copy, mock_paste):
        """Test selection capture when response area cannot be found."""
        with patch.object(self.response_capture, '_find_response_area', return_value=None):
            result = self.response_capture._capture_via_selection(self.mock_window_info)
            
            assert result is None
    
    @patch('builtins.__import__', side_effect=ImportError("No module named 'pyperclip'"))
    def test_capture_via_selection_no_pyperclip(self, mock_import):
        """Test selection capture when pyperclip is not available."""
        result = self.response_capture._capture_via_selection(self.mock_window_info)
        
        assert result is None
    
    def test_find_response_area_success(self):
        """Test successful response area location finding."""
        result = self.response_capture._find_response_area(self.mock_window_info)
        
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        # Check coordinates are within window bounds
        x, y = result
        assert 100 <= x <= 900  # window bounds
        assert 100 <= y <= 700
    
    def test_find_response_area_small_window(self):
        """Test response area finding with small window."""
        small_window = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(0, 0),
            size=(200, 150),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
        
        result = self.response_capture._find_response_area(small_window)
        
        assert result is not None
        x, y = result
        assert 0 <= x <= 200
        assert 0 <= y <= 150
    
    def test_is_response_complete_complete_responses(self):
        """Test response completeness detection for complete responses."""
        complete_responses = [
            "This is a complete response.",
            "Here's a detailed explanation of the topic.",
            "The answer to your question is yes, because of several reasons.",
        ]
        
        for response in complete_responses:
            result = self.response_capture._is_response_complete(response)
            assert result is True, f"Failed for response: {response}"
    
    def test_is_response_complete_incomplete_responses(self):
        """Test response completeness detection for incomplete responses."""
        incomplete_responses = [
            "This response is incomplete...",
            "typing...",
            "thinking...",
            "Short",  # Too short
            "",  # Empty
            "   ",  # Whitespace only
        ]
        
        for response in incomplete_responses:
            result = self.response_capture._is_response_complete(response)
            assert result is False, f"Incorrectly marked complete: {response}"
    
    def test_parse_and_clean_response_basic_cleaning(self):
        """Test basic response parsing and cleaning."""
        raw_response = """
        ChatGPT
        This is the actual response content.
        It has multiple lines.
        Copy
        Share
        """
        
        result = self.response_capture._parse_and_clean_response(raw_response)
        
        assert "ChatGPT" not in result
        assert "Copy" not in result
        assert "Share" not in result
        assert "This is the actual response content." in result
        assert "It has multiple lines." in result
    
    def test_parse_and_clean_response_empty_input(self):
        """Test response parsing with empty input."""
        result = self.response_capture._parse_and_clean_response("")
        assert result == ""
        
        result = self.response_capture._parse_and_clean_response(None)
        assert result == ""
    
    def test_parse_and_clean_response_length_limit(self):
        """Test response parsing with length limiting."""
        # Create a very long response
        long_response = "A" * 60000
        
        # Set a smaller max length for testing
        self.response_capture.max_response_length = 1000
        
        result = self.response_capture._parse_and_clean_response(long_response)
        
        assert len(result) <= 1020  # 1000 + "... [truncated]"
        assert result.endswith("... [truncated]")
    
    def test_is_ui_line_ui_patterns(self):
        """Test UI line detection for common UI patterns."""
        ui_lines = [
            "12:34 PM",
            "Copy",
            "Share",
            "Like",
            "Dislike",
            "ChatGPT",
            "New chat",
            "...",
            "",
            "   ",
        ]
        
        for line in ui_lines:
            result = self.response_capture._is_ui_line(line)
            assert result is True, f"Failed to detect UI line: '{line}'"
    
    def test_is_ui_line_content_lines(self):
        """Test UI line detection for actual content lines."""
        content_lines = [
            "This is actual response content.",
            "Here's a detailed explanation.",
            "The answer is 42.",
            "Let me help you with that.",
        ]
        
        for line in content_lines:
            result = self.response_capture._is_ui_line(line)
            assert result is False, f"Incorrectly marked as UI: '{line}'"
    
    def test_get_conversation_history_success(self):
        """Test successful conversation history capture."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        
        conversation_text = "User: Hello\nAssistant: Hi there!\nUser: How are you?\nAssistant: I'm doing well!"
        
        with patch.object(self.response_capture, '_capture_conversation_area', return_value=conversation_text):
            result = self.response_capture.get_conversation_history(max_messages=4)
            
            assert len(result) > 0
            assert all(isinstance(msg, dict) for msg in result)
            assert all('role' in msg and 'content' in msg for msg in result)
    
    def test_get_conversation_history_window_not_found(self):
        """Test conversation history capture when window not found."""
        self.mock_window_manager.find_chatgpt_window.return_value = None
        
        result = self.response_capture.get_conversation_history()
        
        assert result == []
    
    def test_get_conversation_history_focus_failed(self):
        """Test conversation history capture when window focus fails."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = False
        
        result = self.response_capture.get_conversation_history()
        
        assert result == []
    
    def test_parse_conversation_history_simple(self):
        """Test parsing simple conversation history."""
        conversation_text = """
        Hello there!
        How can I help you today?
        Can you explain quantum physics?
        Quantum physics is the study of matter and energy at the smallest scales.
        """
        
        result = self.response_capture._parse_conversation_history(conversation_text, 10)
        
        assert len(result) > 0
        assert all('role' in msg and 'content' in msg for msg in result)
    
    def test_parse_conversation_history_empty(self):
        """Test parsing empty conversation history."""
        result = self.response_capture._parse_conversation_history("", 10)
        assert result == []
        
        result = self.response_capture._parse_conversation_history(None, 10)
        assert result == []
    
    def test_parse_conversation_history_max_messages(self):
        """Test conversation history parsing with message limit."""
        # Create a long conversation
        conversation_text = "\n".join([f"Message {i}" for i in range(20)])
        
        result = self.response_capture._parse_conversation_history(conversation_text, 5)
        
        assert len(result) <= 5
    
    def test_looks_like_user_message_positive_cases(self):
        """Test user message detection for positive cases."""
        user_messages = [
            "Can you help me?",
            "Please explain this.",
            "How does this work?",
            "What is the answer?",
            "Why is this happening?",
            "When should I do this?",
            "Where can I find it?",
        ]
        
        for message in user_messages:
            result = self.response_capture._looks_like_user_message(message)
            assert result is True, f"Failed to detect user message: '{message}'"
    
    def test_looks_like_user_message_negative_cases(self):
        """Test user message detection for negative cases."""
        assistant_messages = [
            "I can help you with that.",
            "Here's the explanation you requested.",
            "The answer is 42.",
            "This is because of several factors.",
        ]
        
        for message in assistant_messages:
            result = self.response_capture._looks_like_user_message(message)
            assert result is False, f"Incorrectly detected as user message: '{message}'"
    
    def test_configuration_options(self):
        """Test ResponseCapture with custom configuration."""
        config = {
            'response_timeout': 60,
            'polling_interval': 2.0,
            'max_response_length': 100000
        }
        
        response_capture = ResponseCapture(self.mock_window_manager, config)
        
        assert response_capture.response_timeout == 60
        assert response_capture.polling_interval == 2.0
        assert response_capture.max_response_length == 100000
    
    def test_default_configuration(self):
        """Test ResponseCapture with default configuration."""
        response_capture = ResponseCapture(self.mock_window_manager)
        
        assert response_capture.response_timeout == 30
        assert response_capture.polling_interval == 1.0
        assert response_capture.max_response_length == 50000