#!/bin/bash
# ASR Web Service Launcher
# 自动检测虚拟环境并启动服务
# 可在任何机器上运行（只需安装 QwenPaw）

set -e

echo "🚀 Starting ASR Web Service..."
echo ""

# 获取当前目录作为项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 尝试检测 QwenPaw venv 位置
VENV_PATH="$HOME/.qwenpaw/venv/bin/activate"

# 检查是否激活在 venv 中
if [[ "$VIRTUAL_ENV" != "" ]]; then
    # 已经在虚拟环境中
    echo "✅ Using existing virtual environment: $VIRTUAL_ENV"
else
    # 检测 venv 是否存在
    if [ ! -f "$VENV_PATH" ]; then
        echo "⚠️  QwenPaw venv not found at $VENV_PATH"
        echo ""
        echo "Please install QwenPaw first, or activate a virtual environment manually."
        echo ""
        echo "Options:"
        echo "  1. Install QwenPaw and run this script again"
        echo "  2. Create your own venv: python3 -m venv venv"
        echo "  3. Activate existing venv: source /path/to/venv/bin/activate"
        exit 1
    fi
    
    echo "Found QwenPaw at: $HOME/.qwenpaw/venv"
    echo "Activating virtual environment..."
    
    # 激活虚拟环境
    source "$VENV_PATH"
fi

# 切换到项目目录
cd "$PROJECT_ROOT"

# 检查必要依赖
echo "Checking dependencies..."
python3 -c "import flask; import torch; import funasr; import sounddevice" 2>/dev/null || {
    echo "⚠️  Missing dependencies. Installing now..."
    pip install --quiet flask torch funasr sounddevice numpy pydub
}

echo ""
echo "✅ Dependencies OK!"
echo ""
echo "Starting server on http://localhost:5000 ..."
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# 启动服务
exec python3 app.py
