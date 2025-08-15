"""
Unit tests for the MessageSender class in windows_automation module.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, Tuple

from src.windows_automation import (
    MessageSender, 
    WindowManager, 
    WindowInfo, 
    WindowState, 
    ChatGPTWindowError
)


class TestMessageSender:
    """Test cases for MessageSender class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_window_manager = Mock(spec=WindowManager)
        self.message_sender = MessageSender(self.mock_window_manager)
        
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
    
    @patch('src.windows_automation.pyautogui.click')
    @patch('src.windows_automation.pyautogui.press')
    @patch('src.windows_automation.time.sleep')
    def test_send_message_success_typing(self, mock_sleep, mock_press, mock_click):
        """Test successful message sending using typing method."""
        # Setup mocks
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        self.mock_window_manager.validate_window_state.return_value = True
        
        message = "Hello, ChatGPT!"
        
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)), \
             patch.object(self.message_sender, '_send_via_typing', return_value=True):
            
            result = self.message_sender.send_message(message, use_clipboard=False)
            
            assert result is True
            mock_click.assert_called_once_with(400, 500)
            mock_press.assert_called_once_with('enter')
    
    @patch('src.windows_automation.pyautogui.click')
    @patch('src.windows_automation.pyautogui.press')
    @patch('src.windows_automation.time.sleep')
    def test_send_message_success_clipboard(self, mock_sleep, mock_press, mock_click):
        """Test successful message sending using clipboard method."""
        # Setup mocks
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        self.mock_window_manager.validate_window_state.return_value = True
        
        message = "A" * 1000  # Long message
        
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)), \
             patch.object(self.message_sender, '_send_via_clipboard', return_value=True):
            
            result = self.message_sender.send_message(message, use_clipboard=True)
            
            assert result is True
            mock_click.assert_called_once_with(400, 500)
            mock_press.assert_called_once_with('enter')
    
    def test_send_message_window_not_found(self):
        """Test message sending when ChatGPT window is not found."""
        self.mock_window_manager.find_chatgpt_window.return_value = None
        
        result = self.message_sender.send_message("Test message")
        
        assert result is False
    
    def test_send_message_focus_failed(self):
        """Test message sending when window focus fails."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = False
        
        result = self.message_sender.send_message("Test message")
        
        assert result is False
    
    @patch('src.windows_automation.pyautogui.click')
    def test_send_message_input_field_not_found(self, mock_click):
        """Test message sending when input field cannot be found."""
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        self.mock_window_manager.validate_window_state.return_value = True
        
        with patch.object(self.message_sender, '_find_input_field', return_value=None):
            result = self.message_sender.send_message("Test message")
            
            assert result is False
            mock_click.assert_not_called()
    
    def test_find_input_field_success(self):
        """Test successful input field detection."""
        window_info = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(100, 100),
            size=(800, 600),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
        
        result = self.message_sender._find_input_field(window_info)
        
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) == 2
        
        # Check that coordinates are within window bounds
        x, y = result
        assert 100 <= x <= 900  # window_x to window_x + width
        assert 100 <= y <= 700  # window_y to window_y + height
    
    def test_find_input_field_small_window(self):
        """Test input field detection with a small window."""
        small_window = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(0, 0),
            size=(300, 200),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
        
        result = self.message_sender._find_input_field(small_window)
        
        # Should still find a position within bounds
        assert result is not None
        x, y = result
        assert 0 <= x <= 300
        assert 0 <= y <= 200
    
    @patch('src.windows_automation.pyautogui.hotkey')
    @patch('src.windows_automation.pyautogui.write')
    @patch('src.windows_automation.time.sleep')
    def test_send_via_typing_success(self, mock_sleep, mock_write, mock_hotkey):
        """Test successful message typing."""
        message = "Hello!"
        
        result = self.message_sender._send_via_typing(message)
        
        assert result is True
        mock_hotkey.assert_called_with('ctrl', 'a')  # Clear existing text
        assert mock_write.call_count == len(message)  # One call per character
    
    @patch('src.windows_automation.pyautogui.hotkey')
    @patch('src.windows_automation.pyautogui.write')
    @patch('src.windows_automation.pyautogui.press')
    def test_send_via_typing_with_newlines(self, mock_press, mock_write, mock_hotkey):
        """Test typing message with newline characters."""
        message = "Line 1\nLine 2\rLine 3"
        
        result = self.message_sender._send_via_typing(message)
        
        assert result is True
        # Should handle newlines with shift+enter
        assert mock_press.call_count == 2  # Two newline characters
        mock_press.assert_called_with('shift', 'enter')
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('src.windows_automation.pyautogui.hotkey')
    @patch('src.windows_automation.time.sleep')
    def test_send_via_clipboard_success(self, mock_sleep, mock_hotkey, mock_copy, mock_paste):
        """Test successful message pasting via clipboard."""
        message = "Hello, clipboard!"
        original_clipboard = "original content"
        
        mock_paste.return_value = original_clipboard
        
        result = self.message_sender._send_via_clipboard(message)
        
        assert result is True
        
        # Check clipboard operations
        assert mock_copy.call_count == 2  # Copy message, then restore original
        mock_copy.assert_any_call(message)
        mock_copy.assert_any_call(original_clipboard)
        
        # Check keyboard operations
        mock_hotkey.assert_any_call('ctrl', 'a')  # Select all
        mock_hotkey.assert_any_call('ctrl', 'v')  # Paste
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('src.windows_automation.pyautogui.hotkey')
    def test_send_via_clipboard_no_original_content(self, mock_hotkey, mock_copy, mock_paste):
        """Test clipboard pasting when original clipboard is empty."""
        message = "Test message"
        
        mock_paste.side_effect = Exception("No clipboard content")
        
        result = self.message_sender._send_via_clipboard(message)
        
        assert result is True
        mock_copy.assert_called_once_with(message)  # Only copy message, no restore
    
    @patch('builtins.__import__', side_effect=ImportError("No module named 'pyperclip'"))
    def test_send_via_clipboard_fallback_to_typing(self, mock_import):
        """Test clipboard method falling back to typing when pyperclip unavailable."""
        message = "Test message"
        
        with patch.object(self.message_sender, '_send_via_typing', return_value=True) as mock_typing:
            result = self.message_sender._send_via_clipboard(message)
            
            assert result is True
            mock_typing.assert_called_once_with(message)
    
    @patch('src.windows_automation.pyautogui.click')
    @patch('src.windows_automation.pyautogui.write')
    @patch('src.windows_automation.pyautogui.press')
    @patch('src.windows_automation.time.sleep')
    def test_validate_input_field_success(self, mock_sleep, mock_press, mock_write, mock_click):
        """Test successful input field validation."""
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)):
            result = self.message_sender.validate_input_field(self.mock_window_info)
            
            assert result is True
            mock_click.assert_called_once_with(400, 500)
            mock_write.assert_called_once_with('a')
            mock_press.assert_called_once_with('backspace')
    
    def test_validate_input_field_not_found(self):
        """Test input field validation when field cannot be found."""
        with patch.object(self.message_sender, '_find_input_field', return_value=None):
            result = self.message_sender.validate_input_field(self.mock_window_info)
            
            assert result is False
    
    @patch('src.windows_automation.pyautogui.click')
    @patch('src.windows_automation.pyautogui.hotkey')
    @patch('src.windows_automation.pyautogui.press')
    @patch('src.windows_automation.time.sleep')
    def test_clear_input_field_success(self, mock_sleep, mock_press, mock_hotkey, mock_click):
        """Test successful input field clearing."""
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)):
            result = self.message_sender.clear_input_field(self.mock_window_info)
            
            assert result is True
            mock_click.assert_called_once_with(400, 500)
            mock_hotkey.assert_called_once_with('ctrl', 'a')
            mock_press.assert_called_once_with('delete')
    
    def test_clear_input_field_not_found(self):
        """Test input field clearing when field cannot be found."""
        with patch.object(self.message_sender, '_find_input_field', return_value=None):
            result = self.message_sender.clear_input_field(self.mock_window_info)
            
            assert result is False
    
    def test_auto_clipboard_decision_short_message(self):
        """Test automatic clipboard decision for short messages."""
        # Setup mocks
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        self.mock_window_manager.validate_window_state.return_value = True
        
        short_message = "Short message"
        
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)), \
             patch.object(self.message_sender, '_send_via_typing', return_value=True) as mock_typing, \
             patch.object(self.message_sender, '_send_via_clipboard', return_value=True) as mock_clipboard, \
             patch('src.windows_automation.pyautogui.click'), \
             patch('src.windows_automation.pyautogui.press'):
            
            result = self.message_sender.send_message(short_message)
            
            assert result is True
            mock_typing.assert_called_once()
            mock_clipboard.assert_not_called()
    
    def test_auto_clipboard_decision_long_message(self):
        """Test automatic clipboard decision for long messages."""
        # Setup mocks
        self.mock_window_manager.find_chatgpt_window.return_value = self.mock_window_info
        self.mock_window_manager.focus_window.return_value = True
        self.mock_window_manager.validate_window_state.return_value = True
        
        long_message = "A" * 1000  # Long message exceeding clipboard threshold
        
        with patch.object(self.message_sender, '_find_input_field', return_value=(400, 500)), \
             patch.object(self.message_sender, '_send_via_typing', return_value=True) as mock_typing, \
             patch.object(self.message_sender, '_send_via_clipboard', return_value=True) as mock_clipboard, \
             patch('src.windows_automation.pyautogui.click'), \
             patch('src.windows_automation.pyautogui.press'):
            
            result = self.message_sender.send_message(long_message)
            
            assert result is True
            mock_clipboard.assert_called_once()
            mock_typing.assert_not_called()
    
    def test_configuration_options(self):
        """Test MessageSender with custom configuration."""
        config = {
            'typing_delay': 0.1,
            'max_message_length': 5000,
            'clipboard_threshold': 1000
        }
        
        message_sender = MessageSender(self.mock_window_manager, config)
        
        assert message_sender.typing_delay == 0.1
        assert message_sender.max_message_length == 5000
        assert message_sender.clipboard_threshold == 1000
    
    def test_default_configuration(self):
        """Test MessageSender with default configuration."""
        message_sender = MessageSender(self.mock_window_manager)
        
        assert message_sender.typing_delay == 0.05
        assert message_sender.max_message_length == 2000
        assert message_sender.clipboard_threshold == 500