# macOS视觉智能体 - 计算器功能使用指南

## 功能概述

本项目已成功实现Mac系统计算器应用的自动打开功能，支持通过编程方式控制macOS应用程序启动。

## 🚀 快速开始

### 1. 运行演示脚本

```bash
# 基础功能测试
python3 test_calculator.py

# 完整功能演示（包含交互模式）
python3 simple_calculator_demo.py
```

### 2. 编程方式使用

#### 直接使用操作服务

```python
from src.config.settings import get_settings
from src.services.action_service import ActionService

# 初始化服务
settings = get_settings()
action_service = ActionService(settings)
action_service.start()

# 打开计算器
success = action_service.open_calculator()
print(f"计算器打开{'成功' if success else '失败'}")

# 打开其他应用
success = action_service.open_application("TextEdit")
print(f"文本编辑器打开{'成功' if success else '失败'}")

# 停止服务
action_service.stop()
```

#### 使用智能体工具

```python
from src.tools.action_tools import ActionExecutionTools
from src.services.action_service import ActionService
from src.config.settings import get_settings

# 初始化
settings = get_settings()
action_service = ActionService(settings)
action_service.start()

# 创建工具集合
action_tools = ActionExecutionTools(action_service)

# 使用工具打开计算器
result = action_tools.open_calculator._run()
print(f"工具执行结果: {result}")

# 使用工具打开指定应用
result = action_tools.open_application._run("Safari")
print(f"Safari打开结果: {result}")

action_service.stop()
```

## 🛠️ 技术实现

### 核心组件

1. **ActionService** (`src/services/action_service.py`)
   - `open_calculator()`: 专门打开计算器的方法
   - `open_application(app_name)`: 通用应用程序打开方法
   - 支持Hammerspoon和系统原生方法

2. **ActionExecutionTools** (`src/tools/action_tools.py`)
   - `OpenCalculatorTool`: 计算器打开工具
   - `OpenApplicationTool`: 通用应用打开工具
   - 为CrewAI智能体提供工具接口

3. **AgentManager** (`src/core/agent_manager.py`)
   - 集成了新的应用程序工具
   - 支持通过自然语言命令控制

### 实现方法

#### 方法1: Hammerspoon (推荐)
```lua
hs.application.launchOrFocus("Calculator")
```

#### 方法2: macOS原生命令
```bash
open -a Calculator
```

## 📋 支持的应用程序

### 系统内置应用
- `Calculator` - 计算器
- `TextEdit` - 文本编辑器
- `Safari` - Safari浏览器
- `System Preferences` - 系统偏好设置
- `Finder` - 访达
- `Mail` - 邮件
- `Calendar` - 日历
- `Notes` - 备忘录

### 第三方应用
- 使用应用程序的确切名称（如显示在Applications文件夹中）
- 例如：`Google Chrome`, `Visual Studio Code`, `Slack`

## 🔧 配置选项

### 安全设置

在 `src/config/settings.py` 中可以配置：

```python
class SafetySettings(BaseModel):
    enable_validation: bool = True  # 启用操作验证
    forbidden_areas: List[Dict] = []  # 禁止操作区域
    max_click_rate: int = 10  # 最大点击频率
```

### Hammerspoon设置

```python
class HammerspoonSettings(BaseModel):
    screenshot_dir: str = "data/screenshots"
    click_delay: float = 0.1  # 点击延迟
    safety_margin: int = 10  # 安全边距
```

## 🚨 权限要求

### macOS权限
1. **辅助功能权限**
   - 系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能
   - 添加终端或Python解释器

2. **自动化权限**
   - 系统偏好设置 > 安全性与隐私 > 隐私 > 自动化
   - 允许应用控制其他应用

### Hammerspoon安装（可选）
```bash
brew install hammerspoon
```

## 📊 使用示例

### 示例1: 批量打开应用

```python
def open_work_apps():
    """打开工作相关应用"""
    apps = ["Calculator", "TextEdit", "Safari", "Mail"]
    
    action_service = ActionService(get_settings())
    action_service.start()
    
    for app in apps:
        success = action_service.open_application(app)
        print(f"{app}: {'✅' if success else '❌'}")
    
    action_service.stop()
```

### 示例2: 条件性应用启动

```python
def smart_calculator_open():
    """智能计算器打开"""
    action_service = ActionService(get_settings())
    action_service.start()
    
    # 检查服务状态
    status = action_service.get_status()
    if not status['is_running']:
        print("服务未运行")
        return
    
    # 打开计算器
    if action_service.open_calculator():
        print("计算器已打开，可以开始计算")
        
        # 记录操作历史
        history = action_service.get_action_history(1)
        print(f"最后操作: {history[-1] if history else '无'}")
    
    action_service.stop()
```

## 🐛 故障排除

### 常见问题

1. **应用打开失败**
   - 检查应用程序名称是否正确
   - 确认应用程序已安装
   - 检查系统权限设置

2. **Hammerspoon不可用**
   - 系统会自动回退到原生方法
   - 安装Hammerspoon可获得更好性能

3. **权限被拒绝**
   - 检查辅助功能权限
   - 重启终端或IDE
   - 确认Python解释器有权限

### 调试模式

```python
# 启用详细日志
from src.utils.logger import setup_logger
logger = setup_logger("debug", level="DEBUG")

# 查看操作历史
history = action_service.get_action_history()
for action in history:
    print(f"{action['type']}: {action['success']}")
```

## 🔮 扩展功能

### 添加新应用支持

1. 在ActionService中添加专用方法：
```python
def open_chrome(self) -> bool:
    """打开Chrome浏览器"""
    return self.open_application("Google Chrome")
```

2. 创建对应的工具类：
```python
class OpenChromeTool(BaseTool, LoggerMixin):
    name: str = "open_chrome"
    # ... 实现细节
```

3. 在ActionExecutionTools中注册：
```python
self.open_chrome = OpenChromeTool(action_service)
```

## 📈 性能优化

- 使用Hammerspoon可提升响应速度
- 批量操作时添加适当延迟
- 定期清理操作历史记录
- 启用操作验证确保安全性

## 🤝 贡献

欢迎提交Issue和Pull Request来改进计算器功能！

---

**注意**: 此功能需要适当的系统权限，请确保在安全的环境中使用。