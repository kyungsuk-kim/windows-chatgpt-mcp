"""
Logging Configuration - Structured logging and debugging capabilities

This module provides comprehensive logging configuration with structured logging,
performance monitoring, metrics collection, and log rotation management.
"""

import logging
import logging.handlers
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, asdict
from functools import wraps
from contextlib import contextmanager
import threading
from enum import Enum


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    log_level: LogLevel = LogLevel.INFO
    log_dir: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console: bool = True
    enable_file: bool = True
    enable_structured: bool = True
    enable_performance: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'getMessage', 'exc_info',
                              'exc_text', 'stack_info']:
                    log_data[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class PerformanceMonitor:
    """Performance monitoring and metrics collection."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: List[PerformanceMetric] = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.performance")
    
    def record_metric(self, metric: PerformanceMetric) -> None:
        """Record a performance metric."""
        with self.lock:
            self.metrics.append(metric)
            
            # Log the metric
            self.logger.info(
                f"Performance: {metric.operation} took {metric.duration:.3f}s",
                extra={
                    "operation": metric.operation,
                    "duration": metric.duration,
                    "success": metric.success,
                    "metadata": metric.metadata,
                    "metric_type": "performance"
                }
            )
    
    def get_metrics(self, operation: Optional[str] = None, 
                   since: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Get performance metrics with optional filtering."""
        with self.lock:
            filtered_metrics = self.metrics.copy()
            
            if operation:
                filtered_metrics = [m for m in filtered_metrics if m.operation == operation]
            
            if since:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
            
            return filtered_metrics
    
    def get_statistics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get performance statistics."""
        metrics = self.get_metrics(operation)
        
        if not metrics:
            return {"count": 0}
        
        durations = [m.duration for m in metrics]
        success_count = sum(1 for m in metrics if m.success)
        
        return {
            "count": len(metrics),
            "success_rate": success_count / len(metrics),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations)
        }
    
    def clear_old_metrics(self, older_than: timedelta = timedelta(hours=24)) -> None:
        """Clear metrics older than specified time."""
        cutoff = datetime.now() - older_than
        
        with self.lock:
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        with self.lock:
            self.metrics.clear()


class LoggingManager:
    """Central logging manager for the application."""
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        """Initialize logging manager."""
        self.config = config or LoggingConfig()
        self.performance_monitor = PerformanceMonitor()
        self.loggers: Dict[str, logging.Logger] = {}
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Create log directory if needed
        if self.config.enable_file and self.config.log_dir:
            Path(self.config.log_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config.log_level.value)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        if self.config.enable_console:
            self._add_console_handler(root_logger)
        
        # Add file handler
        if self.config.enable_file:
            self._add_file_handler(root_logger)
    
    def _add_console_handler(self, logger: logging.Logger) -> None:
        """Add console handler to logger."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.config.log_level.value)
        
        if self.config.enable_structured:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(
                self.config.log_format,
                self.config.date_format
            ))
        
        logger.addHandler(console_handler)
    
    def _add_file_handler(self, logger: logging.Logger) -> None:
        """Add rotating file handler to logger."""
        if not self.config.log_dir:
            return
        
        log_file = Path(self.config.log_dir) / "windows_chatgpt_mcp.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_file_size,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.config.log_level.value)
        
        if self.config.enable_structured:
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(logging.Formatter(
                self.config.log_format,
                self.config.date_format
            ))
        
        logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def set_log_level(self, level: Union[LogLevel, str, int]) -> None:
        """Set the log level for all loggers."""
        if isinstance(level, str):
            level = LogLevel[level.upper()]
        elif isinstance(level, int):
            level = LogLevel(level)
        
        self.config.log_level = level
        
        # Update all existing loggers
        root_logger = logging.getLogger()
        root_logger.setLevel(level.value)
        
        for handler in root_logger.handlers:
            handler.setLevel(level.value)
    
    def enable_debug_mode(self) -> None:
        """Enable debug mode with verbose logging."""
        self.set_log_level(LogLevel.DEBUG)
        
        # Add debug-specific configuration
        debug_logger = self.get_logger("debug")
        debug_logger.info("Debug mode enabled", extra={"debug_mode": True})
    
    def get_performance_monitor(self) -> PerformanceMonitor:
        """Get the performance monitor instance."""
        return self.performance_monitor
    
    def log_system_info(self) -> None:
        """Log system information for debugging."""
        import platform
        import psutil
        
        system_logger = self.get_logger("system")
        
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": {
                "total": psutil.disk_usage('.').total,
                "used": psutil.disk_usage('.').used,
                "free": psutil.disk_usage('.').free
            },
        }
        
        system_logger.info("System information", extra=system_info)
    
    def cleanup(self) -> None:
        """Clean up logging resources."""
        # Clear old performance metrics
        self.performance_monitor.clear_old_metrics()
        
        # Close all handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)


# Global logging manager instance
_logging_manager: Optional[LoggingManager] = None


