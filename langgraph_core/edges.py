"""LangGraph 边定义

定义节点之间的条件分支逻辑
"""

import logging
from typing import Literal

from .state import VisionAgentState

logger = logging.getLogger(__name__)

# 定义节点名称常量
COMMAND_ANALYZER = "command_analyzer"
SCREEN_CAPTURE = "screen_capture"
SCREEN_ANALYZER = "screen_analyzer"
ACTION_EXECUTOR = "action_executor"
RESULT_VALIDATOR = "result_validator"
ERROR_HANDLER = "error_handler"
END = "__end__"


def should_continue_after_analyzer(state: VisionAgentState) -> Literal["screen_capture", "__end__"]:
    """决定分析器节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否有错误
        if state.get('error_message'):
            logger.warning("命令分析失败，结束流程")
            return END
        
        # 检查是否有执行计划
        execution_plan = state.get('execution_plan', [])
        if not execution_plan:
            logger.warning("没有生成执行计划，结束流程")
            return END
        
        # 检查任务类型
        task_type = state.get('task_type', '')
        if task_type == 'unknown':
            logger.warning("未知任务类型，结束流程")
            return END
        
        logger.info("命令分析完成，继续屏幕捕获")
        return SCREEN_CAPTURE
        
    except Exception as e:
        logger.error(f"分析器后续流程判断失败: {str(e)}")
        return END


def should_continue_after_capture(state: VisionAgentState) -> Literal["screen_analyzer", "error_handler"]:
    """决定屏幕捕获节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否有错误
        if state.get('error_message'):
            logger.warning("屏幕捕获失败，进入错误处理")
            return ERROR_HANDLER
        
        # 检查是否有屏幕截图
        screen_analysis = state.get('screen_analysis', {})
        if not screen_analysis.get('screenshot_path'):
            logger.warning("没有屏幕截图，进入错误处理")
            return ERROR_HANDLER
        
        logger.info("屏幕捕获完成，继续屏幕分析")
        return SCREEN_ANALYZER
        
    except Exception as e:
        logger.error(f"屏幕捕获后续流程判断失败: {str(e)}")
        return ERROR_HANDLER


def should_continue_after_screen_analysis(state: VisionAgentState) -> Literal["action_executor", "error_handler"]:
    """决定屏幕分析节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否有错误
        if state.get('error_message'):
            logger.warning("屏幕分析失败，进入错误处理")
            return ERROR_HANDLER
        
        # 检查是否找到目标元素
        screen_analysis = state.get('screen_analysis', {})
        target_elements = screen_analysis.get('target_elements', [])
        
        if not target_elements:
            logger.warning("未找到目标元素，进入错误处理")
            return ERROR_HANDLER
        
        logger.info("屏幕分析完成，继续操作执行")
        return ACTION_EXECUTOR
        
    except Exception as e:
        logger.error(f"屏幕分析后续流程判断失败: {str(e)}")
        return ERROR_HANDLER


def should_continue_after_execution(state: VisionAgentState) -> Literal["result_validator", "error_handler"]:
    """决定操作执行节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否有错误
        if state.get('error_message'):
            logger.warning("操作执行失败，进入错误处理")
            return ERROR_HANDLER
        
        # 检查执行结果
        execution_results = state.get('execution_results', [])
        if not execution_results:
            logger.warning("没有执行结果，进入错误处理")
            return ERROR_HANDLER
        
        logger.info("操作执行完成，继续结果验证")
        return RESULT_VALIDATOR
        
    except Exception as e:
        logger.error(f"操作执行后续流程判断失败: {str(e)}")
        return ERROR_HANDLER


