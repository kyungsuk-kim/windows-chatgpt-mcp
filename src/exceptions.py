"""
Custom exceptions for Windows ChatGPT MCP tool.

This module defines custom exception classes for different error categories
to provide better error handling and user-friendly error messages.
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors that can occur in the system."""
    CONNECTION = "connection"
    AUTOMATION = "automation"
    PROTOCOL = "protocol"
    CONFIGURATION = "configuration"
    WINDOW = "window"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    SYSTEM = "system"


class MCPError(Exception):
    """Base exception class for all MCP-related errors."""
    
    def __init__(
        self, 
        message: str, 
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = False,
        user_message: Optional[str] = None
    ):
        """
        Initialize MCP error.
        
        Args:
            message: Technical error message for logging
            category: Error category for classification
            details: Additional error details and context
            recoverable: Whether this error can be recovered from
            user_message: User-friendly error message for MCP responses
        """
        super().__init__(message)
        self.category = category
        self.details = details or {}
        self.recoverable = recoverable
        self.user_message = user_message or self._generate_user_message()
    
    def _generate_user_message(self) -> str:
        """Generate a user-friendly error message."""
        category_messages = {
            ErrorCategory.CONNECTION: "Unable to connect to ChatGPT. Please ensure ChatGPT is running and accessible.",
            ErrorCategory.AUTOMATION: "Failed to interact with ChatGPT interface. Please check if ChatGPT window is visible and responsive.",
            ErrorCategory.PROTOCOL: "Communication error occurred. Please try again.",
            ErrorCategory.CONFIGURATION: "Configuration error. Please check your settings.",
            ErrorCategory.WINDOW: "Cannot find or access ChatGPT window. Please ensure ChatGPT is running.",
            ErrorCategory.TIMEOUT: "Operation timed out. ChatGPT may be busy or unresponsive.",
            ErrorCategory.VALIDATION: "Invalid input provided. Please check your request.",
            ErrorCategory.SYSTEM: "An unexpected error occurred. Please try again."
        }
        return category_messages.get(self.category, "An error occurred.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging and debugging."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "category": self.category.value,
            "details": self.details,
            "recoverable": self.recoverable,
            "user_message": self.user_message
        }


class ChatGPTConnectionError(MCPError):
    """Raised when unable to connect to or find ChatGPT application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.CONNECTION,
            details=details,
            recoverable=True,
            user_message="Cannot connect to ChatGPT. Please ensure ChatGPT is running and try again."
        )


class ChatGPTWindowError(MCPError):
    """Raised when ChatGPT window cannot be found or accessed."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            category=ErrorCategory.WINDOW,
            details=details,
            recoverable=True,
            user_message="Cannot find ChatGPT window. Please ensure ChatGPT is open and visible."
        )


class AutomationError(MCPError):
    """Raised when UI automation operations fail."""
    
    def __init__(self, message: str, operation: str, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details["operation"] = operation
        
        super().__init__(
            message=message,
            category=ErrorCategory.AUTOMATION,
            details=enhanced_details,
            recoverable=True,
            user_message=f"Failed to {operation}. Please ensure ChatGPT window is accessible and try again."
        )


class ResponseTimeoutError(MCPError):
    """Raised when waiting for ChatGPT response times out."""
    
    def __init__(self, timeout_duration: float, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        enhanced_details["timeout_duration"] = timeout_duration
        
        super().__init__(
            message=f"Response timeout after {timeout_duration} seconds",
            category=ErrorCategory.TIMEOUT,
            details=enhanced_details,
            recoverable=True,
            user_message=f"ChatGPT did not respond within {timeout_duration} seconds. It may be processing a complex request or experiencing issues."
        )


class ConfigurationError(MCPError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        if config_key:
            enhanced_details["config_key"] = config_key
        
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            details=enhanced_details,
            recoverable=False,
            user_message="Configuration error. Please check your settings and try again."
        )


class ValidationError(MCPError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            details=details,
            recoverable=False,
            user_message=f"Invalid input: {message}"
        )


class ProtocolError(MCPError):
    """Raised when MCP protocol communication fails."""
    
    def __init__(self, message: str, request_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        if request_id:
            enhanced_details["request_id"] = request_id
        
        super().__init__(
            message=message,
            category=ErrorCategory.PROTOCOL,
            details=enhanced_details,
            recoverable=True,
            user_message="Communication error occurred. Please try your request again."
        )


class ParsingError(MCPError):
    """Raised when response parsing fails."""
    
    def __init__(self, message: str, content: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        if content:
            enhanced_details["content"] = content[:200] + "..." if len(content) > 200 else content
        
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            details=enhanced_details,
            recoverable=True,
            user_message="Failed to parse response content. Please try again."
        )


class SystemError(MCPError):
    """Raised for system-level errors and unexpected exceptions."""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None, details: Optional[Dict[str, Any]] = None):
        enhanced_details = details or {}
        if original_exception:
            enhanced_details["original_exception"] = str(original_exception)
            enhanced_details["exception_type"] = type(original_exception).__name__
        
        super().__init__(
            message=message,
            category=ErrorCategory.SYSTEM,
            details=enhanced_details,
            recoverable=False,
            user_message="An unexpected system error occurred. Please try again or contact support if the issue persists."
        )


# Convenience functions for creating common errors
def create_window_not_found_error(search_patterns: Optional[list] = None) -> ChatGPTWindowError:
    """Create a standardized window not found error."""
    details = {}
    if search_patterns:
        details["search_patterns"] = search_patterns
    
    return ChatGPTWindowError(
        "ChatGPT window not found using any search pattern",
        details=details
    )


def create_automation_timeout_error(operation: str, timeout: float) -> AutomationError:
    """Create a standardized automation timeout error."""
    return AutomationError(
        f"Automation operation '{operation}' timed out after {timeout} seconds",
        operation=operation,
        details={"timeout": timeout}
    )


def create_invalid_message_error(message: str, reason: str) -> ValidationError:
    """Create a standardized invalid message error."""
    return ValidationError(
        f"Invalid message: {reason}",
        field="message",
        value=message[:100] + "..." if len(message) > 100 else message
    )


def wrap_system_error(original_exception: Exception, context: str) -> SystemError:
    """Wrap an unexpected exception as a SystemError."""
    return SystemError(
        f"System error in {context}: {str(original_exception)}",
        original_exception=original_exception,
        details={"context": context}
    )