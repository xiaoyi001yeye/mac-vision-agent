#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算器打开演示脚本
展示如何使用macOS视觉智能体系统打开计算器
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.config.settings import get_settings
from src.core.agent_manager import AgentManager
from src.utils.logger import setup_logger

def demo_open_calculator():
    """演示打开计算器功能"""
    print("🤖 macOS视觉智能体 - 计算器演示")
    print("=" * 50)
    
    try:
        # 设置日志
        logger = setup_logger("calculator_demo")
        logger.info("开始计算器演示")
        
        # 加载配置
        settings = get_settings()
        logger.info("配置加载完成")
        
        # 初始化智能体管理器
        agent_manager = AgentManager(settings)
        logger.info("智能体管理器初始化完成")
        
        # 启动系统
        agent_manager.start()
        logger.info("智能体系统启动成功")
        
        print("\n🚀 系统已启动，准备打开计算器...")
        
        # 使用智能体处理打开计算器的命令
        commands = [
            "打开计算器",
            "启动Calculator应用",
            "open calculator"
        ]
        
        for i, command in enumerate(commands, 1):
            print(f"\n📝 测试命令 {i}: {command}")
            print("-" * 30)
            
            try:
                result = agent_manager.process_command(command)
                
                if result['success']:
                    print(f"✅ 命令执行成功！")
                    print(f"📊 执行时间: {result['duration']:.2f}秒")
                    print(f"📋 结果: {result['result'][:200]}..." if len(result['result']) > 200 else f"📋 结果: {result['result']}")
                else:
                    print(f"❌ 命令执行失败")
                    print(f"📋 结果: {result.get('result', '未知错误')}")
                
            except Exception as e:
                print(f"❌ 命令处理异常: {e}")
                logger.error(f"命令处理异常: {e}")
            
            # 等待一下再执行下一个命令
            import time
            time.sleep(2)
        
        # 停止系统
        agent_manager.stop()
        logger.info("智能体系统已停止")
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        if 'logger' in locals():
            logger.error(f"演示失败: {e}")

def simple_calculator_demo():
    """简单的计算器打开演示"""
    print("\n🔧 简单演示 - 直接使用操作服务")
    print("=" * 40)
    
    try:
        from src.services.action_service import ActionService
        
        # 设置日志
        logger = setup_logger("simple_demo")
        
        # 加载配置
        settings = get_settings()
        
        # 初始化操作服务
        action_service = ActionService(settings)
        action_service.start()
        
        print("\n📱 直接打开计算器...")
        success = action_service.open_calculator()
        
        if success:
            print("✅ 计算器打开成功！")
        else:
            print("❌ 计算器打开失败")
        
        # 测试其他应用
        print("\n📱 测试打开其他应用...")
        apps = ["TextEdit", "System Preferences"]
        
        for app in apps:
            print(f"  正在打开 {app}...")
            success = action_service.open_application(app)
            print(f"  {'✅ 成功' if success else '❌ 失败'}")
        
        action_service.stop()
        
    except Exception as e:
        print(f"❌ 简单演示失败: {e}")

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示")
    print("=" * 40)
    print("输入应用程序名称来打开，或输入 'quit' 退出")
    
    try:
        from src.services.action_service import ActionService
        
        # 设置服务
        settings = get_settings()
        action_service = ActionService(settings)
        action_service.start()
        
        while True:
            app_name = input("\n请输入应用程序名称 (如: Calculator, Safari, TextEdit): ").strip()
            
            if app_name.lower() in ['quit', 'exit', 'q']:
                break
            
            if not app_name:
                continue
            
            print(f"正在打开 {app_name}...")
            success = action_service.open_application(app_name)
            
            if success:
                print(f"✅ {app_name} 打开成功！")
            else:
                print(f"❌ {app_name} 打开失败，请检查应用程序名称是否正确")
        
        action_service.stop()
        print("👋 交互式演示结束")
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，演示结束")
    except Exception as e:
        print(f"❌ 交互式演示失败: {e}")

def main():
    """主演示函数"""
    print("🚀 macOS视觉智能体 - 计算器功能演示")
    print("=" * 60)
    
    # 简单演示
    simple_calculator_demo()
    
    # 询问是否进行完整演示
    print("\n" + "=" * 60)
    choice = input("是否进行完整的智能体演示？(y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是']:
        demo_open_calculator()
    
    # 询问是否进行交互式演示
    print("\n" + "=" * 60)
    choice = input("是否进行交互式演示？(y/n): ").strip().lower()
    
    if choice in ['y', 'yes', '是']:
        interactive_demo()
    
    print("\n🎉 所有演示完成！")
    print("\n💡 使用说明:")
    print("- 系统已成功实现Mac计算器打开功能")
    print("- 支持通过智能体命令或直接API调用")
    print("- 兼容Hammerspoon和系统原生方法")
    print("- 可扩展支持其他应用程序")

if __name__ == "__main__":
    main()