"""结果验证和错误处理节点

负责验证执行结果和处理错误情况
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from ..state import VisionAgentState

logger = logging.getLogger(__name__)


def result_validator_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """结果验证节点
    
    验证执行结果，判断任务是否完成以及是否成功
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info("开始验证执行结果")
    
    try:
        execution_plan = state.get('execution_plan', [])
        current_step = state.get('current_step', 0)
        execution_results = state.get('execution_results', [])
        error_message = state.get('error_message')
        
        # 检查是否有错误
        if error_message:
            logger.warning(f"检测到错误: {error_message}")
            return _handle_error_validation(state)
        
        # 检查是否所有步骤都已完成
        if current_step >= len(execution_plan):
            logger.info("所有执行步骤已完成")
            return _validate_completion(state, execution_results)
        
        # 验证当前步骤的执行结果
        if execution_results:
            last_result = execution_results[-1]
            if not last_result.get('success', False):
                logger.warning(f"步骤 {current_step} 执行失败")
                return {
                    "error_message": last_result.get('error_message', '步骤执行失败'),
                    "messages": [AIMessage(content=f"步骤 {current_step} 执行失败: {last_result.get('error_message', '未知错误')}")]
                }
        
        # 继续执行下一步
        logger.info(f"步骤 {current_step} 验证通过，准备执行下一步")
        return {
            "messages": [AIMessage(content=f"步骤 {current_step} 验证通过")],
            "debug_info": {
                **state.get('debug_info', {}),
                "validation_timestamp": _get_timestamp(),
                "validation_status": "passed"
            }
        }
        
    except Exception as e:
        logger.error(f"结果验证失败: {str(e)}")
        return {
            "error_message": f"结果验证失败: {str(e)}",
            "messages": [AIMessage(content=f"结果验证失败: {str(e)}")]
        }


