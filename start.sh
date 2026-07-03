#!/bin/bash
# ASR Web Service Launcher
# 
# 自动创建或复用虚拟环境，无需人工干预
#
# Usage:
#   ./start.sh                    # 自动处理所有事情
#   bash start.sh                 # Windows PowerShell
#
# ⚠️ 重要：需要 Python 3.9+（numpy 1.26+ 的要求）
#    如果你的系统是 Python 3.8，请先升级：
#      brew install python@3.12
#      /opt/homebrew/bin/python3 --version

set -e

echo "🚀 Mac System Audio Recognition Tool"
echo "====================================="
echo ""

# 获取当前目录作为项目根目录（完全通用）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 🎯 关键：优先使用 Homebrew 的 Python（通常是新版本）
if [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_CMD="/opt/homebrew/bin/python3"
elif [ -x "/usr/local/bin/python3" ]; then
    PYTHON_CMD="/usr/local/bin/python3"
else
    PYTHON_CMD="python3"
fi

# 检查 Python 版本
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1,2)

echo "🐍 Using Python: $PYTHON_CMD"
echo "   Version: $PYTHON_VERSION"

# 检查 Python 版本是否 >= 3.9
if [ "$(printf '%s\n' "3.9" "$MAJOR_MINOR" | sort -V | head -n1)" != "3.9" ]; then
    echo ""
    echo "❌ Error: Python $PYTHON_VERSION is too old!"
    echo "   This project requires Python 3.9 or higher."
    echo ""
    echo "   Solutions:"
    echo "   1. Install via Homebrew: brew install python@3.12"
    echo "   2. Then run: /opt/homebrew/bin/python3 --version"
    echo "   3. Update ~/.zshrc or ~/.bash_profile to use the new Python"
    echo ""
    exit 1
fi

echo "   ✅ Python version check passed!"
echo ""

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
        echo "🆕 Creating new virtual environment with $PYTHON_CMD..."
        $PYTHON_CMD -m venv venv
        
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

# 根据 Python 版本选择合适的 numpy/scipy/numba 组合
if [ "$(printf '%s\n' "3.9" "$MAJOR_MINOR" | sort -V | head -n1)" = "3.9" ]; then
    # Python 3.9+ (推荐配置)
    echo "   → Using Python 3.9+ optimized stack:"
    echo "      numpy==1.26.4, scipy==1.12.0, numba==0.59.1"
    NUMBA_VERSION="0.59.1"
    NUMPY_VERSION="1.26.4"
    SCIPY_VERSION="1.12.0"
else
    # Python 3.8 (降级配置)
    echo "   → Using Python 3.8 compatible stack:"
    echo "      numpy==1.24.4, scipy==1.10.0, numba==0.57.1"
    NUMBA_VERSION="0.57.1"
    NUMPY_VERSION="1.24.4"
    SCIPY_VERSION="1.10.0"
fi

echo ""
echo "This may take a few minutes (downloading PyTorch ~800MB)..."
echo "Please wait..."
echo ""

pip install \
    torch==2.2.2 \
    torchaudio==2.2.2 \
    --index-url https://download.pytorch.org/whl/cpu \
    --only-binary=:all: \
    --quiet || {
    echo "⚠️ Fallback: Installing torch from normal source..."
    pip install torch==2.2.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
}

# 从 PyPI 安装 numpy/scipy/numba（不在 torch 仓库）
echo "   → Installing NumPy stack..."
pip install \
    numpy==$NUMPY_VERSION \
    scipy==$SCIPY_VERSION \
    numba==$NUMBA_VERSION \
    --only-binary=:all: \
    --quiet || {
    echo "⚠️ Fallback: Installing without --only-binary..."
    pip install numpy==$NUMPY_VERSION scipy==$SCIPY_VERSION numba==$NUMBA_VERSION
}

pip install \
    funasr==1.1.9 \
    flask>=2.0.0 \
    sounddevice>=0.4.6 \
    pydub>=0.25.0 \
    librosa>=0.10.0 \
    modelscope \
    omegaconf \
    transformers \
    tensorboardX \
    torch-complex \
    hydra-core \
    kaldiio \
    jaconv \
    jamo \
    editdistance \
    sentencepiece \
    jieba \
    pytorch-wpe \
    --quiet

# 额外显式安装关键间接依赖（确保完整性）
echo "   → Installing additional dependencies..."
pip install \
    decorator \
    joblib \
    msgpack \
    pooch \
    lazy_loader \
    platformdirs \
    narwhals \
    threadpoolctl \
    audioread \
    soxr \
    --quiet

echo ""
echo "✅ All dependencies installed successfully!"
echo ""
echo "Starting Web Server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# 保存 PID 到文件（供 stop.sh 使用）
echo $$ > "$PROJECT_ROOT/.asr.pid"

# 启动服务（使用当前激活环境的 python3，确保与 pip install 一致）
exec python3 app.py
