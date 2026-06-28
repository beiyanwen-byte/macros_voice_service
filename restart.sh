#!/bin/bash
# 重启 ASR 服务脚本

cd /Users/tanyanwen/asr_project

# 停止旧进程
pkill -f "asr_core" 2>/dev/null
sleep 1

echo "正在启动新服务..."
python3 asr.py start
