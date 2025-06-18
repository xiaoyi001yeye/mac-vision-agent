#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕工具模块
为CrewAI智能体提供屏幕捕获功能
"""

import json
from typing import Dict, Any, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

from ..services.screen_service import ScreenService
from ..utils.logger import LoggerMixin

class ScreenCaptureInput(BaseModel):
    """屏幕捕获输入参数"""
    region: Optional[Dict[str, int]] = Field(
        default=None,
        description="捕获区域，格式: {'x': int, 'y': int, 'width': int, 'height': int}，None表示全屏"
    )
    save_path: Optional[str] = Field(
        default=None,
        description="保存路径，None表示不保存到文件"
    )
    format: str = Field(
        default="PNG",
        description="图像格式，支持PNG、JPEG等"
    )

class ScreenTool(BaseTool, LoggerMixin):
    """屏幕捕获工具"""
    
    name: str = "screen_capture"
    description: str = (
        "捕获屏幕截图的工具。可以捕获全屏或指定区域的截图。"
        "输入参数:"
        "- region: 可选，捕获区域 {'x': int, 'y': int, 'width': int, 'height': int}"
        "- save_path: 可选，保存路径"
        "- format: 图像格式，默认PNG"
        "返回: 包含截图信息的JSON字符串"
    )
    args_schema = ScreenCaptureInput
    
    def __init__(self, screen_service: ScreenService, **kwargs):
        super().__init__(**kwargs)
        self.screen_service = screen_service
    
    def _run(self, region: Optional[Dict[str, int]] = None, 
             save_path: Optional[str] = None, 
             format: str = "PNG") -> str:
        """执行屏幕捕获"""
        try:
            self.logger.info(f"执行屏幕捕获，区域: {region}")
            
            # 捕获屏幕
            image_data = self.screen_service.capture_screen(
                region=region,
                save_path=save_path,
                format=format
            )
            
            if image_data is None:
                return json.dumps({
                    "success": False,
                    "error": "屏幕捕获失败"
                })
            
            result = {
                "success": True,
                "image_path": image_data.get("image_path"),
                "image_size": image_data.get("image_size"),
                "capture_time": image_data.get("capture_time"),
                "region": region,
                "format": format
            }
            
            self.logger.info("屏幕捕获成功")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"屏幕捕获工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ScreenAnalysisInput(BaseModel):
    """屏幕分析输入参数"""
    image_path: str = Field(
        description="要分析的图像路径"
    )
    analysis_type: str = Field(
        default="general",
        description="分析类型: general(通用), ui_elements(UI元素), text(文本识别)"
    )

class ScreenAnalysisTool(BaseTool, LoggerMixin):
    """屏幕分析工具"""
    
    name: str = "screen_analysis"
    description: str = (
        "分析屏幕截图的工具。可以识别UI元素、提取文本等。"
        "输入参数:"
        "- image_path: 要分析的图像路径"
        "- analysis_type: 分析类型(general/ui_elements/text)"
        "返回: 包含分析结果的JSON字符串"
    )
    args_schema = ScreenAnalysisInput
    
    def __init__(self, screen_service: ScreenService, **kwargs):
        super().__init__(**kwargs)
        self.screen_service = screen_service
    
    def _run(self, image_path: str, analysis_type: str = "general") -> str:
        """执行屏幕分析"""
        try:
            self.logger.info(f"执行屏幕分析，图像: {image_path}, 类型: {analysis_type}")
            
            # 根据分析类型执行不同的分析
            if analysis_type == "ui_elements":
                result = self.screen_service.analyze_ui_elements(image_path)
            elif analysis_type == "text":
                result = self.screen_service.extract_text(image_path)
            else:  # general
                result = self.screen_service.analyze_screen(image_path)
            
            if result is None:
                return json.dumps({
                    "success": False,
                    "error": "屏幕分析失败"
                })
            
            analysis_result = {
                "success": True,
                "analysis_type": analysis_type,
                "image_path": image_path,
                "result": result
            }
            
            self.logger.info("屏幕分析成功")
            return json.dumps(analysis_result)
            
        except Exception as e:
            self.logger.error(f"屏幕分析工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ScreenInfoInput(BaseModel):
    """屏幕信息输入参数"""
    info_type: str = Field(
        default="size",
        description="信息类型: size(尺寸), resolution(分辨率), all(全部)"
    )

class ScreenInfoTool(BaseTool, LoggerMixin):
    """屏幕信息工具"""
    
    name: str = "screen_info"
    description: str = (
        "获取屏幕信息的工具。可以获取屏幕尺寸、分辨率等信息。"
        "输入参数:"
        "- info_type: 信息类型(size/resolution/all)"
        "返回: 包含屏幕信息的JSON字符串"
    )
    args_schema = ScreenInfoInput
    
    def __init__(self, screen_service: ScreenService, **kwargs):
        super().__init__(**kwargs)
        self.screen_service = screen_service
    
    def _run(self, info_type: str = "size") -> str:
        """获取屏幕信息"""
        try:
            self.logger.info(f"获取屏幕信息，类型: {info_type}")
            
            screen_info = self.screen_service.get_screen_info()
            
            if info_type == "size":
                result = {
                    "width": screen_info.get("width"),
                    "height": screen_info.get("height")
                }
            elif info_type == "resolution":
                result = {
                    "resolution": screen_info.get("resolution"),
                    "scale_factor": screen_info.get("scale_factor")
                }
            else:  # all
                result = screen_info
            
            info_result = {
                "success": True,
                "info_type": info_type,
                "screen_info": result
            }
            
            self.logger.info("获取屏幕信息成功")
            return json.dumps(info_result)
            
        except Exception as e:
            self.logger.error(f"屏幕信息工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })