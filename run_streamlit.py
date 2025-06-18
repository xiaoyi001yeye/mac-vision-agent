#!/usr/bin/env python3
"""
Streamlit应用启动脚本
用于启动macOS视觉智能体的Web界面
"""

import os
import sys
import subprocess
import signal
from pathlib import Path

def setup_environment():
    """设置环境"""
    # 确保必要的目录存在
    directories = [
        "data/screenshots",
        "data/cache", 
        "data/models",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 目录已创建: {directory}")

def signal_handler(sig, frame):
    """信号处理器"""
    print("\n👋 正在退出Streamlit应用...")
    sys.exit(0)

def main():
    """主函数"""
    print("🚀 启动macOS视觉智能体 Streamlit应用")
    print("=" * 50)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 设置环境
        print("🔧 设置环境...")
        setup_environment()
        
        # 获取当前脚本目录
        current_dir = Path(__file__).parent.absolute()
        streamlit_app_path = current_dir / "streamlit_app.py"
        
        if not streamlit_app_path.exists():
            print(f"❌ 找不到Streamlit应用文件: {streamlit_app_path}")
            return
        
        print(f"\n🌐 启动Streamlit应用...")
        print(f"📁 应用路径: {streamlit_app_path}")
        print("\n" + "=" * 50)
        print("🎉 应用启动成功！")
        print("📱 请在浏览器中访问: http://localhost:8501")
        print("🛑 按 Ctrl+C 停止应用")
        print("=" * 50 + "\n")
        
        # 设置环境变量跳过Streamlit的邮箱输入
        env = os.environ.copy()
        env['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
        
        # 启动Streamlit
        cmd = [
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            str(streamlit_app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false",
            "--global.developmentMode", "false"
        ]
        
        # 使用Popen来避免邮箱输入问题
        process = subprocess.Popen(
            cmd, 
            cwd=current_dir,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 立即发送空行跳过邮箱输入
        try:
            process.stdin.write('\n')
            process.stdin.flush()
        except:
            pass
        
        # 实时输出日志
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                # 检查是否启动成功
                if "You can now view your Streamlit app in your browser" in output:
                    print("\n🎉 Streamlit应用启动成功！")
                    print("🌐 访问地址: http://localhost:8501")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        print("\n🔚 程序结束")

if __name__ == "__main__":
    main()