"""
Unit tests for the WindowManager class in windows_automation module.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Optional, List

from src.windows_automation import (
    WindowManager, 
    WindowInfo, 
    WindowState
)
from src.exceptions import ChatGPTWindowError, SystemError


class TestWindowManager:
    """Test cases for WindowManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.window_manager = WindowManager()
        
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
    
    @patch('src.windows_automation.gw.getWindowsWithTitle')
    @patch('src.windows_automation.win32gui.GetWindowText')
    @patch('src.windows_automation.win32gui.GetWindowRect')
    @patch('src.windows_automation.win32gui.IsWindowVisible')
    @patch('src.windows_automation.win32gui.GetWindowPlacement')
    @patch('src.windows_automation.win32process.GetWindowThreadProcessId')
    def test_find_chatgpt_window_success(self, mock_get_thread_id, mock_get_placement,
                                       mock_is_visible, mock_get_rect, mock_get_text,
                                       mock_get_windows):
        """Test successful ChatGPT window detection."""
        # Setup mocks
        mock_window = Mock()
        mock_window._hWnd = 12345
        mock_window.visible = True
        mock_window.width = 800
        mock_window.height = 600
        mock_get_windows.return_value = [mock_window]
        
        mock_get_text.return_value = "ChatGPT"
        mock_get_rect.return_value = (100, 100, 900, 700)
        mock_is_visible.return_value = True
        mock_get_placement.return_value = (0, 1, (0, 0), (0, 0), (100, 100, 900, 700))
        mock_get_thread_id.return_value = (1234, 9876)
        
        # Test
        result = self.window_manager.find_chatgpt_window()
        
        # Assertions
        assert result is not None
        assert result.handle == 12345
        assert result.title == "ChatGPT"
        assert result.position == (100, 100)
        assert result.size == (800, 600)
        assert result.is_visible is True
        assert result.state == WindowState.NORMAL
        assert result.process_id == 9876
    
    @patch('src.windows_automation.gw.getWindowsWithTitle')
    @patch('src.windows_automation.gw.getAllWindows')
    @patch.object(WindowManager, '_search_by_process_name')
    def test_find_chatgpt_window_not_found(self, mock_search_process, mock_get_all_windows, mock_get_windows):
        """Test when ChatGPT window is not found."""
        mock_get_windows.return_value = []
        mock_get_all_windows.return_value = []
        mock_search_process.return_value = None
        
        result = self.window_manager.find_chatgpt_window()
        
        assert result is None
    
    @patch('src.windows_automation.gw.getWindowsWithTitle')
    def test_find_chatgpt_window_exception(self, mock_get_windows):
        """Test exception handling in window detection."""
        mock_get_windows.side_effect = Exception("Test exception")
        
        with pytest.raises(SystemError):
            self.window_manager.find_chatgpt_window()
    
    def test_is_likely_chatgpt_window_valid(self):
        """Test window validation for likely ChatGPT windows."""
        mock_window = Mock()
        mock_window.visible = True
        mock_window.width = 800
        mock_window.height = 600
        
        result = self.window_manager._is_likely_chatgpt_window(mock_window)
        assert result is True
    
    def test_is_likely_chatgpt_window_too_small(self):
        """Test window validation rejects windows that are too small."""
        mock_window = Mock()
        mock_window.visible = True
        mock_window.width = 200  # Too small
        mock_window.height = 600
        
        result = self.window_manager._is_likely_chatgpt_window(mock_window)
        assert result is False
    
    def test_is_likely_chatgpt_window_not_visible(self):
        """Test window validation rejects invisible windows."""
        mock_window = Mock()
        mock_window.visible = False
        mock_window.width = 800
        mock_window.height = 600
        
        result = self.window_manager._is_likely_chatgpt_window(mock_window)
        assert result is False
    
    def test_matches_chatgpt_pattern_positive_cases(self):
        """Test ChatGPT pattern matching for positive cases."""
        test_cases = [
            "ChatGPT",
            "OpenAI ChatGPT",
            "ChatGPT - OpenAI",
            "Some ChatGPT Window",
            "GPT-4 Interface",
            "OpenAI Application"
        ]
        
        for title in test_cases:
            result = self.window_manager._matches_chatgpt_pattern(title)
            assert result is True, f"Failed for title: {title}"
    
    def test_matches_chatgpt_pattern_negative_cases(self):
        """Test ChatGPT pattern matching for negative cases."""
        test_cases = [
            "Notepad",
            "Chrome Browser",
            "Visual Studio Code",
            "",
            None
        ]
        
        for title in test_cases:
            result = self.window_manager._matches_chatgpt_pattern(title)
            assert result is False, f"Incorrectly matched title: {title}"
    
    @patch('src.windows_automation.win32gui.ShowWindow')
    @patch('src.windows_automation.win32gui.SetForegroundWindow')
    @patch('src.windows_automation.win32gui.BringWindowToTop')
    @patch('src.windows_automation.win32gui.GetForegroundWindow')
    def test_focus_window_success(self, mock_get_foreground, mock_bring_to_top,
                                mock_set_foreground, mock_show_window):
        """Test successful window focusing."""
        mock_get_foreground.return_value = 12345  # Same as our window handle
        
        result = self.window_manager.focus_window(self.mock_window_info)
        
        assert result is True
        mock_set_foreground.assert_called_once_with(12345)
        mock_bring_to_top.assert_called_once_with(12345)
    
    @patch('src.windows_automation.win32gui.ShowWindow')
    @patch('src.windows_automation.win32gui.SetForegroundWindow')
    @patch('src.windows_automation.win32gui.BringWindowToTop')
    @patch('src.windows_automation.win32gui.GetForegroundWindow')
    def test_focus_window_minimized(self, mock_get_foreground, mock_bring_to_top,
                                  mock_set_foreground, mock_show_window):
        """Test focusing a minimized window."""
        minimized_window = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(100, 100),
            size=(800, 600),
            is_visible=True,
            state=WindowState.MINIMIZED,
            process_id=9876
        )
        
        mock_get_foreground.return_value = 12345
        
        result = self.window_manager.focus_window(minimized_window)
        
        assert result is True
        mock_show_window.assert_called_once()  # Should restore window
        mock_set_foreground.assert_called_once_with(12345)
    
    @patch('src.windows_automation.win32gui.SetWindowPos')
    def test_position_window_success(self, mock_set_window_pos):
        """Test successful window positioning."""
        result = self.window_manager.position_window(
            self.mock_window_info, 200, 150, 1000, 800
        )
        
        assert result is True
        mock_set_window_pos.assert_called_once()
    
    @patch('src.windows_automation.win32gui.SetWindowPos')
    def test_position_window_keep_current_size(self, mock_set_window_pos):
        """Test window positioning while keeping current size."""
        result = self.window_manager.position_window(
            self.mock_window_info, 200, 150
        )
        
        assert result is True
        # Should use current size (800, 600) from mock_window_info
        args = mock_set_window_pos.call_args[0]
        assert args[4] == 800  # width
        assert args[5] == 600  # height
    
    @patch('src.windows_automation.win32gui.IsWindow')
    @patch('src.windows_automation.win32gui.IsWindowVisible')
    def test_validate_window_state_valid(self, mock_is_visible, mock_is_window):
        """Test window state validation for valid window."""
        mock_is_window.return_value = True
        mock_is_visible.return_value = True
        
        result = self.window_manager.validate_window_state(self.mock_window_info)
        
        assert result is True
    
    @patch('src.windows_automation.win32gui.IsWindow')
    def test_validate_window_state_invalid_handle(self, mock_is_window):
        """Test window state validation for invalid handle."""
        mock_is_window.return_value = False
        
        result = self.window_manager.validate_window_state(self.mock_window_info)
        
        assert result is False
    
    @patch('src.windows_automation.win32gui.IsWindow')
    @patch('src.windows_automation.win32gui.IsWindowVisible')
    def test_validate_window_state_not_visible(self, mock_is_visible, mock_is_window):
        """Test window state validation for invisible window."""
        mock_is_window.return_value = True
        mock_is_visible.return_value = False
        
        result = self.window_manager.validate_window_state(self.mock_window_info)
        
        assert result is False
    
    def test_validate_window_state_too_small(self):
        """Test window state validation for window that's too small."""
        small_window = WindowInfo(
            handle=12345,
            title="ChatGPT",
            position=(100, 100),
            size=(200, 100),  # Too small
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
        
        with patch('src.windows_automation.win32gui.IsWindow', return_value=True), \
             patch('src.windows_automation.win32gui.IsWindowVisible', return_value=True):
            
            result = self.window_manager.validate_window_state(small_window)
            assert result is False
    
    def test_cache_functionality(self):
        """Test window handle caching functionality."""
        # Test cache timeout
        self.window_manager.cached_window_handle = 12345
        self.window_manager.last_cache_time = time.time() - 100  # Old cache
        
        with patch('src.windows_automation.win32gui.IsWindow', return_value=True):
            result = self.window_manager._is_cache_valid()
            assert result is False  # Should be invalid due to timeout
    
    @patch('src.windows_automation.win32gui.IsWindow')
    def test_is_window_valid(self, mock_is_window):
        """Test window handle validation."""
        mock_is_window.return_value = True
        
        result = self.window_manager._is_window_valid(12345)
        assert result is True
        
        mock_is_window.return_value = False
        result = self.window_manager._is_window_valid(12345)
        assert result is False
    
    @patch('src.windows_automation.gw.getWindowsWithTitle')
    def test_get_all_chatgpt_windows(self, mock_get_windows):
        """Test getting all ChatGPT windows."""
        # Setup multiple mock windows
        mock_window1 = Mock()
        mock_window1._hWnd = 12345
        mock_window1.visible = True
        mock_window1.width = 800
        mock_window1.height = 600
        
        mock_window2 = Mock()
        mock_window2._hWnd = 67890
        mock_window2.visible = True
        mock_window2.width = 1000
        mock_window2.height = 700
        
        mock_get_windows.return_value = [mock_window1, mock_window2]
        
        with patch.object(self.window_manager, '_create_window_info') as mock_create:
            mock_create.side_effect = [
                WindowInfo(12345, "ChatGPT 1", (0, 0), (800, 600), True, WindowState.NORMAL, 1),
                WindowInfo(67890, "ChatGPT 2", (0, 0), (1000, 700), True, WindowState.NORMAL, 2)
            ]
            
            result = self.window_manager.get_all_chatgpt_windows()
            
            assert len(result) == 2
            assert result[0].handle == 12345
            assert result[1].handle == 67890


class TestWindowInfo:
    """Test cases for WindowInfo dataclass."""
    
    def test_window_info_creation(self):
        """Test WindowInfo object creation."""
        window_info = WindowInfo(
            handle=12345,
            title="Test Window",
            position=(100, 200),
            size=(800, 600),
            is_visible=True,
            state=WindowState.NORMAL,
            process_id=9876
        )
        
        assert window_info.handle == 12345
        assert window_info.title == "Test Window"
        assert window_info.position == (100, 200)
        assert window_info.size == (800, 600)
        assert window_info.is_visible is True
        assert window_info.state == WindowState.NORMAL
        assert window_info.process_id == 9876


class TestWindowState:
    """Test cases for WindowState enum."""
    
    def test_window_state_values(self):
        """Test WindowState enum values."""
        assert WindowState.NORMAL.value == "normal"
        assert WindowState.MINIMIZED.value == "minimized"
        assert WindowState.MAXIMIZED.value == "maximized"
        assert WindowState.HIDDEN.value == "hidden"
        assert WindowState.NOT_FOUND.value == "not_found"


class TestChatGPTWindowError:
    """Test cases for ChatGPTWindowError exception."""
    
    def test_exception_creation(self):
        """Test ChatGPTWindowError exception creation."""
        error = ChatGPTWindowError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)