#!/bin/bash
# ASR Web Service Launcher
# 
# 支持所有用户在任何机器上运行
# 无需预先安装 QwenPaw，自动检测或使用虚拟环境
#
# Usage:
#   ./start.sh                    # 使用当前激活的 virtualenv
#   bash start.sh                 # 同上（Windows PowerShell）
#
# 或者手动创建虚拟环境后运行：
#   python3 -m venv venv
#   source venv/bin/activate
#   python app.py

set -e

echo "🚀 Mac System Audio Recognition Tool"
echo "====================================="
echo ""

# 获取当前目录作为项目根目录（完全通用）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查是否已经在虚拟环境中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Using active virtual environment:"
    echo "   $VIRTUAL_ENV"
    echo ""
else
    echo "⚠️  No virtual environment detected!"
    echo ""
    echo "This project requires a Python virtual environment with:"
    echo "  • Flask (Web server)"
    echo "  • PyTorch + FunASR (voice recognition)"
    echo "  • SoundDevice (audio capture)"
    echo ""
    
    # 提示用户创建虚拟环境
    read -p "Would you like to create one now? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "❌ Please create a virtual environment manually:"
        echo ""
        echo "  Option 1 (Recommended):"
        echo "    python3 -m venv venv"
        echo "    source venv/bin/activate"
        echo "    pip install flask torch funasr sounddevice numpy pydub"
        echo ""
        echo "  Option 2 (Use your own env):"
        echo "    conda create -n asr_env python=3.10"
        echo "    conda activate asr_env"
        echo "    pip install flask torch funasr sounddevice numpy pydub"
        echo ""
        exit 0
    fi
    
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # 激活新创建的虚拟环境
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate.bat
    else
        # macOS/Linux
        source venv/bin/activate
    fi
fi

# 切换到项目目录
cd "$PROJECT_ROOT"

# 检查并安装依赖
echo "Checking dependencies..."
python3 -c "import flask; import torch; import funasr; import sounddevice" 2>/dev/null || {
    echo "⚠️  Some dependencies are missing. Installing now..."
    pip install --quiet flask torch funasr sounddevice numpy pydub
}

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "Starting Web Server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# 启动服务
exec python3 app.py
