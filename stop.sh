#!/bin/bash
# ASR Web Service Stopper
# 
# 优雅停止运行中的 ASR Web 服务
# 支持通过端口查找进程或 PID 文件
#
# Usage:
#   ./stop.sh                   # 停止当前项目的服务
#   ./stop.sh <port>            # 停止指定端口的服务
#   ./stop.sh <pid>             # 停止指定 PID 的进程
#
# Examples:
#   ./stop.sh                   # 停止 5000 端口的服务
#   ./stop.sh 8080              # 停止 8080 端口的服务
#   ./stop.sh 12345             # 停止 PID 为 12345 的进程

set -e

echo "🛑 Stopping ASR Web Service..."
echo ""

# 获取项目根目录（与 start.sh 保持一致）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认端口
DEFAULT_PORT=5000
PORT="${1:-$DEFAULT_PORT}"

# 方法 1: 检查 PID 文件
PID_FILE="$PROJECT_ROOT/.asr.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Found running process (PID: $PID) via PID file"
        kill -TERM $PID
        
        # 等待进程退出（最多 10 秒）
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "✅ Process stopped gracefully"
                rm -f "$PID_FILE"
                exit 0
            fi
            sleep 1
        done
        
        # 强制杀死
        echo "⚠️  Process did not stop, forcing kill..."
        kill -KILL $PID
        rm -f "$PID_FILE"
        echo "✅ Process forcefully killed"
        exit 0
    else
        echo "⚠️  PID file exists but process is not running"
        rm -f "$PID_FILE"
    fi
fi

# 方法 2: 通过端口查找进程
echo "Searching for process on port $PORT..."
PID=$(lsof -t -i:$PORT 2>/dev/null || true)

if [ -n "$PID" ]; then
    echo "Found running process (PID: $PID) on port $PORT"
    kill -TERM $PID
    
    # 等待进程退出（最多 10 秒）
    for i in {1..10}; do
        if ! lsof -i:$PORT > /dev/null 2>&1; then
            echo "✅ Port $PORT released"
            exit 0
        fi
        sleep 1
    done
    
    # 强制杀死
    echo "⚠️  Process did not stop, forcing kill..."
    kill -KILL $PID
    echo "✅ Forcefully killed process on port $PORT"
else
    echo "❌ No process found on port $PORT"
    echo ""
    echo "To check what's running:"
    echo "  lsof -i :$PORT"
    echo ""
    echo "Or find all Python processes related to ASR:"
    echo "  ps aux | grep 'python.*app.py' | grep -v grep"
fi
