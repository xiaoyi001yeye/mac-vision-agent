#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的计算器打开演示
直接使用操作服务，不依赖CrewAI
"""

import sys
import time
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings
from src.services.action_service import ActionService
from src.utils.logger import setup_logger

def demo_calculator():
    """演示计算器打开功能"""
    print("🤖 macOS视觉智能体 - 计算器功能演示")
    print("=" * 50)
    
    try:
        # 设置日志
        logger = setup_logger("calculator_demo")
        logger.info("开始计算器演示")
        
        # 加载配置
        print("📋 加载配置...")
        settings = get_settings()
        print("✅ 配置加载完成")
        
        # 初始化操作服务
        print("🔧 初始化操作服务...")
        action_service = ActionService(settings)
        print("✅ 操作服务初始化完成")
        
        # 启动服务
        print("🚀 启动操作服务...")
        action_service.start()
        print("✅ 操作服务启动成功")
        
        # 显示服务状态
        status = action_service.get_status()
        print("\n📊 服务状态:")
        print(f"  - 运行状态: {'✅ 运行中' if status['is_running'] else '❌ 未运行'}")
        print(f"  - Hammerspoon: {'✅ 可用' if status['hammerspoon_available'] else '❌ 不可用，使用PyAutoGUI'}")
        if status['screen_size']:
            print(f"  - 屏幕尺寸: {status['screen_size'][0]}x{status['screen_size'][1]}")
        
        # 演示打开计算器
        print("\n📱 演示1: 打开计算器")
        print("-" * 30)
        success = action_service.open_calculator()
        
        if success:
            print("✅ 计算器打开成功！")
            print("💡 您应该能看到计算器应用程序已经打开")
        else:
            print("❌ 计算器打开失败")
        
        time.sleep(2)
        
        # 演示打开其他应用
        print("\n📱 演示2: 打开其他应用程序")
        print("-" * 30)
        
        apps_to_test = [
            ("TextEdit", "文本编辑器"),
            ("System Preferences", "系统偏好设置"),
            ("Finder", "访达")
        ]
        
        for app_name, app_desc in apps_to_test:
            print(f"\n正在打开 {app_desc} ({app_name})...")
            success = action_service.open_application(app_name)
            
            if success:
                print(f"✅ {app_desc} 打开成功！")
            else:
                print(f"❌ {app_desc} 打开失败")
            
            time.sleep(1)
        
        # 显示操作历史
        print("\n📜 操作历史:")
        print("-" * 30)
        history = action_service.get_action_history(10)
        
        for i, action in enumerate(history[-5:], 1):  # 显示最近5个操作
            timestamp = time.strftime('%H:%M:%S', time.localtime(action['timestamp']))
            status_icon = "✅" if action['success'] else "❌"
            print(f"  {i}. [{timestamp}] {status_icon} {action['type']}: {action['params']}")
        
        # 停止服务
        print("\n🛑 停止操作服务...")
        action_service.stop()
        print("✅ 操作服务已停止")
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        if 'logger' in locals():
            logger.error(f"演示失败: {e}")
        return False

def interactive_mode():
    """交互模式"""
    print("\n🎮 交互模式")
    print("=" * 40)
    print("输入应用程序名称来打开，或输入命令:")
    print("  - 'calculator' 或 'calc': 打开计算器")
    print("  - 'status': 查看服务状态")
    print("  - 'history': 查看操作历史")
    print("  - 'quit' 或 'exit': 退出")
    
    try:
        # 初始化服务
        settings = get_settings()
        action_service = ActionService(settings)
        action_service.start()
        
        print("\n✅ 交互模式已启动")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                # 处理特殊命令
                if user_input.lower() in ['calculator', 'calc']:
                    print("正在打开计算器...")
                    success = action_service.open_calculator()
                    print(f"{'✅ 成功' if success else '❌ 失败'}")
                    
                elif user_input.lower() == 'status':
                    status = action_service.get_status()
                    print("📊 服务状态:")
                    for key, value in status.items():
                        print(f"  - {key}: {value}")
                        
                elif user_input.lower() == 'history':
                    history = action_service.get_action_history(5)
                    print("📜 最近操作历史:")
                    for i, action in enumerate(history, 1):
                        timestamp = time.strftime('%H:%M:%S', time.localtime(action['timestamp']))
                        status_icon = "✅" if action['success'] else "❌"
                        print(f"  {i}. [{timestamp}] {status_icon} {action['type']}")
                        
                else:
                    # 尝试打开应用程序
                    print(f"正在打开 {user_input}...")
                    success = action_service.open_application(user_input)
                    
                    if success:
                        print(f"✅ {user_input} 打开成功！")
                    else:
                        print(f"❌ {user_input} 打开失败，请检查应用程序名称")
                        print("💡 提示: 尝试使用英文应用名称，如 Calculator, Safari, TextEdit")
                
            except KeyboardInterrupt:
                print("\n收到中断信号...")
                break
            except Exception as e:
                print(f"❌ 处理命令时出错: {e}")
        
        action_service.stop()
        print("\n👋 交互模式结束")
        
    except Exception as e:
        print(f"❌ 交互模式失败: {e}")

def main():
    """主函数"""
    print("🚀 macOS视觉智能体 - 计算器功能演示")
    print("=" * 60)
    
    # 运行基础演示
    demo_success = demo_calculator()
    
    if demo_success:
        print("\n" + "=" * 60)
        choice = input("演示成功！是否进入交互模式？(y/n): ").strip().lower()
        
        if choice in ['y', 'yes', '是']:
            interactive_mode()
    
    print("\n🎉 程序结束")
    print("\n💡 功能说明:")
    print("- ✅ 成功实现Mac计算器打开功能")
    print("- ✅ 支持多种应用程序启动")
    print("- ✅ 兼容Hammerspoon和系统原生方法")
    print("- ✅ 提供操作历史记录")
    print("- ✅ 包含安全验证机制")
    
    print("\n🔧 技术特性:")
    print("- 使用macOS原生'open'命令")
    print("- 支持Hammerspoon增强功能")
    print("- 完整的日志记录系统")
    print("- 操作安全性验证")

if __name__ == "__main__":
    main()