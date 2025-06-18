"""操作执行节点

负责执行具体的操作任务
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from ..state import VisionAgentState, ExecutionResult
from src.services.action_service import ActionService
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def action_executor_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """操作执行节点
    
    根据执行计划和目标元素执行具体操作
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info("开始执行操作")
    
    try:
        execution_plan = state.get('execution_plan', [])
        current_step = state.get('current_step', 0)
        target_elements = state.get('target_elements', [])
        
        if not execution_plan:
            raise ValueError("没有可执行的计划")
        
        if current_step >= len(execution_plan):
            # 所有步骤已完成
            return {
                "is_completed": True,
                "is_success": True,
                "messages": [AIMessage(content="所有操作步骤已完成")]
            }
        
        # 获取当前步骤信息
        current_step_info = execution_plan[current_step]
        action_type = current_step_info.get('action_type')
        parameters = current_step_info.get('parameters', {})
        
        # 初始化服务
        settings = Settings()
        action_service = ActionService(settings)
        action_service.start()  # 启动服务
        
        # 执行操作
        execution_result = _execute_action(
            action_service=action_service,
            action_type=action_type,
            parameters=parameters,
            target_elements=target_elements,
            step_info=current_step_info
        )
        
        # 更新执行结果
        execution_results = state.get('execution_results', [])
        execution_results.append(execution_result)
        
        # 准备返回的状态更新
        result_update = {
            "execution_results": execution_results,
            "current_step": current_step + 1,
            "messages": [AIMessage(content=f"已执行步骤 {current_step + 1}: {current_step_info.get('description')}")],
            "debug_info": {
                **state.get('debug_info', {}),
                f"step_{current_step}_result": execution_result,
                "execution_timestamp": _get_timestamp()
            }
        }
        
        # 检查是否需要重新分析屏幕
        if _should_reanalyze_screen(action_type, execution_result):
            result_update["need_reanalyze"] = True
        
        # 如果执行失败，设置错误信息
        if not execution_result['success']:
            result_update["error_message"] = execution_result.get('error_message', '操作执行失败')
        
        logger.info(f"步骤 {current_step + 1} 执行完成，成功: {execution_result['success']}")
        
        return result_update
        
    except Exception as e:
        logger.error(f"操作执行失败: {str(e)}")
        return {
            "error_message": f"操作执行失败: {str(e)}",
            "messages": [AIMessage(content=f"操作执行失败: {str(e)}")]
        }


def _execute_action(
    action_service: ActionService,
    action_type: str,
    parameters: Dict[str, Any],
    target_elements: list,
    step_info: Dict[str, Any]
) -> ExecutionResult:
    """执行具体操作
    
    Args:
        action_service: 操作服务实例
        action_type: 操作类型
        parameters: 操作参数
        target_elements: 目标元素列表
        step_info: 步骤信息
        
    Returns:
        执行结果
    """
    import time
    start_time = time.time()
    
    try:
        result_data = None
        success = False
        
        if action_type == 'click':
            success, result_data = _execute_click(action_service, target_elements, parameters)
        
        elif action_type == 'type':
            success, result_data = _execute_type(action_service, parameters)
        
        elif action_type == 'scroll':
            success, result_data = _execute_scroll(action_service, parameters)
        
        elif action_type == 'open_app':
            success, result_data = _execute_open_app(action_service, parameters)
        
        elif action_type == 'wait':
            success, result_data = _execute_wait(parameters)
        
        elif action_type == 'analyze':
            success, result_data = True, {"message": "屏幕分析完成"}
        
        else:
            raise ValueError(f"不支持的操作类型: {action_type}")
        
        execution_time = time.time() - start_time
        
        return ExecutionResult(
            step_id=step_info.get('step_id', 0),
            success=success,
            result_data=result_data,
            error_message=None if success else result_data.get('error', '操作失败'),
            execution_time=execution_time,
            screenshot_after=None  # 可以在这里添加执行后截图
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"执行操作 {action_type} 时发生错误: {str(e)}")
        
        return ExecutionResult(
            step_id=step_info.get('step_id', 0),
            success=False,
            result_data=None,
            error_message=str(e),
            execution_time=execution_time,
            screenshot_after=None
        )


def _execute_click(action_service: ActionService, target_elements: list, parameters: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """执行点击操作"""
    if not target_elements:
        return False, {"error": "没有找到可点击的目标元素"}
    
    # 选择置信度最高的元素
    target_element = target_elements[0]
    coordinates = target_element.get('coordinates', {})
    
    if not coordinates or not all(k in coordinates for k in ['x', 'y']):
        return False, {"error": "目标元素坐标信息不完整"}
    
    try:
        # 计算点击坐标（元素中心点）
        click_x = coordinates['x'] + coordinates.get('width', 0) // 2
        click_y = coordinates['y'] + coordinates.get('height', 0) // 2
        
        # 执行点击
        action_service.click(click_x, click_y)
        
        return True, {
            "action": "click",
            "coordinates": {"x": click_x, "y": click_y},
            "target_element": target_element
        }
        
    except Exception as e:
        return False, {"error": f"点击操作失败: {str(e)}"}


def _execute_type(action_service: ActionService, parameters: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """执行输入操作"""
    text = parameters.get('text', '')
    if not text:
        return False, {"error": "没有指定要输入的文本"}
    
    try:
        action_service.type_text(text)
        return True, {"action": "type", "text": text}
    except Exception as e:
        return False, {"error": f"输入操作失败: {str(e)}"}


def _execute_scroll(action_service: ActionService, parameters: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """执行滚动操作"""
    direction = parameters.get('direction', 'down')
    amount = parameters.get('amount', 3)
    
    try:
        if direction == 'up':
            action_service.scroll_up(amount)
        elif direction == 'down':
            action_service.scroll_down(amount)
        elif direction == 'left':
            action_service.scroll_left(amount)
        elif direction == 'right':
            action_service.scroll_right(amount)
        else:
            return False, {"error": f"不支持的滚动方向: {direction}"}
        
        return True, {"action": "scroll", "direction": direction, "amount": amount}
    except Exception as e:
        return False, {"error": f"滚动操作失败: {str(e)}"}


def _execute_open_app(action_service: ActionService, parameters: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """执行打开应用操作"""
    app_name = parameters.get('app_name', '')
    if not app_name:
        return False, {"error": "没有指定要打开的应用程序名称"}
    
    try:
        success = action_service.open_application(app_name)
        if success:
            return True, {"action": "open_app", "app_name": app_name}
        else:
            return False, {"error": f"无法打开应用程序: {app_name}"}
    except Exception as e:
        return False, {"error": f"打开应用失败: {str(e)}"}


def _execute_wait(parameters: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """执行等待操作"""
    import time
    
    duration = parameters.get('duration', 1.0)
    try:
        time.sleep(duration)
        return True, {"action": "wait", "duration": duration}
    except Exception as e:
        return False, {"error": f"等待操作失败: {str(e)}"}


def _should_reanalyze_screen(action_type: str, execution_result: ExecutionResult) -> bool:
    """判断是否需要重新分析屏幕
    
    某些操作（如点击、打开应用）可能会改变屏幕内容，需要重新分析
    """
    if not execution_result['success']:
        return False
    
    # 这些操作类型通常会改变屏幕内容
    screen_changing_actions = ['click', 'open_app', 'scroll']
    return action_type in screen_changing_actions


def _get_timestamp() -> str:
    """获取当前时间戳"""
    import time
    return str(time.time())