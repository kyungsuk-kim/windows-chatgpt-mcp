"""
Tests for the logging configuration system.

This module contains comprehensive tests for structured logging, performance monitoring,
and debugging capabilities.
"""

import pytest
import logging
import json
import time
import tempfile
import shutil
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict

from src.logging_config import (
    LoggingManager, LoggingConfig, LogLevel, StructuredFormatter,
    PerformanceMonitor, PerformanceMetric, 
    setup_logging, get_logger, get_logging_manager,
    log_performance, log_operation, log_function_call,
    log_mcp_request, log_mcp_response, log_automation_action
)


class TestLoggingConfig:
    """Test cases for LoggingConfig."""
    
    def test_default_config(self):
        """Test default logging configuration."""
        config = LoggingConfig()
        
        assert config.log_level == LogLevel.INFO
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.backup_count == 5
        assert config.enable_console is True
        assert config.enable_file is True
        assert config.enable_structured is True
        assert config.enable_performance is True
    
    def test_custom_config(self):
        """Test custom logging configuration."""
        config = LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir="/custom/logs",
            max_file_size=5 * 1024 * 1024,
            backup_count=3,
            enable_console=False,
            enable_structured=False
        )
        
        assert config.log_level == LogLevel.DEBUG
        assert config.log_dir == "/custom/logs"
        assert config.max_file_size == 5 * 1024 * 1024
        assert config.backup_count == 3
        assert config.enable_console is False
        assert config.enable_structured is False


