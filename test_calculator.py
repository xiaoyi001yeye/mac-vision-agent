#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打开计算器功能
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings
from src.services.action_service import ActionService
from src.utils.logger import setup_logger

def test_calculator():
    """测试打开计算器功能"""
    print("🧪 测试打开计算器功能")
    print("=" * 40)
    
    try:
        # 设置日志
        logger = setup_logger("test_calculator")
        
        # 加载配置
        settings = get_settings()
        logger.info("配置加载完成")
        
        # 初始化操作服务
        action_service = ActionService(settings)
        logger.info("操作服务初始化完成")
        
        # 启动服务
        action_service.start()
        logger.info("操作服务启动成功")
        
        # 测试打开计算器
        print("\n📱 正在打开计算器...")
        success = action_service.open_calculator()
        
        if success:
            print("✅ 计算器打开成功！")
            logger.info("计算器打开成功")
        else:
            print("❌ 计算器打开失败")
            logger.error("计算器打开失败")
        
        # 获取服务状态
        status = action_service.get_status()
        print(f"\n📊 服务状态:")
        print(f"  - 运行状态: {status['is_running']}")
        print(f"  - Hammerspoon可用: {status['hammerspoon_available']}")
        print(f"  - 屏幕尺寸: {status['screen_size']}")
        print(f"  - 操作历史数量: {status['action_history_count']}")
        
        # 停止服务
        action_service.stop()
        logger.info("操作服务已停止")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        if 'logger' in locals():
            logger.error(f"测试失败: {e}")
        return False

def test_open_application():
    """测试通用应用程序打开功能"""
    print("\n🧪 测试通用应用程序打开功能")
    print("=" * 40)
    
    try:
        # 设置日志
        logger = setup_logger("test_app")
        
        # 加载配置
        settings = get_settings()
        
        # 初始化操作服务
        action_service = ActionService(settings)
        action_service.start()
        
        # 测试打开不同应用程序
        apps_to_test = ["Calculator", "TextEdit", "Safari"]
        
        for app_name in apps_to_test:
            print(f"\n📱 正在打开 {app_name}...")
            success = action_service.open_application(app_name)
            
            if success:
                print(f"✅ {app_name} 打开成功！")
            else:
                print(f"❌ {app_name} 打开失败")
            
            # 等待一下再测试下一个
            import time
            time.sleep(1)
        
        action_service.stop()
        
    except Exception as e:
        print(f"❌ 通用应用测试失败: {e}")
        if 'logger' in locals():
            logger.error(f"通用应用测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 macOS视觉智能体 - 计算器功能测试")
    print("=" * 50)
    
    # 测试计算器
    calculator_success = test_calculator()
    
    # 测试通用应用程序打开
    test_open_application()
    
    print("\n" + "=" * 50)
    if calculator_success:
        print("🎉 测试完成！计算器功能正常工作")
    else:
        print("⚠️  测试完成，但计算器功能可能存在问题")
    
    print("\n💡 提示:")
    print("- 确保系统允许应用程序控制计算机")
    print("- 如果使用Hammerspoon，确保已正确安装和配置")
    print("- 检查系统安全设置中的辅助功能权限")

if __name__ == "__main__":
    main()