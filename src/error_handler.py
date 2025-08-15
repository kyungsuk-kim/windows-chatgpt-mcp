"""
Error Handler - Comprehensive error handling and recovery system

This module provides centralized error handling, recovery mechanisms, and user-friendly
error message formatting for the Windows ChatGPT MCP tool.
"""

import logging
import asyncio
import traceback
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .exceptions import (
    MCPError, ErrorCategory, ChatGPTConnectionError, ChatGPTWindowError,
    AutomationError, ResponseTimeoutError, ConfigurationError, ValidationError,
    ProtocolError, SystemError, wrap_system_error
)


class RecoveryStrategy(Enum):
    """Recovery strategies for different types of errors."""
    RETRY = "retry"
    RETRY_WITH_DELAY = "retry_with_delay"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK = "fallback"
    FAIL_FAST = "fail_fast"
    USER_INTERVENTION = "user_intervention"


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_multiplier: float = 2.0
    jitter: bool = True


@dataclass
class ErrorContext:
    """Context information for error handling."""
    operation: str
    timestamp: datetime
    attempt_count: int = 0
    previous_errors: List[Exception] = None
    user_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.previous_errors is None:
            self.previous_errors = []
        if self.user_data is None:
            self.user_data = {}


class ErrorHandler:
    """
    Comprehensive error handling and recovery system.
    
    Provides centralized error handling, retry mechanisms, and user-friendly
    error message formatting for MCP responses.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the error handler.
        
        Args:
            logger: Logger instance. If None, creates a default logger.
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_stats = {}
        self.recovery_strategies = self._setup_recovery_strategies()
        
    def _setup_recovery_strategies(self) -> Dict[ErrorCategory, RecoveryStrategy]:
        """Set up default recovery strategies for different error categories."""
        return {
            ErrorCategory.CONNECTION: RecoveryStrategy.RETRY_WITH_DELAY,
            ErrorCategory.AUTOMATION: RecoveryStrategy.RETRY_WITH_BACKOFF,
            ErrorCategory.PROTOCOL: RecoveryStrategy.RETRY,
            ErrorCategory.CONFIGURATION: RecoveryStrategy.FAIL_FAST,
            ErrorCategory.WINDOW: RecoveryStrategy.RETRY_WITH_DELAY,
            ErrorCategory.TIMEOUT: RecoveryStrategy.RETRY_WITH_BACKOFF,
            ErrorCategory.VALIDATION: RecoveryStrategy.FAIL_FAST,
            ErrorCategory.SYSTEM: RecoveryStrategy.USER_INTERVENTION
        }
    
    def set_recovery_strategy(self, category: ErrorCategory, strategy: RecoveryStrategy) -> None:
        """
        Set a custom recovery strategy for an error category.
        
        Args:
            category: Error category
            strategy: Recovery strategy to use
        """
        self.recovery_strategies[category] = strategy
        self.logger.info(f"Set recovery strategy for {category.value} to {strategy.value}")
    
    async def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        retry_config: Optional[RetryConfig] = None
    ) -> Optional[Any]:
        """
        Handle an error with appropriate recovery strategy.
        
        Args:
            error: The exception that occurred
            context: Error context information
            retry_config: Retry configuration (optional)
            
        Returns:
            Recovery result if successful, None if recovery failed
        """
        # Convert to MCPError if needed
        if not isinstance(error, MCPError):
            error = wrap_system_error(error, context.operation)
        
        # Log the error
        self._log_error(error, context)
        
        # Update error statistics
        self._update_error_stats(error, context)
        
        # Determine recovery strategy
        strategy = self.recovery_strategies.get(error.category, RecoveryStrategy.FAIL_FAST)
        
        # Execute recovery strategy
        return await self._execute_recovery_strategy(error, context, strategy, retry_config)
    
    def _log_error(self, error: MCPError, context: ErrorContext) -> None:
        """Log error with appropriate level and context."""
        error_dict = error.to_dict()
        # Remove 'message' key to avoid conflict with LogRecord.message
        if 'message' in error_dict:
            error_dict['error_message'] = error_dict.pop('message')
        
        error_dict.update({
            "operation": context.operation,
            "attempt_count": context.attempt_count,
            "timestamp": context.timestamp.isoformat()
        })
        
        if error.recoverable:
            self.logger.warning(f"Recoverable error in {context.operation}: {error}", extra=error_dict)
        else:
            self.logger.error(f"Non-recoverable error in {context.operation}: {error}", extra=error_dict)
            
        # Log stack trace for system errors
        if error.category == ErrorCategory.SYSTEM:
            self.logger.debug(f"Stack trace for system error: {traceback.format_exc()}")
    
    def _update_error_stats(self, error: MCPError, context: ErrorContext) -> None:
        """Update error statistics for monitoring."""
        category = error.category.value
        operation = context.operation
        
        if category not in self.error_stats:
            self.error_stats[category] = {}
        
        if operation not in self.error_stats[category]:
            self.error_stats[category][operation] = {
                "count": 0,
                "last_occurrence": None,
                "recoverable_count": 0,
                "non_recoverable_count": 0
            }
        
        stats = self.error_stats[category][operation]
        stats["count"] += 1
        stats["last_occurrence"] = context.timestamp
        
        if error.recoverable:
            stats["recoverable_count"] += 1
        else:
            stats["non_recoverable_count"] += 1
    
    async def _execute_recovery_strategy(
        self,
        error: MCPError,
        context: ErrorContext,
        strategy: RecoveryStrategy,
        retry_config: Optional[RetryConfig]
    ) -> Optional[Any]:
        """Execute the appropriate recovery strategy."""
        if strategy == RecoveryStrategy.FAIL_FAST:
            return None
        
        if strategy == RecoveryStrategy.USER_INTERVENTION:
            self.logger.error(f"User intervention required for error in {context.operation}: {error.user_message}")
            return None
        
        # For retry strategies, we don't actually retry here - that's handled by the retry decorator
        # This method just determines if recovery is possible
        if strategy in [RecoveryStrategy.RETRY, RecoveryStrategy.RETRY_WITH_DELAY, RecoveryStrategy.RETRY_WITH_BACKOFF]:
            if not error.recoverable:
                return None
            
            # Check if we've exceeded max attempts
            config = retry_config or RetryConfig()
            if context.attempt_count >= config.max_attempts:
                self.logger.error(f"Max retry attempts ({config.max_attempts}) exceeded for {context.operation}")
                return None
        
        return "recoverable"  # Signal that recovery should be attempted
    
    def format_error_for_mcp(self, error: Exception, context: Optional[ErrorContext] = None) -> List[TextContent]:
        """
        Format an error for MCP response.
        
        Args:
            error: The exception that occurred
            context: Optional error context
            
        Returns:
            List of TextContent for MCP response
        """
        if isinstance(error, MCPError):
            message = error.user_message
            
            # Add context if available and error is recoverable
            if context and error.recoverable:
                if context.attempt_count > 1:
                    message += f" (Attempt {context.attempt_count})"
        else:
            message = "An unexpected error occurred. Please try again."
        
        return [TextContent(type="text", text=f"Error: {message}")]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get current error statistics."""
        return {
            "error_stats": self.error_stats,
            "recovery_strategies": {k.value: v.value for k, v in self.recovery_strategies.items()}
        }
    
    def reset_error_stats(self) -> None:
        """Reset error statistics."""
        self.error_stats.clear()
        self.logger.info("Error statistics reset")


