#!/bin/bash
# ASR Web Service Launcher
# 
# 自动创建或复用虚拟环境，无需人工干预
#
# Usage:
#   ./start.sh                    # 自动处理所有事情
#   bash start.sh                 # Windows PowerShell
#
# 行为说明：
# - 如果当前已有激活的 virtualenv → 直接使用
# - 如果项目目录下有 venv → 直接使用该 venv
# - 如果都没有 → 静默创建新的 venv（不需要确认）

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
    # 检查项目目录下是否有 venv
    if [ -d "$PROJECT_ROOT/venv" ]; then
        echo "📦 Found existing virtual environment in project directory."
        
        # 激活已有的 venv
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            source venv/Scripts/activate.bat
        else
            # macOS/Linux
            source venv/bin/activate
        fi
        
        echo "   $PROJECT_ROOT/venv"
        echo ""
    else
        # 创建新的 venv（静默创建，不询问）
        echo "🆕 Creating new virtual environment..."
        python3 -m venv venv
        
        # 激活新创建的 venv
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            source venv/Scripts/activate.bat
        else
            # macOS/Linux
            source venv/bin/activate
        fi
        
        echo "✅ Virtual environment created at: $PROJECT_ROOT/venv"
        echo ""
    fi
fi

# 切换到项目目录
cd "$PROJECT_ROOT"

# 升级 pip
echo "🔧 Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# 检查并安装依赖
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --quiet -r requirements.txt
else
    # 如果没有 requirements.txt，安装基本依赖
    echo "   Using bundled dependency versions for stability..."
    pip install --quiet \
        "funasr==1.1.9" \
        "torch==2.2.2" \
        "numpy<2.0" \
        "flask" \
        "sounddevice" \
        "pydub" \
        --index-url https://download.pytorch.org/whl/cpu
fi

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "Starting Web Server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# 保存 PID 到文件（供 stop.sh 使用）
echo $$ > "$PROJECT_ROOT/.asr.pid"

# 启动服务
exec python3 app.py
