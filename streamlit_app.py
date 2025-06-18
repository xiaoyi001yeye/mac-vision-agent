import streamlit as st
import sys
import os
from datetime import datetime
import time
from typing import Dict, List, Optional, Any

# 添加项目路径到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.config.settings import get_settings
    from src.services.action_service import ActionService
    from src.utils.logger import setup_logger
except ImportError as e:
    st.error(f"导入模块失败: {e}")
    st.stop()

# 设置页面配置
st.set_page_config(
    page_title="macOS 视觉智能体",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化日志
logger = setup_logger("streamlit_app")

class SimpleAgentInterface:
    """简化的智能体界面类"""
    
    def __init__(self):
        self.settings = None
        self.action_service = None
        self.is_initialized = False
        
    def initialize_services(self) -> bool:
        """初始化服务"""
        try:
            if not self.is_initialized:
                # 获取设置
                self.settings = get_settings()
                
                # 初始化操作服务
                self.action_service = ActionService(self.settings)
                self.action_service.start()
                
                self.is_initialized = True
                logger.info("服务初始化完成")
                return True
        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            return False
    
    def stop_services(self):
        """停止服务"""
        try:
            if self.action_service:
                self.action_service.stop()
            self.is_initialized = False
            logger.info("服务已停止")
        except Exception as e:
            logger.error(f"停止服务时出错: {e}")
    
    def execute_simple_command(self, command: str) -> str:
        """执行简单命令"""
        try:
            if not self.is_initialized:
                return "❌ 服务未初始化，请先启动服务"
            
            logger.info(f"执行命令: {command}")
            
            # 简单的命令映射
            command_lower = command.lower()
            
            if "计算器" in command or "calculator" in command_lower:
                success = self.action_service.open_calculator()
                return "✅ 计算器已打开" if success else "❌ 计算器打开失败"
            
            elif "文本编辑" in command or "textedit" in command_lower:
                success = self.action_service.open_application("TextEdit")
                return "✅ 文本编辑器已打开" if success else "❌ 文本编辑器打开失败"
            
            elif "safari" in command_lower or "浏览器" in command:
                success = self.action_service.open_application("Safari")
                return "✅ Safari浏览器已打开" if success else "❌ Safari浏览器打开失败"
            
            elif "finder" in command_lower or "访达" in command:
                success = self.action_service.open_application("Finder")
                return "✅ Finder已打开" if success else "❌ Finder打开失败"
            
            elif "系统偏好" in command or "system preferences" in command_lower:
                success = self.action_service.open_application("System Preferences")
                return "✅ 系统偏好设置已打开" if success else "❌ 系统偏好设置打开失败"
            
            else:
                # 尝试作为应用程序名称打开
                app_name = command.strip()
                success = self.action_service.open_application(app_name)
                return f"✅ {app_name}已打开" if success else f"❌ {app_name}打开失败，请检查应用程序名称"
                
        except Exception as e:
            logger.error(f"命令执行出错: {e}")
            return f"❌ 执行出错: {str(e)}"
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            'initialized': self.is_initialized,
            'action_service': False
        }
        
        try:
            if self.action_service:
                action_status = self.action_service.get_status()
                status['action_service'] = action_status.get('is_running', False)
        except Exception as e:
            logger.error(f"获取服务状态出错: {e}")
        
        return status

# 初始化会话状态
if 'agent_interface' not in st.session_state:
    st.session_state.agent_interface = SimpleAgentInterface()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'service_started' not in st.session_state:
    st.session_state.service_started = False

