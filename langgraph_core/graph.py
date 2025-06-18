"""LangGraph 图构建器

构建和配置完整的视觉智能体工作流图
"""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import VisionAgentState, create_initial_state
from .nodes.analyzer import command_analyzer_node
from .nodes.screen import screen_capture_node, screen_analyzer_node
from .nodes.executor import action_executor_node
from .nodes.validator import result_validator_node, error_handler_node
from .edges import (
    create_conditional_edges,
    COMMAND_ANALYZER,
    SCREEN_CAPTURE,
    SCREEN_ANALYZER,
    ACTION_EXECUTOR,
    RESULT_VALIDATOR,
    ERROR_HANDLER
)

logger = logging.getLogger(__name__)


class VisionAgentGraph:
    """视觉智能体图管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化图管理器
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        self.graph = None
        self.compiled_graph = None
        self.checkpointer = MemorySaver()
        
        # 设置默认配置
        self.default_config = {
            "max_retries": 3,
            "timeout": 30,
            "debug": False
        }
        self.config = {**self.default_config, **self.config}
        
        logger.info(f"初始化视觉智能体图，配置: {self.config}")
    
    def build_graph(self) -> StateGraph:
        """构建状态图
        
        Returns:
            构建好的状态图
        """
        logger.info("开始构建LangGraph状态图")
        
        # 创建状态图
        graph = StateGraph(VisionAgentState)
        
        # 添加节点
        self._add_nodes(graph)
        
        # 添加边
        self._add_edges(graph)
        
        # 设置入口点
        graph.set_entry_point(COMMAND_ANALYZER)
        
        self.graph = graph
        logger.info("LangGraph状态图构建完成")
        
        return graph
    
    def _add_nodes(self, graph: StateGraph) -> None:
        """添加所有节点
        
        Args:
            graph: 状态图实例
        """
        logger.info("添加图节点")
        
        # 添加各个功能节点
        graph.add_node(COMMAND_ANALYZER, command_analyzer_node)
        graph.add_node(SCREEN_CAPTURE, screen_capture_node)
        graph.add_node(SCREEN_ANALYZER, screen_analyzer_node)
        graph.add_node(ACTION_EXECUTOR, action_executor_node)
        graph.add_node(RESULT_VALIDATOR, result_validator_node)
        graph.add_node(ERROR_HANDLER, error_handler_node)
        
        logger.info("所有节点添加完成")
    
    def _add_edges(self, graph: StateGraph) -> None:
        """添加所有边
        
        Args:
            graph: 状态图实例
        """
        logger.info("添加图边")
        
        # 获取条件边配置
        conditional_edges = create_conditional_edges()
        
        # 添加条件边
        for node_name, edge_config in conditional_edges.items():
            graph.add_conditional_edges(
                node_name,
                edge_config["function"],
                edge_config["path_map"]
            )
        
        logger.info("所有边添加完成")
    
    def compile_graph(self) -> Any:
        """编译图
        
        Returns:
            编译后的图实例
        """
        if not self.graph:
            self.build_graph()
        
        logger.info("开始编译LangGraph")
        
        # 编译图，启用检查点功能
        self.compiled_graph = self.graph.compile(
            checkpointer=self.checkpointer,
            debug=self.config.get("debug", False)
        )
        
        logger.info("LangGraph编译完成")
        
        return self.compiled_graph
    
    def create_thread_config(self, thread_id: str = None) -> Dict[str, Any]:
        """创建线程配置
        
        Args:
            thread_id: 线程ID，如果不提供则自动生成
            
        Returns:
            线程配置字典
        """
        if not thread_id:
            import uuid
            thread_id = str(uuid.uuid4())
        
        return {
            "configurable": {
                "thread_id": thread_id,
                "max_retries": self.config.get("max_retries", 3),
                "timeout": self.config.get("timeout", 30)
            }
        }
    
    async def arun(self, user_input: str, thread_id: str = None) -> Dict[str, Any]:
        """异步运行图
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Returns:
            执行结果
        """
        if not self.compiled_graph:
            self.compile_graph()
        
        # 创建初始状态
        initial_state = create_initial_state(
            user_command=user_input,
            max_retries=self.config.get("max_retries", 3)
        )
        
        # 创建线程配置
        thread_config = self.create_thread_config(thread_id)
        
        logger.info(f"开始异步执行图，用户输入: {user_input}")
        
        try:
            # 异步执行图
            result = await self.compiled_graph.ainvoke(
                initial_state,
                config=thread_config
            )
            
            logger.info("图执行完成")
            return result
            
        except Exception as e:
            logger.error(f"图执行失败: {str(e)}")
            return {
                "error_message": f"图执行失败: {str(e)}",
                "is_completed": True,
                "is_success": False
            }
    
    def run(self, user_input: str, thread_id: str = None) -> Dict[str, Any]:
        """同步运行图
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Returns:
            执行结果
        """
        if not self.compiled_graph:
            self.compile_graph()
        
        # 创建初始状态
        initial_state = create_initial_state(
            user_command=user_input,
            max_retries=self.config.get("max_retries", 3)
        )
        
        # 创建线程配置
        thread_config = self.create_thread_config(thread_id)
        
        logger.info(f"开始异步执行图，用户输入: {user_input}")
        
        try:
            # 同步执行图
            result = self.compiled_graph.invoke(
                initial_state,
                config=thread_config
            )
            
            logger.info("图执行完成")
            return result
            
        except Exception as e:
            logger.error(f"图执行失败: {str(e)}")
            return {
                "error_message": f"图执行失败: {str(e)}",
                "is_completed": True,
                "is_success": False
            }
    
    async def astream(self, user_input: str, thread_id: str = None):
        """异步流式执行图
        
        Args:
            user_input: 用户输入
            thread_id: 线程ID
            
        Yields:
            执行过程中的状态更新
        """
        if not self.compiled_graph:
            self.compile_graph()
        
        # 创建初始状态
        initial_state = create_initial_state(
            user_command=user_input,
            max_retries=self.config.get("max_retries", 3)
        )
        
        # 创建线程配置
        thread_config = self.create_thread_config(thread_id)
        
        logger.info(f"开始异步流式执行图，用户输入: {user_input}")
        
        try:
            # 异步流式执行图
            async for chunk in self.compiled_graph.astream(
                initial_state,
                config=thread_config
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"流式执行失败: {str(e)}")
            yield {
                "error": {
                    "error_message": f"流式执行失败: {str(e)}",
                    "is_completed": True,
                    "is_success": False
                }
            }
    
    def get_graph_visualization(self) -> str:
        """获取图的可视化表示
        
        Returns:
            图的Mermaid格式字符串
        """
        if not self.compiled_graph:
            self.compile_graph()
        
        try:
            # 获取图的可视化
            return self.compiled_graph.get_graph().draw_mermaid()
        except Exception as e:
            logger.error(f"获取图可视化失败: {str(e)}")
            return f"无法生成图可视化: {str(e)}"
    
    def get_state_history(self, thread_id: str) -> list:
        """获取指定线程的状态历史
        
        Args:
            thread_id: 线程ID
            
        Returns:
            状态历史列表
        """
        if not self.compiled_graph:
            return []
        
        try:
            thread_config = self.create_thread_config(thread_id)
            # 获取状态历史
            history = list(self.compiled_graph.get_state_history(thread_config))
            return history
        except Exception as e:
            logger.error(f"获取状态历史失败: {str(e)}")
            return []


def create_vision_agent_graph(config: Dict[str, Any] = None) -> VisionAgentGraph:
    """创建视觉智能体图实例
    
    Args:
        config: 配置参数
        
    Returns:
        视觉智能体图实例
    """
    return VisionAgentGraph(config)


# 便捷函数
def quick_run(user_input: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """快速运行视觉智能体
    
    Args:
        user_input: 用户输入
        config: 配置参数
        
    Returns:
        执行结果
    """
    graph = create_vision_agent_graph(config)
    return graph.run(user_input)


async def aquick_run(user_input: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """快速异步运行视觉智能体
    
    Args:
        user_input: 用户输入
        config: 配置参数
        
    Returns:
        执行结果
    """
    graph = create_vision_agent_graph(config)
    return await graph.arun(user_input)