"""
Unit tests for configuration management system.

Tests configuration loading, validation, and management functionality.
"""

import asyncio
import json
import os
import tempfile
import unittest
import uuid
import shutil
from unittest.mock import patch, mock_open
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import ConfigManager, ConfigurationError, WindowDetectionConfig, AutomationConfig


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        # Use unique filename for each test to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        self.config_path = os.path.join(self.temp_dir, f"test_config_{unique_id}.json")
        # Ensure no config file exists initially
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        # Create a fresh config manager for each test
        self.config_manager = ConfigManager(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        try:
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            # Also clean up any config.json in current directory
            cwd_config = os.path.join(os.getcwd(), "config.json")
            if os.path.exists(cwd_config):
                os.remove(cwd_config)
        except Exception:
            pass  # Ignore cleanup errors
    
    def test_default_config_creation(self):
        """Test that default configuration is created when no config file exists."""
        async def run_test():
            await self.config_manager.load_config()
            
            # Check that config file was created
            self.assertTrue(os.path.exists(self.config_path))
            
            # Check that all required sections exist
            self.assertIn("window_detection", self.config_manager.config_data)
            self.assertIn("automation", self.config_manager.config_data)
            self.assertIn("server", self.config_manager.config_data)
            self.assertIn("chatgpt", self.config_manager.config_data)
        
        asyncio.run(run_test())
    
    def test_config_loading_from_file(self):
        """Test loading configuration from existing file."""
        # Create test config file
        test_config = {
            "window_detection": {
                "window_title_patterns": ["Test ChatGPT"],
                "window_class_names": ["TestClass"],
                "search_timeout": 5.0,
                "focus_retry_attempts": 2,
                "focus_retry_delay": 0.5
            },
            "automation": {
                "typing_delay": 0.1,
                "response_timeout": 20.0,
                "response_check_interval": 1.0,
                "max_response_wait_time": 40.0,
                "clipboard_fallback_threshold": 500,
                "screenshot_on_error": False
            },
            "server": {
                "server_name": "test-server",
                "server_version": "0.1.0",
                "log_level": "DEBUG",
                "max_concurrent_requests": 3,
                "request_timeout": 60.0
            },
            "chatgpt": {
                "input_field_selector": "test-input",
                "response_container_selector": "test-response",
                "new_chat_button_selector": "test-button",
                "conversation_history_selector": "test-history",
                "loading_indicator_selector": "test-loading"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        async def run_test():
            await self.config_manager.load_config()
            
            # Check that custom values were loaded
            self.assertEqual(
                self.config_manager.config_data["window_detection"]["window_title_patterns"],
                ["Test ChatGPT"]
            )
            self.assertEqual(
                self.config_manager.config_data["automation"]["typing_delay"],
                0.1
            )
            self.assertEqual(
                self.config_manager.config_data["server"]["server_name"],
                "test-server"
            )
        
        asyncio.run(run_test())
    
    def test_config_validation_invalid_window_patterns(self):
        """Test configuration validation with invalid window patterns."""
        # Create invalid config
        invalid_config = {
            "window_detection": {
                "window_title_patterns": [],  # Empty patterns should be invalid
                "window_class_names": ["TestClass"],
                "search_timeout": 5.0,
                "focus_retry_attempts": 2,
                "focus_retry_delay": 0.5
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        async def run_test():
            with self.assertRaises(ConfigurationError):
                await self.config_manager.load_config()
        
        asyncio.run(run_test())
    
    def test_config_validation_invalid_timeouts(self):
        """Test configuration validation with invalid timeout values."""
        # Create invalid config
        invalid_config = {
            "window_detection": {
                "search_timeout": -1.0  # Negative timeout should be invalid
            },
            "automation": {
                "response_timeout": 0.0  # Zero timeout should be invalid
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        async def run_test():
            with self.assertRaises(ConfigurationError):
                await self.config_manager.load_config()
        
        asyncio.run(run_test())
    
    def test_config_validation_invalid_log_level(self):
        """Test configuration validation with invalid log level."""
        # Create invalid config
        invalid_config = {
            "server": {
                "log_level": "INVALID_LEVEL"  # Invalid log level
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        async def run_test():
            with self.assertRaises(ConfigurationError):
                await self.config_manager.load_config()
        
        asyncio.run(run_test())
    
    def test_get_config_value(self):
        """Test getting configuration values."""
        async def run_test():
            # Ensure we start with a fresh config manager and no existing config file
            self.assertFalse(os.path.exists(self.config_path))
            await self.config_manager.load_config()
            
            # Test getting existing value from default config
            value = self.config_manager.get_config_value("server", "server_name")
            self.assertEqual(value, "windows-chatgpt-mcp")
            
            # Test getting non-existent value with default
            value = self.config_manager.get_config_value("nonexistent", "key", "default")
            self.assertEqual(value, "default")
            
            # Test getting non-existent value without default
            value = self.config_manager.get_config_value("nonexistent", "key")
            self.assertIsNone(value)
        
        asyncio.run(run_test())
    
    def test_set_config_value(self):
        """Test setting configuration values."""
        async def run_test():
            await self.config_manager.load_config()
            
            # Set new value
            self.config_manager.set_config_value("server", "server_name", "new-name")
            value = self.config_manager.get_config_value("server", "server_name")
            self.assertEqual(value, "new-name")
            
            # Set value in new section
            self.config_manager.set_config_value("new_section", "new_key", "new_value")
            value = self.config_manager.get_config_value("new_section", "new_key")
            self.assertEqual(value, "new_value")
        
        asyncio.run(run_test())
    
    def test_window_pattern_management(self):
        """Test window pattern management methods."""
        async def run_test():
            await self.config_manager.load_config()
            
            # Test adding pattern
            self.config_manager.add_window_pattern("New Pattern")
            patterns = self.config_manager.config_data["window_detection"]["window_title_patterns"]
            self.assertIn("New Pattern", patterns)
            
            # Test adding duplicate pattern (should not duplicate)
            original_length = len(patterns)
            self.config_manager.add_window_pattern("New Pattern")
            self.assertEqual(len(patterns), original_length)
            
            # Test removing pattern
            removed = self.config_manager.remove_window_pattern("New Pattern")
            self.assertTrue(removed)
            self.assertNotIn("New Pattern", patterns)
            
            # Test removing non-existent pattern
            removed = self.config_manager.remove_window_pattern("Non-existent")
            self.assertFalse(removed)
        
        asyncio.run(run_test())
    
    def test_config_objects_creation(self):
        """Test that configuration objects are created correctly."""
        async def run_test():
            await self.config_manager.load_config()
            
            # Check that all config objects are created
            self.assertIsInstance(self.config_manager.window_detection, WindowDetectionConfig)
            self.assertIsInstance(self.config_manager.automation, AutomationConfig)
            self.assertIsNotNone(self.config_manager.server)
            self.assertIsNotNone(self.config_manager.chatgpt)
            
            # Check that values are correctly mapped
            self.assertEqual(
                self.config_manager.window_detection.search_timeout,
                self.config_manager.config_data["window_detection"]["search_timeout"]
            )
        
        asyncio.run(run_test())
    
    def test_config_save(self):
        """Test configuration saving."""
        async def run_test():
            await self.config_manager.load_config()
            
            # Modify configuration
            self.config_manager.set_config_value("server", "server_name", "modified-name")
            
            # Save configuration
            await self.config_manager.save_config()
            
            # Load configuration in new manager to verify save
            new_manager = ConfigManager(self.config_path)
            await new_manager.load_config()
            
            value = new_manager.get_config_value("server", "server_name")
            self.assertEqual(value, "modified-name")
        
        asyncio.run(run_test())
    
    def test_config_merge_with_defaults(self):
        """Test that partial configuration is merged with defaults."""
        # Create partial config file
        partial_config = {
            "server": {
                "server_name": "custom-server"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(partial_config, f)
        
        async def run_test():
            await self.config_manager.load_config()
            
            # Check that custom value is preserved
            self.assertEqual(
                self.config_manager.config_data["server"]["server_name"],
                "custom-server"
            )
            
            # Check that default values are still present
            self.assertIn("window_detection", self.config_manager.config_data)
            self.assertIn("automation", self.config_manager.config_data)
            self.assertIn("chatgpt", self.config_manager.config_data)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()