#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础功能测试脚本
避免需要权限的操作，专注测试核心模块
"""

import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试基础导入"""
    print("=== 测试基础导入 ===")
    
    # 测试标准库
    try:
        import json
        import time
        from pathlib import Path
        print("✓ 标准库导入成功")
    except Exception as e:
        print(f"✗ 标准库导入失败: {e}")
    
    # 测试第三方库（不需要权限的）
    try:
        from PIL import Image
        print("✓ PIL 导入成功")
    except Exception as e:
        print(f"✗ PIL 导入失败: {e}")
    
    try:
        import numpy as np
        print("✓ numpy 导入成功")
    except Exception as e:
        print(f"✗ numpy 导入失败: {e}")
    
    try:
        import requests
        print("✓ requests 导入成功")
    except Exception as e:
        print(f"✗ requests 导入失败: {e}")
    
    try:
        from pydantic import BaseModel
        print("✓ pydantic 导入成功")
    except Exception as e:
        print(f"✗ pydantic 导入失败: {e}")

def test_mlx():
    """测试MLX（如果可用）"""
    print("\n=== 测试MLX ===")
    
    try:
        import mlx.core as mx
        print("✓ MLX core 导入成功")
        
        # 简单的MLX测试
        a = mx.array([1, 2, 3])
        b = mx.array([4, 5, 6])
        c = a + b
        print(f"✓ MLX 计算测试成功: [1,2,3] + [4,5,6] = {c.tolist()}")
        
    except Exception as e:
        print(f"✗ MLX 测试失败: {e}")
    
    try:
        from mlx_vlm import load, generate
        print("✓ MLX-VLM 导入成功")
    except Exception as e:
        print(f"✗ MLX-VLM 导入失败: {e}")

def test_config():
    """测试配置模块"""
    print("\n=== 测试配置模块 ===")
    
    try:
        from config.settings import Settings, get_settings
        settings = get_settings()
        print(f"应用名称: {settings.app_name}")
        print(f"版本: {settings.version}")
        print(f"调试模式: {settings.debug}")
        print("✓ Settings 测试成功")
    except Exception as e:
        print(f"✗ Settings 测试失败: {e}")

def test_logger():
    """测试日志模块"""
    print("\n=== 测试日志模块 ===")
    
    try:
        from utils.logger import setup_logger
        logger = setup_logger()
        logger.info("日志模块测试")
        print("✓ 日志模块测试成功")
    except Exception as e:
        print(f"✗ 日志模块测试失败: {e}")

def test_services_basic():
    """测试服务模块基础功能（不涉及权限）"""
    print("\n=== 测试服务模块基础功能 ===")
    
    try:
        import sys
        sys.path.append('/Users/weiyi/code/mac-vision-agent/src')
        from config.settings import Settings, get_settings
        settings = get_settings()
        
        # 测试VLM服务（模拟模式）
        from services.vlm_service import VLMService
        vlm_service = VLMService(settings)
        print("✓ VLMService 创建成功")
        
        # 测试模拟模式
        if hasattr(vlm_service, 'simulation_mode'):
            print(f"  - 模拟模式: {vlm_service.simulation_mode}")
        
    except Exception as e:
        print(f"✗ VLMService 测试失败: {e}")
    
    try:
        # 测试屏幕服务（不执行实际截图）
        from services.screen_service import ScreenService
        screen_service = ScreenService(settings)
        print("✓ ScreenService 创建成功")
        
    except Exception as e:
        print(f"✗ ScreenService 测试失败: {e}")
    
    try:
        # 测试操作服务（不执行实际操作）
        from services.action_service import ActionService
        action_service = ActionService(settings)
        print("✓ ActionService 创建成功")
        
    except Exception as e:
        print(f"✗ ActionService 测试失败: {e}")

def test_tools():
    """测试工具模块"""
    print("\n=== 测试工具模块 ===")
    
    try:
        # 跳过CrewAI工具测试，因为crewai_tools未安装
        print("⚠ 跳过CrewAI工具测试（crewai_tools未安装）")
        print("✓ 工具模块测试跳过")
        
    except Exception as e:
        print(f"✗ 工具模块导入失败: {e}")

def create_test_directories():
    """创建测试目录"""
    directories = [
        "logs",
        "data",
        "data/screenshots",
        "data/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ 测试目录创建完成")

def main():
    """主函数"""
    print("=== macOS Vision Agent 基础测试 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print()
    
    # 创建目录
    create_test_directories()
    
    # 运行测试
    test_imports()
    test_mlx()
    test_config()
    test_logger()
    test_services_basic()
    test_tools()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，说明基础环境配置正确。")
    print("如果需要测试GUI功能，请确保已授予必要的权限。")

if __name__ == "__main__":
    main()