#!/usr/bin/env python3
"""
FunASR 音频识别核心模块
提供 ASREngine 类用于流式识别系统音频
"""

import os
import sys
import time
import threading
import numpy as np
import sounddevice as sd
from datetime import datetime
from pathlib import Path
from queue import Queue

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"

# 确保输出目录存在
TRANSCRIPTS_DIR.mkdir(exist_ok=True)


class ASREngine:
    """FunASR 音频识别引擎"""
    
    def __init__(self, log_callback=None):
        """
        初始化 ASR 引擎
        
        Args:
            log_callback: 日志回调函数 (msg, level)，level 可选值: info/success/warning/error
        """
        self.log_callback = log_callback or (lambda m, l: print(f"[{l}] {m}"))
        
        self.model = None
        self.is_loaded = False
        self.running = False
        self.audio_buffer = []
        self.sample_rate = 16000
        self.buffer_duration = 10.0  # 10 秒滑动窗口
        self.volume_threshold = 0.005  # 音量阈值（降低以适应内置麦克风的低音量）
        
        self.stream = None
        self.queue = Queue()
    
    def log(self, msg, level="info"):
        """输出日志"""
        try:
            self.log_callback(msg, level)
        except:
            print(f"[{level}] {msg}")
    
    def load_model(self):
        """
        加载 FunASR 模型（阻塞操作）
        
        Returns:
            bool: 是否成功加载
        """
        try:
            from funasr import AutoModel
            
            self.log("正在初始化 FunASR...", "info")
            self.log("加载 paraformer-zh 模型（从缓存）...", "info")
            
            # 在 CPU 上加载，不启用 VAD 和标点生成
            # disable_update=True: 禁用版本检查（加快速度）
            self.model = AutoModel(
                model="paraformer-zh",
                device="cpu",
                vad_model=None,  # 禁用 VAD
                punc_model=None,   # 禁用标点
                disable_update=True  # ⭐ 禁用版本检查
            )
            
            self.is_loaded = True
            self.log("✅ 模型加载完成！", "success")
            return True
            
        except Exception as e:
            self.log(f"❌ 模型加载失败: {e}", "error")
            import traceback
            traceback.print_exc()
            return False
    
    def start_recognition(self, output_file=None, transcript_callback=None, blocking=False):
        """
        开始音频识别
        
        Args:
            output_file: 输出文件路径（如 None 则自动生成）
            transcript_callback: 转录结果回调函数(text_line)
        
        Returns:
            str: 输出文件路径
        """
        if not self.is_loaded:
            raise RuntimeError("模型未加载，请先调用 load_model()")
        
        # 生成输出文件路径
        if output_file is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
            output_file = TRANSCRIPTS_DIR / f"{timestamp}.txt"
        else:
            output_file = Path(output_file)
        
        self.output_file = output_file
        self.transcript_callback = transcript_callback
        self.running = True
        self.audio_buffer = []
        
        # 创建文件并写入头部
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 识别开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 输出文件：{output_file}\n")
            
            # 记录设备信息
            try:
                device_info = sd.query_devices(sd.default.device[0])
                f.write(f"# 音频设备：{device_info['name']}\n")
            except:
                f.write("# 音频设备：default\n")
        
        self.log(f"🎤 开始录制：{output_file.name}", "info")
        
        # 启动音频流
        try:
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=self._audio_callback
            )
            self.stream.start()
            
            if blocking:
                # 阻塞模式：直接在当前线程运行识别循环
                self._recognition_loop()
                return None
            else:
                # 非阻塞模式：启动后台线程
                thread = threading.Thread(target=self._recognition_loop, daemon=True)
                thread.start()
                return str(output_file)
            
        except Exception as e:
            self.log(f"❌ 启动音频流失败: {e}", "error")
            self.running = False
            raise
    
    def _audio_callback(self, indata, frames, time_info, status):
        """音频流回调"""
        if status:
            self.log(f"音频状态：{status}", "warning")
        if self.running:
            self.queue.put(indata.copy())
    
    def _recognition_loop(self):
        """识别主循环（后台线程）"""
        silence_count = 0
        
        while self.running:
            try:
                # 获取音频块
                try:
                    audio_chunk = self.queue.get(timeout=1.0)
                    self.audio_buffer.append(audio_chunk)
                except:
                    continue
                
                # 检查缓冲区大小
                total_samples = sum(len(chunk) for chunk in self.audio_buffer)
                if total_samples < self.sample_rate * self.buffer_duration:
                    continue
                
                # 合并音频
                audio_data = np.vstack(self.audio_buffer)
                if audio_data.ndim > 1:
                    audio_data = audio_data.mean(axis=1)
                
                # 清空缓冲区
                self.audio_buffer = []
                
                # 音量检测
                rms = np.sqrt(np.mean(audio_data ** 2))
                print(f"[DEBUG] RMS={rms:.4f}, threshold={self.volume_threshold}", flush=True)
                
                if rms < self.volume_threshold:
                    silence_count += 1
                    if silence_count % 5 == 0:
                        print(f"[DEBUG] 静音跳过 (连续 {silence_count} 次)", flush=True)
                    continue
                
                print(f"[DEBUG] 音量正常，开始识别...", flush=True)
                silence_count = 0
                
                # 识别
                try:
                    audio_np = np.array(audio_data.flatten(), dtype=np.float32)
                    result = self.model.generate(input=audio_np)
                    
                    if result and len(result) > 0:
                        if isinstance(result[0], dict):
                            text = result[0].get('text', '')
                        elif isinstance(result[0], str):
                            text = result[0]
                        else:
                            text = str(result[0])
                        
                        if text:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            line = f"[{timestamp}] {text}"
                            
                            # 写入文件
                            with open(self.output_file, 'a', encoding='utf-8') as f:
                                f.write(line + "\n")
                                f.flush()
                            
                            print(f"[RESULT] {line}", flush=True)
                            
                            # 回调
                            if self.transcript_callback:
                                self.transcript_callback(line)
                            
                except Exception as e:
                    self.log(f"识别错误: {e}", "error")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                # self.log(f"循环错误: {e}", "error")
                time.sleep(0.1)
    
    def stop_recognition(self, wait=True):
        """停止识别
        
        Args:
            wait: 是否等待最后一次识别完成（默认 True）
        """
        self.log("⏹️ 正在停止识别...", "info")
        self.running = False
        
        if wait:
            self.log("⏳ 等待最后一次识别完成...", "info")
            time.sleep(2)  # 等待 2 秒让当前识别完成
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # 写入结束标记
        if hasattr(self, 'output_file'):
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n# 识别结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.log("✅ 识别已停止", "success")
    
    def list_devices(self):
        """列出音频设备"""
        devices = sd.query_devices()
        self.log("\n可用的输入设备:", "info")
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                default_marker = " [默认]" if i == sd.default.device[0] else ""
                self.log(f"  [{i}] {dev['name']}{default_marker}", "info")
        return devices
