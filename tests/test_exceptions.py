"""
Tests for custom exceptions.

This module contains tests for all custom exception classes and their functionality.
"""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.exceptions import (
    ErrorCategory, MCPError, ChatGPTConnectionError, ChatGPTWindowError,
    AutomationError, ResponseTimeoutError, ConfigurationError, ValidationError,
    ProtocolError, SystemError, create_window_not_found_error,
    create_automation_timeout_error, create_invalid_message_error, wrap_system_error
)


class TestErrorCategory:
    """Test cases for ErrorCategory enum."""
    
    def test_error_categories_exist(self):
        """Test that all expected error categories exist."""
        expected_categories = [
            "connection", "automation", "protocol", "configuration",
            "window", "timeout", "validation", "system"
        ]
        
        for category in expected_categories:
            assert hasattr(ErrorCategory, category.upper())
            assert ErrorCategory[category.upper()].value == category


class TestMCPError:
    """Test cases for the base MCPError class."""
    
    def test_basic_initialization(self):
        """Test basic MCPError initialization."""
        error = MCPError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.category == ErrorCategory.SYSTEM
        assert error.details == {}
        assert error.recoverable is False
        assert error.user_message == "An unexpected error occurred. Please try again."
    
    def test_full_initialization(self):
        """Test MCPError initialization with all parameters."""
        details = {"key": "value", "number": 42}
        error = MCPError(
            message="Technical error",
            category=ErrorCategory.CONNECTION,
            details=details,
            recoverable=True,
            user_message="Custom user message"
        )
        
        assert str(error) == "Technical error"
        assert error.category == ErrorCategory.CONNECTION
        assert error.details == details
        assert error.recoverable is True
        assert error.user_message == "Custom user message"
    
    def test_user_message_generation(self):
        """Test automatic user message generation for different categories."""
        test_cases = [
            (ErrorCategory.CONNECTION, "Unable to connect to ChatGPT"),
            (ErrorCategory.AUTOMATION, "Failed to interact with ChatGPT interface"),
            (ErrorCategory.PROTOCOL, "Communication error occurred"),
            (ErrorCategory.CONFIGURATION, "Configuration error"),
            (ErrorCategory.WINDOW, "Cannot find or access ChatGPT window"),
            (ErrorCategory.TIMEOUT, "Operation timed out"),
            (ErrorCategory.VALIDATION, "Invalid input provided"),
            (ErrorCategory.SYSTEM, "An unexpected error occurred")
        ]
        
        for category, expected_text in test_cases:
            error = MCPError("Technical message", category=category)
            assert expected_text in error.user_message
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        details = {"context": "test"}
        error = MCPError(
            message="Test error",
            category=ErrorCategory.AUTOMATION,
            details=details,
            recoverable=True,
            user_message="User message"
        )
        
        result = error.to_dict()
        
        expected_keys = ["error_type", "message", "category", "details", "recoverable", "user_message"]
        for key in expected_keys:
            assert key in result
        
        assert result["error_type"] == "MCPError"
        assert result["message"] == "Test error"
        assert result["category"] == "automation"
        assert result["details"] == details
        assert result["recoverable"] is True
        assert result["user_message"] == "User message"


class TestChatGPTConnectionError:
    """Test cases for ChatGPTConnectionError."""
    
    def test_initialization(self):
        """Test ChatGPTConnectionError initialization."""
        details = {"process_id": 1234}
        error = ChatGPTConnectionError("Connection failed", details=details)
        
        assert str(error) == "Connection failed"
        assert error.category == ErrorCategory.CONNECTION
        assert error.details == details
        assert error.recoverable is True
        assert "Cannot connect to ChatGPT" in error.user_message
    
    def test_default_user_message(self):
        """Test default user message for connection errors."""
        error = ChatGPTConnectionError("Technical connection error")
        
        assert "Cannot connect to ChatGPT" in error.user_message
        assert "ensure ChatGPT is running" in error.user_message


class TestChatGPTWindowError:
    """Test cases for ChatGPTWindowError."""
    
    def test_initialization(self):
        """Test ChatGPTWindowError initialization."""
        details = {"search_patterns": ["ChatGPT", "OpenAI"]}
        error = ChatGPTWindowError("Window not found", details=details)
        
        assert str(error) == "Window not found"
        assert error.category == ErrorCategory.WINDOW
        assert error.details == details
        assert error.recoverable is True
        assert "Cannot find ChatGPT window" in error.user_message


