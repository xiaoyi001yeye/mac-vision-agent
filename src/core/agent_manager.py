#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体管理器
基于CrewAI框架的多智能体协作管理
"""

import time
from typing import Dict, List, Optional, Any, Union
from crewai import Agent, Task, Crew
from crewai.process import Process
from crewai.tools import BaseTool

from ..utils.logger import LoggerMixin, log_execution_time
from ..config.settings import Settings
from ..services.screen_service import ScreenService
from ..services.vlm_service import VLMService
from ..services.action_service import ActionService
from ..tools.screen_tools import ScreenCaptureTools
from ..tools.vlm_tools import VLMAnalysisTools
from ..tools.action_tools import ActionExecutionTools

class AgentManager(LoggerMixin):
    """智能体管理器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.is_running = False
        
        # 初始化服务
        self.screen_service = ScreenService(settings)
        self.vlm_service = VLMService(settings)
        self.action_service = ActionService(settings)
        
        # 初始化工具
        self.screen_tools = ScreenCaptureTools(self.screen_service)
        self.vlm_tools = VLMAnalysisTools(self.vlm_service)
        self.action_tools = ActionExecutionTools(self.action_service)
        
        # 智能体和任务
        self.agents = {}
        self.tasks = {}
        self.crew = None
        
        self.logger.info("智能体管理器初始化完成")
    
    def _create_agents(self):
        """创建智能体"""
        self.logger.info("创建智能体...")
        
        # 屏幕理解智能体
        self.agents['screen_analyst'] = Agent(
            role='屏幕理解专家',
            goal='理解当前屏幕内容并识别可操作元素',
            backstory=(
                '你是一个专门分析macOS界面的视觉智能体。'
                '你能够准确识别屏幕上的各种UI元素，包括按钮、文本框、菜单等，'
                '并能理解它们的功能和位置关系。'
            ),
            tools=[
                self.screen_tools.capture_screen,
                self.vlm_tools.analyze_screen,
                self.vlm_tools.identify_elements
            ],
            memory=self.settings.crewai.memory_enabled,
            verbose=self.settings.crewai.verbose,
            max_iter=self.settings.crewai.max_iter
        )
        
        # 操作执行智能体
        self.agents['action_executor'] = Agent(
            role='操作执行专家',
            goal='根据分析结果执行精确的GUI操作',
            backstory=(
                '你是一个专门执行macOS GUI操作的智能体。'
                '你能够根据屏幕分析结果，安全、准确地执行各种操作，'
                '包括点击、输入、拖拽等，并能验证操作结果。'
            ),
            tools=[
                self.action_tools.click_element,
                self.action_tools.type_text,
                self.action_tools.drag_element,
                self.action_tools.validate_action,
                self.action_tools.open_application,
                self.action_tools.open_calculator
            ],
            memory=self.settings.crewai.memory_enabled,
            verbose=self.settings.crewai.verbose,
            max_iter=self.settings.crewai.max_iter
        )
        
        # 任务协调智能体
        self.agents['task_coordinator'] = Agent(
            role='任务协调专家',
            goal='协调多个智能体完成复杂任务',
            backstory=(
                '你是一个任务协调专家，负责将复杂的用户指令分解为'
                '可执行的子任务，并协调其他智能体按正确顺序执行。'
            ),
            tools=[],
            memory=self.settings.crewai.memory_enabled,
            verbose=self.settings.crewai.verbose,
            max_iter=self.settings.crewai.max_iter
        )
        
        self.logger.info(f"创建了 {len(self.agents)} 个智能体")
    
    def _create_tasks(self, user_command: str):
        """创建任务"""
        self.logger.info(f"为命令创建任务: {user_command}")
        
        # 任务分析
        self.tasks['analyze_task'] = Task(
            description=f"""
            分析用户命令: "{user_command}"
            
            你需要:
            1. 理解用户的意图和目标
            2. 确定需要执行的操作类型
            3. 识别可能的风险和注意事项
            4. 制定执行计划
            
            输出格式:
            - 任务类型: [点击/输入/拖拽/复合操作]
            - 目标描述: [具体要做什么]
            - 执行步骤: [详细的步骤列表]
            - 风险评估: [可能的风险和预防措施]
            """,
            agent=self.agents['task_coordinator'],
            expected_output='任务分析报告，包含执行计划和风险评估'
        )
        
        # 屏幕分析
        self.tasks['analyze_screen'] = Task(
            description="""
            捕获并分析当前屏幕内容
            
            你需要:
            1. 捕获当前屏幕截图
            2. 使用VLM分析屏幕内容
            3. 识别所有可操作的UI元素
            4. 确定目标元素的位置和属性
            
            输出格式:
            - 屏幕描述: [当前屏幕的整体描述]
            - 元素列表: [所有识别到的UI元素]
            - 目标元素: [与任务相关的关键元素]
            - 坐标信息: [目标元素的精确位置]
            """,
            agent=self.agents['screen_analyst'],
            expected_output='屏幕分析报告，包含元素识别和位置信息'
        )
        
        # 操作执行
        self.tasks['execute_action'] = Task(
            description="""
            根据屏幕分析结果执行操作
            
            你需要:
            1. 根据分析结果确定具体操作
            2. 验证操作的安全性
            3. 执行操作
            4. 验证操作结果
            
            输出格式:
            - 执行操作: [具体执行的操作]
            - 操作参数: [操作的详细参数]
            - 执行结果: [操作是否成功]
            - 后续建议: [下一步建议]
            """,
            agent=self.agents['action_executor'],
            expected_output='操作执行报告，包含执行结果和状态'
        )
        
        self.logger.info(f"创建了 {len(self.tasks)} 个任务")
    
    def _create_crew(self):
        """创建智能体团队"""
        self.logger.info("创建智能体团队...")
        
        task_list = [
            self.tasks['analyze_task'],
            self.tasks['analyze_screen'],
            self.tasks['execute_action']
        ]
        
        self.crew = Crew(
            agents=list(self.agents.values()),
            tasks=task_list,
            process=Process.sequential,
            memory=self.settings.crewai.memory_enabled,
            verbose=self.settings.crewai.verbose,
            max_execution_time=self.settings.crewai.max_execution_time
        )
        
        self.logger.info("智能体团队创建完成")
    
    @log_execution_time("agent_manager_start")
    def start(self):
        """启动智能体管理器"""
        if self.is_running:
            self.logger.warning("智能体管理器已在运行")
            return
        
        try:
            self.logger.info("启动智能体管理器...")
            
            # 启动服务
            self.screen_service.start()
            self.vlm_service.start()
            self.action_service.start()
            
            # 创建智能体
            self._create_agents()
            
            self.is_running = True
            self.logger.info("智能体管理器启动成功")
            
        except Exception as e:
            self.logger.error(f"启动智能体管理器失败: {e}")
            raise
    
    @log_execution_time("process_command")
    def process_command(self, command: str) -> Dict[str, Any]:
        """处理用户命令"""
        if not self.is_running:
            raise RuntimeError("智能体管理器未启动")
        
        try:
            self.logger.info(f"处理命令: {command}")
            start_time = time.time()
            
            # 创建任务
            self._create_tasks(command)
            
            # 创建团队
            self._create_crew()
            
            # 执行任务
            result = self.crew.kickoff()
            
            duration = time.time() - start_time
            self.log_performance("command_execution", duration, command=command)
            
            self.logger.info(f"命令执行完成，耗时: {duration:.2f}秒")
            
            return {
                'success': True,
                'result': str(result),
                'duration': duration,
                'command': command
            }
            
        except Exception as e:
            self.logger.error(f"处理命令失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def stop(self):
        """停止智能体管理器"""
        if not self.is_running:
            return
        
        try:
            self.logger.info("停止智能体管理器...")
            
            # 停止服务
            if hasattr(self, 'action_service'):
                self.action_service.stop()
            if hasattr(self, 'vlm_service'):
                self.vlm_service.stop()
            if hasattr(self, 'screen_service'):
                self.screen_service.stop()
            
            self.is_running = False
            self.logger.info("智能体管理器已停止")
            
        except Exception as e:
            self.logger.error(f"停止智能体管理器时出错: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            'is_running': self.is_running,
            'agents_count': len(self.agents),
            'tasks_count': len(self.tasks),
            'services': {
                'screen_service': self.screen_service.is_running if hasattr(self, 'screen_service') else False,
                'vlm_service': self.vlm_service.is_running if hasattr(self, 'vlm_service') else False,
                'action_service': self.action_service.is_running if hasattr(self, 'action_service') else False
            }
        }