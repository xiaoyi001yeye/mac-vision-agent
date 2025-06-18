# macOS 视觉智能体系统技术栈分析 (MVP 精简版)

## 概述

本文档基于 `use-case-diagram.md` 中定义的核心和高优先级用例需求，分析了实现 macOS 视觉智能体系统 MVP (Minimum Viable Product) 所需的最小化技术栈。目标是以最小的代价实现核心功能，包括屏幕内容理解、自动化操作和基础的安全监控。

## 核心技术栈架构 (MVP)

### 1. 编程语言

#### 主要语言
- **Python 3.9+**
  - 用途：系统主体开发语言
  - 优势：丰富的AI/ML生态、跨平台支持、开发效率高
  - 应用场景：模型推理、业务逻辑、核心控制流

#### 辅助语言
- **Swift / Objective-C**
  - 用途：macOS原生API调用
  - 应用场景：ScreenCaptureKit集成、Accessibility API访问、系统级事件模拟

### 2. 视觉语言模型 (VLM) 技术栈

#### 模型框架
- **MLX Framework**
  - 用途：Apple Silicon优化的机器学习框架
  - 优势：原生Apple Silicon支持、内存效率高
  - 应用场景：VLM模型推理
- **Transformers (Hugging Face)**
  - 用途：模型加载和管理
  - 应用场景：模型下载、预处理、后处理

#### 支持的VLM模型 (示例)
- **选择一个轻量级且高效的VLM模型** (如 Qwen2-VL-Chat-Int4, LLaVA 系列的小参数模型)
  - 技术：多模态Transformer架构
  - 特点：满足基本的视觉理解和指令跟随能力
  - 备注：MVP阶段专注于集成一个模型，后续可扩展支持更多模型。

### 3. 屏幕感知技术栈

#### 屏幕捕获
- **ScreenCaptureKit (macOS 12.3+)**
  - 用途：高性能屏幕截图
  - 优势：系统级API、高质量、低延迟
  - 实现：Swift/Objective-C封装，Python调用

#### UI结构提取
- **macapptree** (或直接使用 PyObjC 调用 Accessibility API)
  - 用途：提取macOS应用UI元素树
  - 技术：Accessibility API封装
  - 输出：结构化UI元素信息
- **PyObjC**
  - 用途：Python调用Objective-C/Swift框架
  - 应用：Accessibility API访问、ScreenCaptureKit调用

#### 图像处理
- **Pillow (PIL)**
  - 用途：基础图像预处理、格式转换
- **NumPy**
  - 用途：数值计算、数组操作 (MLX和图像处理常依赖)

### 4. 自动化操作技术栈

#### 鼠标键盘控制
- **PyAutoGUI**
  - 用途：跨平台GUI自动化
  - 功能：鼠标点击、键盘输入
- **Quartz Event Services** (通过 PyObjC 或 Swift 辅助库调用)
  - 用途：系统级事件生成
  - 优势：更可靠的事件模拟，尤其在某些应用中

#### macOS原生API
- **Core Graphics** (通过 PyObjC 或 Swift 辅助库调用)
  - 用途：坐标系统、显示信息

### 5. 系统架构技术栈

#### 异步编程
- **asyncio**
  - 用途：异步任务处理、并发控制 (核心PCA循环)
- **queue** (Python内置)
  - 用途：线程/协程安全的消息传递

#### 数据验证与配置
- **pydantic**
  - 用途：数据验证、简单配置管理

### 6. 数据存储技术栈 (MVP)

#### 配置管理
- **PyYAML** 或 **python-dotenv**
  - 用途：YAML配置文件解析或环境变量管理

#### 状态与历史记录
- **SQLite**
  - 用途：轻量级数据库，用于存储任务历史、简单状态或用户偏好（如果需要）
- **pickle/joblib**
  - 用途：对象序列化、简单模型/数据缓存

### 7. 安全监控技术栈 (MVP)