class TestStructuredFormatter:
    """Test cases for StructuredFormatter."""
    
    @pytest.fixture
    def formatter(self):
        """Create a StructuredFormatter instance."""
        return StructuredFormatter()
    
    @pytest.fixture
    def log_record(self):
        """Create a test log record."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.funcName = "test_function"
        record.module = "test_module"
        return record
    
    def test_basic_formatting(self, formatter, log_record):
        """Test basic structured formatting."""
        formatted = formatter.format(log_record)
        data = json.loads(formatted)
        
        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Test message"
        assert data["module"] == "test_module"
        assert data["function"] == "test_function"
        assert data["line"] == 42
        assert "timestamp" in data
    
    def test_extra_fields(self, formatter, log_record):
        """Test formatting with extra fields."""
        log_record.custom_field = "custom_value"
        log_record.operation = "test_operation"
        
        formatted = formatter.format(log_record)
        data = json.loads(formatted)
        
        assert data["custom_field"] == "custom_value"
        assert data["operation"] == "test_operation"
    
    def test_exception_formatting(self, formatter, log_record):
        """Test formatting with exception info."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            log_record.exc_info = sys.exc_info()
        
        formatted = formatter.format(log_record)
        data = json.loads(formatted)
        
        assert "exception" in data
        assert "ValueError: Test exception" in data["exception"]


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create a PerformanceMonitor instance."""
        return PerformanceMonitor()
    
    @pytest.fixture
    def sample_metric(self):
        """Create a sample performance metric."""
        return PerformanceMetric(
            operation="test_operation",
            duration=1.5,
            timestamp=datetime.now(),
            success=True,
            metadata={"test": "data"}
        )
    
    def test_record_metric(self, monitor, sample_metric):
        """Test recording a performance metric."""
        monitor.record_metric(sample_metric)
        
        metrics = monitor.get_metrics()
        assert len(metrics) == 1
        assert metrics[0].operation == "test_operation"
        assert metrics[0].duration == 1.5
        assert metrics[0].success is True
    
    def test_get_metrics_filtering(self, monitor):
        """Test filtering metrics by operation and time."""
        now = datetime.now()
        old_time = now - timedelta(hours=2)
        
        # Add metrics
        monitor.record_metric(PerformanceMetric("op1", 1.0, now, True))
        monitor.record_metric(PerformanceMetric("op2", 2.0, now, True))
        monitor.record_metric(PerformanceMetric("op1", 1.5, old_time, False))
        
        # Test operation filtering
        op1_metrics = monitor.get_metrics(operation="op1")
        assert len(op1_metrics) == 2
        assert all(m.operation == "op1" for m in op1_metrics)
        
        # Test time filtering
        recent_metrics = monitor.get_metrics(since=now - timedelta(minutes=30))
        assert len(recent_metrics) == 2
        assert all(m.timestamp >= now - timedelta(minutes=30) for m in recent_metrics)
        
        # Test combined filtering
        recent_op1 = monitor.get_metrics(operation="op1", since=now - timedelta(minutes=30))
        assert len(recent_op1) == 1
        assert recent_op1[0].operation == "op1"
        assert recent_op1[0].timestamp >= now - timedelta(minutes=30)
    
    def test_get_statistics(self, monitor):
        """Test getting performance statistics."""
        # Add test metrics
        monitor.record_metric(PerformanceMetric("test_op", 1.0, datetime.now(), True))
        monitor.record_metric(PerformanceMetric("test_op", 2.0, datetime.now(), True))
        monitor.record_metric(PerformanceMetric("test_op", 1.5, datetime.now(), False))
        
        stats = monitor.get_statistics("test_op")
        
        assert stats["count"] == 3
        assert stats["success_rate"] == 2/3
        assert stats["avg_duration"] == 1.5
        assert stats["min_duration"] == 1.0
        assert stats["max_duration"] == 2.0
        assert stats["total_duration"] == 4.5
    
    def test_get_statistics_empty(self, monitor):
        """Test getting statistics with no metrics."""
        stats = monitor.get_statistics("nonexistent_op")
        assert stats["count"] == 0
    
    def test_clear_old_metrics(self, monitor):
        """Test clearing old metrics."""
        now = datetime.now()
        old_time = now - timedelta(hours=25)  # Older than default 24 hours
        
        # Add metrics
        monitor.record_metric(PerformanceMetric("op1", 1.0, now, True))
        monitor.record_metric(PerformanceMetric("op2", 2.0, old_time, True))
        
        assert len(monitor.get_metrics()) == 2
        
        monitor.clear_old_metrics()
        
        remaining_metrics = monitor.get_metrics()
        assert len(remaining_metrics) == 1
        assert remaining_metrics[0].operation == "op1"
    
    def test_reset_metrics(self, monitor, sample_metric):
        """Test resetting all metrics."""
        monitor.record_metric(sample_metric)
        assert len(monitor.get_metrics()) == 1
        
        monitor.reset_metrics()
        assert len(monitor.get_metrics()) == 0


class TestLoggingManager:
    """Test cases for LoggingManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close any open log handlers before cleanup
        logging.shutdown()
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, files might still be locked by logging handlers
            import time
            time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Ignore if we can't clean up
    
    @pytest.fixture
    def config(self, temp_dir):
        """Create a test logging configuration."""
        return LoggingConfig(
            log_level=LogLevel.DEBUG,
            log_dir=temp_dir,
            enable_console=True,
            enable_file=True,
            enable_structured=True
        )
    
    def test_initialization(self, config):
        """Test LoggingManager initialization."""
        manager = LoggingManager(config)
        
        assert manager.config == config
        assert isinstance(manager.performance_monitor, PerformanceMonitor)
        assert isinstance(manager.loggers, dict)
    
    def test_get_logger(self, config):
        """Test getting loggers."""
        manager = LoggingManager(config)
        
        logger1 = manager.get_logger("test.logger1")
        logger2 = manager.get_logger("test.logger2")
        logger1_again = manager.get_logger("test.logger1")
        
        assert isinstance(logger1, logging.Logger)
        assert isinstance(logger2, logging.Logger)
        assert logger1 is logger1_again  # Should return same instance
        assert logger1 is not logger2
    
    def test_set_log_level(self, config):
        """Test setting log level."""
        manager = LoggingManager(config)
        
        # Test with LogLevel enum
        manager.set_log_level(LogLevel.ERROR)
        assert manager.config.log_level == LogLevel.ERROR
        
        # Test with string
        manager.set_log_level("WARNING")
        assert manager.config.log_level == LogLevel.WARNING
        
        # Test with int
        manager.set_log_level(logging.DEBUG)
        assert manager.config.log_level == LogLevel.DEBUG
    
    def test_enable_debug_mode(self, config):
        """Test enabling debug mode."""
        manager = LoggingManager(config)
        
        manager.enable_debug_mode()
        assert manager.config.log_level == LogLevel.DEBUG
    
    def test_log_directory_creation(self, temp_dir):
        """Test that log directory is created."""
        log_dir = Path(temp_dir) / "test_logs"
        config = LoggingConfig(log_dir=str(log_dir), enable_file=True)
        
        assert not log_dir.exists()
        
        LoggingManager(config)
        
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    @patch('platform.platform')
    @patch('platform.python_version')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_log_system_info(self, mock_disk_usage, mock_virtual_memory, mock_cpu_count, mock_python_version, mock_platform_info, config):
        """Test logging system information."""
        # Mock system info
        mock_platform_info.return_value = "Windows-10"
        mock_python_version.return_value = "3.9.0"
        mock_cpu_count.return_value = 8
        mock_virtual_memory.return_value = Mock(total=16*1024**3, available=8*1024**3)
        mock_disk_usage.return_value = Mock(total=1024**4, used=512**3, free=512**3)
        
        manager = LoggingManager(config)
        
        with patch.object(manager.get_logger("system"), 'info') as mock_info:
            manager.log_system_info()
            mock_info.assert_called_once()
            
            # Check that system info was logged
            call_args = mock_info.call_args
            assert "System information" in call_args[0][0]
            assert "platform" in call_args[1]["extra"]


