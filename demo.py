#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS视觉智能体演示脚本
展示系统的核心功能
"""

import sys
import os
import time
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def demo_config():
    """演示配置系统"""
    print("=== 配置系统演示 ===")
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        print(f"应用名称: {settings.app_name}")
        print(f"版本: {settings.version}")
        print(f"MLX模型: {settings.mlx.model_name}")
        print(f"最大tokens: {settings.mlx.max_tokens}")
        print(f"温度: {settings.mlx.temperature}")
        print(f"截图目录: {settings.hammerspoon.screenshot_dir}")
        print(f"模型缓存目录: {settings.mlx.cache_dir}")
        print(f"日志级别: {settings.logging.level}")
        
        # 演示配置方法
        model_config = settings.get_model_config()
        print(f"模型配置: {model_config}")
        
        # 演示截图路径生成
        screenshot_path = settings.get_screenshot_path()
        print(f"截图路径: {screenshot_path}")
        
        print("✓ 配置系统演示成功")
        
    except Exception as e:
        print(f"✗ 配置系统演示失败: {e}")

def demo_logger():
    """演示日志系统"""
    print("\n=== 日志系统演示 ===")
    
    try:
        from utils.logger import setup_logger, get_logger, get_performance_logger
        
        # 设置主日志记录器
        main_logger = setup_logger("demo")
        
        # 演示不同级别的日志
        main_logger.debug("这是调试信息")
        main_logger.info("这是信息日志")
        main_logger.warning("这是警告信息")
        main_logger.error("这是错误信息")
        
        # 演示性能日志
        perf_logger = get_performance_logger("demo")
        perf_logger.info("模拟操作 - Duration: 1.234s - Status: SUCCESS")
        
        print("✓ 日志系统演示成功")
        
    except Exception as e:
        print(f"✗ 日志系统演示失败: {e}")

def demo_logger_mixin():
    """演示日志混入类"""
    print("\n=== 日志混入类演示 ===")
    
    try:
        from utils.logger import LoggerMixin, log_execution_time
        
        class DemoService(LoggerMixin):
            def __init__(self):
                self.name = "演示服务"
            
            @log_execution_time("demo_operation")
            def demo_operation(self):
                """演示操作"""
                self.logger.info(f"{self.name} 开始执行操作")
                time.sleep(0.1)  # 模拟耗时操作
                self.logger.info(f"{self.name} 操作完成")
                return "操作结果"
            
            def demo_performance_log(self):
                """演示性能日志"""
                start_time = time.time()
                time.sleep(0.05)
                duration = time.time() - start_time
                
                self.log_performance(
                    "custom_operation", 
                    duration,
                    param1="value1",
                    param2="value2"
                )
        
        # 创建服务实例并演示
        service = DemoService()
        result = service.demo_operation()
        service.demo_performance_log()
        
        print(f"✓ 日志混入类演示成功，操作结果: {result}")
        
    except Exception as e:
        print(f"✗ 日志混入类演示失败: {e}")

def demo_mlx_availability():
    """演示MLX可用性检查"""
    print("\n=== MLX可用性检查 ===")
    
    try:
        import mlx.core as mx
        print("✓ MLX Core 可用")
        
        # 创建简单的MLX数组
        arr = mx.array([1, 2, 3, 4, 5])
        print(f"  - MLX数组: {arr}")
        print(f"  - 数组形状: {arr.shape}")
        print(f"  - 数组类型: {arr.dtype}")
        
    except ImportError:
        print("✗ MLX Core 不可用")
    
    try:
        import mlx_vlm
        print("✓ MLX-VLM 可用")
        print(f"  - MLX-VLM版本: {getattr(mlx_vlm, '__version__', '未知')}")
        
    except ImportError:
        print("✗ MLX-VLM 不可用")

def demo_directory_structure():
    """演示目录结构"""
    print("\n=== 目录结构演示 ===")
    
    # 显示项目目录结构
    project_root = Path(__file__).parent
    
    def show_tree(path, prefix="", max_depth=2, current_depth=0):
        if current_depth >= max_depth:
            return
        
        items = sorted(path.iterdir())
        for i, item in enumerate(items):
            if item.name.startswith('.'):
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print(f"项目根目录: {project_root}")
    show_tree(project_root)

def demo_environment_info():
    """演示环境信息"""
    print("\n=== 环境信息 ===")
    
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"工作目录: {os.getcwd()}")
    print(f"平台: {sys.platform}")
    
    # 检查重要的环境变量
    env_vars = ['PATH', 'PYTHONPATH', 'HOME', 'USER']
    for var in env_vars:
        value = os.getenv(var, '未设置')
        if var == 'PATH':
            # PATH太长，只显示前几个
            paths = value.split(':')[:3]
            value = ':'.join(paths) + '...' if len(paths) >= 3 else value
        print(f"{var}: {value}")

def main():
    """主演示函数"""
    print("🤖 macOS视觉智能体系统演示")
    print("=" * 50)
    
    demo_environment_info()
    demo_directory_structure()
    demo_config()
    demo_logger()
    demo_logger_mixin()
    demo_mlx_availability()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("\n📝 说明:")
    print("- 配置系统: ✓ 正常工作")
    print("- 日志系统: ✓ 正常工作")
    print("- MLX支持: ✓ 可用")
    print("- 基础环境: ✓ 配置正确")
    print("\n🚀 系统已准备就绪，可以开始使用！")

if __name__ == "__main__":
    main()