class TestAutomationError:
    """Test cases for AutomationError."""
    
    def test_initialization(self):
        """Test AutomationError initialization."""
        details = {"coordinates": (100, 200)}
        error = AutomationError("Click failed", "click_button", details=details)
        
        assert str(error) == "Click failed"
        assert error.category == ErrorCategory.AUTOMATION
        assert error.details["operation"] == "click_button"
        assert error.details["coordinates"] == (100, 200)
        assert error.recoverable is True
        assert "Failed to click_button" in error.user_message
    
    def test_operation_in_details(self):
        """Test that operation is added to details."""
        error = AutomationError("Test error", "send_message")
        
        assert error.details["operation"] == "send_message"


class TestResponseTimeoutError:
    """Test cases for ResponseTimeoutError."""
    
    def test_initialization(self):
        """Test ResponseTimeoutError initialization."""
        timeout_duration = 30.5
        details = {"request_id": "123"}
        error = ResponseTimeoutError(timeout_duration, details=details)
        
        assert f"Response timeout after {timeout_duration} seconds" in str(error)
        assert error.category == ErrorCategory.TIMEOUT
        assert error.details["timeout_duration"] == timeout_duration
        assert error.details["request_id"] == "123"
        assert error.recoverable is True
        assert f"{timeout_duration} seconds" in error.user_message
    
    def test_timeout_in_user_message(self):
        """Test timeout duration appears in user message."""
        error = ResponseTimeoutError(45.0)
        
        assert "45.0 seconds" in error.user_message
        assert "did not respond" in error.user_message


class TestConfigurationError:
    """Test cases for ConfigurationError."""
    
    def test_initialization(self):
        """Test ConfigurationError initialization."""
        details = {"file_path": "/path/to/config"}
        error = ConfigurationError("Config missing", config_key="api_key", details=details)
        
        assert str(error) == "Config missing"
        assert error.category == ErrorCategory.CONFIGURATION
        assert error.details["config_key"] == "api_key"
        assert error.details["file_path"] == "/path/to/config"
        assert error.recoverable is False
        assert "Configuration error" in error.user_message
    
    def test_config_key_in_details(self):
        """Test that config_key is added to details when provided."""
        error = ConfigurationError("Missing setting", config_key="timeout")
        
        assert error.details["config_key"] == "timeout"
    
    def test_no_config_key(self):
        """Test initialization without config_key."""
        error = ConfigurationError("General config error")
        
        assert "config_key" not in error.details


class TestValidationError:
    """Test cases for ValidationError."""
    
    def test_initialization(self):
        """Test ValidationError initialization."""
        error = ValidationError("Invalid format", field="email", value="invalid-email")
        
        assert str(error) == "Invalid format"
        assert error.category == ErrorCategory.VALIDATION
        assert error.details["field"] == "email"
        assert error.details["value"] == "invalid-email"
        assert error.recoverable is False
        assert "Invalid input: Invalid format" in error.user_message
    
    def test_optional_parameters(self):
        """Test ValidationError with optional parameters."""
        error = ValidationError("General validation error")
        
        assert "field" not in error.details
        assert "value" not in error.details
    
    def test_none_value_handling(self):
        """Test handling of None value."""
        error = ValidationError("Test error", field="test", value=None)
        
        assert error.details["field"] == "test"
        assert "value" not in error.details


class TestProtocolError:
    """Test cases for ProtocolError."""
    
    def test_initialization(self):
        """Test ProtocolError initialization."""
        details = {"method": "send_message"}
        error = ProtocolError("Protocol error", request_id="req-123", details=details)
        
        assert str(error) == "Protocol error"
        assert error.category == ErrorCategory.PROTOCOL
        assert error.details["request_id"] == "req-123"
        assert error.details["method"] == "send_message"
        assert error.recoverable is True
        assert "Communication error occurred" in error.user_message
    
    def test_request_id_in_details(self):
        """Test that request_id is added to details when provided."""
        error = ProtocolError("Test error", request_id="abc-123")
        
        assert error.details["request_id"] == "abc-123"


