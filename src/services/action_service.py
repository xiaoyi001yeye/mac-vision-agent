#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作执行服务模块
提供GUI自动化操作功能
"""

import time
import subprocess
from typing import Dict, Any, Tuple, Optional, List, Union
from pathlib import Path
import pyautogui
from pynput import mouse, keyboard

from ..utils.logger import LoggerMixin, log_execution_time
from ..config.settings import Settings

class ActionService(LoggerMixin):
    """操作执行服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.is_running = False
        self.hammerspoon_available = False
        
        # 检查Hammerspoon可用性
        self._check_hammerspoon()
        
        # 配置PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = self.settings.hammerspoon.click_delay
        
        # 操作历史记录
        self.action_history = []
        
        self.logger.info("操作执行服务初始化完成")
    
    def _check_hammerspoon(self):
        """检查Hammerspoon是否可用"""
        try:
            result = subprocess.run(
                ['hs', '-c', 'print("test")'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.hammerspoon_available = True
                self.logger.info("Hammerspoon可用于操作执行")
            else:
                self.logger.warning("Hammerspoon不可用，将使用PyAutoGUI")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.warning(f"检查Hammerspoon失败: {e}，将使用PyAutoGUI")
    
    def start(self):
        """启动操作执行服务"""
        if self.is_running:
            return
        
        try:
            self.logger.info("启动操作执行服务...")
            
            # 获取屏幕尺寸用于边界检查
            self.screen_width, self.screen_height = self._get_screen_size()
            self.logger.info(f"屏幕尺寸: {self.screen_width}x{self.screen_height}")
            
            self.is_running = True
            self.logger.info("操作执行服务启动成功")
            
        except Exception as e:
            self.logger.error(f"启动操作执行服务失败: {e}")
            raise
    
    def _get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        try:
            if self.hammerspoon_available:
                return self._get_screen_size_hammerspoon()
            else:
                return self._get_screen_size_pyautogui()
        except Exception as e:
            self.logger.warning(f"获取屏幕尺寸失败，使用默认值: {e}")
            return (1920, 1080)  # 默认尺寸
    
    def _get_screen_size_hammerspoon(self) -> Tuple[int, int]:
        """使用Hammerspoon获取屏幕尺寸"""
        lua_command = '''
        local screen = hs.screen.mainScreen()
        local frame = screen:frame()
        print(frame.w .. "," .. frame.h)
        '''
        
        result = subprocess.run(
            ['hs', '-c', lua_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            width, height = map(int, result.stdout.strip().split(","))
            return (width, height)
        else:
            raise RuntimeError(f"Hammerspoon获取屏幕尺寸失败: {result.stderr}")
    
    def _get_screen_size_pyautogui(self) -> Tuple[int, int]:
        """使用PyAutoGUI获取屏幕尺寸"""
        size = pyautogui.size()
        return (size.width, size.height)
    
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """验证坐标是否在屏幕范围内"""
        margin = self.settings.hammerspoon.safety_margin
        
        if (x < margin or x > self.screen_width - margin or
            y < margin or y > self.screen_height - margin):
            return False
        
        # 检查是否在禁止区域
        for area in self.settings.safety.forbidden_areas:
            if (area['x'] <= x <= area['x'] + area['width'] and
                area['y'] <= y <= area['y'] + area['height']):
                return False
        
        return True
    
    def _record_action(self, action_type: str, params: Dict[str, Any], result: bool):
        """记录操作历史"""
        action_record = {
            'timestamp': time.time(),
            'type': action_type,
            'params': params,
            'success': result
        }
        
        self.action_history.append(action_record)
        
        # 保持历史记录数量在合理范围内
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-500:]
    
    @log_execution_time("click_at")
    def click_at(self, x: int, y: int, button: str = "left", double_click: bool = False) -> bool:
        """在指定位置点击"""
        if not self.is_running:
            raise RuntimeError("操作执行服务未启动")
        
        # 验证坐标
        if not self._validate_coordinates(x, y):
            self.logger.error(f"坐标验证失败: ({x}, {y})")
            self._record_action("click", {"x": x, "y": y, "button": button}, False)
            return False
        
        try:
            if self.hammerspoon_available:
                result = self._click_with_hammerspoon(x, y, button, double_click)
            else:
                result = self._click_with_pyautogui(x, y, button, double_click)
            
            self._record_action("click", {"x": x, "y": y, "button": button, "double": double_click}, result)
            
            if result:
                self.logger.info(f"点击成功: ({x}, {y})")
            else:
                self.logger.error(f"点击失败: ({x}, {y})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"点击操作异常: {e}")
            self._record_action("click", {"x": x, "y": y, "button": button}, False)
            return False
    
    def _click_with_hammerspoon(self, x: int, y: int, button: str, double_click: bool) -> bool:
        """使用Hammerspoon执行点击"""
        try:
            if double_click:
                lua_command = f'''
                hs.mouse.setAbsolutePosition({{x = {x}, y = {y}}})
                hs.timer.usleep(100000)
                hs.mouse.doubleLeftClick({{x = {x}, y = {y}}})
                print("SUCCESS")
                '''
            else:
                click_method = "leftClick" if button == "left" else "rightClick"
                lua_command = f'''
                hs.mouse.setAbsolutePosition({{x = {x}, y = {y}}})
                hs.timer.usleep(100000)
                hs.mouse.{click_method}({{x = {x}, y = {y}}})
                print("SUCCESS")
                '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and "SUCCESS" in result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Hammerspoon点击操作超时")
            return False
    
    def _click_with_pyautogui(self, x: int, y: int, button: str, double_click: bool) -> bool:
        """使用PyAutoGUI执行点击"""
        try:
            if double_click:
                pyautogui.doubleClick(x, y, button=button)
            else:
                pyautogui.click(x, y, button=button)
            
            return True
            
        except Exception as e:
            self.logger.error(f"PyAutoGUI点击失败: {e}")
            return False
    
    @log_execution_time("type_text")
    def type_text(self, text: str, interval: float = 0.01) -> bool:
        """输入文本"""
        if not self.is_running:
            raise RuntimeError("操作执行服务未启动")
        
        if not text:
            self.logger.warning("输入文本为空")
            return False
        
        try:
            if self.hammerspoon_available:
                result = self._type_with_hammerspoon(text)
            else:
                result = self._type_with_pyautogui(text, interval)
            
            self._record_action("type", {"text": text[:50], "length": len(text)}, result)
            
            if result:
                self.logger.info(f"文本输入成功，长度: {len(text)}")
            else:
                self.logger.error("文本输入失败")
            
            return result
            
        except Exception as e:
            self.logger.error(f"文本输入异常: {e}")
            self._record_action("type", {"text": text[:50], "length": len(text)}, False)
            return False
    
    def _type_with_hammerspoon(self, text: str) -> bool:
        """使用Hammerspoon输入文本"""
        try:
            # 转义特殊字符
            escaped_text = text.replace('"', '\\"').replace('\n', '\\n')
            
            lua_command = f'''
            hs.eventtap.keyStrokes("{escaped_text}")
            print("SUCCESS")
            '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0 and "SUCCESS" in result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Hammerspoon文本输入超时")
            return False
    
    def _type_with_pyautogui(self, text: str, interval: float) -> bool:
        """使用PyAutoGUI输入文本"""
        try:
            pyautogui.typewrite(text, interval=interval)
            return True
            
        except Exception as e:
            self.logger.error(f"PyAutoGUI文本输入失败: {e}")
            return False
    
    @log_execution_time("drag")
    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 1.0) -> bool:
        """拖拽操作"""
        if not self.is_running:
            raise RuntimeError("操作执行服务未启动")
        
        # 验证坐标
        if not (self._validate_coordinates(from_x, from_y) and 
                self._validate_coordinates(to_x, to_y)):
            self.logger.error(f"拖拽坐标验证失败: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            return False
        
        try:
            if self.hammerspoon_available:
                result = self._drag_with_hammerspoon(from_x, from_y, to_x, to_y, duration)
            else:
                result = self._drag_with_pyautogui(from_x, from_y, to_x, to_y, duration)
            
            params = {
                "from_x": from_x, "from_y": from_y,
                "to_x": to_x, "to_y": to_y,
                "duration": duration
            }
            self._record_action("drag", params, result)
            
            if result:
                self.logger.info(f"拖拽成功: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            else:
                self.logger.error(f"拖拽失败: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"拖拽操作异常: {e}")
            return False
    
    def _drag_with_hammerspoon(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float) -> bool:
        """使用Hammerspoon执行拖拽"""
        try:
            duration_ms = int(duration * 1000000)  # 转换为微秒
            
            lua_command = f'''
            hs.mouse.setAbsolutePosition({{x = {from_x}, y = {from_y}}})
            hs.timer.usleep(100000)
            hs.mouse.leftClick({{x = {from_x}, y = {from_y}}})
            hs.timer.usleep(100000)
            hs.mouse.dragTo({{x = {to_x}, y = {to_y}}})
            hs.timer.usleep({duration_ms})
            print("SUCCESS")
            '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return result.returncode == 0 and "SUCCESS" in result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Hammerspoon拖拽操作超时")
            return False
    
    def _drag_with_pyautogui(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float) -> bool:
        """使用PyAutoGUI执行拖拽"""
        try:
            pyautogui.drag(to_x - from_x, to_y - from_y, duration=duration, button='left')
            return True
            
        except Exception as e:
            self.logger.error(f"PyAutoGUI拖拽失败: {e}")
            return False
    
    def key_press(self, key: str, modifiers: List[str] = None) -> bool:
        """按键操作"""
        if not self.is_running:
            raise RuntimeError("操作执行服务未启动")
        
        try:
            if modifiers is None:
                modifiers = []
            
            if self.hammerspoon_available:
                result = self._key_press_hammerspoon(key, modifiers)
            else:
                result = self._key_press_pyautogui(key, modifiers)
            
            self._record_action("keypress", {"key": key, "modifiers": modifiers}, result)
            
            if result:
                self.logger.info(f"按键成功: {'+'.join(modifiers + [key])}")
            else:
                self.logger.error(f"按键失败: {'+'.join(modifiers + [key])}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"按键操作异常: {e}")
            return False
    
    def _key_press_hammerspoon(self, key: str, modifiers: List[str]) -> bool:
        """使用Hammerspoon执行按键"""
        try:
            if modifiers:
                modifier_str = ', '.join([f'"{mod}"' for mod in modifiers])
                lua_command = f'''
                hs.eventtap.keyStroke({{{modifier_str}}}, "{key}")
                print("SUCCESS")
                '''
            else:
                lua_command = f'''
                hs.eventtap.keyStroke({{}}, "{key}")
                print("SUCCESS")
                '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and "SUCCESS" in result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Hammerspoon按键操作超时")
            return False
    
    def _key_press_pyautogui(self, key: str, modifiers: List[str]) -> bool:
        """使用PyAutoGUI执行按键"""
        try:
            if modifiers:
                pyautogui.hotkey(*modifiers, key)
            else:
                pyautogui.press(key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"PyAutoGUI按键失败: {e}")
            return False
    
    def validate_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证操作安全性"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        if not self.settings.safety.enable_validation:
            return validation_result
        
        # 坐标验证
        if action_type in ['click', 'drag']:
            if action_type == 'click':
                coords = [(params.get('x', 0), params.get('y', 0))]
            else:  # drag
                coords = [
                    (params.get('from_x', 0), params.get('from_y', 0)),
                    (params.get('to_x', 0), params.get('to_y', 0))
                ]
            
            for x, y in coords:
                if not self._validate_coordinates(x, y):
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"坐标超出安全范围: ({x}, {y})")
        
        # 文本输入验证
        if action_type == 'type':
            text = params.get('text', '')
            if len(text) > 1000:
                validation_result['warnings'].append("输入文本过长，可能影响性能")
            
            # 检查敏感内容（可以根据需要扩展）
            sensitive_patterns = ['rm -rf', 'sudo', 'password']
            for pattern in sensitive_patterns:
                if pattern.lower() in text.lower():
                    validation_result['warnings'].append(f"检测到敏感内容: {pattern}")
        
        return validation_result
    
    def get_action_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取操作历史"""
        return self.action_history[-limit:]
    
    def stop(self):
        """停止操作执行服务"""
        if not self.is_running:
            return
        
        try:
            self.logger.info("停止操作执行服务...")
            self.is_running = False
            self.logger.info("操作执行服务已停止")
            
        except Exception as e:
            self.logger.error(f"停止操作执行服务时出错: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            'is_running': self.is_running,
            'hammerspoon_available': self.hammerspoon_available,
            'screen_size': (self.screen_width, self.screen_height) if hasattr(self, 'screen_width') else None,
            'action_history_count': len(self.action_history),
            'safety_enabled': self.settings.safety.enable_validation
        }

    def open_application(self, app_name: str) -> bool:
        """打开指定的应用程序"""
        if not self.is_running:
            raise RuntimeError("操作执行服务未启动")
        
        try:
            if self.hammerspoon_available:
                result = self._open_app_with_hammerspoon(app_name)
            else:
                result = self._open_app_with_subprocess(app_name)
            
            self._record_action("open_app", {"app_name": app_name}, result)
            
            if result:
                self.logger.info(f"应用程序启动成功: {app_name}")
            else:
                self.logger.error(f"应用程序启动失败: {app_name}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"启动应用程序异常: {e}")
            self._record_action("open_app", {"app_name": app_name}, False)
            return False
    
    def _open_app_with_hammerspoon(self, app_name: str) -> bool:
        """使用Hammerspoon打开应用程序"""
        try:
            lua_command = f'''
            hs.application.launchOrFocus("{app_name}")
            print("SUCCESS")
            '''
            
            result = subprocess.run(
                ['hs', '-c', lua_command],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and "SUCCESS" in result.stdout
            
        except subprocess.TimeoutExpired:
            self.logger.error("Hammerspoon应用启动操作超时")
            return False
    
    def _open_app_with_subprocess(self, app_name: str) -> bool:
        """使用subprocess打开应用程序"""
        try:
            # 使用macOS的open命令启动应用
            result = subprocess.run(
                ['open', '-a', app_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"subprocess启动应用失败: {e}")
            return False
    
    def open_calculator(self) -> bool:
        """打开计算器应用"""
        return self.open_application("Calculator")