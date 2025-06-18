# macOS Vision Agent

基于MLX-VLM、Hammerspoon、CrewAI和PyAutoGUI的macOS视觉智能体系统。

## 系统架构

本系统采用模块化设计，包含以下核心组件：

### 核心服务
- **屏幕感知服务** (`ScreenService`): 负责屏幕捕获和图像处理
- **VLM推理服务** (`VLMService`): 基于MLX-VLM进行视觉语言模型推理
- **操作执行服务** (`ActionService`): 提供GUI自动化操作功能
- **智能体管理器** (`AgentManager`): 基于CrewAI管理多智能体协作

### CrewAI工具
- **屏幕工具** (`ScreenTool`): 屏幕捕获、分析和信息获取
- **VLM工具** (`VLMTool`): 图像分析、UI元素检测、文本提取
- **操作工具** (`ActionTool`): 点击、输入、拖拽、按键等操作

### 智能体角色
- **屏幕理解专家**: 分析屏幕内容，识别UI元素
- **操作执行专家**: 执行具体的GUI操作
- **任务协调专家**: 协调整体任务流程

## 功能特性

### 屏幕感知
- 支持Hammerspoon和PyAutoGUI两种屏幕捕获方式
- 全屏或区域截图
- 屏幕信息获取（尺寸、分辨率等）
- 图像预处理和优化

### 视觉理解
- 基于MLX-VLM的图像分析
- UI元素识别和定位
- 可点击元素查找
- 文本提取和识别
- 支持模拟模式用于开发测试

### 自动化操作
- 精确的鼠标点击（支持左键、右键、双击）
- 文本输入和键盘操作
- 拖拽操作
- 组合键支持
- 操作安全验证
- 操作历史记录

### 安全特性
- 坐标边界检查
- 禁止区域设置
- 操作验证机制
- 详细的日志记录
- 错误处理和恢复

## 安装要求

### 系统要求
- macOS 10.15+
- Python 3.8+
- Hammerspoon (可选，推荐)

### Python依赖
```bash
pip install -r requirements.txt
```

### 主要依赖包
- `crewai`: 多智能体协作框架
- `mlx`: Apple Silicon机器学习框架
- `mlx-vlm`: 视觉语言模型支持
- `pyautogui`: GUI自动化
- `pillow`: 图像处理
- `opencv-python`: 计算机视觉
- `pydantic`: 数据验证

## 快速开始

### 1. 安装依赖
```bash
cd /Users/weiyi/code/mac-vision-agent
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）
```bash
export MLX_VLM_MODEL_NAME="mlx-community/llava-1.5-7b-4bit"
export ENABLE_HAMMERSPOON="true"
export LOG_LEVEL="INFO"
```

### 3. 运行系统
```bash
python main.py
```

### 4. 交互命令
系统启动后，可以使用以下命令：
- `help`: 显示帮助信息
- `status`: 查看系统状态
- `screenshot`: 截取屏幕
- `analyze <prompt>`: 分析当前屏幕
- `click <x> <y>`: 点击指定位置
- `type <text>`: 输入文本
- `task <description>`: 执行复杂任务
- `quit`: 退出系统

## 配置说明

系统配置通过 `src/config/settings.py` 管理，支持环境变量覆盖：

### MLX-VLM配置
```python
MLX_VLM_MODEL_NAME="mlx-community/llava-1.5-7b-4bit"
MLX_VLM_MAX_TOKENS=512
MLX_VLM_TEMPERATURE=0.7
MLX_VLM_SIMULATION_MODE=False
```

### Hammerspoon配置
```python
ENABLE_HAMMERSPOON=True
HAMMERSPOON_CLICK_DELAY=0.1
HAMMERSPOON_SAFETY_MARGIN=10
```

### 安全配置
```python
SAFETY_ENABLE_VALIDATION=True
SAFETY_FORBIDDEN_AREAS='[{"x":0,"y":0,"width":100,"height":50}]'
```

## 开发指南

### 项目结构
```
mac-vision-agent/
├── main.py                 # 主入口文件
├── requirements.txt        # 依赖包列表
├── README.md              # 项目文档
├── logs/                  # 日志目录
├── data/                  # 数据目录
│   ├── screenshots/       # 截图存储
│   └── models/           # 模型缓存
└── src/                   # 源代码
    ├── config/           # 配置模块
    │   └── settings.py   # 系统配置
    ├── core/             # 核心模块
    │   └── agent_manager.py  # 智能体管理器
    ├── services/         # 服务模块
    │   ├── screen_service.py   # 屏幕服务
    │   ├── vlm_service.py      # VLM服务
    │   └── action_service.py   # 操作服务
    ├── tools/            # CrewAI工具
    │   ├── screen_tool.py      # 屏幕工具
    │   ├── vlm_tool.py         # VLM工具
    │   └── action_tool.py      # 操作工具
    └── utils/            # 工具模块
        └── logger.py     # 日志工具
```

### 添加新功能

1. **添加新服务**：在 `src/services/` 目录下创建新的服务模块
2. **添加新工具**：在 `src/tools/` 目录下创建对应的CrewAI工具
3. **添加新智能体**：在 `src/core/agent_manager.py` 中定义新的智能体角色
4. **更新配置**：在 `src/config/settings.py` 中添加相关配置项

### 调试技巧

1. **查看日志**：所有日志都输出到 `logs/` 目录
2. **模拟模式**：设置 `MLX_VLM_SIMULATION_MODE=True` 进行无模型测试
3. **安全模式**：启用操作验证避免误操作
4. **截图调试**：使用 `screenshot` 命令查看当前屏幕状态

## 故障排除

### 常见问题

1. **Hammerspoon不可用**
   - 确保已安装Hammerspoon
   - 检查Hammerspoon是否在运行
   - 验证命令行工具 `hs` 是否可用

2. **MLX模型加载失败**
   - 检查模型名称是否正确
   - 确保有足够的内存
   - 尝试使用模拟模式进行测试

3. **权限问题**
   - 确保Python有屏幕录制权限
   - 检查辅助功能权限设置
   - 验证文件读写权限

4. **性能问题**
   - 调整图像处理参数
   - 优化VLM推理设置
   - 监控内存使用情况

### 日志分析

系统提供详细的日志记录：
- `logs/app.log`: 应用主日志
- `logs/error.log`: 错误日志
- `logs/performance.log`: 性能日志

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建Issue或联系开发团队。