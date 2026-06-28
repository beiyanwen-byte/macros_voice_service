#!/usr/bin/env python3
"""
Mac 系统音频识别命令行工具
使用 FunASR paraformer-zh 模型进行语音识别
"""

import os
import sys
import time
import signal
import argparse
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
PID_FILE = PROJECT_ROOT / ".asr_pid"
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"


def get_pid():
    """读取 PID 文件"""
    if not PID_FILE.exists():
        return None
    try:
        with open(PID_FILE, 'r') as f:
            return int(f.read().strip())
    except (ValueError, IOError):
        return None


def is_process_running(pid):
    """检查进程是否运行"""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def stop_asr():
    """停止 ASR 服务"""
    pid = get_pid()
    if pid is None:
        print("ASR 服务未运行（无 PID 文件）")
        return
    
    if not is_process_running(pid):
        print("ASR 服务未运行（进程不存在）")
        os.remove(PID_FILE)
        return
    
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(0.5)
        if is_process_running(pid):
            os.kill(pid, signal.SIGKILL)
        os.remove(PID_FILE)
        print(f"ASR 服务已停止（PID: {pid}）")
    except Exception as e:
        print(f"停止失败：{e}")


def status_asr():
    """查看 ASR 服务状态"""
    pid = get_pid()
    if pid is None:
        print("ASR 服务：未运行")
        return
    
    if is_process_running(pid):
        print(f"ASR 服务：运行中（PID: {pid}）")
    else:
        print("ASR 服务：异常（PID 文件存在但进程不存在）")
        os.remove(PID_FILE)


def list_devices():
    """列出可用的音频输入设备"""
    import sounddevice as sd
    devices = sd.query_devices()
    print("\n可用的输入设备:")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  [{i}] {dev['name']} (channels: {dev['max_input_channels']})")


# 使用 QwenPaw 虚拟环境中的 Python（已配置好所有依赖）
PYTHON_CMD = "/Users/tanyanwen/.qwenpaw/venv/bin/python3"

def start_asr():
    """启动 ASR 服务（前台模式，直接显示日志）"""
    # 确保 transcripts 目录存在
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    
    import subprocess
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_file = TRANSCRIPTS_DIR / f"{timestamp}.txt"
    
    cmd = [
        PYTHON_CMD,
        str(PROJECT_ROOT / "asr_core.py"),
        "--output", str(output_file)
    ]
    
    print(f"\n🚀 正在启动 ASR 服务...")
    print(f"📁 识别结果将保存到：{output_file}")
    print("-" * 60 + "\n")
    
    # 强制刷新输出
    sys.stdout.flush()
    sys.stderr.flush()
    
    # 使用当前进程的 env 和输出流
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    process = subprocess.run(cmd, env=env, cwd=str(PROJECT_ROOT))
    
    print("\n" + "=" * 60)
    print("ASR 服务已停止")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Mac 系统音频识别工具")
    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "devices"],
        help="命令：start（启动）| stop（停止）| status（状态）| devices（设备列表）"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_asr()
    elif args.command == "stop":
        stop_asr()
    elif args.command == "status":
        status_asr()
    elif args.command == "devices":
        list_devices()


if __name__ == "__main__":
    main()
