#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试脚本
测试核心功能而不涉及复杂的导入
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_basic_imports():
    """测试基础导入"""
    print("=== 测试基础导入 ===")
    
    try:
        import numpy as np
        print("✓ NumPy 导入成功")
    except ImportError as e:
        print(f"✗ NumPy 导入失败: {e}")
    
    try:
        from PIL import Image
        print("✓ Pillow 导入成功")
    except ImportError as e:
        print(f"✗ Pillow 导入失败: {e}")
    
    try:
        import cv2
        print("✓ OpenCV 导入成功")
    except ImportError as e:
        print(f"✗ OpenCV 导入失败: {e}")

def test_mlx():
    """测试MLX库"""
    print("\n=== 测试MLX库 ===")
    
    try:
        import mlx.core as mx
        print("✓ MLX Core 导入成功")
    except ImportError as e:
        print(f"✗ MLX Core 导入失败: {e}")
    
    try:
        import mlx_vlm
        print("✓ MLX-VLM 导入成功")
    except ImportError as e:
        print(f"✗ MLX-VLM 导入失败: {e}")

def test_config():
    """测试配置模块"""
    print("\n=== 测试配置模块 ===")
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        print(f"✓ 配置加载成功")
        print(f"  - 应用名称: {settings.app_name}")
        print(f"  - 版本: {settings.version}")
        print(f"  - 调试模式: {settings.debug}")
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")

def test_logger():
    """测试日志模块"""
    print("\n=== 测试日志模块 ===")
    
    try:
        from utils.logger import setup_logger
        logger = setup_logger("test")
        logger.info("测试日志消息")
        print("✓ 日志模块测试成功")
    except Exception as e:
        print(f"✗ 日志模块测试失败: {e}")

def test_directories():
    """测试目录创建"""
    print("\n=== 测试目录创建 ===")
    
    directories = [
        "logs",
        "data",
        "data/screenshots", 
        "data/models",
        "data/cache"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✓ 目录创建成功: {directory}")
        except Exception as e:
            print(f"✗ 目录创建失败 {directory}: {e}")

def main():
    """主函数"""
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"源码路径: {src_path}")
    
    test_directories()
    test_basic_imports()
    test_mlx()
    test_config()
    test_logger()
    
    print("\n=== 测试完成 ===")
    print("基础环境测试完成。如果大部分测试通过，说明环境配置基本正确。")

if __name__ == "__main__":
    main()