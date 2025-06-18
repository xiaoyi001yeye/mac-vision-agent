# 🚀 macOS视觉智能体 - 快速启动指南

## 📋 系统状态

✅ **基础环境**: 已配置完成  
✅ **依赖安装**: 已完成  
✅ **配置系统**: 正常工作  
✅ **日志系统**: 正常工作  
✅ **MLX支持**: 可用 (v0.1.15)  
⚠️ **CrewAI工具**: 需要额外配置  

## 🏗️ 项目结构

```
mac-vision-agent/
├── src/                    # 源代码目录
│   ├── config/            # 配置模块
│   ├── services/          # 核心服务
│   ├── tools/             # CrewAI工具
│   ├── agents/            # 智能体定义
│   ├── core/              # 核心管理器
│   └── utils/             # 工具函数
├── data/                  # 数据目录
│   ├── screenshots/       # 截图存储
│   ├── models/           # 模型缓存
│   └── cache/            # 临时缓存
├── logs/                 # 日志文件
├── hammerspoon/          # Hammerspoon脚本
├── requirements.txt      # Python依赖
├── demo.py              # 功能演示
├── simple_test.py       # 简化测试
└── README.md            # 详细文档
```

## 🧪 测试系统

### 1. 基础功能测试
```bash
python3 simple_test.py
```

### 2. 完整功能演示
```bash
python3 demo.py
```

## ⚙️ 核心配置

### MLX-VLM 配置
- **模型**: qwen2-vl-2b
- **最大tokens**: 1000
- **温度**: 0.1
- **缓存目录**: data/models

### 屏幕捕获配置
- **方法**: hammerspoon (推荐) / pyautogui
- **截图目录**: data/screenshots
- **图像质量**: 95%
- **最大分辨率**: 1920x1080

### 安全配置
- **操作验证**: 启用
- **确认破坏性操作**: 启用
- **最大点击距离**: 50像素

## 🔧 下一步配置

### 1. 安装CrewAI工具 (可选)
```bash
pip3 install crewai-tools
```

### 2. 配置Hammerspoon (推荐)
1. 安装Hammerspoon: `brew install hammerspoon`
2. 启动Hammerspoon并授予权限
3. 将`hammerspoon/`目录下的脚本复制到Hammerspoon配置目录

### 3. 配置API密钥 (可选)
创建`.env`文件:
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## 🎯 使用示例

### 基础服务使用
```python
from config.settings import get_settings
from services.vlm_service import VLMService
from services.screen_service import ScreenService
from services.action_service import ActionService

# 获取配置
settings = get_settings()

# 初始化服务
vlm_service = VLMService(settings)
screen_service = ScreenService(settings)
action_service = ActionService(settings)

# 启动服务
vlm_service.start()
screen_service.start()
action_service.start()
```

### 屏幕截图
```python
# 全屏截图
screenshot = screen_service.capture_screen()

# 区域截图
screenshot = screen_service.capture_region(x=100, y=100, width=800, height=600)
```

### 图像分析
```python
# 分析图像
result = vlm_service.analyze_image(
    image_path="screenshot.png",
    prompt="描述这个界面上的元素"
)
```

### 自动化操作
```python
# 点击操作
action_service.click(x=500, y=300)

# 输入文本
action_service.type_text("Hello, World!")

# 按键操作
action_service.key_press("cmd+c")
```

## 🐛 故障排除

### 常见问题

1. **权限问题**
   - 确保已授予屏幕录制权限
   - 确保已授予辅助功能权限

2. **MLX模型加载失败**
   - 检查网络连接
   - 确保有足够的磁盘空间
   - 查看`logs/`目录下的错误日志

3. **Hammerspoon连接失败**
   - 确保Hammerspoon正在运行
   - 检查Lua脚本是否正确加载

### 日志查看
```bash
# 查看主日志
tail -f logs/agent_*.log

# 查看错误日志
tail -f logs/error.log

# 查看性能日志
tail -f logs/performance.log
```

## 📚 更多信息

- 详细文档: [README.md](README.md)
- 配置说明: [src/config/settings.py](src/config/settings.py)
- 服务文档: [src/services/](src/services/)
- 工具文档: [src/tools/](src/tools/)

## 🤝 获取帮助

如果遇到问题:
1. 查看日志文件
2. 运行测试脚本诊断
3. 检查系统权限设置
4. 参考详细文档

---

🎉 **恭喜！** 您的macOS视觉智能体系统已准备就绪！