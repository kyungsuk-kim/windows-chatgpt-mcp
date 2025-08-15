"""
Configuration Manager - Handle configuration and settings

This module provides configuration management for the Windows ChatGPT MCP server,
including ChatGPT window detection parameters and user preferences.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class WindowDetectionConfig:
    """Configuration for ChatGPT window detection"""
    window_title_patterns: List[str]
    window_class_names: List[str]
    search_timeout: float
    focus_retry_attempts: int
    focus_retry_delay: float


@dataclass
class AutomationConfig:
    """Configuration for Windows automation behavior"""
    typing_delay: float
    response_timeout: float
    response_check_interval: float
    max_response_wait_time: float
    clipboard_fallback_threshold: int
    screenshot_on_error: bool


@dataclass
class ServerConfig:
    """Configuration for MCP server behavior"""
    server_name: str
    server_version: str
    log_level: str
    max_concurrent_requests: int
    request_timeout: float


@dataclass
class ChatGPTConfig:
    """Configuration specific to ChatGPT interaction"""
    input_field_selector: str
    response_container_selector: str
    new_chat_button_selector: str
    conversation_history_selector: str
    loading_indicator_selector: str


class ConfigManager:
    """
    Manages configuration loading, validation, and access for the MCP server.
    
    Handles server settings, ChatGPT window detection parameters, and user preferences.
    """
    
    DEFAULT_CONFIG = {
        "window_detection": {
            "window_title_patterns": [
                "ChatGPT",
                "OpenAI ChatGPT",
                "ChatGPT - Google Chrome",
                "ChatGPT - Microsoft Edge",
                "ChatGPT - Mozilla Firefox"
            ],
            "window_class_names": [
                "Chrome_WidgetWin_1",
                "MozillaWindowClass",
                "ApplicationFrameWindow"
            ],
            "search_timeout": 10.0,
            "focus_retry_attempts": 3,
            "focus_retry_delay": 1.0
        },
        "automation": {
            "typing_delay": 0.05,
            "response_timeout": 30.0,
            "response_check_interval": 0.5,
            "max_response_wait_time": 60.0,
            "clipboard_fallback_threshold": 1000,
            "screenshot_on_error": True
        },
        "server": {
            "server_name": "windows-chatgpt-mcp",
            "server_version": "1.0.0",
            "log_level": "INFO",
            "max_concurrent_requests": 5,
            "request_timeout": 120.0
        },
        "chatgpt": {
            "input_field_selector": "textarea[data-id='root']",
            "response_container_selector": "[data-message-author-role='assistant']",
            "new_chat_button_selector": "[data-testid='new-chat-button']",
            "conversation_history_selector": "[data-testid='conversation-turn']",
            "loading_indicator_selector": "[data-testid='loading-indicator']"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        self.config_data: Dict[str, Any] = {}
        
        # Configuration objects
        self.window_detection: Optional[WindowDetectionConfig] = None
        self.automation: Optional[AutomationConfig] = None
        self.server: Optional[ServerConfig] = None
        self.chatgpt: Optional[ChatGPTConfig] = None
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try multiple locations in order of preference
        possible_paths = [
            os.path.join(os.getcwd(), "config.json"),
            os.path.join(os.path.expanduser("~"), ".windows-chatgpt-mcp", "config.json"),
            os.path.join(os.path.dirname(__file__), "..", "config.json")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return the first path as default (will be created if needed)
        return possible_paths[0]
    
    async def load_config(self) -> None:
        """
        Load configuration from file or create default configuration.
        
        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        try:
            if os.path.exists(self.config_path):
                self.logger.info(f"Loading configuration from {self.config_path}")
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                self._validate_config()
            else:
                self.logger.info(f"Configuration file not found at {self.config_path}, using defaults")
                self.config_data = self.DEFAULT_CONFIG.copy()
                await self.save_config()
            
            # Create configuration objects
            self._create_config_objects()
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def _validate_config(self) -> None:
        """
        Validate the loaded configuration.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Merge with defaults to ensure all required keys exist
        self._merge_with_defaults()
        
        # Validate specific configuration sections
        self._validate_window_detection_config()
        self._validate_automation_config()
        self._validate_server_config()
        self._validate_chatgpt_config()
    
    def _merge_with_defaults(self) -> None:
        """Merge loaded configuration with defaults to ensure all keys exist."""
        def merge_dicts(default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config_data = merge_dicts(self.DEFAULT_CONFIG, self.config_data)
    
    def _validate_window_detection_config(self) -> None:
        """Validate window detection configuration."""
        wd_config = self.config_data.get("window_detection", {})
        
        if not wd_config.get("window_title_patterns"):
            raise ConfigurationError("window_title_patterns cannot be empty")
        
        if wd_config.get("search_timeout", 0) <= 0:
            raise ConfigurationError("search_timeout must be positive")
        
        if wd_config.get("focus_retry_attempts", 0) < 0:
            raise ConfigurationError("focus_retry_attempts must be non-negative")
    
    def _validate_automation_config(self) -> None:
        """Validate automation configuration."""
        auto_config = self.config_data.get("automation", {})
        
        if auto_config.get("typing_delay", 0) < 0:
            raise ConfigurationError("typing_delay must be non-negative")
        
        if auto_config.get("response_timeout", 0) <= 0:
            raise ConfigurationError("response_timeout must be positive")
        
        if auto_config.get("response_check_interval", 0) <= 0:
            raise ConfigurationError("response_check_interval must be positive")
    
    def _validate_server_config(self) -> None:
        """Validate server configuration."""
        server_config = self.config_data.get("server", {})
        
        if not server_config.get("server_name"):
            raise ConfigurationError("server_name cannot be empty")
        
        if server_config.get("max_concurrent_requests", 0) <= 0:
            raise ConfigurationError("max_concurrent_requests must be positive")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if server_config.get("log_level") not in valid_log_levels:
            raise ConfigurationError(f"log_level must be one of {valid_log_levels}")
    
    def _validate_chatgpt_config(self) -> None:
        """Validate ChatGPT-specific configuration."""
        chatgpt_config = self.config_data.get("chatgpt", {})
        
        required_selectors = [
            "input_field_selector",
            "response_container_selector",
            "new_chat_button_selector"
        ]
        
        for selector in required_selectors:
            if not chatgpt_config.get(selector):
                raise ConfigurationError(f"{selector} cannot be empty")
    
    def _create_config_objects(self) -> None:
        """Create typed configuration objects from loaded data."""
        self.window_detection = WindowDetectionConfig(**self.config_data["window_detection"])
        self.automation = AutomationConfig(**self.config_data["automation"])
        self.server = ServerConfig(**self.config_data["server"])
        self.chatgpt = ChatGPTConfig(**self.config_data["chatgpt"])
    
    async def save_config(self) -> None:
        """
        Save current configuration to file.
        
        Raises:
            ConfigurationError: If configuration saving fails
        """
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            raise ConfigurationError(f"Failed to save configuration: {str(e)}")
    
    def get_config_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by section and key.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config_data.get(section, {}).get(key, default)
    
    def set_config_value(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value by section and key.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        
        self.config_data[section][key] = value
        
        # Recreate configuration objects
        self._create_config_objects()
    
    def get_window_detection_config(self) -> WindowDetectionConfig:
        """Get window detection configuration."""
        if not self.window_detection:
            raise ConfigurationError("Configuration not loaded")
        return self.window_detection
    
    def get_automation_config(self) -> AutomationConfig:
        """Get automation configuration."""
        if not self.automation:
            raise ConfigurationError("Configuration not loaded")
        return self.automation
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        if not self.server:
            raise ConfigurationError("Configuration not loaded")
        return self.server
    
    def get_chatgpt_config(self) -> ChatGPTConfig:
        """Get ChatGPT configuration."""
        if not self.chatgpt:
            raise ConfigurationError("Configuration not loaded")
        return self.chatgpt
    
    def update_window_patterns(self, patterns: List[str]) -> None:
        """
        Update window title patterns for ChatGPT detection.
        
        Args:
            patterns: List of window title patterns
        """
        self.config_data["window_detection"]["window_title_patterns"] = patterns
        self.window_detection = WindowDetectionConfig(**self.config_data["window_detection"])
    
    def add_window_pattern(self, pattern: str) -> None:
        """
        Add a new window title pattern.
        
        Args:
            pattern: Window title pattern to add
        """
        patterns = self.config_data["window_detection"]["window_title_patterns"]
        if pattern not in patterns:
            patterns.append(pattern)
            self.window_detection = WindowDetectionConfig(**self.config_data["window_detection"])
    
    def remove_window_pattern(self, pattern: str) -> bool:
        """
        Remove a window title pattern.
        
        Args:
            pattern: Window title pattern to remove
            
        Returns:
            True if pattern was removed, False if not found
        """
        patterns = self.config_data["window_detection"]["window_title_patterns"]
        if pattern in patterns:
            patterns.remove(pattern)
            self.window_detection = WindowDetectionConfig(**self.config_data["window_detection"])
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return self.config_data.copy()
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return json.dumps(self.config_data, indent=2)


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass