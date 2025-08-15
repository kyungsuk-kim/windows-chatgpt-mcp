"""
Tests for the error handling system.

This module contains comprehensive tests for error handling, recovery mechanisms,
and user-friendly error message formatting.
"""

import pytest
import asyncio
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Any, Dict, List

from src.error_handler import (
    ErrorHandler, RecoveryStrategy, RetryConfig, ErrorContext,
    with_error_handling, handle_mcp_tool_error, safe_automation_call,
    get_global_error_handler, set_global_error_handler
)
from src.exceptions import (
    MCPError, ErrorCategory, ChatGPTConnectionError, ChatGPTWindowError,
    AutomationError, ResponseTimeoutError, ConfigurationError, ValidationError,
    ProtocolError, SystemError
)


class TestErrorHandler:
    """Test cases for the ErrorHandler class."""
    
    @pytest.fixture
    def error_handler(self):
        """Create an ErrorHandler instance for testing."""
        logger = Mock(spec=logging.Logger)
        return ErrorHandler(logger)
    
    @pytest.fixture
    def error_context(self):
        """Create an ErrorContext instance for testing."""
        return ErrorContext(
            operation="test_operation",
            timestamp=datetime.now(),
            attempt_count=1
        )
    
    def test_initialization(self, error_handler):
        """Test ErrorHandler initialization."""
        assert error_handler.logger is not None
        assert isinstance(error_handler.error_stats, dict)
        assert isinstance(error_handler.recovery_strategies, dict)
        
        # Check default recovery strategies
        assert error_handler.recovery_strategies[ErrorCategory.CONNECTION] == RecoveryStrategy.RETRY_WITH_DELAY
        assert error_handler.recovery_strategies[ErrorCategory.AUTOMATION] == RecoveryStrategy.RETRY_WITH_BACKOFF
        assert error_handler.recovery_strategies[ErrorCategory.CONFIGURATION] == RecoveryStrategy.FAIL_FAST
    
    def test_set_recovery_strategy(self, error_handler):
        """Test setting custom recovery strategies."""
        error_handler.set_recovery_strategy(ErrorCategory.CONNECTION, RecoveryStrategy.FAIL_FAST)
        assert error_handler.recovery_strategies[ErrorCategory.CONNECTION] == RecoveryStrategy.FAIL_FAST
        
        # Verify logging was called
        error_handler.logger.info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_error_with_mcp_error(self, error_handler, error_context):
        """Test handling MCPError instances."""
        error = ChatGPTConnectionError("Connection failed", {"detail": "test"})
        
        result = await error_handler.handle_error(error, error_context)
        
        # Should return "recoverable" for recoverable errors with retry strategy
        assert result == "recoverable"
        
        # Verify logging
        error_handler.logger.warning.assert_called_once()
        
        # Verify error stats updated
        assert "connection" in error_handler.error_stats
        assert "test_operation" in error_handler.error_stats["connection"]
        assert error_handler.error_stats["connection"]["test_operation"]["count"] == 1
    
    @pytest.mark.asyncio
    async def test_handle_error_with_regular_exception(self, error_handler, error_context):
        """Test handling regular exceptions (converted to SystemError)."""
        error = ValueError("Regular exception")
        
        result = await error_handler.handle_error(error, error_context)
        
        # Should return None for non-recoverable system errors
        assert result is None
        
        # Verify logging was called (may be called multiple times due to recovery strategy)
        assert error_handler.logger.error.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_handle_error_fail_fast_strategy(self, error_handler, error_context):
        """Test fail fast recovery strategy."""
        error = ConfigurationError("Config error")
        
        result = await error_handler.handle_error(error, error_context)
        
        # Should return None for fail fast strategy
        assert result is None
    
    @pytest.mark.asyncio
    async def test_handle_error_max_attempts_exceeded(self, error_handler, error_context):
        """Test handling when max attempts are exceeded."""
        error = ChatGPTConnectionError("Connection failed")
        error_context.attempt_count = 5  # Exceed default max attempts
        
        result = await error_handler.handle_error(error, error_context, RetryConfig(max_attempts=3))
        
        # Should return None when max attempts exceeded
        assert result is None
        
        # Verify error logging
        error_handler.logger.error.assert_called()
    
    def test_format_error_for_mcp_with_mcp_error(self, error_handler):
        """Test formatting MCPError for MCP response."""
        error = ChatGPTWindowError("Window not found")
        context = ErrorContext("test_op", datetime.now(), attempt_count=2)
        
        result = error_handler.format_error_for_mcp(error, context)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Cannot find ChatGPT window" in result[0].text
        assert "(Attempt 2)" in result[0].text
    
    def test_format_error_for_mcp_with_regular_exception(self, error_handler):
        """Test formatting regular exception for MCP response."""
        error = ValueError("Regular error")
        
        result = error_handler.format_error_for_mcp(error)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "An unexpected error occurred" in result[0].text
    
    def test_get_error_stats(self, error_handler):
        """Test getting error statistics."""
        # Add some test data
        error_handler.error_stats = {
            "connection": {
                "test_op": {"count": 5, "recoverable_count": 3, "non_recoverable_count": 2}
            }
        }
        
        stats = error_handler.get_error_stats()
        
        assert "error_stats" in stats
        assert "recovery_strategies" in stats
        assert stats["error_stats"]["connection"]["test_op"]["count"] == 5
    
    def test_reset_error_stats(self, error_handler):
        """Test resetting error statistics."""
        # Add some test data
        error_handler.error_stats = {"test": "data"}
        
        error_handler.reset_error_stats()
        
        assert len(error_handler.error_stats) == 0
        error_handler.logger.info.assert_called_with("Error statistics reset")


class TestRetryDecorator:
    """Test cases for the retry decorator."""
    
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful execution without retries."""
        call_count = 0
        
        @with_error_handling("test_operation")
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_func()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_recoverable_error(self):
        """Test retry behavior on recoverable errors."""
        call_count = 0
        
        @with_error_handling("test_operation", retry_config=RetryConfig(max_attempts=3, base_delay=0.01))
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ChatGPTConnectionError("Connection failed")
            return "success"
        
        result = await test_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_fail_after_max_attempts(self):
        """Test failure after max retry attempts."""
        call_count = 0
        
        @with_error_handling("test_operation", retry_config=RetryConfig(max_attempts=2, base_delay=0.01))
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ChatGPTConnectionError("Connection failed")
        
        with pytest.raises(ChatGPTConnectionError):
            await test_func()
        
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_no_retry_on_non_recoverable_error(self):
        """Test no retry on non-recoverable errors."""
        call_count = 0
        
        @with_error_handling("test_operation")
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ConfigurationError("Config error")
        
        with pytest.raises(ConfigurationError):
            await test_func()
        
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_system_error_wrapping(self):
        """Test wrapping of regular exceptions as SystemError."""
        @with_error_handling("test_operation")
        async def test_func():
            raise ValueError("Regular error")
        
        with pytest.raises(SystemError) as exc_info:
            await test_func()
        
        assert "test_operation" in str(exc_info.value)
        assert "Regular error" in str(exc_info.value)


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    @pytest.mark.asyncio
    async def test_handle_mcp_tool_error(self):
        """Test MCP tool error handling."""
        error = ValidationError("Invalid input", field="message")
        
        result = await handle_mcp_tool_error(error, "send_message")
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Invalid input" in result[0].text
    
    @pytest.mark.asyncio
    async def test_safe_automation_call_success(self):
        """Test successful safe automation call."""
        async def test_func(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = await safe_automation_call(test_func, "test_op", "a", "b", kwarg1="c")
        
        assert result == "a-b-c"
    
    @pytest.mark.asyncio
    async def test_safe_automation_call_with_error(self):
        """Test safe automation call with error."""
        async def test_func():
            raise AutomationError("Automation failed", "test_operation")
        
        with pytest.raises(AutomationError):
            await safe_automation_call(test_func, "test_op")
    
    def test_global_error_handler(self):
        """Test global error handler management."""
        # Get initial global handler
        handler1 = get_global_error_handler()
        assert isinstance(handler1, ErrorHandler)
        
        # Should return same instance
        handler2 = get_global_error_handler()
        assert handler1 is handler2
        
        # Set custom handler
        custom_handler = ErrorHandler()
        set_global_error_handler(custom_handler)
        
        handler3 = get_global_error_handler()
        assert handler3 is custom_handler
        assert handler3 is not handler1


class TestErrorRecoveryScenarios:
    """Test cases for specific error recovery scenarios."""
    
    @pytest.fixture
    def error_handler(self):
        """Create an ErrorHandler instance for testing."""
        return ErrorHandler()
    
    @pytest.mark.asyncio
    async def test_connection_error_recovery(self, error_handler):
        """Test recovery from connection errors."""
        context = ErrorContext("connect_to_chatgpt", datetime.now())
        error = ChatGPTConnectionError("ChatGPT not running")
        
        result = await error_handler.handle_error(error, context)
        
        assert result == "recoverable"
        assert error_handler.recovery_strategies[ErrorCategory.CONNECTION] == RecoveryStrategy.RETRY_WITH_DELAY
    
    @pytest.mark.asyncio
    async def test_window_error_recovery(self, error_handler):
        """Test recovery from window errors."""
        context = ErrorContext("find_window", datetime.now())
        error = ChatGPTWindowError("Window not found")
        
        result = await error_handler.handle_error(error, context)
        
        assert result == "recoverable"
    
    @pytest.mark.asyncio
    async def test_timeout_error_recovery(self, error_handler):
        """Test recovery from timeout errors."""
        context = ErrorContext("wait_for_response", datetime.now())
        error = ResponseTimeoutError(30.0)
        
        result = await error_handler.handle_error(error, context)
        
        assert result == "recoverable"
        assert error_handler.recovery_strategies[ErrorCategory.TIMEOUT] == RecoveryStrategy.RETRY_WITH_BACKOFF
    
    @pytest.mark.asyncio
    async def test_validation_error_no_recovery(self, error_handler):
        """Test no recovery for validation errors."""
        context = ErrorContext("validate_input", datetime.now())
        error = ValidationError("Invalid message format")
        
        result = await error_handler.handle_error(error, context)
        
        assert result is None  # No recovery for validation errors
    
    @pytest.mark.asyncio
    async def test_configuration_error_no_recovery(self, error_handler):
        """Test no recovery for configuration errors."""
        context = ErrorContext("load_config", datetime.now())
        error = ConfigurationError("Missing config file")
        
        result = await error_handler.handle_error(error, context)
        
        assert result is None  # No recovery for configuration errors


class TestErrorStatistics:
    """Test cases for error statistics tracking."""
    
    @pytest.fixture
    def error_handler(self):
        """Create an ErrorHandler instance for testing."""
        return ErrorHandler()
    
    @pytest.mark.asyncio
    async def test_error_stats_tracking(self, error_handler):
        """Test error statistics tracking."""
        context1 = ErrorContext("operation1", datetime.now())
        context2 = ErrorContext("operation2", datetime.now())
        
        error1 = ChatGPTConnectionError("Connection failed")
        error2 = AutomationError("Automation failed", "click_button")
        error3 = ChatGPTConnectionError("Another connection error")
        
        await error_handler.handle_error(error1, context1)
        await error_handler.handle_error(error2, context2)
        await error_handler.handle_error(error3, context1)
        
        stats = error_handler.get_error_stats()
        
        # Check connection errors
        connection_stats = stats["error_stats"]["connection"]["operation1"]
        assert connection_stats["count"] == 2
        assert connection_stats["recoverable_count"] == 2
        assert connection_stats["non_recoverable_count"] == 0
        
        # Check automation errors
        automation_stats = stats["error_stats"]["automation"]["operation2"]
        assert automation_stats["count"] == 1
        assert automation_stats["recoverable_count"] == 1
    
    @pytest.mark.asyncio
    async def test_error_stats_reset(self, error_handler):
        """Test error statistics reset."""
        context = ErrorContext("test_op", datetime.now())
        error = ChatGPTConnectionError("Test error")
        
        await error_handler.handle_error(error, context)
        
        # Verify stats exist
        assert len(error_handler.error_stats) > 0
        
        # Reset stats
        error_handler.reset_error_stats()
        
        # Verify stats are cleared
        assert len(error_handler.error_stats) == 0


@pytest.mark.asyncio
async def test_retry_delay_calculation():
    """Test retry delay calculation for different strategies."""
    from src.error_handler import _calculate_retry_delay
    
    config = RetryConfig(base_delay=1.0, backoff_multiplier=2.0, max_delay=10.0, jitter=False)
    
    # Test no delay for RETRY strategy
    delay = await _calculate_retry_delay(1, config, RecoveryStrategy.RETRY)
    assert delay == 0.0
    
    # Test fixed delay for RETRY_WITH_DELAY strategy
    delay = await _calculate_retry_delay(1, config, RecoveryStrategy.RETRY_WITH_DELAY)
    assert delay == 1.0
    
    # Test exponential backoff for RETRY_WITH_BACKOFF strategy
    delay1 = await _calculate_retry_delay(1, config, RecoveryStrategy.RETRY_WITH_BACKOFF)
    delay2 = await _calculate_retry_delay(2, config, RecoveryStrategy.RETRY_WITH_BACKOFF)
    delay3 = await _calculate_retry_delay(3, config, RecoveryStrategy.RETRY_WITH_BACKOFF)
    
    assert delay1 == 1.0
    assert delay2 == 2.0
    assert delay3 == 4.0
    
    # Test max delay cap
    delay_high = await _calculate_retry_delay(10, config, RecoveryStrategy.RETRY_WITH_BACKOFF)
    assert delay_high == 10.0  # Should be capped at max_delay


@pytest.mark.asyncio
async def test_jitter_in_retry_delay():
    """Test jitter in retry delay calculation."""
    from src.error_handler import _calculate_retry_delay
    
    config = RetryConfig(base_delay=1.0, backoff_multiplier=2.0, jitter=True)
    
    delays = []
    for _ in range(10):
        delay = await _calculate_retry_delay(2, config, RecoveryStrategy.RETRY_WITH_BACKOFF)
        delays.append(delay)
    
    # With jitter, delays should vary
    assert len(set(delays)) > 1  # Should have different values
    
    # All delays should be between 50% and 100% of calculated delay (2.0)
    for delay in delays:
        assert 1.0 <= delay <= 2.0


if __name__ == "__main__":
    pytest.main([__file__])