def with_error_handling(
    operation_name: str,
    error_handler: Optional[ErrorHandler] = None,
    retry_config: Optional[RetryConfig] = None
):
    """
    Decorator for adding comprehensive error handling to functions.
    
    Args:
        operation_name: Name of the operation for logging and context
        error_handler: Error handler instance (optional)
        retry_config: Retry configuration (optional)
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            handler = error_handler or ErrorHandler()
            config = retry_config or RetryConfig()
            
            context = ErrorContext(
                operation=operation_name,
                timestamp=datetime.now()
            )
            
            last_error = None
            
            for attempt in range(1, config.max_attempts + 1):
                context.attempt_count = attempt
                
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_error = e
                    context.previous_errors.append(e)
                    
                    # Handle the error
                    recovery_result = await handler.handle_error(e, context, config)
                    
                    # If recovery is not possible, break the retry loop
                    if recovery_result is None:
                        break
                    
                    # If this is not the last attempt, wait before retrying
                    if attempt < config.max_attempts:
                        delay = await _calculate_retry_delay(attempt, config, handler.recovery_strategies.get(
                            getattr(e, 'category', ErrorCategory.SYSTEM)
                        ))
                        if delay > 0:
                            await asyncio.sleep(delay)
            
            # If we get here, all retries failed
            if isinstance(last_error, MCPError):
                raise last_error
            else:
                raise wrap_system_error(last_error, operation_name)
        
        return wrapper
    return decorator


async def _calculate_retry_delay(
    attempt: int,
    config: RetryConfig,
    strategy: Optional[RecoveryStrategy]
) -> float:
    """Calculate delay before retry based on strategy and configuration."""
    if strategy == RecoveryStrategy.RETRY:
        return 0.0
    
    if strategy == RecoveryStrategy.RETRY_WITH_DELAY:
        return config.base_delay
    
    if strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
        delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        delay = min(delay, config.max_delay)
        
        # Add jitter if enabled
        if config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 50-100% of calculated delay
        
        return delay
    
    return 0.0


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_global_error_handler() -> ErrorHandler:
    """Get or create the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_global_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _global_error_handler
    _global_error_handler = handler


# Convenience functions for common error handling patterns
async def handle_mcp_tool_error(error: Exception, tool_name: str) -> List[TextContent]:
    """
    Handle errors in MCP tool execution and format for response.
    
    Args:
        error: The exception that occurred
        tool_name: Name of the MCP tool
        
    Returns:
        List of TextContent for MCP response
    """
    handler = get_global_error_handler()
    context = ErrorContext(
        operation=f"mcp_tool_{tool_name}",
        timestamp=datetime.now()
    )
    
    # Log and handle the error
    await handler.handle_error(error, context)
    
    # Format for MCP response
    return handler.format_error_for_mcp(error, context)


async def safe_automation_call(
    func: Callable[..., Awaitable[Any]],
    operation_name: str,
    *args,
    **kwargs
) -> Any:
    """
    Safely execute an automation function with error handling.
    
    Args:
        func: Function to execute
        operation_name: Name of the operation
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Function result
        
    Raises:
        MCPError: If the operation fails after retries
    """
    @with_error_handling(operation_name)
    async def wrapper():
        return await func(*args, **kwargs)
    
    return await wrapper()