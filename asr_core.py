#!/usr/bin/env python3
"""
FunASR 音频识别核心模块
捕获系统音频并实时识别，保存结果到文件
"""

import os
import sys
import time
import signal
import threading
import numpy as np
import sounddevice as sd
from datetime import datetime
from pathlib import Path
from queue import Queue

# 全局标志
running = True
audio_queue = Queue()


def signal_handler(signum, frame):
    """处理停止信号"""
    global running
    running = False
    print("\n收到停止信号，正在关闭...")


def list_audio_devices():
    """列出可用的音频输入设备"""
    devices = sd.query_devices()
    print("\n可用的输入设备:")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  [{i}] {dev['name']} (channels: {dev['max_input_channels']})")
    return devices


def get_default_input_device():
    """获取默认输入设备，优先选择 BlackHole 虚拟声卡"""
    devices = sd.query_devices()
    
    # 优先查找 BlackHole 设备
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and 'blackhole' in dev['name'].lower():
            print(f"使用 BlackHole 虚拟声卡：{dev['name']} (ID: {i})")
            return dev, i
    
    # 其次查找多输出/聚合设备
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and any(kw in dev['name'] for kw in ['Multi', 'Aggregate', 'Meet', 'Teams']):
            print(f"使用会议设备：{dev['name']} (ID: {i})")
            return dev, i
    
    # 回退到默认设备
    try:
        default = sd.query_devices(kind='input')
        print(f"使用默认输入设备：{default['name']}")
        return default, None
    except Exception as e:
        print(f"无法获取默认输入设备：{e}")
        return None, None


def audio_callback(indata, frames, time_info, status):
    """音频流回调函数"""
    if status:
        print(f"音频状态：{status}", file=sys.stderr)
    if running:
        audio_queue.put(indata.copy())


def init_funasr():
    """初始化 FunASR 模型"""
    try:
        from funasr import AutoModel
        
        print("正在加载 FunASR paraformer-zh 模型...")
        print("(首次加载可能需要 2-3 分钟，请耐心等待)")
        
        # 不启用 VAD 和标点，避免 transformers 依赖问题
        model = AutoModel(
            model="paraformer-zh",
            device="cpu"
        )
        print("✅ 模型加载完成！")
        return model
    except Exception as e:
        print(f"❌ FunASR 初始化失败：{e}")
        return None


def recognize_audio(model, output_file):
    """持续识别音频并写入文件"""
    global running
    
    # 累积音频缓冲区（用于流式处理）
    audio_buffer = []
    buffer_duration = 10.0  # 10 秒识别一次（确保句子完整）
    sample_rate = 16000
    
    # 新增：音量阈值参数（0.0-1.0，建议 0.03-0.05）
    volume_threshold = 0.04  # 低于此值认为是静音/噪音，跳过识别
    
    # 启动时立即创建文件并写入头部
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 识别开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 输出文件：{output_file}\n")
        
        # 获取设备名称
        try:
            device_info = sd.query_devices(sd.default.device[0])
            f.write(f"# 音频设备：{device_info['name']}\n")
        except:
            f.write("# 音频设备：default\n")
    
    print("\n" + "="*50)
    print("✅ FunASR 模型已加载完成")
    print("="*50)
    print("🎤 可以录制系统声音了！")
    print("-"*50)
    print("请确保:")
    print("  1. 系统音频输出已路由到 BlackHole 虚拟声卡")
    print("  2. 播放音频即可实时识别为文字")
    print("-"*50)
    print(f"📁 识别结果将保存到：{output_file}")
    print("="*50 + "\n")
    
    # 重新打开文件用于追加
    with open(output_file, 'a', encoding='utf-8') as f:
        while running:
            try:
                # 从队列获取音频块
                try:
                    audio_chunk = audio_queue.get(timeout=1.0)
                    audio_buffer.append(audio_chunk)
                except:
                    continue
                
                # 检查是否达到识别间隔
                total_samples = sum(len(chunk) for chunk in audio_buffer)
                if total_samples < sample_rate * buffer_duration:
                    continue
                
                # 合并音频块
                audio_data = np.vstack(audio_buffer)
                
                # 转换为单声道
                if audio_data.ndim > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # 计算音频音量（RMS 值）
                rms = np.sqrt(np.mean(audio_data ** 2))
                print(f"💬 检测到音量：{rms:.4f} (阈值：{volume_threshold})", end="")
                
                # 如果音量低于阈值，跳过识别
                if rms < volume_threshold:
                    print(" → 静音/噪音，跳过本次识别\n")
                    audio_buffer = []
                    continue
                
                print(f" → 有效语音，开始识别...\n")
                audio_buffer = []
                
                # 重采样到 16kHz（如果必要）
                # 注意：实际项目中需要 proper resampling
                
                # 识别
                try:
                    # FunASR 需要 numpy 数组或特定格式
                    audio_np = np.array(audio_data.flatten(), dtype=np.float32)
                    
                    result = model.generate(input=audio_np)
                    
                    if result and len(result) > 0:
                        # 新版本返回格式可能是 dict 或 str
                        if isinstance(result[0], dict):
                            text = result[0].get('text', '')
                        elif isinstance(result[0], str):
                            text = result[0]
                        else:
                            text = str(result[0])
                        
                        if text:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            line = f"[{timestamp}] {text}\n"
                            f.write(line)
                            f.flush()
                            print(line.strip())
                except Exception as e:
                    print(f"识别错误：{e}", file=sys.stderr)
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"处理错误：{e}", file=sys.stderr)
                time.sleep(0.1)
        
        # 写入结束时间
        f.write(f"\n# 识别结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="输出文件路径")
    parser.add_argument("--device", type=int, default=None, help="音频设备 ID")
    args = parser.parse_args()
    
    # 设置信号处理
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # 列出设备（可选）
    # list_audio_devices()
    
    # 获取输入设备
    device_info, device_id = get_default_input_device()
    if device_info is None:
        print("错误：无法获取音频输入设备")
        sys.exit(1)
    
    # 如果找到了具体设备 ID，使用它
    if device_id is not None:
        args.device = device_id
    
    # 初始化 FunASR
    model = init_funasr()
    if model is None:
        print("错误：FunASR 初始化失败")
        sys.exit(1)
    
    # 启动音频流
    sample_rate = 16000
    channels = 1
    
    print(f"启动音频流：{sample_rate}Hz, {channels} 声道")
    
    with sd.InputStream(
        device=args.device,
        channels=channels,
        samplerate=sample_rate,
        callback=audio_callback
    ):
        # 开始识别
        recognize_audio(model, args.output)
    
    print("ASR 服务已关闭")


if __name__ == "__main__":
    main()
