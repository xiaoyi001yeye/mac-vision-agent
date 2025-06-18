"""屏幕相关节点

包括屏幕捕获和屏幕分析功能
"""

import logging
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage

from ..state import VisionAgentState, UIElement
from src.services.screen_service import ScreenService
from src.services.vlm_service import VLMService
from src.config.settings import Settings

logger = logging.getLogger(__name__)


def screen_capture_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """屏幕捕获节点
    
    捕获当前屏幕截图
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info("开始捕获屏幕截图")
    
    try:
        # 初始化服务
        settings = Settings()
        screen_service = ScreenService(settings)
        screen_service.start()  # 启动服务
        
        # 捕获屏幕截图
        screenshot_path = screen_service.capture_screen()
        
        logger.info(f"屏幕截图已保存: {screenshot_path}")
        
        return {
            "screenshot_path": screenshot_path,
            "messages": [AIMessage(content="已捕获屏幕截图")],
            "debug_info": {
                **state.get('debug_info', {}),
                "screenshot_timestamp": _get_timestamp(),
                "screenshot_path": screenshot_path
            }
        }
        
    except Exception as e:
        logger.error(f"屏幕捕获失败: {str(e)}")
        return {
            "error_message": f"屏幕捕获失败: {str(e)}",
            "messages": [AIMessage(content=f"屏幕捕获失败: {str(e)}")]
        }


def screen_analyzer_node(state: VisionAgentState, config: RunnableConfig) -> Dict[str, Any]:
    """屏幕分析节点
    
    分析屏幕截图，识别UI元素和目标元素
    
    Args:
        state: 当前状态
        config: 运行配置
        
    Returns:
        状态更新字典
    """
    logger.info("开始分析屏幕内容")
    
    try:
        screenshot_path = state.get('screenshot_path')
        if not screenshot_path:
            raise ValueError("没有可用的屏幕截图")
        
        # 初始化服务
        settings = Settings()
        vlm_service = VLMService(settings)
        vlm_service.start()  # 启动VLM服务
        
        # 构建分析提示
        analysis_prompt = _build_screen_analysis_prompt(state)
        
        # 分析屏幕内容
        analysis_result = vlm_service.analyze_image(
            image_path=screenshot_path,
            prompt=analysis_prompt
        )
        
        # 解析分析结果
        screen_analysis = _parse_screen_analysis(analysis_result)
        ui_elements = _extract_ui_elements(screen_analysis)
        target_elements = _identify_target_elements(ui_elements, state)
        
        logger.info(f"屏幕分析完成，识别到 {len(ui_elements)} 个UI元素")
        
        return {
            "screen_analysis": screen_analysis,
            "ui_elements": ui_elements,
            "target_elements": target_elements,
            "messages": [AIMessage(content=f"已分析屏幕，识别到 {len(ui_elements)} 个UI元素")],
            "debug_info": {
                **state.get('debug_info', {}),
                "screen_analysis_timestamp": _get_timestamp(),
                "analysis_result": analysis_result
            }
        }
        
    except Exception as e:
        logger.error(f"屏幕分析失败: {str(e)}")
        return {
            "error_message": f"屏幕分析失败: {str(e)}",
            "messages": [AIMessage(content=f"屏幕分析失败: {str(e)}")]
        }


def _build_screen_analysis_prompt(state: VisionAgentState) -> str:
    """构建屏幕分析提示词"""
    task_type = state.get('task_type', 'analyze')
    task_intent = state.get('task_intent', '')
    execution_plan = state.get('execution_plan', [])
    
    current_step = state.get('current_step', 0)
    current_step_info = ""
    if execution_plan and current_step < len(execution_plan):
        step = execution_plan[current_step]
        current_step_info = f"""
当前执行步骤: {step.get('description', '')}
目标元素: {step.get('target', {}).get('description', '')}
"""
    
    return f"""
请分析这个macOS屏幕截图，并提供详细的UI元素信息。

任务上下文:
- 任务类型: {task_type}
- 任务意图: {task_intent}
{current_step_info}

请识别并返回以下信息（JSON格式）：
{{
    "screen_description": "屏幕整体描述",
    "active_application": "当前活跃的应用程序",
    "ui_elements": [
        {{
            "element_id": "唯一标识符",
            "element_type": "元素类型(button/input/text/image/menu/window等)",
            "coordinates": {{"x": 0, "y": 0, "width": 0, "height": 0}},
            "text": "元素文本内容",
            "attributes": {{"placeholder": "", "enabled": true, "visible": true}},
            "confidence": 0.95,
            "accessibility_info": {{"role": "", "label": ""}}
        }}
    ],
    "layout_info": {{
        "windows": ["窗口信息"],
        "menus": ["菜单信息"],
        "dialogs": ["对话框信息"]
    }}
}}

注意事项:
1. 坐标使用屏幕绝对坐标
2. 重点识别可交互元素（按钮、输入框、链接等）
3. 如果是特定任务，重点标注相关的目标元素
4. 置信度范围0-1，表示识别的准确性
5. 考虑macOS的UI设计特点
"""


def _parse_screen_analysis(analysis_result: str) -> Dict[str, Any]:
    """解析屏幕分析结果"""
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
                "screen_description": analysis_result,
                "active_application": "Unknown",
                "ui_elements": [],
                "layout_info": {"windows": [], "menus": [], "dialogs": []}
            }
    except json.JSONDecodeError:
        logger.warning("无法解析屏幕分析JSON，使用默认结构")
        result = {
            "screen_description": analysis_result,
            "active_application": "Unknown",
            "ui_elements": [],
            "layout_info": {"windows": [], "menus": [], "dialogs": []}
        }
    
    return result


def _extract_ui_elements(screen_analysis: Dict[str, Any]) -> List[UIElement]:
    """从屏幕分析结果中提取UI元素"""
    ui_elements = []
    
    raw_elements = screen_analysis.get('ui_elements', [])
    for i, element in enumerate(raw_elements):
        try:
            ui_element = UIElement(
                element_id=element.get('element_id', f"element_{i}"),
                element_type=element.get('element_type', 'unknown'),
                coordinates=element.get('coordinates', {'x': 0, 'y': 0, 'width': 0, 'height': 0}),
                text=element.get('text'),
                attributes=element.get('attributes'),
                confidence=float(element.get('confidence', 0.5)),
                accessibility_info=element.get('accessibility_info')
            )
            ui_elements.append(ui_element)
        except Exception as e:
            logger.warning(f"解析UI元素失败: {e}")
            continue
    
    return ui_elements


def _identify_target_elements(ui_elements: List[UIElement], state: VisionAgentState) -> List[UIElement]:
    """识别目标操作元素"""
    target_elements = []
    
    task_type = state.get('task_type')
    execution_plan = state.get('execution_plan', [])
    current_step = state.get('current_step', 0)
    
    if not execution_plan or current_step >= len(execution_plan):
        return target_elements
    
    current_step_info = execution_plan[current_step]
    target_description = current_step_info.get('target', {}).get('description', '')
    action_type = current_step_info.get('action_type')
    
    # 根据任务类型和目标描述筛选元素
    for element in ui_elements:
        is_target = False
        
        # 基于元素类型的匹配
        if action_type == 'click' and element['element_type'] in ['button', 'link', 'menu_item']:
            is_target = True
        elif action_type == 'type' and element['element_type'] in ['input', 'textarea', 'textfield']:
            is_target = True
        
        # 基于文本内容的匹配
        if target_description and element.get('text'):
            if target_description.lower() in element['text'].lower():
                is_target = True
        
        # 基于置信度的过滤
        if is_target and element['confidence'] > 0.7:
            target_elements.append(element)
    
    # 按置信度排序
    target_elements.sort(key=lambda x: x['confidence'], reverse=True)
    
    return target_elements


def _get_timestamp() -> str:
    """获取当前时间戳"""
    import time
    return str(time.time())