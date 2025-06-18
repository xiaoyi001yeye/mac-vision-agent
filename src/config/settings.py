#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
管理系统的各种配置参数
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MLXConfig(BaseModel):
    """MLX-VLM配置"""
    model_name: str = Field(default="qwen2-vl-2b", description="VLM模型名称")
    max_tokens: int = Field(default=1000, description="最大生成token数")
    temperature: float = Field(default=0.1, description="生成温度")
    cache_dir: str = Field(default="data/models", description="模型缓存目录")
    device: str = Field(default="auto", description="设备类型")

class HammerspoonConfig(BaseModel):
    """Hammerspoon配置"""
    script_path: str = Field(default="hammerspoon/automation.lua", description="Lua脚本路径")
    screenshot_dir: str = Field(default="data/screenshots", description="截图保存目录")
    click_delay: float = Field(default=0.1, description="点击延迟(秒)")
    safety_margin: int = Field(default=10, description="安全边距(像素)")

class CrewAIConfig(BaseModel):
    """CrewAI配置"""
    memory_enabled: bool = Field(default=True, description="是否启用记忆")
    max_execution_time: int = Field(default=300, description="最大执行时间(秒)")
    verbose: bool = Field(default=True, description="是否详细输出")
    max_iter: int = Field(default=5, description="最大迭代次数")

class ScreenCaptureConfig(BaseModel):
    """屏幕捕获配置"""
    method: str = Field(default="hammerspoon", description="捕获方法: hammerspoon/pyautogui")
    quality: int = Field(default=95, description="图像质量(1-100)")
    max_width: int = Field(default=1920, description="最大宽度")
    max_height: int = Field(default=1080, description="最大高度")
    format: str = Field(default="PNG", description="图像格式")

class SafetyConfig(BaseModel):
    """安全配置"""
    enable_validation: bool = Field(default=True, description="是否启用操作验证")
    confirm_destructive: bool = Field(default=True, description="是否确认破坏性操作")
    max_click_distance: int = Field(default=50, description="最大点击距离(像素)")
    forbidden_areas: list = Field(default_factory=list, description="禁止操作区域")

class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    max_file_size: int = Field(default=10*1024*1024, description="最大文件大小(字节)")
    backup_count: int = Field(default=5, description="备份文件数量")
    performance_logging: bool = Field(default=True, description="是否启用性能日志")

class Settings(BaseModel):
    """主配置类"""
    
    # 基础配置
    app_name: str = Field(default="macOS视觉智能体", description="应用名称")
    version: str = Field(default="1.0.0", description="版本号")
    debug: bool = Field(default=False, description="调试模式")
    
    # 各模块配置
    mlx: MLXConfig = Field(default_factory=MLXConfig)
    hammerspoon: HammerspoonConfig = Field(default_factory=HammerspoonConfig)
    crewai: CrewAIConfig = Field(default_factory=CrewAIConfig)
    screen_capture: ScreenCaptureConfig = Field(default_factory=ScreenCaptureConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # 环境变量配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API密钥")
    
    def __init__(self, **kwargs):
        # 从环境变量加载配置
        env_config = self._load_from_env()
        
        # 合并配置
        merged_config = {**env_config, **kwargs}
        
        super().__init__(**merged_config)
        
        # 创建必要的目录
        self._create_directories()
    
    def _load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {}
        
        # 基础配置
        if os.getenv("DEBUG"):
            config["debug"] = os.getenv("DEBUG").lower() == "true"
        
        # API密钥
        if os.getenv("OPENAI_API_KEY"):
            config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("ANTHROPIC_API_KEY"):
            config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY")
        
        # MLX配置
        mlx_config = {}
        if os.getenv("MLX_MODEL_NAME"):
            mlx_config["model_name"] = os.getenv("MLX_MODEL_NAME")
        if os.getenv("MLX_MAX_TOKENS"):
            mlx_config["max_tokens"] = int(os.getenv("MLX_MAX_TOKENS"))
        if os.getenv("MLX_TEMPERATURE"):
            mlx_config["temperature"] = float(os.getenv("MLX_TEMPERATURE"))
        
        if mlx_config:
            config["mlx"] = mlx_config
        
        return config
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            "data/models",  # self.mlx.cache_dir
            "data/screenshots",  # self.hammerspoon.screenshot_dir
            "logs",
            "data/cache",
            "hammerspoon"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            "name": self.mlx.model_name,
            "max_tokens": self.mlx.max_tokens,
            "temperature": self.mlx.temperature,
            "cache_dir": self.mlx.cache_dir
        }
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug or os.getenv("ENVIRONMENT", "production") == "development"
    
    def get_screenshot_path(self, filename: str = None) -> str:
        """获取截图文件路径"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        return str(Path(self.hammerspoon.screenshot_dir) / filename)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump()
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        import json
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Settings':
        """从文件加载配置"""
        import json
        
        with open(filepath, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return cls(**config_data)

# 全局配置实例
_settings = None

def get_settings() -> Settings:
    """获取全局配置实例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def reload_settings() -> Settings:
    """重新加载配置"""
    global _settings
    _settings = Settings()
    return _settings