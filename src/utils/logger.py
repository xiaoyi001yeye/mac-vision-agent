#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
提供统一的日志配置和管理功能
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def setup_logger(name="mac_vision_agent", level=logging.INFO):
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 按日期轮转
    today = datetime.now().strftime("%Y%m%d")
    file_handler = TimedRotatingFileHandler(
        log_dir / f"agent_{today}.log",
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # 性能日志处理器
    perf_handler = RotatingFileHandler(
        log_dir / "performance.log",
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    perf_handler.setLevel(logging.INFO)
    perf_formatter = logging.Formatter(
        '%(asctime)s - PERF - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    perf_handler.setFormatter(perf_formatter)
    
    # 创建性能日志记录器
    perf_logger = logging.getLogger(f"{name}.performance")
    perf_logger.setLevel(logging.INFO)
    perf_logger.addHandler(perf_handler)
    
    return logger

def get_logger(name="mac_vision_agent"):
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    return logging.getLogger(name)

def get_performance_logger(name="mac_vision_agent"):
    """
    获取性能日志记录器
    
    Args:
        name: 基础日志记录器名称
        
    Returns:
        logging.Logger: 性能日志记录器
    """
    return logging.getLogger(f"{name}.performance")

class LoggerMixin:
    """
    日志记录器混入类
    为其他类提供日志功能
    """
    
    @property
    def logger(self):
        """获取日志记录器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger()
        return self._logger
    
    @property
    def perf_logger(self):
        """获取性能日志记录器"""
        if not hasattr(self, '_perf_logger'):
            self._perf_logger = get_performance_logger()
        return self._perf_logger
    
    def log_performance(self, operation, duration, **kwargs):
        """
        记录性能日志
        
        Args:
            operation: 操作名称
            duration: 耗时(秒)
            **kwargs: 额外信息
        """
        extra_info = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        message = f"{operation} - Duration: {duration:.3f}s"
        if extra_info:
            message += f" - {extra_info}"
        self.perf_logger.info(message)

# 装饰器：自动记录函数执行时间
def log_execution_time(operation_name=None):
    """
    装饰器：记录函数执行时间
    
    Args:
        operation_name: 操作名称，默认使用函数名
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 获取性能日志记录器
                perf_logger = get_performance_logger()
                op_name = operation_name or func.__name__
                perf_logger.info(f"{op_name} - Duration: {duration:.3f}s - Status: SUCCESS")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # 记录失败的操作
                perf_logger = get_performance_logger()
                op_name = operation_name or func.__name__
                perf_logger.info(f"{op_name} - Duration: {duration:.3f}s - Status: FAILED - Error: {str(e)}")
                
                raise
        
        return wrapper
    return decorator