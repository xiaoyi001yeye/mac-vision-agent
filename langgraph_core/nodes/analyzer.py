"""命令分析节点

负责分析用户指令，理解意图并制定执行计划
"""

import logging
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from ..state import VisionAgentState, ExecutionStep
from src.services.vlm_service import VLMService
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def command_analyzer_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """分析用户命令节点
    
    分析用户指令，确定任务类型、意图，并制定初步的执行计划
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info(f"开始分析用户命令: {state['user_command']}")
    
    try:
        # 初始化VLM服务
        settings = Settings()
        vlm_service = VLMService(settings)
        
        # 构建分析提示
        analysis_prompt = _build_analysis_prompt(state['user_command'])
        
        # 由于这是文本分析，我们使用模拟方式
        # 在实际应用中，这里应该调用专门的文本分析服务
        analysis_result = f"任务类型: 通用操作\n任务意图: {state['user_command']}\n建议步骤: 1. 分析屏幕 2. 执行操作"
        
        # 解析分析结果
        task_info = _parse_analysis_result(analysis_result)
        
        # 创建执行计划
        execution_plan = _create_execution_plan(task_info)
        
        # 更新消息历史
        new_messages = [
            HumanMessage(content=state['user_command']),
            AIMessage(content=f"已分析指令，任务类型: {task_info['task_type']}，计划执行 {len(execution_plan)} 个步骤")
        ]
        
        logger.info(f"命令分析完成，任务类型: {task_info['task_type']}")
        
        return {
            "task_type": task_info['task_type'],
            "task_intent": task_info['task_intent'],
            "execution_plan": execution_plan,
            "messages": new_messages,
            "debug_info": {
                **state.get('debug_info', {}),
                "analysis_result": analysis_result,
                "analysis_timestamp": _get_timestamp()
            }
        }
        
    except Exception as e:
        logger.error(f"命令分析失败: {str(e)}")
        return {
            "error_message": f"命令分析失败: {str(e)}",
            "messages": [AIMessage(content=f"抱歉，无法理解您的指令: {str(e)}")]
        }


def _build_analysis_prompt(user_command: str) -> str:
    """构建分析提示词"""
    return f"""
请分析以下用户指令，并提供结构化的分析结果：

用户指令: "{user_command}"

请分析并返回以下信息（JSON格式）：
{{
    "task_type": "任务类型(click/type/scroll/drag/analyze/open_app/close_app/other)",
    "task_intent": "任务意图的详细描述",
    "target_description": "目标元素的描述（如果适用）",
    "action_parameters": {{
        "text_to_type": "需要输入的文本（如果是输入任务）",
        "app_name": "应用程序名称（如果是打开/关闭应用）",
        "scroll_direction": "滚动方向（如果是滚动任务）",
        "other_params": "其他相关参数"
    }},
    "complexity": "任务复杂度(simple/medium/complex)",
    "estimated_steps": "预估执行步骤数"
}}

注意：
1. 如果指令不明确，task_type设为"analyze"
2. 尽可能详细地描述任务意图
3. 考虑macOS系统的特点
"""


def _parse_analysis_result(analysis_result: str) -> Dict[str, Any]:
    """解析VLM分析结果"""
    import json
    
    try:
        # 尝试解析JSON
        if '{' in analysis_result and '}' in analysis_result:
            json_start = analysis_result.find('{')
            json_end = analysis_result.rfind('}') + 1
            json_str = analysis_result[json_start:json_end]
            result = json.loads(json_str)
        else:
            # 如果不是JSON格式，创建默认结构
            result = {
                "task_type": "analyze",
                "task_intent": analysis_result,
                "target_description": "",
                "action_parameters": {},
                "complexity": "medium",
                "estimated_steps": 1
            }
    except json.JSONDecodeError:
        logger.warning("无法解析VLM返回的JSON，使用默认结构")
        result = {
            "task_type": "analyze",
            "task_intent": analysis_result,
            "target_description": "",
            "action_parameters": {},
            "complexity": "medium",
            "estimated_steps": 1
        }
    
    return result


def _create_execution_plan(task_info: Dict[str, Any]) -> List[ExecutionStep]:
    """根据任务信息创建执行计划"""
    task_type = task_info.get('task_type', 'analyze')
    action_params = task_info.get('action_parameters', {})
    
    plan = []
    
    if task_type == 'click':
        plan.append(ExecutionStep(
            step_id=1,
            action_type='click',
            target={'description': task_info.get('target_description', '')},
            parameters={},
            description=f"点击 {task_info.get('target_description', '目标元素')}",
            expected_result="成功点击目标元素"
        ))
    
    elif task_type == 'type':
        plan.extend([
            ExecutionStep(
                step_id=1,
                action_type='click',
                target={'description': task_info.get('target_description', '输入框')},
                parameters={},
                description="点击输入框",
                expected_result="输入框获得焦点"
            ),
            ExecutionStep(
                step_id=2,
                action_type='type',
                target=None,
                parameters={'text': action_params.get('text_to_type', '')},
                description=f"输入文本: {action_params.get('text_to_type', '')}",
                expected_result="文本成功输入"
            )
        ])
    
    elif task_type == 'scroll':
        plan.append(ExecutionStep(
            step_id=1,
            action_type='scroll',
            target=None,
            parameters={'direction': action_params.get('scroll_direction', 'down')},
            description=f"向{action_params.get('scroll_direction', '下')}滚动",
            expected_result="页面成功滚动"
        ))
    
    elif task_type == 'open_app':
        plan.append(ExecutionStep(
            step_id=1,
            action_type='open_app',
            target=None,
            parameters={'app_name': action_params.get('app_name', '')},
            description=f"打开应用程序: {action_params.get('app_name', '')}",
            expected_result="应用程序成功启动"
        ))
    
    else:  # analyze or other
        plan.append(ExecutionStep(
            step_id=1,
            action_type='analyze',
            target=None,
            parameters={},
            description="分析当前屏幕内容",
            expected_result="获得屏幕分析结果"
        ))
    
    return plan


def _get_timestamp() -> str:
    """获取当前时间戳"""
    import time
    return str(time.time())