def get_logging_manager() -> LoggingManager:
    """Get or create the global logging manager."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def setup_logging(config: Optional[LoggingConfig] = None) -> LoggingManager:
    """Set up logging with the given configuration."""
    global _logging_manager
    _logging_manager = LoggingManager(config)
    return _logging_manager


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return get_logging_manager().get_logger(name)


def log_performance(operation_name: str, include_args: bool = False):
    """
    Decorator for logging performance metrics of functions.
    
    Args:
        operation_name: Name of the operation for metrics
        include_args: Whether to include function arguments in metadata
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            metadata = {}
            
            if include_args:
                metadata["args_count"] = len(args)
                metadata["kwargs_keys"] = list(kwargs.keys())
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                metadata["error"] = str(e)
                metadata["error_type"] = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                metric = PerformanceMetric(
                    operation=operation_name,
                    duration=duration,
                    timestamp=datetime.now(),
                    success=success,
                    metadata=metadata
                )
                get_logging_manager().performance_monitor.record_metric(metric)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            metadata = {}
            
            if include_args:
                metadata["args_count"] = len(args)
                metadata["kwargs_keys"] = list(kwargs.keys())
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                metadata["error"] = str(e)
                metadata["error_type"] = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                metric = PerformanceMetric(
                    operation=operation_name,
                    duration=duration,
                    timestamp=datetime.now(),
                    success=success,
                    metadata=metadata
                )
                get_logging_manager().performance_monitor.record_metric(metric)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def log_operation(operation_name: str, logger: Optional[logging.Logger] = None, 
                 extra_data: Optional[Dict[str, Any]] = None):
    """
    Context manager for logging operations with timing.
    
    Args:
        operation_name: Name of the operation
        logger: Logger to use (optional)
        extra_data: Additional data to log
    """
    if logger is None:
        logger = get_logger("operations")
    
    start_time = time.time()
    extra = extra_data or {}
    extra.update({"operation": operation_name, "operation_start": True})
    
    logger.info(f"Starting operation: {operation_name}", extra=extra)
    
    try:
        yield
        success = True
    except Exception as e:
        success = False
        extra.update({"error": str(e), "error_type": type(e).__name__})
        logger.error(f"Operation failed: {operation_name}", extra=extra, exc_info=True)
        raise
    finally:
        duration = time.time() - start_time
        extra.update({
            "operation_end": True,
            "duration": duration,
            "success": success
        })
        
        if success:
            logger.info(f"Completed operation: {operation_name} in {duration:.3f}s", extra=extra)
        
        # Record performance metric
        metric = PerformanceMetric(
            operation=operation_name,
            duration=duration,
            timestamp=datetime.now(),
            success=success,
            metadata=extra_data or {}
        )
        get_logging_manager().performance_monitor.record_metric(metric)


def log_function_call(logger: Optional[logging.Logger] = None, 
                     log_args: bool = False, log_result: bool = False):
    """
    Decorator for logging function calls.
    
    Args:
        logger: Logger to use (optional)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            extra = {"function": func.__name__, "module": func.__module__}
            
            if log_args:
                extra["args"] = str(args)[:200]  # Limit length
                extra["kwargs"] = {k: str(v)[:100] for k, v in kwargs.items()}
            
            logger.debug(f"Calling function: {func.__name__}", extra=extra)
            
            try:
                result = await func(*args, **kwargs)
                
                if log_result:
                    extra["result"] = str(result)[:200]  # Limit length
                
                logger.debug(f"Function completed: {func.__name__}", extra=extra)
                return result
                
            except Exception as e:
                extra["error"] = str(e)
                logger.error(f"Function failed: {func.__name__}", extra=extra, exc_info=True)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            extra = {"function": func.__name__, "module": func.__module__}
            
            if log_args:
                extra["args"] = str(args)[:200]  # Limit length
                extra["kwargs"] = {k: str(v)[:100] for k, v in kwargs.items()}
            
            logger.debug(f"Calling function: {func.__name__}", extra=extra)
            
            try:
                result = func(*args, **kwargs)
                
                if log_result:
                    extra["result"] = str(result)[:200]  # Limit length
                
                logger.debug(f"Function completed: {func.__name__}", extra=extra)
                return result
                
            except Exception as e:
                extra["error"] = str(e)
                logger.error(f"Function failed: {func.__name__}", extra=extra, exc_info=True)
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience functions for common logging patterns
def log_mcp_request(request_data: Dict[str, Any], logger: Optional[logging.Logger] = None) -> None:
    """Log MCP request data."""
    if logger is None:
        logger = get_logger("mcp.requests")
    
    logger.info("MCP request received", extra={
        "request_type": "mcp",
        "method": request_data.get("method"),
        "params": request_data.get("params", {}),
        "request_id": request_data.get("id")
    })


def log_mcp_response(response_data: Dict[str, Any], duration: float, 
                    logger: Optional[logging.Logger] = None) -> None:
    """Log MCP response data."""
    if logger is None:
        logger = get_logger("mcp.responses")
    
    logger.info("MCP response sent", extra={
        "response_type": "mcp",
        "duration": duration,
        "success": "error" not in response_data,
        "response_size": len(str(response_data))
    })


def log_automation_action(action: str, target: str, success: bool, 
                         details: Optional[Dict[str, Any]] = None,
                         logger: Optional[logging.Logger] = None) -> None:
    """Log automation action."""
    if logger is None:
        logger = get_logger("automation")
    
    extra = {
        "action": action,
        "target": target,
        "success": success,
        "automation_type": "windows"
    }
    
    if details:
        extra.update(details)
    
    level = logging.INFO if success else logging.WARNING
    message = f"Automation action: {action} on {target}"
    
    logger.log(level, message, extra=extra)