#!/usr/bin/env python3
"""
RMS 音量测试工具
用于检测小音量视频的实际 RMS 值，帮助校准音量阈值

使用方法:
1. 启动此脚本
2. 播放小音量视频（如 B 站视频）
3. 观察实时 RMS 值
4. 按 Ctrl+C 停止
"""

import numpy as np
import sounddevice as sd
import time
import sys

# 配置
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 10  # 测试时长（秒）
WINDOW_SIZE = 0.5  # 每次检测的窗口大小（秒）

print("=" * 60)
print("🎤 RMS 音量测试工具")
print("=" * 60)
print(f"采样率：{SAMPLE_RATE} Hz")
print(f"声道：{CHANNELS} (单声道)")
print(f"测试时长：{DURATION} 秒")
print(f"窗口大小：{WINDOW_SIZE} 秒")
print("=" * 60)
print("")
print("📋 操作步骤:")
print("1. 播放小音量视频（如 B 站视频）")
print("2. 观察下方的实时 RMS 值")
print("3. 记录最小值、最大值和平均值")
print("4. 按 Ctrl+C 可随时停止")
print("")
print("⏱️  开始测试...")
print("-" * 60)

# 统计数据
rms_values = []
min_rms = float('inf')
max_rms = 0
start_time = time.time()

def audio_callback(indata, frames, time_info, status):
    """音频回调函数"""
    global min_rms, max_rms, rms_values
    
    # 转换为单声道
    if indata.shape[1] > 1:
        audio_data = indata.mean(axis=1)
    else:
        audio_data = indata.flatten()
    
    # 计算 RMS
    rms = np.sqrt(np.mean(audio_data ** 2))
    rms_values.append(rms)
    
    # 更新极值
    min_rms = min(min_rms, rms)
    max_rms = max(max_rms, rms)
    
    # 实时显示
    elapsed = time.time() - start_time
    if elapsed < DURATION:
        print(f"⏱️ {elapsed:5.1f}s | RMS: {rms:.6f} | 当前：{rms:.4f} | 最小：{min_rms:.4f} | 最大：{max_rms:.4f}", 
              end='\r', flush=True)

try:
    # 启动音频流
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * WINDOW_SIZE)
    ):
        # 等待指定时长
        while time.time() - start_time < DURATION:
            time.sleep(0.1)
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
        # 统计分析
        if rms_values:
            avg_rms = np.mean(rms_values)
            std_rms = np.std(rms_values)
            p50 = np.percentile(rms_values, 50)
            p90 = np.percentile(rms_values, 90)
            p95 = np.percentile(rms_values, 95)
            
            print(f"📊 统计结果:")
            print(f"  最小值 (Min):  {min_rms:.6f}")
            print(f"  最大值 (Max):  {max_rms:.6f}")
            print(f"  平均值 (Avg):  {avg_rms:.6f}")
            print(f"  标准差 (Std):  {std_rms:.6f}")
            print("")
            print(f"  中位数 (P50):  {p50:.6f}")
            print(f"  90% 分位 (P90): {p90:.6f}")
            print(f"  95% 分位 (P95): {p95:.6f}")
            print("")
            print("💡 建议阈值设置:")
            print(f"  保守方案：threshold = {min_rms * 0.5:.6f} (最小值的 50%)")
            print(f"  平衡方案：threshold = {p50 * 0.3:.6f} (中位数的 30%)")
            print(f"  激进方案：threshold = {avg_rms * 0.2:.6f} (平均值的 20%)")
            print("")
            print("📝 下一步:")
            print("  1. 将建议的阈值复制到 asr_core.py 的 volume_threshold")
            print("  2. 或者等待动态阈值功能实现")
            print("=" * 60)
        
except KeyboardInterrupt:
    print("\n\n⚠️  用户中断测试")
    if rms_values:
        avg_rms = np.mean(rms_values)
        print(f"当前 RMS 平均值：{avg_rms:.6f}")
        print(f"最小值：{min_rms:.6f}")
        print(f"最大值：{max_rms:.6f}")
        
except Exception as e:
    print(f"\n❌ 错误：{e}")
    print("")
    print("可能的原因:")
    print("  1. 没有可用的麦克风设备")
    print("  2. BlackHole 未正确配置")
    print("  3. 系统音频权限未开启")
    print("")
    print("解决方法:")
    print("  1. 检查 系统偏好设置 → 安全性与隐私 → 麦克风")
    print("  2. 确认已创建「多输出设备」(BlackHole 2ch + 内建输出)")
    print("  3. 运行以下命令查看可用设备:")
    print("     python3 -c \"import sounddevice as sd; print(sd.query_devices())\"")
    sys.exit(1)
