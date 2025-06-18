#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS视觉智能体系统 - 主入口文件
基于CrewAI、MLX-VLM、Hammerspoon等框架的集成实现
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.agent_manager import AgentManager
from src.utils.logger import setup_logger
from src.config.settings import Settings

def setup_environment():
    """设置运行环境"""
    # 创建必要的目录
    directories = [
        'logs',
        'data/screenshots', 
        'data/models',
        'data/cache',
        'hammerspoon'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 设置日志
    logger = setup_logger()
    logger.info("环境设置完成")
    
    return logger

def main():
    """主函数"""
    try:
        # 设置环境
        logger = setup_environment()
        logger.info("=" * 50)
        logger.info("macOS视觉智能体系统启动")
        logger.info("=" * 50)
        
        # 加载配置
        settings = Settings()
        logger.info(f"配置加载完成: {settings.model_config}")
        
        # 初始化智能体管理器
        agent_manager = AgentManager(settings)
        logger.info("智能体管理器初始化完成")
        
        # 启动系统
        agent_manager.start()
        
        # 交互式命令行
        print("\n欢迎使用macOS视觉智能体系统!")
        print("输入指令或'quit'退出")
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                    
                if not user_input:
                    continue
                    
                logger.info(f"用户输入: {user_input}")
                
                # 处理用户指令
                result = agent_manager.process_command(user_input)
                print(f"\n结果: {result}")
                
            except KeyboardInterrupt:
                print("\n\n收到中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"处理命令时出错: {e}")
                print(f"错误: {e}")
        
        # 清理资源
        agent_manager.stop()
        logger.info("系统正常退出")
        
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"系统启动失败: {e}")
        else:
            print(f"系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()