def should_continue_after_validation(state: VisionAgentState) -> Literal["screen_capture", "__end__", "error_handler"]:
    """决定结果验证节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否已完成
        if state.get('is_completed'):
            logger.info("任务已完成，结束流程")
            return END
        
        # 检查是否有错误
        if state.get('error_message'):
            logger.warning("验证发现错误，进入错误处理")
            return ERROR_HANDLER
        
        # 检查是否需要继续执行下一步
        execution_plan = state.get('execution_plan', [])
        current_step = state.get('current_step', 0)
        
        if current_step >= len(execution_plan):
            logger.info("所有步骤已完成，结束流程")
            return END
        
        # 检查是否需要重新分析屏幕
        if state.get('need_reanalyze'):
            logger.info("需要重新分析屏幕，返回屏幕捕获")
            return SCREEN_CAPTURE
        
        # 继续下一步，重新捕获屏幕
        logger.info("继续下一步，重新捕获屏幕")
        return SCREEN_CAPTURE
        
    except Exception as e:
        logger.error(f"验证后续流程判断失败: {str(e)}")
        return ERROR_HANDLER


def should_continue_after_error_handling(state: VisionAgentState) -> Literal["screen_capture", "screen_analyzer", "action_executor", "__end__"]:
    """决定错误处理节点后的流向
    
    Args:
        state: 当前状态
        
    Returns:
        下一个节点名称
    """
    try:
        # 检查是否已完成（失败或成功）
        if state.get('is_completed'):
            logger.info("错误处理完成，任务结束")
            return END
        
        # 检查重试次数
        retry_count = state.get('retry_count', 0)
        max_retries = state.get('max_retries', 3)
        
        if retry_count >= max_retries:
            logger.error("已达到最大重试次数，结束流程")
            return END
        
        # 根据错误处理策略决定下一步
        debug_info = state.get('debug_info', {})
        latest_retry_key = f"retry_{retry_count}_strategy"
        
        if latest_retry_key in debug_info:
            strategy = debug_info[latest_retry_key]
            strategy_type = strategy.get('type', 'reanalyze_screen')
            
            if strategy_type == 'reanalyze_screen':
                logger.info("重试策略: 重新分析屏幕")
                return SCREEN_CAPTURE
            elif strategy_type == 'retry_current_step':
                logger.info("重试策略: 重试当前步骤")
                return ACTION_EXECUTOR
            elif strategy_type == 'modify_plan':
                logger.info("重试策略: 修改计划，重新分析")
                return SCREEN_CAPTURE
        
        # 默认策略：重新分析屏幕
        logger.info("使用默认重试策略: 重新分析屏幕")
        return SCREEN_CAPTURE
        
    except Exception as e:
        logger.error(f"错误处理后续流程判断失败: {str(e)}")
        return END


def create_conditional_edges() -> dict:
    """创建条件边配置
    
    Returns:
        条件边配置字典
    """
    return {
        COMMAND_ANALYZER: {
            "function": should_continue_after_analyzer,
            "path_map": {
                SCREEN_CAPTURE: SCREEN_CAPTURE,
                END: END
            }
        },
        SCREEN_CAPTURE: {
            "function": should_continue_after_capture,
            "path_map": {
                SCREEN_ANALYZER: SCREEN_ANALYZER,
                ERROR_HANDLER: ERROR_HANDLER
            }
        },
        SCREEN_ANALYZER: {
            "function": should_continue_after_screen_analysis,
            "path_map": {
                ACTION_EXECUTOR: ACTION_EXECUTOR,
                ERROR_HANDLER: ERROR_HANDLER
            }
        },
        ACTION_EXECUTOR: {
            "function": should_continue_after_execution,
            "path_map": {
                RESULT_VALIDATOR: RESULT_VALIDATOR,
                ERROR_HANDLER: ERROR_HANDLER
            }
        },
        RESULT_VALIDATOR: {
            "function": should_continue_after_validation,
            "path_map": {
                SCREEN_CAPTURE: SCREEN_CAPTURE,
                ERROR_HANDLER: ERROR_HANDLER,
                END: END
            }
        },
        ERROR_HANDLER: {
            "function": should_continue_after_error_handling,
            "path_map": {
                SCREEN_CAPTURE: SCREEN_CAPTURE,
                SCREEN_ANALYZER: SCREEN_ANALYZER,
                ACTION_EXECUTOR: ACTION_EXECUTOR,
                END: END
            }
        }
    }