class TestDecorators:
    """Test cases for logging decorators."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Close any open log handlers before cleanup
        logging.shutdown()
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # On Windows, files might still be locked by logging handlers
            import time
            time.sleep(0.1)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Ignore if we can't clean up
    
    @pytest.fixture
    def setup_logging_manager(self, temp_dir):
        """Set up logging manager for tests."""
        config = LoggingConfig(log_dir=temp_dir, enable_performance=True)
        return setup_logging(config)
    
    @pytest.mark.asyncio
    async def test_log_performance_async_success(self, setup_logging_manager):
        """Test log_performance decorator with async function success."""
        @log_performance("test_async_operation")
        async def test_async_func(x, y):
            await asyncio.sleep(0.01)  # Small delay
            return x + y
        
        result = await test_async_func(1, 2)
        
        assert result == 3
        
        # Check that metric was recorded
        monitor = setup_logging_manager.get_performance_monitor()
        metrics = monitor.get_metrics("test_async_operation")
        assert len(metrics) == 1
        assert metrics[0].success is True
        assert metrics[0].duration > 0
    
    @pytest.mark.asyncio
    async def test_log_performance_async_failure(self, setup_logging_manager):
        """Test log_performance decorator with async function failure."""
        @log_performance("test_async_operation")
        async def test_async_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await test_async_func()
        
        # Check that metric was recorded with failure
        monitor = setup_logging_manager.get_performance_monitor()
        metrics = monitor.get_metrics("test_async_operation")
        assert len(metrics) == 1
        assert metrics[0].success is False
        assert "error" in metrics[0].metadata
    
    def test_log_performance_sync_success(self, setup_logging_manager):
        """Test log_performance decorator with sync function success."""
        @log_performance("test_sync_operation")
        def test_sync_func(x, y):
            time.sleep(0.01)  # Small delay
            return x * y
        
        result = test_sync_func(3, 4)
        
        assert result == 12
        
        # Check that metric was recorded
        monitor = setup_logging_manager.get_performance_monitor()
        metrics = monitor.get_metrics("test_sync_operation")
        assert len(metrics) == 1
        assert metrics[0].success is True
        assert metrics[0].duration > 0
    
    def test_log_performance_with_args(self, setup_logging_manager):
        """Test log_performance decorator with argument logging."""
        @log_performance("test_operation", include_args=True)
        def test_func(a, b, c=None):
            return a + b
        
        result = test_func(1, 2, c="test")
        
        assert result == 3
        
        # Check that arguments were logged in metadata
        monitor = setup_logging_manager.get_performance_monitor()
        metrics = monitor.get_metrics("test_operation")
        assert len(metrics) == 1
        assert "args_count" in metrics[0].metadata
        assert "kwargs_keys" in metrics[0].metadata
        assert metrics[0].metadata["args_count"] == 2
        assert "c" in metrics[0].metadata["kwargs_keys"]
    
    @pytest.mark.asyncio
    async def test_log_operation_context_manager(self, setup_logging_manager):
        """Test log_operation context manager."""
        logger = get_logger("test")
        
        with patch.object(logger, 'info') as mock_info:
            with log_operation("test_context_operation", logger):
                await asyncio.sleep(0.01)
            
            # Should have been called twice: start and end
            assert mock_info.call_count == 2
            
            # Check start call
            start_call = mock_info.call_args_list[0]
            assert "Starting operation" in start_call[0][0]
            assert start_call[1]["extra"]["operation_start"] is True
            
            # Check end call
            end_call = mock_info.call_args_list[1]
            assert "Completed operation" in end_call[0][0]
            assert end_call[1]["extra"]["operation_end"] is True
            assert end_call[1]["extra"]["success"] is True
            assert "duration" in end_call[1]["extra"]
    
    @pytest.mark.asyncio
    async def test_log_operation_with_error(self, setup_logging_manager):
        """Test log_operation context manager with error."""
        logger = get_logger("test")
        
        with patch.object(logger, 'info') as mock_info, \
             patch.object(logger, 'error') as mock_error:
            
            with pytest.raises(ValueError):
                with log_operation("test_error_operation", logger):
                    raise ValueError("Test error")
            
            # Should have start info and error calls
            mock_info.assert_called_once()
            mock_error.assert_called_once()
            
            # Check error call
            error_call = mock_error.call_args
            assert "Operation failed" in error_call[0][0]
            assert error_call[1]["extra"]["success"] is False
    
    @pytest.mark.asyncio
    async def test_log_function_call_decorator(self, setup_logging_manager):
        """Test log_function_call decorator."""
        logger = get_logger("test")
        
        @log_function_call(logger, log_args=True, log_result=True)
        async def test_func(x, y=None):
            return x * 2
        
        with patch.object(logger, 'debug') as mock_debug:
            result = await test_func(5, y="test")
            
            assert result == 10
            
            # Should have been called twice: start and end
            assert mock_debug.call_count == 2
            
            # Check calls contain function info
            calls = mock_debug.call_args_list
            assert any("Calling function" in str(call) for call in calls)
            assert any("Function completed" in str(call) for call in calls)


class TestConvenienceFunctions:
    """Test cases for convenience logging functions."""
    
    def test_log_mcp_request(self):
        """Test MCP request logging."""
        with patch('src.logging_config.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            request_data = {
                "method": "call_tool",
                "params": {"name": "test_tool"},
                "id": "123"
            }
            
            log_mcp_request(request_data)
            
            mock_get_logger.assert_called_with("mcp.requests")
            mock_logger.info.assert_called_once()
            
            call_args = mock_logger.info.call_args
            assert "MCP request received" in call_args[0][0]
            assert call_args[1]["extra"]["method"] == "call_tool"
            assert call_args[1]["extra"]["request_id"] == "123"
    
    def test_log_mcp_response(self):
        """Test MCP response logging."""
        with patch('src.logging_config.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            response_data = {"result": "success"}
            duration = 1.5
            
            log_mcp_response(response_data, duration)
            
            mock_get_logger.assert_called_with("mcp.responses")
            mock_logger.info.assert_called_once()
            
            call_args = mock_logger.info.call_args
            assert "MCP response sent" in call_args[0][0]
            assert call_args[1]["extra"]["duration"] == 1.5
            assert call_args[1]["extra"]["success"] is True
    
    def test_log_automation_action(self):
        """Test automation action logging."""
        with patch('src.logging_config.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            log_automation_action(
                action="click",
                target="button",
                success=True,
                details={"coordinates": (100, 200)}
            )
            
            mock_get_logger.assert_called_with("automation")
            mock_logger.log.assert_called_once()
            
            call_args = mock_logger.log.call_args
            assert call_args[0][0] == logging.INFO  # Log level
            assert "Automation action: click on button" in call_args[0][1]
            assert call_args[1]["extra"]["action"] == "click"
            assert call_args[1]["extra"]["target"] == "button"
            assert call_args[1]["extra"]["success"] is True
            assert call_args[1]["extra"]["coordinates"] == (100, 200)


class TestGlobalFunctions:
    """Test cases for global logging functions."""
    
    def test_setup_logging(self):
        """Test setup_logging function."""
        config = LoggingConfig(log_level=LogLevel.DEBUG)
        manager = setup_logging(config)
        
        assert isinstance(manager, LoggingManager)
        assert manager.config == config
        
        # Test that global manager is set
        global_manager = get_logging_manager()
        assert global_manager is manager
    
    def test_get_logger(self):
        """Test get_logger function."""
        logger = get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"


if __name__ == "__main__":
    pytest.main([__file__])