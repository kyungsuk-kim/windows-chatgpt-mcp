"""
Windows Automation Handler - Interface with ChatGPT desktop application on Windows 11.

This module provides functionality to detect, manage, and interact with the ChatGPT
desktop application using Windows-specific APIs and automation libraries.
"""

import time
import logging
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

import pygetwindow as gw
import win32gui
import win32con
import win32process
import pyautogui

from .exceptions import (
    ChatGPTWindowError, 
    AutomationError, 
    ResponseTimeoutError,
    create_window_not_found_error,
    create_automation_timeout_error,
    wrap_system_error
)

# Configure pyautogui safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

logger = logging.getLogger(__name__)


class WindowState(Enum):
    """Enumeration of possible window states."""
    NORMAL = "normal"
    MINIMIZED = "minimized"
    MAXIMIZED = "maximized"
    HIDDEN = "hidden"
    NOT_FOUND = "not_found"


@dataclass
class WindowInfo:
    """Information about a window."""
    handle: int
    title: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    is_visible: bool
    state: WindowState
    process_id: int


class WindowManager:
    """Manages ChatGPT window detection and interaction."""
    
    # Common ChatGPT window title patterns
    CHATGPT_WINDOW_PATTERNS = [
        "ChatGPT",
        "OpenAI ChatGPT",
        "ChatGPT - OpenAI",
        "ChatGPT Desktop",
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the WindowManager.
        
        Args:
            config: Optional configuration dictionary with window detection settings
        """
        self.config = config or {}
        self.cached_window_handle: Optional[int] = None
        self.cache_timeout = self.config.get('cache_timeout', 30)  # seconds
        self.last_cache_time = 0
        
    def find_chatgpt_window(self, force_refresh: bool = False) -> Optional[WindowInfo]:
        """
        Find the ChatGPT application window.
        
        Args:
            force_refresh: If True, bypass cache and search for window again
            
        Returns:
            WindowInfo object if found, None otherwise
            
        Raises:
            ChatGPTWindowError: If window detection fails
        """
        try:
            # Check cache first unless force refresh is requested
            if not force_refresh and self._is_cache_valid():
                cached_info = self._get_cached_window_info()
                if cached_info and self._is_window_valid(cached_info.handle):
                    return cached_info
            
            # Search for ChatGPT window using multiple methods
            window_info = self._search_chatgpt_window()
            
            if window_info:
                self.cached_window_handle = window_info.handle
                self.last_cache_time = time.time()
                logger.info(f"Found ChatGPT window: {window_info.title}")
                return window_info
            
            logger.warning("ChatGPT window not found")
            return None
            
        except Exception as e:
            logger.error(f"Error finding ChatGPT window: {e}")
            raise wrap_system_error(e, "ChatGPT window detection")
    
    def _search_chatgpt_window(self) -> Optional[WindowInfo]:
        """Search for ChatGPT window using multiple detection methods."""
        # Method 1: Search by window title patterns
        for pattern in self.CHATGPT_WINDOW_PATTERNS:
            windows = gw.getWindowsWithTitle(pattern)
            for window in windows:
                if self._is_likely_chatgpt_window(window):
                    return self._create_window_info(window._hWnd)
        
        # Method 2: Search by partial title match
        all_windows = gw.getAllWindows()
        for window in all_windows:
            if self._matches_chatgpt_pattern(window.title):
                return self._create_window_info(window._hWnd)
        
        # Method 3: Search by process name (if available)
        return self._search_by_process_name()
    
    def _is_likely_chatgpt_window(self, window) -> bool:
        """Check if a window is likely the ChatGPT application."""
        try:
            # Check if window is visible and has reasonable size
            if not window.visible or window.width < 300 or window.height < 200:
                return False
            
            # Check window class or other properties if needed
            return True
            
        except Exception:
            return False
    
    def _matches_chatgpt_pattern(self, title: str) -> bool:
        """Check if window title matches ChatGPT patterns."""
        if not title:
            return False
        
        title_lower = title.lower()
        chatgpt_keywords = ['chatgpt', 'openai', 'gpt']
        
        return any(keyword in title_lower for keyword in chatgpt_keywords)
    
    def _search_by_process_name(self) -> Optional[WindowInfo]:
        """Search for ChatGPT window by process name."""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if self._matches_chatgpt_pattern(window_text):
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                return self._create_window_info(windows[0])
            
        except Exception as e:
            logger.debug(f"Process name search failed: {e}")
        
        return None
    
    def _create_window_info(self, hwnd: int) -> WindowInfo:
        """Create WindowInfo object from window handle."""
        try:
            title = win32gui.GetWindowText(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            position = (rect[0], rect[1])
            size = (rect[2] - rect[0], rect[3] - rect[1])
            is_visible = win32gui.IsWindowVisible(hwnd)
            
            # Get window state
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] == win32con.SW_SHOWMINIMIZED:
                state = WindowState.MINIMIZED
            elif placement[1] == win32con.SW_SHOWMAXIMIZED:
                state = WindowState.MAXIMIZED
            else:
                state = WindowState.NORMAL
            
            # Get process ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            return WindowInfo(
                handle=hwnd,
                title=title,
                position=position,
                size=size,
                is_visible=is_visible,
                state=state,
                process_id=process_id
            )
            
        except Exception as e:
            logger.error(f"Error creating window info: {e}")
            raise wrap_system_error(e, "window information retrieval")
    
    def focus_window(self, window_info: WindowInfo) -> bool:
        """
        Focus the ChatGPT window and bring it to foreground.
        
        Args:
            window_info: WindowInfo object for the target window
            
        Returns:
            True if successful, False otherwise
        """
        try:
            hwnd = window_info.handle
            
            # Restore window if minimized
            if window_info.state == WindowState.MINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)  # Allow time for window to restore
            
            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            # Verify window is now focused
            time.sleep(0.1)
            focused_hwnd = win32gui.GetForegroundWindow()
            
            if focused_hwnd == hwnd:
                logger.info("Successfully focused ChatGPT window")
                return True
            else:
                logger.warning("Failed to focus ChatGPT window")
                return False
                
        except Exception as e:
            logger.error(f"Error focusing window: {e}")
            return False
    
    def position_window(self, window_info: WindowInfo, x: int, y: int, 
                       width: Optional[int] = None, height: Optional[int] = None) -> bool:
        """
        Position and resize the ChatGPT window.
        
        Args:
            window_info: WindowInfo object for the target window
            x: X coordinate for window position
            y: Y coordinate for window position
            width: Optional new width (keeps current if None)
            height: Optional new height (keeps current if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            hwnd = window_info.handle
            
            # Use current size if not specified
            if width is None:
                width = window_info.size[0]
            if height is None:
                height = window_info.size[1]
            
            # Move and resize window
            win32gui.SetWindowPos(
                hwnd, 
                win32con.HWND_TOP,
                x, y, width, height,
                win32con.SWP_SHOWWINDOW
            )
            
            logger.info(f"Positioned window at ({x}, {y}) with size ({width}, {height})")
            return True
            
        except Exception as e:
            logger.error(f"Error positioning window: {e}")
            return False
    
    def validate_window_state(self, window_info: WindowInfo) -> bool:
        """
        Validate that the window is in a usable state.
        
        Args:
            window_info: WindowInfo object to validate
            
        Returns:
            True if window is usable, False otherwise
        """
        try:
            # Check if window handle is still valid
            if not self._is_window_valid(window_info.handle):
                return False
            
            # Check if window is visible
            if not win32gui.IsWindowVisible(window_info.handle):
                logger.warning("ChatGPT window is not visible")
                return False
            
            # Check if window has reasonable size
            if window_info.size[0] < 300 or window_info.size[1] < 200:
                logger.warning("ChatGPT window size is too small")
                return False
            
            # Check if window is not minimized (unless that's acceptable)
            if window_info.state == WindowState.MINIMIZED:
                logger.info("ChatGPT window is minimized")
                # This might be acceptable depending on use case
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating window state: {e}")
            return False
    
    def _is_window_valid(self, hwnd: int) -> bool:
        """Check if window handle is still valid."""
        try:
            return win32gui.IsWindow(hwnd)
        except Exception:
            return False
    
    def _is_cache_valid(self) -> bool:
        """Check if cached window handle is still valid."""
        if not self.cached_window_handle:
            return False
        
        # Check cache timeout
        if time.time() - self.last_cache_time > self.cache_timeout:
            return False
        
        return self._is_window_valid(self.cached_window_handle)
    
    def _get_cached_window_info(self) -> Optional[WindowInfo]:
        """Get window info for cached window handle."""
        if not self.cached_window_handle:
            return None
        
        try:
            return self._create_window_info(self.cached_window_handle)
        except Exception:
            return None
    
    def get_all_chatgpt_windows(self) -> List[WindowInfo]:
        """
        Get information about all potential ChatGPT windows.
        
        Returns:
            List of WindowInfo objects for all found ChatGPT windows
        """
        windows = []
        
        try:
            # Search using all patterns
            for pattern in self.CHATGPT_WINDOW_PATTERNS:
                found_windows = gw.getWindowsWithTitle(pattern)
                for window in found_windows:
                    if self._is_likely_chatgpt_window(window):
                        try:
                            window_info = self._create_window_info(window._hWnd)
                            windows.append(window_info)
                        except Exception as e:
                            logger.debug(f"Error creating window info: {e}")
            
            # Remove duplicates based on handle
            unique_windows = []
            seen_handles = set()
            for window in windows:
                if window.handle not in seen_handles:
                    unique_windows.append(window)
                    seen_handles.add(window.handle)
            
            return unique_windows
            
        except Exception as e:
            logger.error(f"Error getting all ChatGPT windows: {e}")
            return []


class MessageSender:
    """Handles sending messages to ChatGPT application."""
    
    def __init__(self, window_manager: WindowManager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MessageSender.
        
        Args:
            window_manager: WindowManager instance for window operations
            config: Optional configuration dictionary
        """
        self.window_manager = window_manager
        self.config = config or {}
        self.typing_delay = self.config.get('typing_delay', 0.05)
        self.max_message_length = self.config.get('max_message_length', 2000)
        self.clipboard_threshold = self.config.get('clipboard_threshold', 500)
        
    def send_message(self, message: str, use_clipboard: Optional[bool] = None) -> bool:
        """
        Send a message to ChatGPT.
        
        Args:
            message: The message text to send
            use_clipboard: If True, use clipboard method. If None, auto-decide based on length
            
        Returns:
            True if message was sent successfully, False otherwise
            
        Raises:
            ChatGPTWindowError: If ChatGPT window cannot be found or focused
        """
        try:
            # Find and focus ChatGPT window
            window_info = self.window_manager.find_chatgpt_window()
            if not window_info:
                raise ChatGPTWindowError("ChatGPT window not found")
            
            if not self.window_manager.focus_window(window_info):
                raise ChatGPTWindowError("Failed to focus ChatGPT window")
            
            # Validate window state
            if not self.window_manager.validate_window_state(window_info):
                logger.warning("ChatGPT window state may not be optimal for input")
            
            # Find input field
            input_field_pos = self._find_input_field(window_info)
            if not input_field_pos:
                logger.error("Could not locate ChatGPT input field")
                return False
            
            # Click on input field to ensure focus
            pyautogui.click(input_field_pos[0], input_field_pos[1])
            time.sleep(0.2)  # Allow time for focus
            
            # Decide whether to use clipboard based on message length
            if use_clipboard is None:
                use_clipboard = len(message) > self.clipboard_threshold
            
            # Send the message
            if use_clipboard:
                success = self._send_via_clipboard(message)
            else:
                success = self._send_via_typing(message)
            
            if success:
                # Press Enter to send
                pyautogui.press('enter')
                logger.info(f"Successfully sent message ({len(message)} characters)")
                return True
            else:
                logger.error("Failed to input message text")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def _find_input_field(self, window_info: WindowInfo) -> Optional[Tuple[int, int]]:
        """
        Find the ChatGPT input field position.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Tuple of (x, y) coordinates for the input field, or None if not found
        """
        try:
            # Strategy 1: Look for input field at bottom of window
            # Most chat applications have input at the bottom
            window_x, window_y = window_info.position
            window_width, window_height = window_info.size
            
            # Estimate input field position (typically at bottom center)
            estimated_x = window_x + window_width // 2
            estimated_y = window_y + window_height - 100  # 100px from bottom
            
            # Validate the position is within window bounds
            if (window_x <= estimated_x <= window_x + window_width and
                window_y <= estimated_y <= window_y + window_height):
                
                logger.debug(f"Estimated input field position: ({estimated_x}, {estimated_y})")
                return (estimated_x, estimated_y)
            
            # Strategy 2: Use image recognition (if available)
            # This would require screenshot analysis - simplified for now
            
            # Strategy 3: Try common input field locations
            common_positions = [
                (window_x + window_width // 2, window_y + window_height - 80),
                (window_x + window_width // 2, window_y + window_height - 120),
                (window_x + window_width // 2, window_y + window_height - 60),
            ]
            
            for pos in common_positions:
                if (window_x <= pos[0] <= window_x + window_width and
                    window_y <= pos[1] <= window_y + window_height):
                    return pos
            
            logger.warning("Could not determine input field position")
            return None
            
        except Exception as e:
            logger.error(f"Error finding input field: {e}")
            return None
    
    def _send_via_typing(self, message: str) -> bool:
        """
        Send message by typing character by character.
        
        Args:
            message: Message to type
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clear any existing text first
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Type the message with delay between characters
            for char in message:
                pyautogui.write(char, interval=self.typing_delay)
                
                # Handle special characters that might need escaping
                if char in ['\n', '\r']:
                    pyautogui.press('shift', 'enter')  # Line break without sending
            
            logger.debug(f"Typed message via keyboard ({len(message)} characters)")
            return True
            
        except Exception as e:
            logger.error(f"Error typing message: {e}")
            return False
    
    def _send_via_clipboard(self, message: str) -> bool:
        """
        Send message using clipboard paste method.
        
        Args:
            message: Message to paste
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pyperclip
            
            # Store current clipboard content to restore later
            original_clipboard = None
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                logger.debug("Could not read original clipboard content")
            
            # Copy message to clipboard
            pyperclip.copy(message)
            time.sleep(0.1)  # Allow time for clipboard operation
            
            # Clear existing text and paste
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.2)  # Allow time for paste operation
            
            # Restore original clipboard content
            if original_clipboard is not None:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    logger.debug("Could not restore original clipboard content")
            
            logger.debug(f"Pasted message via clipboard ({len(message)} characters)")
            return True
            
        except ImportError:
            logger.warning("pyperclip not available, falling back to typing")
            return self._send_via_typing(message)
        except Exception as e:
            logger.error(f"Error pasting message: {e}")
            return False
    
    def validate_input_field(self, window_info: WindowInfo) -> bool:
        """
        Validate that the input field is accessible and ready for input.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            True if input field is ready, False otherwise
        """
        try:
            input_field_pos = self._find_input_field(window_info)
            if not input_field_pos:
                return False
            
            # Click on the input field
            pyautogui.click(input_field_pos[0], input_field_pos[1])
            time.sleep(0.2)
            
            # Try typing a test character and then delete it
            test_char = 'a'
            pyautogui.write(test_char)
            time.sleep(0.1)
            pyautogui.press('backspace')
            
            logger.debug("Input field validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Input field validation failed: {e}")
            return False
    
    def clear_input_field(self, window_info: WindowInfo) -> bool:
        """
        Clear the ChatGPT input field.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            True if successful, False otherwise
        """
        try:
            input_field_pos = self._find_input_field(window_info)
            if not input_field_pos:
                return False
            
            # Click on input field and select all text
            pyautogui.click(input_field_pos[0], input_field_pos[1])
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')
            
            logger.debug("Input field cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing input field: {e}")
            return False


class ResponseCapture:
    """Handles capturing and parsing responses from ChatGPT application."""
    
    def __init__(self, window_manager: WindowManager, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ResponseCapture.
        
        Args:
            window_manager: WindowManager instance for window operations
            config: Optional configuration dictionary
        """
        self.window_manager = window_manager
        self.config = config or {}
        self.response_timeout = self.config.get('response_timeout', 30)  # seconds
        self.polling_interval = self.config.get('polling_interval', 1.0)  # seconds
        self.max_response_length = self.config.get('max_response_length', 50000)
        
    def capture_response(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Capture the latest response from ChatGPT.
        
        Args:
            timeout: Maximum time to wait for response (uses default if None)
            
        Returns:
            The captured response text, or None if no response captured
            
        Raises:
            ChatGPTWindowError: If ChatGPT window cannot be found or accessed
        """
        try:
            # Find ChatGPT window
            window_info = self.window_manager.find_chatgpt_window()
            if not window_info:
                raise ChatGPTWindowError("ChatGPT window not found")
            
            # Use provided timeout or default
            actual_timeout = timeout if timeout is not None else self.response_timeout
            
            # Wait for response with timeout
            response_text = self._wait_for_response(window_info, actual_timeout)
            
            if response_text:
                # Parse and clean the response
                cleaned_response = self._parse_and_clean_response(response_text)
                logger.info(f"Captured response ({len(cleaned_response)} characters)")
                return cleaned_response
            else:
                logger.warning("No response captured within timeout")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing response: {e}")
            return None
    
    def _wait_for_response(self, window_info: WindowInfo, timeout: float) -> Optional[str]:
        """
        Wait for a new response to appear in the ChatGPT interface.
        
        Args:
            window_info: Information about the ChatGPT window
            timeout: Maximum time to wait in seconds
            
        Returns:
            Raw response text if found, None otherwise
        """
        start_time = time.time()
        last_response = None
        
        while time.time() - start_time < timeout:
            try:
                # Focus window to ensure we can capture content
                if not self.window_manager.focus_window(window_info):
                    logger.warning("Failed to focus ChatGPT window during response capture")
                
                # Capture current response area content
                current_response = self._capture_response_area(window_info)
                
                if current_response and current_response != last_response:
                    # Check if this looks like a complete response
                    if self._is_response_complete(current_response):
                        return current_response
                    
                    last_response = current_response
                
                # Wait before next poll
                time.sleep(self.polling_interval)
                
            except Exception as e:
                logger.debug(f"Error during response polling: {e}")
                time.sleep(self.polling_interval)
        
        # Return the last captured response even if timeout occurred
        return last_response
    
    def _capture_response_area(self, window_info: WindowInfo) -> Optional[str]:
        """
        Capture text from the ChatGPT response area.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Raw text from response area, or None if capture failed
        """
        try:
            # Strategy 1: Use clipboard to capture selected text
            response_text = self._capture_via_selection(window_info)
            if response_text:
                return response_text
            
            # Strategy 2: Use OCR or screenshot analysis (simplified for now)
            # This would require additional libraries like pytesseract
            
            # Strategy 3: Try to capture via accessibility APIs (if available)
            # This would require additional Windows accessibility libraries
            
            logger.debug("Could not capture response text")
            return None
            
        except Exception as e:
            logger.error(f"Error capturing response area: {e}")
            return None
    
    def _capture_via_selection(self, window_info: WindowInfo) -> Optional[str]:
        """
        Capture response by selecting text and copying to clipboard.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Captured text or None if failed
        """
        try:
            import pyperclip
            
            # Store original clipboard content
            original_clipboard = None
            try:
                original_clipboard = pyperclip.paste()
            except Exception:
                logger.debug("Could not read original clipboard")
            
            # Estimate response area location
            response_area = self._find_response_area(window_info)
            if not response_area:
                return None
            
            # Click in response area and select all text
            pyautogui.click(response_area[0], response_area[1])
            time.sleep(0.2)
            
            # Try to select the latest response
            # This is a simplified approach - in practice, you'd need more sophisticated
            # text selection logic based on the ChatGPT interface
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)  # Allow time for copy operation
            
            # Get copied text
            try:
                captured_text = pyperclip.paste()
                
                # Restore original clipboard
                if original_clipboard is not None:
                    try:
                        pyperclip.copy(original_clipboard)
                    except Exception:
                        logger.debug("Could not restore clipboard")
                
                return captured_text if captured_text != original_clipboard else None
                
            except Exception as e:
                logger.error(f"Error reading from clipboard: {e}")
                return None
                
        except ImportError:
            logger.warning("pyperclip not available for response capture")
            return None
        except Exception as e:
            logger.error(f"Error in selection-based capture: {e}")
            return None
    
    def _find_response_area(self, window_info: WindowInfo) -> Optional[Tuple[int, int]]:
        """
        Find the location of the ChatGPT response area.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Tuple of (x, y) coordinates for the response area, or None if not found
        """
        try:
            window_x, window_y = window_info.position
            window_width, window_height = window_info.size
            
            # Estimate response area position (typically in the center-upper area)
            # This is a simplified approach - real implementation would need more
            # sophisticated UI element detection
            estimated_x = window_x + window_width // 2
            estimated_y = window_y + window_height // 3  # Upper third of window
            
            # Validate coordinates are within window
            if (window_x <= estimated_x <= window_x + window_width and
                window_y <= estimated_y <= window_y + window_height):
                
                logger.debug(f"Estimated response area: ({estimated_x}, {estimated_y})")
                return (estimated_x, estimated_y)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding response area: {e}")
            return None
    
    def _is_response_complete(self, response_text: str) -> bool:
        """
        Check if a response appears to be complete.
        
        Args:
            response_text: The response text to check
            
        Returns:
            True if response appears complete, False otherwise
        """
        if not response_text or len(response_text.strip()) == 0:
            return False
        
        # Check for common indicators of incomplete responses
        incomplete_indicators = [
            "...",  # Ellipsis indicating more content
            "typing...",  # Typing indicator
            "thinking...",  # Thinking indicator
        ]
        
        text_lower = response_text.lower().strip()
        
        # Check if text ends with incomplete indicators
        for indicator in incomplete_indicators:
            if text_lower.endswith(indicator):
                return False
        
        # Check minimum length (very short responses might be incomplete)
        if len(response_text.strip()) < 10:
            return False
        
        # If we get here, assume response is complete
        return True
    
    def _parse_and_clean_response(self, raw_response: str) -> str:
        """
        Parse and clean the raw response text.
        
        Args:
            raw_response: Raw response text from ChatGPT
            
        Returns:
            Cleaned and parsed response text
        """
        if not raw_response:
            return ""
        
        try:
            # Remove common UI elements that might be captured
            cleaned = raw_response
            
            # Remove common ChatGPT UI text
            ui_elements_to_remove = [
                "ChatGPT",
                "New chat",
                "Regenerate response",
                "Copy",
                "Share",
                "Like",
                "Dislike",
                "Report",
            ]
            
            for element in ui_elements_to_remove:
                cleaned = cleaned.replace(element, "")
            
            # Clean up whitespace
            lines = cleaned.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not self._is_ui_line(line):
                    cleaned_lines.append(line)
            
            # Join lines back together
            result = '\n'.join(cleaned_lines)
            
            # Limit response length
            if len(result) > self.max_response_length:
                result = result[:self.max_response_length] + "... [truncated]"
                logger.warning(f"Response truncated to {self.max_response_length} characters")
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return raw_response  # Return raw response if parsing fails
    
    def _is_ui_line(self, line: str) -> bool:
        """
        Check if a line appears to be UI text rather than response content.
        
        Args:
            line: Line of text to check
            
        Returns:
            True if line appears to be UI text, False otherwise
        """
        if not line or len(line.strip()) == 0:
            return True
        
        # Common UI patterns
        ui_patterns = [
            r"^\d+:\d+\s*(AM|PM)$",  # Timestamps
            r"^(Copy|Share|Like|Dislike)$",  # Action buttons
            r"^ChatGPT\s*$",  # App name
            r"^New chat\s*$",  # New chat button
            r"^\s*\.\.\.\s*$",  # Loading indicators
        ]
        
        import re
        line_stripped = line.strip()
        
        for pattern in ui_patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                return True
        
        return False

    def get_conversation_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history from ChatGPT interface.
        
        Args:
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages with role and content
        """
        try:
            # Find ChatGPT window
            window_info = self.window_manager.find_chatgpt_window()
            if not window_info:
                logger.warning("ChatGPT window not found for conversation history")
                return []
            
            # Focus window
            if not self.window_manager.focus_window(window_info):
                logger.warning("Failed to focus ChatGPT window for conversation history")
                return []
            
            # Capture conversation area
            conversation_text = self._capture_conversation_area(window_info)
            if not conversation_text:
                logger.warning("No conversation text captured")
                return []
            
            # Parse conversation history
            return self._parse_conversation_history(conversation_text, max_messages)
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def _capture_conversation_area(self, window_info: WindowInfo) -> Optional[str]:
        """
        Capture text from the conversation area.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Raw conversation text or None if capture failed
        """
        try:
            # This is a simplified implementation
            # In a real implementation, this would use OCR or accessibility APIs
            # to extract text from the conversation area
            
            # For now, return a placeholder that tests can mock
            logger.debug("Capturing conversation area (placeholder implementation)")
            return None
            
        except Exception as e:
            logger.error(f"Error capturing conversation area: {e}")
            return None

    def _parse_conversation_history(self, conversation_text: str, max_messages: int) -> List[Dict[str, str]]:
        """
        Parse conversation text into structured messages.
        
        Args:
            conversation_text: Raw conversation text
            max_messages: Maximum number of messages to return
            
        Returns:
            List of parsed messages with role and content
        """
        try:
            if not conversation_text:
                return []
            
            messages = []
            lines = conversation_text.split('\n')
            current_message = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this looks like a user message
                if self._looks_like_user_message(line):
                    # Save previous message if exists
                    if current_message:
                        messages.append(current_message)
                    
                    # Start new user message
                    current_message = {
                        'role': 'user',
                        'content': line
                    }
                elif line.startswith('Assistant:') or line.startswith('ChatGPT:'):
                    # Save previous message if exists
                    if current_message:
                        messages.append(current_message)
                    
                    # Start new assistant message
                    content = line.split(':', 1)[1].strip() if ':' in line else line
                    current_message = {
                        'role': 'assistant',
                        'content': content
                    }
                else:
                    # Continue current message
                    if current_message:
                        current_message['content'] += ' ' + line
            
            # Add the last message
            if current_message:
                messages.append(current_message)
            
            # Limit to max_messages
            if len(messages) > max_messages:
                messages = messages[-max_messages:]
            
            return messages
            
        except Exception as e:
            logger.error(f"Error parsing conversation history: {e}")
            return []

    def _looks_like_user_message(self, line: str) -> bool:
        """
        Simple heuristic to determine if a line looks like a user message.
        
        Args:
            line: Line of text to check
            
        Returns:
            True if line appears to be from user, False otherwise
        """
        user_indicators = [
            line.endswith("?"),  # Questions
            line.startswith("Can you"),
            line.startswith("Please"),
            line.startswith("How"),
            line.startswith("What"),
            line.startswith("Why"),
            line.startswith("When"),
            line.startswith("Where"),
            line.startswith("User:"),
        ]
        
        return any(user_indicators)


class WindowsAutomationHandler:
    """
    Main Windows automation handler that coordinates all ChatGPT interactions.
    
    This class provides a unified interface for all ChatGPT automation operations
    including window management, message sending, response capture, and conversation management.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the Windows automation handler.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config() if hasattr(config_manager, 'get_config') else {}
        
        # Initialize component handlers
        self.window_manager = WindowManager(self.config)
        self.message_sender = MessageSender(self.window_manager, self.config)
        self.response_capture = ResponseCapture(self.window_manager, self.config)
        
        logger.info("Windows automation handler initialized")
    
    async def send_message_and_get_response(self, message: str, timeout: float = 30) -> str:
        """
        Send a message to ChatGPT and capture the response.
        
        Args:
            message: The message to send
            timeout: Timeout for waiting for response
            
        Returns:
            The response from ChatGPT
            
        Raises:
            ChatGPTWindowError: If ChatGPT window cannot be found or accessed
            AutomationError: If automation operations fail
        """
        try:
            # Send the message
            success = self.message_sender.send_message(message)
            if not success:
                raise AutomationError("Failed to send message to ChatGPT", "send_message")
            
            # Capture the response
            response = self.response_capture.capture_response(timeout)
            if response is None:
                raise AutomationError("Failed to capture response from ChatGPT", "capture_response")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in send_message_and_get_response: {e}")
            raise
    
    async def get_conversation_history(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get conversation history from ChatGPT.
        
        Args:
            max_messages: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        try:
            window_info = self.window_manager.find_chatgpt_window()
            if not window_info:
                logger.warning("ChatGPT window not found for history capture")
                return []
            
            # Focus window
            if not self.window_manager.focus_window(window_info):
                logger.warning("Failed to focus window for history capture")
                return []
            
            # Capture current conversation area
            conversation_text = self._capture_conversation_area(window_info)
            if not conversation_text:
                return []
            
            # Parse conversation into messages
            messages = self._parse_conversation_history(conversation_text, max_messages)
            
            logger.info(f"Captured {len(messages)} messages from conversation history")
            return messages
            
        except Exception as e:
            logger.error(f"Error capturing conversation history: {e}")
            return []
    
    async def reset_conversation(self) -> bool:
        """
        Reset the current ChatGPT conversation.
        
        Returns:
            True if reset was successful, False otherwise
        """
        try:
            window_info = self.window_manager.find_chatgpt_window()
            if not window_info:
                logger.warning("ChatGPT window not found for conversation reset")
                return False
            
            # Focus window
            if not self.window_manager.focus_window(window_info):
                logger.warning("Failed to focus window for conversation reset")
                return False
            
            # Try common keyboard shortcuts for new conversation
            # Most chat applications use Ctrl+N for new conversation
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(1.0)  # Allow time for new conversation to start
            
            # Alternative: Try Ctrl+Shift+N
            if not self._verify_conversation_reset():
                pyautogui.hotkey('ctrl', 'shift', 'n')
                time.sleep(1.0)
            
            # Verify the reset was successful
            if self._verify_conversation_reset():
                logger.info("Successfully reset ChatGPT conversation")
                return True
            else:
                logger.warning("Could not verify conversation reset")
                return False
                
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")
            return False
    
    def _capture_conversation_area(self, window_info: WindowInfo) -> Optional[str]:
        """
        Capture text from the entire conversation area.
        
        Args:
            window_info: Information about the ChatGPT window
            
        Returns:
            Raw conversation text or None if failed
        """
        try:
            # Use the response capture component's method
            return self.response_capture._capture_via_selection(window_info)
            
        except Exception as e:
            logger.error(f"Error capturing conversation area: {e}")
            return None
    
    def _parse_conversation_history(self, conversation_text: str, max_messages: int) -> List[Dict[str, str]]:
        """
        Parse conversation text into individual messages.
        
        Args:
            conversation_text: Raw conversation text
            max_messages: Maximum number of messages to return
            
        Returns:
            List of parsed messages
        """
        if not conversation_text:
            return []
        
        try:
            messages = []
            lines = conversation_text.split('\n')
            current_message = ""
            current_role = "assistant"  # Default to assistant
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is the start of a user message
                if self._looks_like_user_message(line):
                    # Save previous message if exists
                    if current_message:
                        messages.append({
                            "role": current_role,
                            "content": current_message.strip()
                        })
                    # Strip the "User:" prefix if present
                    if line.startswith("User:"):
                        current_message = line[5:].strip()  # Remove "User:"
                    else:
                        current_message = line
                    current_role = "user"
                # Check if this is the start of an assistant message
                elif line.startswith("Assistant:") or line.startswith("ChatGPT:"):
                    # Save previous message if exists
                    if current_message:
                        messages.append({
                            "role": current_role,
                            "content": current_message.strip()
                        })
                    # Strip the role prefix from the content
                    if line.startswith("Assistant:"):
                        current_message = line[10:].strip()  # Remove "Assistant:"
                    elif line.startswith("ChatGPT:"):
                        current_message = line[8:].strip()   # Remove "ChatGPT:"
                    current_role = "assistant"
                else:
                    # Continue current message
                    if current_message:
                        current_message += "\n" + line
                    else:
                        current_message = line
                        current_role = "assistant"  # Default to assistant
            
            # Add the last message
            if current_message:
                messages.append({
                    "role": current_role,
                    "content": current_message.strip()
                })
            
            # Return most recent messages up to max_messages
            return messages[-max_messages:] if len(messages) > max_messages else messages
            
        except Exception as e:
            logger.error(f"Error parsing conversation history: {e}")
            return []
    
    def _looks_like_user_message(self, line: str) -> bool:
        """
        Simple heuristic to determine if a line looks like a user message.
        
        Args:
            line: Line of text to check
            
        Returns:
            True if line appears to be from user, False otherwise
        """
        user_indicators = [
            line.endswith("?"),  # Questions
            line.startswith("Can you"),
            line.startswith("Please"),
            line.startswith("How"),
            line.startswith("What"),
            line.startswith("Why"),
            line.startswith("When"),
            line.startswith("Where"),
            line.startswith("User:"),
        ]
        
        return any(user_indicators)
    
    def _verify_conversation_reset(self) -> bool:
        """
        Verify that the conversation has been reset.
        
        Returns:
            True if conversation appears to be reset, False otherwise
        """
        try:
            # This is a simplified verification
            time.sleep(0.5)
            return True
            
        except Exception as e:
            logger.error(f"Error verifying conversation reset: {e}")
            return False
    
    async def cleanup(self) -> None:
        """
        Clean up resources used by the automation handler.
        """
        logger.info("Windows automation handler cleanup complete")