def error_handler_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """错误处理节点
    
    处理执行过程中的错误，决定重试策略
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info("开始处理错误")
    
    try:
        error_message = state.get('error_message', '')
        retry_count = state.get('retry_count', 0)
        max_retries = state.get('max_retries', 3)
        current_step = state.get('current_step', 0)
        
        logger.warning(f"处理错误: {error_message}, 重试次数: {retry_count}/{max_retries}")
        
        # 检查是否超过最大重试次数
        if retry_count >= max_retries:
            logger.error("已达到最大重试次数，任务失败")
            return {
                "is_completed": True,
                "is_success": False,
                "error_message": f"任务失败，已重试 {retry_count} 次: {error_message}",
                "messages": [AIMessage(content=f"任务失败，已达到最大重试次数: {error_message}")]
            }
        
        # 分析错误类型并制定重试策略
        retry_strategy = _analyze_error_and_get_strategy(error_message, state)
        
        # 增加重试次数
        new_retry_count = retry_count + 1
        
        # 准备重试的状态更新
        retry_update = {
            "retry_count": new_retry_count,
            "error_message": None,  # 清除错误信息，准备重试
            "messages": [AIMessage(content=f"第 {new_retry_count} 次重试，策略: {retry_strategy['description']}")],
            "debug_info": {
                **state.get('debug_info', {}),
                f"retry_{new_retry_count}_timestamp": _get_timestamp(),
                f"retry_{new_retry_count}_strategy": retry_strategy,
                f"retry_{new_retry_count}_error": error_message
            }
        }
        
        # 根据重试策略调整状态
        if retry_strategy['type'] == 'reanalyze_screen':
            retry_update["need_reanalyze"] = True
            retry_update["current_step"] = max(0, current_step - 1)  # 回退一步
        
        elif retry_strategy['type'] == 'retry_current_step':
            # 保持当前步骤，重新执行
            pass
        
        elif retry_strategy['type'] == 'modify_plan':
            # 修改执行计划（这里可以添加更复杂的逻辑）
            retry_update["need_reanalyze"] = True
        
        logger.info(f"准备第 {new_retry_count} 次重试，策略: {retry_strategy['type']}")
        
        return retry_update
        
    except Exception as e:
        logger.error(f"错误处理失败: {str(e)}")
        return {
            "is_completed": True,
            "is_success": False,
            "error_message": f"错误处理失败: {str(e)}",
            "messages": [AIMessage(content=f"错误处理失败: {str(e)}")]
        }


def _handle_error_validation(state: VisionAgentState) -> Dict[str, Any]:
    """处理有错误的验证情况"""
    retry_count = state.get('retry_count', 0)
    max_retries = state.get('max_retries', 3)
    
    if retry_count >= max_retries:
        return {
            "is_completed": True,
            "is_success": False,
            "messages": [AIMessage(content="任务失败，已达到最大重试次数")]
        }
    
    # 需要进入错误处理流程
    return {
        "messages": [AIMessage(content="检测到错误，准备重试")]
    }


def _validate_completion(state: VisionAgentState, execution_results: list) -> Dict[str, Any]:
    """验证任务完成情况"""
    # 检查所有步骤是否都成功执行
    all_success = all(result.get('success', False) for result in execution_results)
    
    if all_success:
        logger.info("任务成功完成")
        return {
            "is_completed": True,
            "is_success": True,
            "messages": [AIMessage(content="任务已成功完成！")],
            "debug_info": {
                **state.get('debug_info', {}),
                "completion_timestamp": _get_timestamp(),
                "total_steps": len(execution_results),
                "success_rate": 1.0
            }
        }
    else:
        # 有步骤失败，但已完成所有尝试
        failed_steps = [i for i, result in enumerate(execution_results) if not result.get('success', False)]
        logger.warning(f"任务完成但有失败步骤: {failed_steps}")
        
        return {
            "is_completed": True,
            "is_success": False,
            "error_message": f"部分步骤执行失败: 步骤 {failed_steps}",
            "messages": [AIMessage(content=f"任务完成，但步骤 {failed_steps} 执行失败")],
            "debug_info": {
                **state.get('debug_info', {}),
                "completion_timestamp": _get_timestamp(),
                "total_steps": len(execution_results),
                "failed_steps": failed_steps,
                "success_rate": sum(1 for r in execution_results if r.get('success', False)) / len(execution_results)
            }
        }


def _analyze_error_and_get_strategy(error_message: str, state: VisionAgentState) -> Dict[str, Any]:
    """分析错误并获取重试策略
    
    Args:
        error_message: 错误信息
        state: 当前状态
        
    Returns:
        重试策略字典
    """
    if not error_message:
        error_message = "未知错误"
    
    error_lower = error_message.lower()
    
    # 屏幕相关错误 - 需要重新分析屏幕
    if any(keyword in error_lower for keyword in ['目标元素', '坐标', '截图', '屏幕', 'ui元素']):
        return {
            "type": "reanalyze_screen",
            "description": "重新捕获和分析屏幕",
            "reason": "屏幕内容可能已变化或元素识别有误"
        }
    
    # 操作执行错误 - 重试当前步骤
    if any(keyword in error_lower for keyword in ['点击', 'click', '输入', 'type', '滚动', 'scroll']):
        return {
            "type": "retry_current_step",
            "description": "重试当前操作步骤",
            "reason": "操作执行可能因为时序问题失败"
        }
    
    # 应用程序相关错误 - 重新分析
    if any(keyword in error_lower for keyword in ['应用', 'app', '程序', '窗口']):
        return {
            "type": "reanalyze_screen",
            "description": "重新分析应用程序状态",
            "reason": "应用程序状态可能已变化"
        }
    
    # 默认策略 - 重新分析屏幕
    return {
        "type": "reanalyze_screen",
        "description": "重新分析屏幕内容",
        "reason": "通用错误恢复策略"
    }


def _get_timestamp() -> str:
    """获取当前时间戳"""
    import time
    return str(time.time())