#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
屏幕服务模块
提供屏幕捕获和图像处理功能
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, Union
from PIL import Image, ImageOps
import pyautogui
import cv2
import numpy as np

from ..utils.logger import LoggerMixin, log_execution_time
from ..config.settings import Settings

class ScreenService(LoggerMixin):
    """屏幕服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.is_running = False
        self.hammerspoon_available = False
        
        # 检查Hammerspoon可用性
        self._check_hammerspoon()
        
        # 配置PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        self.logger.info("屏幕服务初始化完成")
    
    def _check_hammerspoon(self):
        """检查Hammerspoon是否可用"""
        try:
            # 检查Hammerspoon是否安装
            result = subprocess.run(
                ['hs', '-c', 'print("test")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.hammerspoon_available = True
                self.logger.info("Hammerspoon可用")
            else:
                self.logger.warning("Hammerspoon不可用，将使用PyAutoGUI")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"检查Hammerspoon失败: {e}，将使用PyAutoGUI")
    
    def start(self):
        """启动屏幕服务"""
        if self.is_running:
            return
        
        try:
            self.logger.info("启动屏幕服务...")
            
            # 创建截图目录
            Path(self.settings.hammerspoon.screenshot_dir).mkdir(parents=True, exist_ok=True)
            
            # 如果使用Hammerspoon，确保Lua脚本存在
            if self.hammerspoon_available and self.settings.screen_capture.method == "hammerspoon":
                self._ensure_hammerspoon_script()
            
            self.is_running = True
            self.logger.info("屏幕服务启动成功")
            
        except Exception as e:
            self.logger.error(f"启动屏幕服务失败: {e}")
            raise
    
    def _ensure_hammerspoon_script(self):
        """确保Hammerspoon脚本存在"""
        script_path = Path(self.settings.hammerspoon.script_path)
        
        if not script_path.exists():
            self.logger.info("创建Hammerspoon脚本...")
            
            # 创建目录
            script_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建Lua脚本
            lua_script = '''
-- macOS视觉智能体 Hammerspoon自动化脚本

local automation = {}

-- 捕获屏幕
function automation.captureScreen(filename)
    local screen = hs.screen.mainScreen()
    if not screen then
        return nil, "无法获取主屏幕"
    end
    
    local image = screen:snapshot()
    if not image then
        return nil, "无法捕获屏幕"
    end
    
    local success = image:saveToFile(filename)
    if success then
        return filename, nil
    else
        return nil, "保存截图失败"
    end
end

-- 获取屏幕尺寸
function automation.getScreenSize()
    local screen = hs.screen.mainScreen()
    if not screen then
        return nil, "无法获取主屏幕"
    end
    
    local frame = screen:frame()
    return {
        width = frame.w,
        height = frame.h,
        x = frame.x,
        y = frame.y
    }, nil
end

-- 点击指定位置
function automation.clickAt(x, y)
    local screen = hs.screen.mainScreen()
    if not screen then
        return false, "无法获取主屏幕"
    end
    
    local frame = screen:frame()
    
    -- 验证坐标
    if x < 0 or x > frame.w or y < 0 or y > frame.h then
        return false, "坐标超出屏幕范围"
    end
    
    -- 执行点击
    hs.mouse.setAbsolutePosition({x = x, y = y})
    hs.timer.usleep(100000)  -- 等待100ms
    hs.mouse.leftClick({x = x, y = y})
    
    return true, nil
end

-- 输入文本
function automation.typeText(text)
    if not text or text == "" then
        return false, "文本为空"
    end
    
    hs.eventtap.keyStrokes(text)
    return true, nil
end

-- 拖拽操作
function automation.dragFromTo(fromX, fromY, toX, toY)
    local screen = hs.screen.mainScreen()
    if not screen then
        return false, "无法获取主屏幕"
    end
    
    local frame = screen:frame()
    
    -- 验证坐标
    if fromX < 0 or fromX > frame.w or fromY < 0 or fromY > frame.h or
       toX < 0 or toX > frame.w or toY < 0 or toY > frame.h then
        return false, "坐标超出屏幕范围"
    end
    
    -- 执行拖拽
    hs.mouse.setAbsolutePosition({x = fromX, y = fromY})
    hs.timer.usleep(100000)
    hs.mouse.leftClick({x = fromX, y = fromY})
    hs.timer.usleep(100000)
    hs.mouse.dragTo({x = toX, y = toY})
    
    return true, nil
end

return automation
'''
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(lua_script)
            
            self.logger.info(f"Hammerspoon脚本已创建: {script_path}")
    
    @log_execution_time("capture_screen")
    def capture_screen(self, filename: Optional[str] = None) -> str:
        """捕获屏幕截图"""
        if not self.is_running:
            raise RuntimeError("屏幕服务未启动")
        
        if filename is None:
            filename = self.settings.get_screenshot_path()
        
        try:
            if (self.hammerspoon_available and 
                self.settings.screen_capture.method == "hammerspoon"):
                return self._capture_with_hammerspoon(filename)
            else:
                return self._capture_with_pyautogui(filename)
                
        except Exception as e:
            self.logger.error(f"捕获屏幕失败: {e}")
            raise
    
    def _capture_with_hammerspoon(self, filename: str) -> str:
        """使用Hammerspoon捕获屏幕"""
        try:
            # 执行Hammerspoon命令
            lua_command = f'''
            local automation = dofile("{self.settings.hammerspoon.script_path}")
            local result, error = automation.captureScreen("{filename}")
            if error then
                print("ERROR:" .. error)
            else
                print("SUCCESS:" .. result)
            end
            '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "SUCCESS:" in result.stdout:
                self.logger.info(f"Hammerspoon截图成功: {filename}")
                return filename
            else:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Hammerspoon截图失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("Hammerspoon截图超时")
    
    def _capture_with_pyautogui(self, filename: str) -> str:
        """使用PyAutoGUI捕获屏幕"""
        try:
            # 捕获屏幕
            screenshot = pyautogui.screenshot()
            
            # 处理图像
            processed_image = self._process_image(screenshot)
            
            # 保存图像
            processed_image.save(filename, 
                               format=self.settings.screen_capture.format,
                               quality=self.settings.screen_capture.quality)
            
            self.logger.info(f"PyAutoGUI截图成功: {filename}")
            return filename
            
        except Exception as e:
            raise RuntimeError(f"PyAutoGUI截图失败: {e}")
    
    def _process_image(self, image: Image.Image) -> Image.Image:
        """处理图像"""
        # 获取配置
        max_width = self.settings.screen_capture.max_width
        max_height = self.settings.screen_capture.max_height
        
        # 调整尺寸
        if image.width > max_width or image.height > max_height:
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            self.logger.debug(f"图像尺寸调整为: {image.size}")
        
        # 确保图像模式正确
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        if not self.is_running:
            raise RuntimeError("屏幕服务未启动")
        
        try:
            if (self.hammerspoon_available and 
                self.settings.screen_capture.method == "hammerspoon"):
                return self._get_screen_size_hammerspoon()
            else:
                return self._get_screen_size_pyautogui()
                
        except Exception as e:
            self.logger.error(f"获取屏幕尺寸失败: {e}")
            raise
    
    def _get_screen_size_hammerspoon(self) -> Tuple[int, int]:
        """使用Hammerspoon获取屏幕尺寸"""
        try:
            lua_command = f'''
            local automation = dofile("{self.settings.hammerspoon.script_path}")
            local size, error = automation.getScreenSize()
            if error then
                print("ERROR:" .. error)
            else
                print("SUCCESS:" .. size.width .. "," .. size.height)
            end
            '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and "SUCCESS:" in result.stdout:
                size_str = result.stdout.split("SUCCESS:")[1].strip()
                width, height = map(int, size_str.split(","))
                return (width, height)
            else:
                raise RuntimeError(f"获取屏幕尺寸失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise RuntimeError("获取屏幕尺寸超时")
    
    def _get_screen_size_pyautogui(self) -> Tuple[int, int]:
        """使用PyAutoGUI获取屏幕尺寸"""
        size = pyautogui.size()
        return (size.width, size.height)
    
    def crop_image(self, image_path: str, x: int, y: int, width: int, height: int) -> str:
        """裁剪图像"""
        try:
            with Image.open(image_path) as img:
                # 裁剪图像
                cropped = img.crop((x, y, x + width, y + height))
                
                # 生成新文件名
                path = Path(image_path)
                new_filename = f"{path.stem}_crop_{x}_{y}_{width}_{height}{path.suffix}"
                new_path = path.parent / new_filename
                
                # 保存裁剪后的图像
                cropped.save(new_path)
                
                self.logger.info(f"图像裁剪成功: {new_path}")
                return str(new_path)
                
        except Exception as e:
            self.logger.error(f"裁剪图像失败: {e}")
            raise
    
    def stop(self):
        """停止屏幕服务"""
        if not self.is_running:
            return
        
        try:
            self.logger.info("停止屏幕服务...")
            self.is_running = False
            self.logger.info("屏幕服务已停止")
            
        except Exception as e:
            self.logger.error(f"停止屏幕服务时出错: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'is_running': self.is_running,
            'hammerspoon_available': self.hammerspoon_available,
            'capture_method': self.settings.screen_capture.method,
            'screenshot_dir': self.settings.hammerspoon.screenshot_dir
        }