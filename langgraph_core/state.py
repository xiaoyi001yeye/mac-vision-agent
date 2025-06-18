"""LangGraph状态定义

定义mac-vision-agent的核心状态结构，用于在不同节点间传递和管理数据
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime
from enum import Enum
from langchain_core.messages import BaseMessage


class VisionAgentState(TypedDict):
    """视觉智能体的核心状态
    
    包含用户指令、屏幕分析、执行计划等完整的执行上下文
    """
    
    # 用户输入和任务信息
    user_command: str  # 用户原始指令
    task_type: Optional[str]  # 任务类型：'click', 'type', 'scroll', 'analyze', etc.
    task_intent: Optional[str]  # 任务意图描述
    
    # 屏幕分析相关
    screenshot_path: Optional[str]  # 屏幕截图路径
    screen_analysis: Optional[Dict[str, Any]]  # 屏幕分析结果
    ui_elements: Optional[List[Dict[str, Any]]]  # 识别的UI元素
    target_elements: Optional[List[Dict[str, Any]]]  # 目标操作元素
    
    # 执行计划和结果
    execution_plan: Optional[List[Dict[str, Any]]]  # 详细执行步骤
    current_step: int  # 当前执行步骤索引
    execution_results: List[Dict[str, Any]]  # 每步执行结果记录
    
    # 状态控制
    retry_count: int  # 当前重试次数
    max_retries: int  # 最大重试次数
    is_completed: bool  # 任务是否完成
    is_success: bool  # 任务是否成功
    error_message: Optional[str]  # 错误信息
    need_reanalyze: bool  # 是否需要重新分析屏幕
    
    # 对话历史（支持多轮交互）
    messages: List[BaseMessage]  # 对话消息历史
    
    # 元数据
    session_id: Optional[str]  # 会话ID
    timestamp: Optional[str]  # 时间戳
    debug_info: Optional[Dict[str, Any]]  # 调试信息


class ExecutionStep(TypedDict):
    """单个执行步骤的定义"""
    step_id: int
    action_type: str  # 'click', 'type', 'scroll', 'wait', etc.
    target: Optional[Dict[str, Any]]  # 目标元素信息
    parameters: Optional[Dict[str, Any]]  # 执行参数
    description: str  # 步骤描述
    expected_result: Optional[str]  # 预期结果


class ExecutionResult(TypedDict):
    """执行结果的定义"""
    step_id: int
    success: bool
    result_data: Optional[Dict[str, Any]]  # 执行结果数据
    error_message: Optional[str]  # 错误信息
    execution_time: float  # 执行耗时
    screenshot_after: Optional[str]  # 执行后的屏幕截图


class UIElement(TypedDict):
    """UI元素的定义"""
    element_id: str
    element_type: str  # 'button', 'input', 'text', 'image', etc.
    coordinates: Dict[str, int]  # {'x': int, 'y': int, 'width': int, 'height': int}
    text: Optional[str]  # 元素文本内容
    attributes: Optional[Dict[str, Any]]  # 其他属性
    confidence: float  # 识别置信度
    accessibility_info: Optional[Dict[str, Any]]  # 无障碍信息


def create_initial_state(
    user_command: str,
    session_id: Optional[str] = None,
    max_retries: int = 3
) -> VisionAgentState:
    """创建初始状态
    
    Args:
        user_command: 用户指令
        session_id: 会话ID
        max_retries: 最大重试次数
        
    Returns:
        初始化的状态对象
    """
    import time
    
    return VisionAgentState(
        user_command=user_command,
        task_type=None,
        task_intent=None,
        screenshot_path=None,
        screen_analysis=None,
        ui_elements=None,
        target_elements=None,
        execution_plan=None,
        current_step=0,
        execution_results=[],
        retry_count=0,
        max_retries=max_retries,
        is_completed=False,
        is_success=False,
        error_message=None,
        need_reanalyze=False,
        messages=[],
        session_id=session_id,
        timestamp=str(time.time()),
        debug_info={}
    )