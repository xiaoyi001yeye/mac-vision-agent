#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的macOS视觉智能体启动脚本
避免复杂依赖，专注核心功能测试
"""

import os
import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_environment():
    """设置环境"""
    # 创建必要的目录
    directories = [
        "logs",
        "data",
        "data/screenshots",
        "data/models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {directory}")

def test_basic_imports():
    """测试基础导入"""
    print("\n=== 测试基础导入 ===")
    
    try:
        import pyautogui
        print("✓ pyautogui 导入成功")
        
        # 测试屏幕截图
        screenshot = pyautogui.screenshot()
        screenshot_path = "data/screenshots/test_screenshot.png"
        screenshot.save(screenshot_path)
        print(f"✓ 屏幕截图保存到: {screenshot_path}")
        
    except Exception as e:
        print(f"✗ pyautogui 测试失败: {e}")
    
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

def test_mlx():
    """测试MLX"""
    print("\n=== 测试MLX ===")
    
    try:
        import mlx.core as mx
        print("✓ MLX core 导入成功")
        
        # 简单的MLX测试
        a = mx.array([1, 2, 3])
        b = mx.array([4, 5, 6])
        c = a + b
        print(f"✓ MLX 计算测试: {a} + {b} = {c}")
        
    except Exception as e:
        print(f"✗ MLX 测试失败: {e}")
    
    try:
        from mlx_vlm import load, generate
        print("✓ MLX-VLM 导入成功")
    except Exception as e:
        print(f"✗ MLX-VLM 导入失败: {e}")

def test_services():
    """测试服务模块"""
    print("\n=== 测试服务模块 ===")
    
    try:
        from services.screen_service import ScreenService
        from config.settings import Settings
        
        settings = Settings()
        screen_service = ScreenService(settings)
        print("✓ ScreenService 创建成功")
        
        # 测试屏幕尺寸获取
        size = screen_service.get_screen_size()
        print(f"✓ 屏幕尺寸: {size}")
        
    except Exception as e:
        print(f"✗ ScreenService 测试失败: {e}")
    
    try:
        from services.vlm_service import VLMService
        from config.settings import Settings
        
        settings = Settings()
        vlm_service = VLMService(settings)
        print("✓ VLMService 创建成功")
        
    except Exception as e:
        print(f"✗ VLMService 测试失败: {e}")
    
    try:
        from services.action_service import ActionService
        from config.settings import Settings
        
        settings = Settings()
        action_service = ActionService(settings)
        print("✓ ActionService 创建成功")
        
    except Exception as e:
        print(f"✗ ActionService 测试失败: {e}")

def interactive_mode():
    """交互模式"""
    print("\n=== 交互模式 ===")
    print("可用命令:")
    print("  screenshot - 截取屏幕")
    print("  screen_info - 显示屏幕信息")
    print("  test_click - 测试点击（安全模式）")
    print("  quit - 退出")
    
    try:
        from services.screen_service import ScreenService
        from services.action_service import ActionService
        from config.settings import Settings
        
        settings = Settings()
        screen_service = ScreenService(settings)
        action_service = ActionService(settings)
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "screenshot":
                    timestamp = int(time.time())
                    filename = f"data/screenshots/interactive_{timestamp}.png"
                    result = screen_service.capture_screen(save_path=filename)
                    if result:
                        print(f"✓ 截图保存到: {filename}")
                    else:
                        print("✗ 截图失败")
                elif command == "screen_info":
                    size = screen_service.get_screen_size()
                    print(f"屏幕尺寸: {size}")
                elif command == "test_click":
                    print("安全测试：将在3秒后点击屏幕中心")
                    time.sleep(3)
                    size = screen_service.get_screen_size()
                    center_x, center_y = size[0] // 2, size[1] // 2
                    result = action_service.click(center_x, center_y)
                    if result:
                        print(f"✓ 点击成功: ({center_x}, {center_y})")
                    else:
                        print("✗ 点击失败")
                else:
                    print(f"未知命令: {command}")
                    
            except KeyboardInterrupt:
                print("\n用户中断")
                break
            except Exception as e:
                print(f"命令执行错误: {e}")
                
    except Exception as e:
        print(f"交互模式初始化失败: {e}")

def main():
    """主函数"""
    print("=== macOS Vision Agent 简化测试 ===")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 设置环境
    setup_environment()
    
    # 测试基础功能
    test_basic_imports()
    test_mlx()
    test_services()
    
    # 进入交互模式
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行错误: {e}")
    
    print("\n程序结束")

if __name__ == "__main__":
    main()