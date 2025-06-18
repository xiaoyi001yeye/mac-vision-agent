#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLM工具模块
为CrewAI智能体提供视觉语言模型推理功能
"""

import json
from typing import Dict, Any, Optional, List
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

from ..services.vlm_service import VLMService
from ..utils.logger import LoggerMixin

class ImageAnalysisInput(BaseModel):
    """图像分析输入参数"""
    image_path: str = Field(
        description="要分析的图像路径"
    )
    prompt: str = Field(
        description="分析提示词，描述你想要模型分析的内容"
    )
    max_tokens: int = Field(
        default=512,
        description="最大生成token数"
    )
    temperature: float = Field(
        default=0.7,
        description="生成温度，控制随机性"
    )

class VLMTool(BaseTool, LoggerMixin):
    """VLM图像分析工具"""
    
    name: str = "vlm_analyze_image"
    description: str = (
        "使用视觉语言模型分析图像的工具。可以理解图像内容并回答相关问题。"
        "输入参数:"
        "- image_path: 要分析的图像路径"
        "- prompt: 分析提示词，描述分析需求"
        "- max_tokens: 最大生成token数(默认512)"
        "- temperature: 生成温度(默认0.7)"
        "返回: 包含分析结果的JSON字符串"
    )
    args_schema = ImageAnalysisInput
    
    def __init__(self, vlm_service: VLMService, **kwargs):
        super().__init__(**kwargs)
        self.vlm_service = vlm_service
    
    def _run(self, image_path: str, prompt: str, 
             max_tokens: int = 512, temperature: float = 0.7) -> str:
        """执行图像分析"""
        try:
            self.logger.info(f"执行VLM图像分析，图像: {image_path}")
            
            # 调用VLM服务进行分析
            analysis_result = self.vlm_service.analyze_image(
                image_path=image_path,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if analysis_result is None:
                return json.dumps({
                    "success": False,
                    "error": "VLM图像分析失败"
                })
            
            result = {
                "success": True,
                "image_path": image_path,
                "prompt": prompt,
                "analysis": analysis_result.get("response"),
                "confidence": analysis_result.get("confidence", 0.0),
                "processing_time": analysis_result.get("processing_time", 0.0),
                "model_info": analysis_result.get("model_info")
            }
            
            self.logger.info("VLM图像分析成功")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"VLM图像分析工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class UIElementDetectionInput(BaseModel):
    """UI元素检测输入参数"""
    image_path: str = Field(
        description="要分析的图像路径"
    )
    element_types: List[str] = Field(
        default=["button", "text", "input", "menu"],
        description="要检测的UI元素类型列表"
    )
    confidence_threshold: float = Field(
        default=0.5,
        description="置信度阈值，低于此值的检测结果将被过滤"
    )

class UIElementDetectionTool(BaseTool, LoggerMixin):
    """UI元素检测工具"""
    
    name: str = "detect_ui_elements"
    description: str = (
        "检测图像中UI元素的工具。可以识别按钮、文本框、菜单等界面元素。"
        "输入参数:"
        "- image_path: 要分析的图像路径"
        "- element_types: 要检测的元素类型列表"
        "- confidence_threshold: 置信度阈值(默认0.5)"
        "返回: 包含检测结果的JSON字符串"
    )
    args_schema = UIElementDetectionInput
    
    def __init__(self, vlm_service: VLMService, **kwargs):
        super().__init__(**kwargs)
        self.vlm_service = vlm_service
    
    def _run(self, image_path: str, 
             element_types: List[str] = None,
             confidence_threshold: float = 0.5) -> str:
        """执行UI元素检测"""
        try:
            if element_types is None:
                element_types = ["button", "text", "input", "menu"]
            
            self.logger.info(f"执行UI元素检测，图像: {image_path}")
            
            # 调用VLM服务进行UI元素识别
            detection_result = self.vlm_service.identify_ui_elements(
                image_path=image_path,
                element_types=element_types,
                confidence_threshold=confidence_threshold
            )
            
            if detection_result is None:
                return json.dumps({
                    "success": False,
                    "error": "UI元素检测失败"
                })
            
            result = {
                "success": True,
                "image_path": image_path,
                "element_types": element_types,
                "confidence_threshold": confidence_threshold,
                "elements": detection_result.get("elements", []),
                "total_count": len(detection_result.get("elements", [])),
                "processing_time": detection_result.get("processing_time", 0.0)
            }
            
            self.logger.info(f"UI元素检测成功，发现{result['total_count']}个元素")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"UI元素检测工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ClickableElementInput(BaseModel):
    """可点击元素查找输入参数"""
    image_path: str = Field(
        description="要分析的图像路径"
    )
    target_description: str = Field(
        description="目标元素的描述，例如'登录按钮'、'搜索框'等"
    )
    search_region: Optional[Dict[str, int]] = Field(
        default=None,
        description="搜索区域，格式: {'x': int, 'y': int, 'width': int, 'height': int}"
    )

class ClickableElementTool(BaseTool, LoggerMixin):
    """可点击元素查找工具"""
    
    name: str = "find_clickable_element"
    description: str = (
        "查找图像中可点击元素的工具。根据描述找到对应的UI元素并返回其位置。"
        "输入参数:"
        "- image_path: 要分析的图像路径"
        "- target_description: 目标元素描述"
        "- search_region: 可选，搜索区域限制"
        "返回: 包含元素位置信息的JSON字符串"
    )
    args_schema = ClickableElementInput
    
    def __init__(self, vlm_service: VLMService, **kwargs):
        super().__init__(**kwargs)
        self.vlm_service = vlm_service
    
    def _run(self, image_path: str, target_description: str,
             search_region: Optional[Dict[str, int]] = None) -> str:
        """查找可点击元素"""
        try:
            self.logger.info(f"查找可点击元素: {target_description}")
            
            # 调用VLM服务查找可点击元素
            element_result = self.vlm_service.find_clickable_elements(
                image_path=image_path,
                target_description=target_description,
                search_region=search_region
            )
            
            if element_result is None:
                return json.dumps({
                    "success": False,
                    "error": "未找到可点击元素"
                })
            
            result = {
                "success": True,
                "image_path": image_path,
                "target_description": target_description,
                "search_region": search_region,
                "elements": element_result.get("elements", []),
                "best_match": element_result.get("best_match"),
                "confidence": element_result.get("confidence", 0.0),
                "processing_time": element_result.get("processing_time", 0.0)
            }
            
            if result["best_match"]:
                self.logger.info(f"找到最佳匹配元素，置信度: {result['confidence']}")
            else:
                self.logger.warning("未找到匹配的可点击元素")
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"可点击元素查找工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class TextExtractionInput(BaseModel):
    """文本提取输入参数"""
    image_path: str = Field(
        description="要分析的图像路径"
    )
    region: Optional[Dict[str, int]] = Field(
        default=None,
        description="提取区域，格式: {'x': int, 'y': int, 'width': int, 'height': int}"
    )
    language: str = Field(
        default="auto",
        description="文本语言，auto表示自动检测"
    )

class TextExtractionTool(BaseTool, LoggerMixin):
    """文本提取工具"""
    
    name: str = "extract_text"
    description: str = (
        "从图像中提取文本的工具。可以识别图像中的文字内容。"
        "输入参数:"
        "- image_path: 要分析的图像路径"
        "- region: 可选，提取区域限制"
        "- language: 文本语言(默认auto)"
        "返回: 包含提取文本的JSON字符串"
    )
    args_schema = TextExtractionInput
    
    def __init__(self, vlm_service: VLMService, **kwargs):
        super().__init__(**kwargs)
        self.vlm_service = vlm_service
    
    def _run(self, image_path: str, 
             region: Optional[Dict[str, int]] = None,
             language: str = "auto") -> str:
        """提取文本"""
        try:
            self.logger.info(f"提取图像文本，图像: {image_path}")
            
            # 构建文本提取提示词
            if region:
                prompt = f"请提取图像中指定区域({region})的所有文本内容，按照从上到下、从左到右的顺序排列。"
            else:
                prompt = "请提取图像中的所有文本内容，按照从上到下、从左到右的顺序排列。"
            
            # 调用VLM服务进行文本提取
            extraction_result = self.vlm_service.analyze_image(
                image_path=image_path,
                prompt=prompt,
                max_tokens=1024,
                temperature=0.1  # 低温度确保准确性
            )
            
            if extraction_result is None:
                return json.dumps({
                    "success": False,
                    "error": "文本提取失败"
                })
            
            result = {
                "success": True,
                "image_path": image_path,
                "region": region,
                "language": language,
                "extracted_text": extraction_result.get("response"),
                "confidence": extraction_result.get("confidence", 0.0),
                "processing_time": extraction_result.get("processing_time", 0.0)
            }
            
            self.logger.info("文本提取成功")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"文本提取工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class ModelStatusInput(BaseModel):
    """模型状态输入参数"""
    include_details: bool = Field(
        default=False,
        description="是否包含详细信息"
    )

class ModelStatusTool(BaseTool, LoggerMixin):
    """模型状态工具"""
    
    name: str = "vlm_model_status"
    description: str = (
        "获取VLM模型状态的工具。可以查看模型是否已加载、性能信息等。"
        "输入参数:"
        "- include_details: 是否包含详细信息(默认False)"
        "返回: 包含模型状态的JSON字符串"
    )
    args_schema = ModelStatusInput
    
    def __init__(self, vlm_service: VLMService, **kwargs):
        super().__init__(**kwargs)
        self.vlm_service = vlm_service
    
    def _run(self, include_details: bool = False) -> str:
        """获取模型状态"""
        try:
            self.logger.info("获取VLM模型状态")
            
            # 获取服务状态
            status = self.vlm_service.get_status()
            
            result = {
                "success": True,
                "model_loaded": status.get("model_loaded", False),
                "is_running": status.get("is_running", False),
                "model_name": status.get("model_name"),
                "simulation_mode": status.get("simulation_mode", False)
            }
            
            if include_details:
                result.update({
                    "memory_usage": status.get("memory_usage"),
                    "inference_count": status.get("inference_count", 0),
                    "average_inference_time": status.get("average_inference_time", 0.0),
                    "last_inference_time": status.get("last_inference_time")
                })
            
            self.logger.info("获取VLM模型状态成功")
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"模型状态工具执行失败: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })