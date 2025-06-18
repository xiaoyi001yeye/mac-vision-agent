#!/usr/bin/env python3
"""Mac Vision Agent - LangGraph版本主入口

使用LangGraph重构的视觉智能体主程序
"""

import os
import sys
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_core.graph import create_vision_agent_graph
from src.config.settings import Settings
from src.utils.logger import setup_logger


class LangGraphVisionAgent:
    """LangGraph版本的视觉智能体"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化智能体
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.settings = Settings()
        self.logger = None
        self.graph = None
        
        # 设置默认配置
        self.default_config = {
            "max_retries": 3,
            "timeout": 30,
            "debug": False,
            "log_level": "INFO"
        }
        self.config = {**self.default_config, **self.config}
    
    def setup_environment(self) -> bool:
        """设置运行环境
        
        Returns:
            是否设置成功
        """
        try:
            # 设置日志
            self.logger = setup_logger(
                name="langgraph_vision_agent",
                level=self.config.get("log_level", "INFO")
            )
            
            self.logger.info("LangGraph视觉智能体环境设置完成")
            self.logger.info(f"配置参数: {self.config}")
            
            return True
            
        except Exception as e:
            print(f"环境设置失败: {str(e)}")
            return False
    
    def initialize_graph(self) -> bool:
        """初始化LangGraph
        
        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("开始初始化LangGraph")
            
            # 创建图实例
            self.graph = create_vision_agent_graph(self.config)
            
            # 编译图
            self.graph.compile_graph()
            
            self.logger.info("LangGraph初始化完成")
            
            # 如果启用调试模式，输出图的可视化
            if self.config.get("debug", False):
                try:
                    mermaid_graph = self.graph.get_graph_visualization()
                    self.logger.debug(f"图可视化:\n{mermaid_graph}")
                except Exception as e:
                    self.logger.warning(f"无法生成图可视化: {str(e)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"LangGraph初始化失败: {str(e)}")
            return False
    
    def start(self) -> bool:
        """启动智能体
        
        Returns:
            是否启动成功
        """
        # 设置环境
        if not self.setup_environment():
            return False
        
        self.logger.info("启动LangGraph视觉智能体")
        
        # 初始化图
        if not self.initialize_graph():
            return False
        
        self.logger.info("LangGraph视觉智能体启动成功")
        return True
    
    def process_command(self, user_input: str, thread_id: str = None) -> Dict[str, Any]:
        """处理用户命令（同步版本）
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Returns:
            处理结果
        """
        if not self.graph:
            return {
                "error_message": "图未初始化",
                "is_completed": True,
                "is_success": False
            }
        
        self.logger.info(f"开始处理命令: {user_input}")
        
        try:
            # 执行图
            result = self.graph.run(user_input, thread_id)
            
            # 记录结果
            if result.get('is_success'):
                self.logger.info("命令执行成功")
            else:
                self.logger.warning(f"命令执行失败: {result.get('error_message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = f"命令处理失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error_message": error_msg,
                "is_completed": True,
                "is_success": False
            }
    
    async def aprocess_command(self, user_input: str, thread_id: str = None) -> Dict[str, Any]:
        """处理用户命令（异步版本）
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Returns:
            处理结果
        """
        if not self.graph:
            return {
                "error_message": "图未初始化",
                "is_completed": True,
                "is_success": False
            }
        
        self.logger.info(f"开始异步处理命令: {user_input}")
        
        try:
            # 异步执行图
            result = await self.graph.arun(user_input, thread_id)
            
            # 记录结果
            if result.get('is_success'):
                self.logger.info("命令执行成功")
            else:
                self.logger.warning(f"命令执行失败: {result.get('error_message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = f"命令处理失败: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error_message": error_msg,
                "is_completed": True,
                "is_success": False
            }
    
    async def stream_command(self, user_input: str, thread_id: str = None):
        """流式处理用户命令
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Yields:
            处理过程中的状态更新
        """
        if not self.graph:
            yield {
                "error": {
                    "error_message": "图未初始化",
                    "is_completed": True,
                    "is_success": False
                }
            }
            return
        
        self.logger.info(f"开始流式处理命令: {user_input}")
        
        try:
            # 流式执行图
            async for chunk in self.graph.astream(user_input, thread_id):
                yield chunk
                
        except Exception as e:
            error_msg = f"流式处理失败: {str(e)}"
            self.logger.error(error_msg)
            yield {
                "error": {
                    "error_message": error_msg,
                    "is_completed": True,
                    "is_success": False
                }
            }
    
    def get_state_history(self, thread_id: str) -> list:
        """获取状态历史
        
        Args:
            thread_id: 线程ID
            
        Returns:
            状态历史列表
        """
        if not self.graph:
            return []
        
        return self.graph.get_state_history(thread_id)
    
    def stop(self):
        """停止智能体"""
        self.logger.info("停止LangGraph视觉智能体")
        # 这里可以添加清理逻辑


def create_cli_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器
    
    Returns:
        参数解析器
    """
    parser = argparse.ArgumentParser(
        description="Mac Vision Agent - LangGraph版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main_langgraph.py --command "打开Safari浏览器"
  python main_langgraph.py --interactive
  python main_langgraph.py --command "点击屏幕中央" --debug
        """
    )
    
    parser.add_argument(
        "--command", "-c",
        type=str,
        help="要执行的命令"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="启动交互模式"
    )
    
    parser.add_argument(
        "--async", "-a",
        action="store_true",
        help="使用异步模式"
    )
    
    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="使用流式模式"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="最大重试次数（默认: 3）"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="超时时间（秒，默认: 30）"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别（默认: INFO）"
    )
    
    return parser


def run_single_command(agent: LangGraphVisionAgent, command: str, use_async: bool = False, use_stream: bool = False):
    """运行单个命令
    
    Args:
        agent: 智能体实例
        command: 要执行的命令
        use_async: 是否使用异步模式
        use_stream: 是否使用流式模式
    """
    if use_stream:
        # 流式模式
        async def stream_runner():
            print(f"\n开始流式执行命令: {command}")
            print("-" * 50)
            
            async for chunk in agent.stream_command(command):
                print(f"状态更新: {chunk}")
            
            print("-" * 50)
            print("流式执行完成")
        
        asyncio.run(stream_runner())
        
    elif use_async:
        # 异步模式
        async def async_runner():
            print(f"\n开始异步执行命令: {command}")
            result = await agent.aprocess_command(command)
            print(f"执行结果: {result}")
        
        asyncio.run(async_runner())
        
    else:
        # 同步模式
        print(f"\n开始执行命令: {command}")
        result = agent.process_command(command)
        print(f"执行结果: {result}")


def run_interactive_mode(agent: LangGraphVisionAgent, use_async: bool = False, use_stream: bool = False):
    """运行交互模式
    
    Args:
        agent: 智能体实例
        use_async: 是否使用异步模式
        use_stream: 是否使用流式模式
    """
    print("\n=== LangGraph视觉智能体交互模式 ===")
    print("输入命令，输入 'quit' 或 'exit' 退出")
    print("输入 'help' 查看帮助信息")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n请输入命令: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("退出交互模式")
                break
            
            if user_input.lower() == 'help':
                print("""
可用命令:
- 任何自然语言指令（如："打开Safari"、"点击屏幕中央"）
- help: 显示此帮助信息
- quit/exit/q: 退出程序
                """)
                continue
            
            # 执行命令
            run_single_command(agent, user_input, use_async, use_stream)
            
        except KeyboardInterrupt:
            print("\n\n收到中断信号，退出程序")
            break
        except Exception as e:
            print(f"\n错误: {str(e)}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # 创建配置
    config = {
        "debug": args.debug,
        "max_retries": args.max_retries,
        "timeout": args.timeout,
        "log_level": args.log_level
    }
    
    # 创建智能体
    agent = LangGraphVisionAgent(config)
    
    # 启动智能体
    if not agent.start():
        print("智能体启动失败")
        sys.exit(1)
    
    try:
        if args.command:
            # 单命令模式
            run_single_command(agent, args.command, getattr(args, 'async', False), args.stream)
        elif args.interactive:
            # 交互模式
            run_interactive_mode(agent, getattr(args, 'async', False), args.stream)
        else:
            # 默认显示帮助
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n收到中断信号")
    except Exception as e:
        print(f"程序执行错误: {str(e)}")
    finally:
        # 停止智能体
        agent.stop()


if __name__ == "__main__":
    main()