class TestSystemError:
    """Test cases for SystemError."""
    
    def test_initialization(self):
        """Test SystemError initialization."""
        original_exception = ValueError("Original error")
        details = {"context": "test_function"}
        error = SystemError("System error occurred", original_exception=original_exception, details=details)
        
        assert str(error) == "System error occurred"
        assert error.category == ErrorCategory.SYSTEM
        assert error.details["original_exception"] == "Original error"
        assert error.details["exception_type"] == "ValueError"
        assert error.details["context"] == "test_function"
        assert error.recoverable is False
        assert "unexpected system error" in error.user_message
    
    def test_without_original_exception(self):
        """Test SystemError without original exception."""
        error = SystemError("General system error")
        
        assert "original_exception" not in error.details
        assert "exception_type" not in error.details
    
    def test_original_exception_details(self):
        """Test that original exception details are captured."""
        original = RuntimeError("Runtime issue")
        error = SystemError("Wrapped error", original_exception=original)
        
        assert error.details["original_exception"] == "Runtime issue"
        assert error.details["exception_type"] == "RuntimeError"


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_create_window_not_found_error(self):
        """Test create_window_not_found_error function."""
        search_patterns = ["ChatGPT", "OpenAI ChatGPT"]
        error = create_window_not_found_error(search_patterns)
        
        assert isinstance(error, ChatGPTWindowError)
        assert "window not found" in str(error)
        assert error.details["search_patterns"] == search_patterns
    
    def test_create_window_not_found_error_no_patterns(self):
        """Test create_window_not_found_error without search patterns."""
        error = create_window_not_found_error()
        
        assert isinstance(error, ChatGPTWindowError)
        assert "search_patterns" not in error.details
    
    def test_create_automation_timeout_error(self):
        """Test create_automation_timeout_error function."""
        error = create_automation_timeout_error("click_button", 5.0)
        
        assert isinstance(error, AutomationError)
        assert "click_button" in str(error)
        assert "timed out after 5.0 seconds" in str(error)
        assert error.details["operation"] == "click_button"
        assert error.details["timeout"] == 5.0
    
    def test_create_invalid_message_error(self):
        """Test create_invalid_message_error function."""
        long_message = "a" * 150  # Message longer than 100 characters
        error = create_invalid_message_error(long_message, "too long")
        
        assert isinstance(error, ValidationError)
        assert "Invalid message: too long" in str(error)
        assert error.details["field"] == "message"
        assert error.details["value"].endswith("...")  # Should be truncated
        assert len(error.details["value"]) == 103  # 100 + "..."
    
    def test_create_invalid_message_error_short(self):
        """Test create_invalid_message_error with short message."""
        short_message = "short"
        error = create_invalid_message_error(short_message, "invalid format")
        
        assert error.details["value"] == short_message  # Should not be truncated
    
    def test_wrap_system_error(self):
        """Test wrap_system_error function."""
        original = KeyError("missing key")
        context = "data_processing"
        error = wrap_system_error(original, context)
        
        assert isinstance(error, SystemError)
        assert "System error in data_processing" in str(error)
        assert "missing key" in str(error)
        assert error.details["context"] == context
        assert error.details["original_exception"] == "'missing key'"  # KeyError string representation includes quotes
        assert error.details["exception_type"] == "KeyError"


class TestErrorInheritance:
    """Test cases for error inheritance and polymorphism."""
    
    def test_all_errors_inherit_from_mcp_error(self):
        """Test that all custom errors inherit from MCPError."""
        error_classes = [
            ChatGPTConnectionError, ChatGPTWindowError, AutomationError,
            ResponseTimeoutError, ConfigurationError, ValidationError,
            ProtocolError, SystemError
        ]
        
        for error_class in error_classes:
            # Create instance with minimal required parameters
            if error_class == AutomationError:
                error = error_class("Test error", "test_operation")
            elif error_class == ResponseTimeoutError:
                error = error_class(30.0)
            else:
                error = error_class("Test error")
            
            assert isinstance(error, MCPError)
            assert isinstance(error, Exception)
    
    def test_error_polymorphism(self):
        """Test that errors can be handled polymorphically."""
        errors = [
            ChatGPTConnectionError("Connection failed"),
            AutomationError("Automation failed", "click"),
            ValidationError("Invalid input"),
            SystemError("System error")
        ]
        
        for error in errors:
            # Should be able to call MCPError methods
            assert hasattr(error, 'to_dict')
            assert hasattr(error, 'user_message')
            assert hasattr(error, 'category')
            assert hasattr(error, 'recoverable')
            
            # Should be able to convert to dict
            error_dict = error.to_dict()
            assert isinstance(error_dict, dict)
            assert "error_type" in error_dict


if __name__ == "__main__":
    pytest.main([__file__])