# -*- coding: utf-8 -*-
"""
操作执行工具集合
为CrewAI智能体提供GUI自动化操作功能的工具集合
"""

from typing import List
from crewai_tools import BaseTool

from ..services.action_service import ActionService
from ..utils.logger import LoggerMixin
from .action_tool import (
    ActionClickTool,
    ActionTypeTool,
    ActionDragTool,
    ActionKeypressTool,
    ActionStatusTool,
    ActionValidationTool,
    OpenApplicationTool,
    OpenCalculatorTool
)

class ActionExecutionTools(LoggerMixin):
    """操作执行工具集合"""
    
    def __init__(self, action_service: ActionService):
        self.action_service = action_service
        
        # 初始化所有工具
        self.click_element = ActionClickTool(action_service)
        self.type_text = ActionTypeTool(action_service)
        self.drag_element = ActionDragTool(action_service)
        self.keypress = ActionKeypressTool(action_service)
        self.get_status = ActionStatusTool(action_service)
        self.validate_action = ActionValidationTool(action_service)
        self.open_application = OpenApplicationTool(action_service)
        self.open_calculator = OpenCalculatorTool(action_service)
        
        self.logger.info("操作执行工具集合初始化完成")
    
    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具列表"""
        return [
            self.click_element,
            self.type_text,
            self.drag_element,
            self.keypress,
            self.get_status,
            self.validate_action,
            self.open_application,
            self.open_calculator
        ]
    
    def get_basic_tools(self) -> List[BaseTool]:
        """获取基础操作工具"""
        return [
            self.click_element,
            self.type_text,
            self.drag_element,
            self.keypress
        ]
    
    def get_application_tools(self) -> List[BaseTool]:
        """获取应用程序操作工具"""
        return [
            self.open_application,
            self.open_calculator
        ]
    
    def get_utility_tools(self) -> List[BaseTool]:
        """获取实用工具"""
        return [
            self.get_status,
            self.validate_action
        ]