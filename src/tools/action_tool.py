#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作工具模块
为CrewAI智能体提供GUI自动化操作功能
"""

import json
from typing import Dict, Any, Optional, List
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

from ..services.action_service import ActionService
from ..utils.logger import LoggerMixin

class ClickInput(BaseModel):
    """点击操作输入参数"""
    x: int = Field(
        description="点击的X坐标"
    )
    y: int = Field(
        description="点击的Y坐标"
    )
    button: str = Field(
        default="left",
        description="鼠标按钮类型: left, right, middle"
    )
    double_click: bool = Field(
        default=False,
        description="是否双击"
    )

class ActionClickTool(BaseTool, LoggerMixin):
    """点击操作工具"""
    
    name: str = "click_at_position"
    description: str = (
        "在指定位置执行鼠标点击操作的工具。"
        "输入参数:"
        "- x: 点击的X坐标"
        "- y: 点击的Y坐标"
        "- button: 鼠标按钮类型(left/right/middle，默认left)"
        "- double_click: 是否双击(默认False)"
        "返回: 包含操作结果的JSON字符串"
    )
    args_schema = ClickInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, x: int, y: int, button: str = "left", double_click: bool = False) -> str:
        """执行点击操作"""
        try:
            self.logger.info(f"执行点击操作: ({x}, {y}), 按钮: {button}, 双击: {double_click}")
            
            # 验证操作安全性
            validation = self.action_service.validate_action(
                "click", 
                {"x": x, "y": y, "button": button}
            )
            
            if not validation["valid"]:
                return json.dumps({
                    "success": False,
                    "error": "操作验证失败",
                    "validation_errors": validation["errors"]
                })
            
            # 执行点击操作
            success = self.action_service.click_at(x, y, button, double_click)
            
            result = {
                "success": success,
                "action": "click",
                "coordinates": {"x": x, "y": y},
                "button": button,
                "double_click": double_click,
                "validation_warnings": validation.get("warnings", [])
            }
            
            if success:
                self.logger.info("点击操作成功")
            else:
                self.logger.error("点击操作失败")
                result["error"] = "点击操作执行失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"点击工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class TypeTextInput(BaseModel):
    """文本输入参数"""
    text: str = Field(
        description="要输入的文本内容"
    )
    interval: float = Field(
        default=0.01,
        description="字符间输入间隔(秒)"
    )

class ActionTypeTextTool(BaseTool, LoggerMixin):
    """文本输入工具"""
    
    name: str = "type_text"
    description: str = (
        "输入文本的工具。可以在当前焦点位置输入指定文本。"
        "输入参数:"
        "- text: 要输入的文本内容"
        "- interval: 字符间输入间隔(默认0.01秒)"
        "返回: 包含操作结果的JSON字符串"
    )
    args_schema = TypeTextInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, text: str, interval: float = 0.01) -> str:
        """执行文本输入"""
        try:
            self.logger.info(f"执行文本输入，长度: {len(text)}")
            
            # 验证操作安全性
            validation = self.action_service.validate_action(
                "type", 
                {"text": text}
            )
            
            if not validation["valid"]:
                return json.dumps({
                    "success": False,
                    "error": "操作验证失败",
                    "validation_errors": validation["errors"]
                })
            
            # 执行文本输入
            success = self.action_service.type_text(text, interval)
            
            result = {
                "success": success,
                "action": "type_text",
                "text_length": len(text),
                "interval": interval,
                "validation_warnings": validation.get("warnings", [])
            }
            
            if success:
                self.logger.info("文本输入成功")
            else:
                self.logger.error("文本输入失败")
                result["error"] = "文本输入执行失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"文本输入工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class DragInput(BaseModel):
    """拖拽操作输入参数"""
    from_x: int = Field(
        description="拖拽起始X坐标"
    )
    from_y: int = Field(
        description="拖拽起始Y坐标"
    )
    to_x: int = Field(
        description="拖拽目标X坐标"
    )
    to_y: int = Field(
        description="拖拽目标Y坐标"
    )
    duration: float = Field(
        default=1.0,
        description="拖拽持续时间(秒)"
    )

class ActionDragTool(BaseTool, LoggerMixin):
    """拖拽操作工具"""
    
    name: str = "drag_from_to"
    description: str = (
        "执行拖拽操作的工具。从一个位置拖拽到另一个位置。"
        "输入参数:"
        "- from_x: 拖拽起始X坐标"
        "- from_y: 拖拽起始Y坐标"
        "- to_x: 拖拽目标X坐标"
        "- to_y: 拖拽目标Y坐标"
        "- duration: 拖拽持续时间(默认1.0秒)"
        "返回: 包含操作结果的JSON字符串"
    )
    args_schema = DragInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 1.0) -> str:
        """执行拖拽操作"""
        try:
            self.logger.info(f"执行拖拽操作: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            
            # 验证操作安全性
            validation = self.action_service.validate_action(
                "drag", 
                {
                    "from_x": from_x, "from_y": from_y,
                    "to_x": to_x, "to_y": to_y,
                    "duration": duration
                }
            )
            
            if not validation["valid"]:
                return json.dumps({
                    "success": False,
                    "error": "操作验证失败",
                    "validation_errors": validation["errors"]
                })
            
            # 执行拖拽操作
            success = self.action_service.drag(from_x, from_y, to_x, to_y, duration)
            
            result = {
                "success": success,
                "action": "drag",
                "from_coordinates": {"x": from_x, "y": from_y},
                "to_coordinates": {"x": to_x, "y": to_y},
                "duration": duration,
                "validation_warnings": validation.get("warnings", [])
            }
            
            if success:
                self.logger.info("拖拽操作成功")
            else:
                self.logger.error("拖拽操作失败")
                result["error"] = "拖拽操作执行失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"拖拽工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class KeyPressInput(BaseModel):
    """按键操作输入参数"""
    key: str = Field(
        description="要按下的键，如'enter', 'space', 'tab'等"
    )
    modifiers: List[str] = Field(
        default=[],
        description="修饰键列表，如['cmd', 'shift']等"
    )

class ActionKeyPressTool(BaseTool, LoggerMixin):
    """按键操作工具"""
    
    name: str = "press_key"
    description: str = (
        "执行按键操作的工具。可以按下单个键或组合键。"
        "输入参数:"
        "- key: 要按下的键名"
        "- modifiers: 修饰键列表(如['cmd', 'shift'])"
        "返回: 包含操作结果的JSON字符串"
    )
    args_schema = KeyPressInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, key: str, modifiers: List[str] = None) -> str:
        """执行按键操作"""
        try:
            if modifiers is None:
                modifiers = []
            
            self.logger.info(f"执行按键操作: {'+'.join(modifiers + [key])}")
            
            # 执行按键操作
            success = self.action_service.key_press(key, modifiers)
            
            result = {
                "success": success,
                "action": "key_press",
                "key": key,
                "modifiers": modifiers,
                "key_combination": "+".join(modifiers + [key])
            }
            
            if success:
                self.logger.info("按键操作成功")
            else:
                self.logger.error("按键操作失败")
                result["error"] = "按键操作执行失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"按键工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ActionHistoryInput(BaseModel):
    """操作历史输入参数"""
    limit: int = Field(
        default=10,
        description="返回的历史记录数量限制"
    )

class ActionHistoryTool(BaseTool, LoggerMixin):
    """操作历史工具"""
    
    name: str = "get_action_history"
    description: str = (
        "获取操作历史记录的工具。可以查看最近执行的操作。"
        "输入参数:"
        "- limit: 返回的历史记录数量(默认10)"
        "返回: 包含操作历史的JSON字符串"
    )
    args_schema = ActionHistoryInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, limit: int = 10) -> str:
        """获取操作历史"""
        try:
            self.logger.info(f"获取操作历史，限制: {limit}")
            
            # 获取操作历史
            history = self.action_service.get_action_history(limit)
            
            result = {
                "success": True,
                "history_count": len(history),
                "limit": limit,
                "history": history
            }
            
            self.logger.info(f"获取操作历史成功，返回{len(history)}条记录")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"操作历史工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ActionStatusInput(BaseModel):
    """操作状态输入参数"""
    include_details: bool = Field(
        default=False,
        description="是否包含详细信息"
    )

class ActionStatusTool(BaseTool, LoggerMixin):
    """操作状态工具"""
    
    name: str = "action_service_status"
    description: str = (
        "获取操作服务状态的工具。可以查看服务是否正常运行。"
        "输入参数:"
        "- include_details: 是否包含详细信息(默认False)"
        "返回: 包含服务状态的JSON字符串"
    )
    args_schema = ActionStatusInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, include_details: bool = False) -> str:
        """获取操作服务状态"""
        try:
            self.logger.info("获取操作服务状态")
            
            # 获取服务状态
            status = self.action_service.get_status()
            
            result = {
                "success": True,
                "is_running": status.get("is_running", False),
                "hammerspoon_available": status.get("hammerspoon_available", False),
                "safety_enabled": status.get("safety_enabled", False)
            }
            
            if include_details:
                result.update({
                    "screen_size": status.get("screen_size"),
                    "action_history_count": status.get("action_history_count", 0)
                })
            
            self.logger.info("获取操作服务状态成功")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"操作状态工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ValidateActionInput(BaseModel):
    """操作验证输入参数"""
    action_type: str = Field(
        description="操作类型: click, type, drag, keypress"
    )
    params: Dict[str, Any] = Field(
        description="操作参数字典"
    )

class ActionValidationTool(BaseTool, LoggerMixin):
    """操作验证工具"""
    
    name: str = "validate_action"
    description: str = (
        "验证操作安全性的工具。在执行操作前检查其安全性。"
        "输入参数:"
        "- action_type: 操作类型(click/type/drag/keypress)"
        "- params: 操作参数字典"
        "返回: 包含验证结果的JSON字符串"
    )
    args_schema = ValidateActionInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, action_type: str, params: Dict[str, Any]) -> str:
        """验证操作安全性"""
        try:
            self.logger.info(f"验证操作安全性: {action_type}")
            
            # 执行操作验证
            validation_result = self.action_service.validate_action(action_type, params)
            
            result = {
                "success": True,
                "action_type": action_type,
                "params": params,
                "validation": validation_result
            }
            
            self.logger.info(f"操作验证完成，有效: {validation_result['valid']}")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"操作验证工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class OpenApplicationInput(BaseModel):
    """打开应用程序输入参数"""
    app_name: str = Field(
        description="要打开的应用程序名称，例如：Calculator, Safari, TextEdit"
    )

class OpenApplicationTool(BaseTool, LoggerMixin):
    """打开应用程序工具"""
    
    name: str = "open_application"
    description: str = (
        "打开指定应用程序的工具。"
        "输入参数:"
        "- app_name: 应用程序名称(如Calculator、Safari、TextEdit等)"
        "返回: 包含操作结果的JSON字符串"
    )
    args_schema = OpenApplicationInput
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self, app_name: str) -> str:
        """打开应用程序"""
        try:
            self.logger.info(f"打开应用程序: {app_name}")
            
            # 执行打开应用程序操作
            success = self.action_service.open_application(app_name)
            
            result = {
                "success": success,
                "action": "open_application",
                "app_name": app_name
            }
            
            if success:
                self.logger.info(f"应用程序 {app_name} 打开成功")
            else:
                self.logger.error(f"应用程序 {app_name} 打开失败")
                result["error"] = "应用程序打开失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"打开应用程序工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class OpenCalculatorTool(BaseTool, LoggerMixin):
    """打开计算器工具"""
    
    name: str = "open_calculator"
    description: str = (
        "快速打开macOS计算器应用程序的工具。"
        "无需输入参数，直接调用即可打开计算器。"
        "返回: 包含操作结果的JSON字符串"
    )
    
    def __init__(self, action_service: ActionService, **kwargs):
        super().__init__(**kwargs)
        self.action_service = action_service
    
    def _run(self) -> str:
        """打开计算器应用"""
        try:
            self.logger.info("打开计算器应用")
            
            # 执行打开计算器操作
            success = self.action_service.open_calculator()
            
            result = {
                "success": success,
                "action": "open_calculator",
                "app_name": "Calculator"
            }
            
            if success:
                self.logger.info("计算器应用打开成功")
            else:
                self.logger.error("计算器应用打开失败")
                result["error"] = "计算器应用打开失败"
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"打开计算器工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })