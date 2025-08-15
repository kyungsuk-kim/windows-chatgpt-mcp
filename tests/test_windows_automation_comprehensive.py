"""
Comprehensive unit tests for Windows automation functionality.

This module provides extensive mocked tests for Windows automation components
without requiring actual GUI interaction.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from typing import Dict, Any, List, Optional

from src.windows_automation import (
    WindowManager, MessageSender, ResponseCapture, WindowInfo, WindowState, WindowsAutomationHandler
)
from src.config import ConfigManager, WindowDetectionConfig, AutomationConfig
from src.exceptions import (
    ChatGPTWindowError, AutomationError, ResponseTimeoutError
)


class TestWindowsAutomationHandlerMocked:
    """Comprehensive mocked tests for WindowsAutomationHandler."""
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        config_manager = Mock(spec=ConfigManager)
        
        # Mock window detection config
        window_config = Mock(spec=WindowDetectionConfig)
        window_config.window_title_patterns = ["ChatGPT"]
        window_config.window_class_names = ["Chrome_WidgetWin_1"]
        window_config.search_timeout = 10.0
        window_config.focus_retry_attempts = 3
        window_config.focus_retry_delay = 1.0
        
        # Mock automation config
        automation_config = Mock(spec=AutomationConfig)
        automation_config.typing_delay = 0.05
        automation_config.response_timeout = 30.0
        automation_config.response_check_interval = 2.0
        automation_config.max_response_wait_time = 60.0
        automation_config.clipboard_fallback_threshold = 1000
        automation_config.screenshot_on_error = True
        
        config_manager.window_detection = window_config
        config_manager.automation = automation_config
        
        return config_manager
    
    @pytest.fixture
    def automation_handler(self, mock_config_manager):
        """Create a WindowsAutomationHandler with mocked dependencies."""
        with patch('src.windows_automation.WindowManager') as mock_window_manager_class, \
             patch('src.windows_automation.MessageSender') as mock_message_sender_class, \
             patch('src.windows_automation.ResponseCapture') as mock_response_capture_class:
            
            # Create mock instances
            mock_window_manager = Mock()
            mock_message_sender = Mock()
            mock_response_capture = Mock()
            
            # Configure mock classes to return mock instances
            mock_window_manager_class.return_value = mock_window_manager
            mock_message_sender_class.return_value = mock_message_sender
            mock_response_capture_class.return_value = mock_response_capture
            
            handler = WindowsAutomationHandler(mock_config_manager)
            
            # Store mock references for test access
            handler._mock_window_manager = mock_window_manager
            handler._mock_message_sender = mock_message_sender
            handler._mock_response_capture = mock_response_capture
            
            return handler
    
    def test_initialization(self, automation_handler, mock_config_manager):
        """Test WindowsAutomationHandler initialization."""
        assert automation_handler.config_manager == mock_config_manager
        assert automation_handler.window_manager is not None
        assert automation_handler.message_sender is not None
        assert automation_handler.response_capture is not None
    
    @pytest.mark.asyncio
    async def test_send_message_and_get_response_success(self, automation_handler):
        """Test successful message sending and response retrieval."""
        # Configure mocks
        automation_handler._mock_window_manager.ensure_chatgpt_window_active = AsyncMock()
        automation_handler._mock_message_sender.send_message = AsyncMock()
        automation_handler._mock_response_capture.wait_for_response = AsyncMock(
            return_value="This is a test response from ChatGPT."
        )
        
        # Test the method
        message = "Hello, ChatGPT!"
        timeout = 30
        response = await automation_handler.send_message_and_get_response(message, timeout)
        
        # Verify calls
        automation_handler._mock_window_manager.ensure_chatgpt_window_active.assert_called_once()
        automation_handler._mock_message_sender.send_message.assert_called_once_with(message)
        automation_handler._mock_response_capture.wait_for_response.assert_called_once_with(timeout)
        
        # Verify response
        assert response == "This is a test response from ChatGPT."
    
    @pytest.mark.asyncio
    async def test_send_message_window_not_found(self, automation_handler):
        """Test handling when ChatGPT window is not found."""
        # Configure mock to raise window error
        automation_handler._mock_window_manager.ensure_chatgpt_window_active = AsyncMock(
            side_effect=ChatGPTWindowError("ChatGPT window not found", "window_detection")
        )
        
        # Test that error is propagated
        with pytest.raises(ChatGPTWindowError):
            await automation_handler.send_message_and_get_response("Hello", 30)
    
    @pytest.mark.asyncio
    async def test_send_message_timeout(self, automation_handler):
        """Test handling of response timeout."""
        # Configure mocks
        automation_handler._mock_window_manager.ensure_chatgpt_window_active = AsyncMock()
        automation_handler._mock_message_sender.send_message = AsyncMock()
        automation_handler._mock_response_capture.wait_for_response = AsyncMock(
            side_effect=ResponseTimeoutError("Response timeout", "response_capture", timeout=30)
        )
        
        # Test that timeout error is propagated
        with pytest.raises(ResponseTimeoutError):
            await automation_handler.send_message_and_get_response("Hello", 30)
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_success(self, automation_handler):
        """Test successful conversation history retrieval."""
        mock_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        automation_handler._mock_conversation_manager.get_conversation_history = AsyncMock(
            return_value=mock_history
        )
        
        result = await automation_handler.get_conversation_history(10)
        
        automation_handler._mock_conversation_manager.get_conversation_history.assert_called_once_with(10)
        assert result == mock_history
    
    @pytest.mark.asyncio
    async def test_reset_conversation_success(self, automation_handler):
        """Test successful conversation reset."""
        automation_handler._mock_conversation_manager.reset_conversation = AsyncMock(
            return_value=True
        )
        
        result = await automation_handler.reset_conversation()
        
        automation_handler._mock_conversation_manager.reset_conversation.assert_called_once()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_reset_conversation_failure(self, automation_handler):
        """Test conversation reset failure."""
        automation_handler._mock_conversation_manager.reset_conversation = AsyncMock(
            return_value=False
        )
        
        result = await automation_handler.reset_conversation()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup(self, automation_handler):
        """Test cleanup process."""
        # Configure cleanup methods
        automation_handler._mock_window_manager.cleanup = AsyncMock()
        automation_handler._mock_message_sender.cleanup = AsyncMock()
        automation_handler._mock_response_capture.cleanup = AsyncMock()
        automation_handler._mock_conversation_manager.cleanup = AsyncMock()
        
        await automation_handler.cleanup()
        
        # Verify all cleanup methods were called
        automation_handler._mock_window_manager.cleanup.assert_called_once()
        automation_handler._mock_message_sender.cleanup.assert_called_once()
        automation_handler._mock_response_capture.cleanup.assert_called_once()
        automation_handler._mock_conversation_manager.cleanup.assert_called_once()


class TestWindowManagerMocked:
    """Mocked tests for WindowManager component."""
    
    @pytest.fixture
    def window_manager(self):
        """Create a WindowManager with mocked dependencies."""
        config = Mock()
        config.window_title_patterns = ["ChatGPT"]
        config.window_class_names = ["Chrome_WidgetWin_1"]
        config.search_timeout = 10.0
        config.focus_retry_attempts = 3
        config.focus_retry_delay = 1.0
        
        with patch('src.windows_automation.gw') as mock_pygetwindow, \
             patch('src.windows_automation.win32gui') as mock_win32gui, \
             patch('src.windows_automation.win32con') as mock_win32con:
            
            manager = WindowManager(config)
            manager._mock_pygetwindow = mock_pygetwindow
            manager._mock_win32gui = mock_win32gui
            manager._mock_win32con = mock_win32con
            
            return manager
    
    @pytest.mark.asyncio
    async def test_find_chatgpt_window_success(self, window_manager):
        """Test successful ChatGPT window detection."""
        # Mock window object
        mock_window = Mock()
        mock_window.title = "ChatGPT - Chrome"
        mock_window._hWnd = 12345
        mock_window.isActive = False
        mock_window.activate = Mock()
        
        window_manager._mock_pygetwindow.getWindowsWithTitle.return_value = [mock_window]
        
        result = await window_manager.find_chatgpt_window()
        
        assert result == mock_window
        window_manager._mock_pygetwindow.getWindowsWithTitle.assert_called()
    
    @pytest.mark.asyncio
    async def test_find_chatgpt_window_not_found(self, window_manager):
        """Test ChatGPT window not found scenario."""
        window_manager._mock_pygetwindow.getWindowsWithTitle.return_value = []
        
        with pytest.raises(ChatGPTWindowError):
            await window_manager.find_chatgpt_window()
    
    @pytest.mark.asyncio
    async def test_ensure_window_active_success(self, window_manager):
        """Test successful window activation."""
        mock_window = Mock()
        mock_window.isActive = False
        mock_window.activate = Mock()
        
        with patch.object(window_manager, 'find_chatgpt_window', return_value=mock_window):
            await window_manager.ensure_chatgpt_window_active()
            
            mock_window.activate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ensure_window_active_already_active(self, window_manager):
        """Test when window is already active."""
        mock_window = Mock()
        mock_window.isActive = True
        mock_window.activate = Mock()
        
        with patch.object(window_manager, 'find_chatgpt_window', return_value=mock_window):
            await window_manager.ensure_chatgpt_window_active()
            
            # Should not call activate if already active
            mock_window.activate.assert_not_called()


class TestMessageSenderMocked:
    """Mocked tests for MessageSender component."""
    
    @pytest.fixture
    def message_sender(self):
        """Create a MessageSender with mocked dependencies."""
        config = Mock()
        config.typing_delay = 0.05
        config.clipboard_fallback_threshold = 1000
        
        with patch('src.windows_automation.pyautogui') as mock_pyautogui, \
             patch('src.windows_automation.pyperclip') as mock_pyperclip:
            
            sender = MessageSender(config)
            sender._mock_pyautogui = mock_pyautogui
            sender._mock_pyperclip = mock_pyperclip
            
            return sender
    
    @pytest.mark.asyncio
    async def test_send_message_short_text(self, message_sender):
        """Test sending short message via typing."""
        message = "Hello, ChatGPT!"
        
        await message_sender.send_message(message)
        
        # Should use typing for short messages
        message_sender._mock_pyautogui.write.assert_called_once_with(
            message, interval=0.05
        )
        message_sender._mock_pyautogui.press.assert_called_once_with('enter')
    
    @pytest.mark.asyncio
    async def test_send_message_long_text_clipboard(self, message_sender):
        """Test sending long message via clipboard."""
        message = "x" * 1500  # Long message exceeding threshold
        
        await message_sender.send_message(message)
        
        # Should use clipboard for long messages
        message_sender._mock_pyperclip.copy.assert_called_once_with(message)
        message_sender._mock_pyautogui.hotkey.assert_called_with('ctrl', 'v')
        message_sender._mock_pyautogui.press.assert_called_with('enter')
    
    @pytest.mark.asyncio
    async def test_send_message_automation_error(self, message_sender):
        """Test handling of automation errors during message sending."""
        message_sender._mock_pyautogui.write.side_effect = Exception("Automation failed")
        
        with pytest.raises(AutomationError):
            await message_sender.send_message("Hello")


class TestResponseCaptureMocked:
    """Mocked tests for ResponseCapture component."""
    
    @pytest.fixture
    def response_capture(self):
        """Create a ResponseCapture with mocked dependencies."""
        config = Mock()
        config.response_timeout = 30.0
        config.response_check_interval = 2.0
        config.max_response_wait_time = 60.0
        
        with patch('src.windows_automation.pyautogui') as mock_pyautogui:
            capture = ResponseCapture(config)
            capture._mock_pyautogui = mock_pyautogui
            
            return capture
    
    @pytest.mark.asyncio
    async def test_wait_for_response_success(self, response_capture):
        """Test successful response capture."""
        # Mock screenshot and text extraction
        mock_screenshot = Mock()
        response_capture._mock_pyautogui.screenshot.return_value = mock_screenshot
        
        with patch.object(response_capture, '_extract_text_from_screenshot', 
                         return_value="This is the response from ChatGPT."):
            
            result = await response_capture.wait_for_response(30)
            
            assert result == "This is the response from ChatGPT."
    
    @pytest.mark.asyncio
    async def test_wait_for_response_timeout(self, response_capture):
        """Test response capture timeout."""
        # Mock screenshot that never finds response
        response_capture._mock_pyautogui.screenshot.return_value = Mock()
        
        with patch.object(response_capture, '_extract_text_from_screenshot', 
                         return_value=None), \
             patch('asyncio.sleep', new_callable=AsyncMock):
            
            with pytest.raises(ResponseTimeoutError):
                await response_capture.wait_for_response(1)  # Short timeout for test


class TestConversationManagerMocked:
    """Mocked tests for ConversationManager component."""
    
    @pytest.fixture
    def conversation_manager(self):
        """Create a ConversationManager with mocked dependencies."""
        with patch('src.windows_automation.pyautogui') as mock_pyautogui:
            manager = ConversationManager()
            manager._mock_pyautogui = mock_pyautogui
            
            return manager
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_success(self, conversation_manager):
        """Test successful conversation history retrieval."""
        mock_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        with patch.object(conversation_manager, '_extract_conversation_from_ui',
                         return_value=mock_history):
            
            result = await conversation_manager.get_conversation_history(10)
            
            assert result == mock_history
    
    @pytest.mark.asyncio
    async def test_reset_conversation_success(self, conversation_manager):
        """Test successful conversation reset."""
        # Mock finding and clicking new chat button
        conversation_manager._mock_pyautogui.locateOnScreen.return_value = (100, 100, 50, 30)
        conversation_manager._mock_pyautogui.center.return_value = (125, 115)
        
        result = await conversation_manager.reset_conversation()
        
        assert result is True
        conversation_manager._mock_pyautogui.click.assert_called_once_with(125, 115)
    
    @pytest.mark.asyncio
    async def test_reset_conversation_button_not_found(self, conversation_manager):
        """Test conversation reset when button is not found."""
        conversation_manager._mock_pyautogui.locateOnScreen.return_value = None
        
        result = await conversation_manager.reset_conversation()
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])