# 主界面
def main():
    st.title("🤖 macOS 视觉智能体")
    st.markdown("基于Streamlit的简化版智能体界面")
    st.markdown("---")
    
    # 侧边栏 - 服务控制
    with st.sidebar:
        st.header("🔧 服务控制")
        
        # 服务状态显示
        status = st.session_state.agent_interface.get_service_status()
        
        if status['initialized']:
            st.success("✅ 服务已启动")
        else:
            st.error("❌ 服务未启动")
        
        # 启动/停止按钮
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 启动服务", disabled=status['initialized']):
                with st.spinner("正在启动服务..."):
                    success = st.session_state.agent_interface.initialize_services()
                    if success:
                        st.session_state.service_started = True
                        st.success("服务启动成功！")
                        st.rerun()
                    else:
                        st.error("服务启动失败！")
        
        with col2:
            if st.button("🛑 停止服务", disabled=not status['initialized']):
                st.session_state.agent_interface.stop_services()
                st.session_state.service_started = False
                st.success("服务已停止")
                st.rerun()
        
        # 详细状态
        st.markdown("### 📊 服务状态")
        action_icon = "✅" if status['action_service'] else "❌"
        st.write(f"{action_icon} 操作服务")
        
        st.markdown("---")
        
        # 快捷操作
        st.header("⚡ 快捷操作")
        
        quick_actions = [
            "打开计算器",
            "打开文本编辑器",
            "打开Safari浏览器",
            "打开Finder",
            "打开系统偏好设置"
        ]
        
        for action in quick_actions:
            if st.button(action, key=f"quick_{action}"):
                if status['initialized']:
                    # 添加到聊天历史
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': action,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    # 执行命令
                    result = st.session_state.agent_interface.execute_simple_command(action)
                    
                    # 添加结果到聊天历史
                    st.session_state.chat_history.append({
                        'type': 'assistant',
                        'content': result,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    st.rerun()
                else:
                    st.warning("请先启动服务")
        
        # 清空聊天历史
        if st.button("🗑️ 清空聊天"):
            st.session_state.chat_history = []
            st.rerun()
    
    # 主聊天界面
    st.header("💬 对话界面")
    
    # 聊天历史显示
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 欢迎使用macOS视觉智能体！请输入您的指令开始对话。")
            
            # 显示示例命令
            st.markdown("### 💡 支持的命令")
            examples = [
                "打开计算器",
                "打开文本编辑器", 
                "打开Safari浏览器",
                "打开Finder",
                "打开系统偏好设置",
                "Calculator",
                "TextEdit",
                "Safari"
            ]
            
            for example in examples:
                st.code(example)
        else:
            # 显示聊天历史
            for message in st.session_state.chat_history:
                timestamp = message['timestamp']
                
                if message['type'] == 'user':
                    st.markdown(f"**🧑 用户** *{timestamp}*")
                    st.markdown(f"> {message['content']}")
                else:
                    st.markdown(f"**🤖 智能体** *{timestamp}*")
                    st.markdown(message['content'])
                
                st.markdown("---")
    
    # 用户输入
    st.markdown("### 💭 输入指令")
    
    # 使用表单来处理输入
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_area(
            "请输入您的指令：",
            placeholder="例如：打开计算器、打开Safari、Calculator等...",
            height=100,
            key="user_input"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            submit_button = st.form_submit_button("🚀 发送")
    
    # 处理用户输入
    if submit_button and user_input.strip():
        if not status['initialized']:
            st.error("❌ 请先启动服务")
        else:
            # 添加用户消息到聊天历史
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # 显示处理中状态
            with st.spinner("🤖 正在处理您的请求..."):
                # 执行命令
                result = st.session_state.agent_interface.execute_simple_command(user_input)
            
            # 添加智能体回复到聊天历史
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': result,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
            # 重新运行以更新界面
            st.rerun()
    
    # 页脚信息
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>🤖 macOS 视觉智能体 - 简化版</p>
            <p>支持基本的macOS应用程序启动功能</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # 清理资源
        if 'agent_interface' in st.session_state:
            st.session_state.agent_interface.stop_services()
        st.write("👋 程序已退出")
    except Exception as e:
        st.error(f"❌ 程序运行出错: {e}")
        logger.error(f"Streamlit应用出错: {e}")