#### 权限与日志
- **macOS Security Framework** (通过 PyObjC 或 Swift 辅助库进行权限检查)
  - 用途：基础权限检查 (如辅助功能是否开启)
- **logging** (Python内置)
  - 用途：结构化日志记录
- **psutil**
  - 用途：基础系统资源监控 (可选，用于调试或非常基础的监控)

### 8. 用户界面技术栈 (MVP)

#### 简单桌面应用 (可选，或命令行界面)
- **Tkinter** (Python内置)
  - 用途：非常简单的GUI界面，用于状态显示或基本交互
  - 备注：MVP阶段可以优先考虑命令行界面 (CLI) 以降低复杂性。

### 9. 测试技术栈 (MVP)

#### 单元测试
- **pytest**
  - 用途：测试框架
- **pytest-asyncio**
  - 用途：异步代码测试
- **unittest.mock** (Python内置)
  - 用途：模拟对象

### 10. 开发工具技术栈 (MVP)

#### 代码质量
- **black**
  - 用途：代码格式化
- **flake8**
  - 用途：代码风格检查

#### 依赖管理
- **Poetry** (推荐) 或 **pip + requirements.txt**
  - 用途：依赖管理、虚拟环境

## 按核心用例分类的技术栈映射 (MVP)

### UC1: 执行桌面任务
**核心技术**:
- Python + asyncio (任务调度)
- MLX + Transformers + VLM模型 (指令理解)
- PyAutoGUI / Quartz Event Services (操作执行)
- SQLite (可选，任务历史)

### UC2: 屏幕内容理解
**核心技术**:
- ScreenCaptureKit (屏幕捕获)
- macapptree / PyObjC + Accessibility API (UI结构)
- MLX + VLM模型 (内容理解)
- Pillow + NumPy (图像处理)

### UC4: 自动化操作
**核心技术**:
- PyAutoGUI / Pynput (输入控制)
- Quartz Event Services (系统级事件)
- Core Graphics (坐标计算)

### UC5: 安全监控 (基础)
**核心技术**:
- psutil (资源监控 - 可选)
- macOS Security Framework (权限检查)
- logging (安全日志)

## 部署和运行环境 (MVP)

### 系统要求
- **操作系统**: macOS 12.3+ (ScreenCaptureKit 要求)
- **硬件**: Apple Silicon Mac (M1/M2/M3)
- **内存**: 8GB+ 统一内存 (取决于VLM模型大小)
- **存储**: 5GB+ 可用空间 (取决于VLM模型大小)

### Python环境
- **Python版本**: 3.9+
- **包管理**: Poetry 或 pip
- **虚拟环境**: venv 或 conda

### 系统权限
- **辅助功能**: 用于UI自动化
- **屏幕录制**: 用于屏幕捕获

## 技术选型原则 (MVP)

### 1. Apple Silicon优化
- 优先选择支持Apple Silicon的原生框架 (MLX)

### 2. 最小化和快速迭代
- 选择实现核心功能所必需的最简技术集。
- 避免过早引入复杂性。

### 3. 安全性基础
- 本地化处理，确保基本权限检查。

### 4. 性能考虑
- 采用异步编程，选择性能较好的原生API。

### 5. 开源优先
- 尽可能使用成熟的开源库。

## 实施建议 (MVP)

### 开发阶段
1. **核心PCA循环**: 专注实现 Perceive (屏幕内容理解) -> Cognize (简单指令理解/决策) -> Act (自动化操作) 的基础循环。
2. **基础模型集成**: 集成一个轻量级VLM模型。
3. **核心API封装**: 封装 ScreenCaptureKit, Accessibility API, Quartz Event Services。
4. **命令行界面**: 优先实现CLI进行测试和交互。
5. **基础日志与错误处理**: 实现必要的日志记录和简单的错误处理机制。

这个精简的技术栈分析为macOS视觉智能体系统的MVP开发提供了指导，旨在快速验证核心功能并为后续迭代打下基础。