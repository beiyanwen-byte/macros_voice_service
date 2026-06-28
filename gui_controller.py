#!/usr/bin/env python3
"""
Mac 系统音频识别工具 - 图形界面版本
基于 tkinter 构建简洁的控制面板
支持双标签页：实时日志 + 实时转录内容
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import os
import sys
import signal
import threading
import time
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
PYTHON_CMD = "/Users/tanyanwen/.qwenpaw/venv/bin/python3"
PID_FILE = PROJECT_ROOT / ".asr_pid"
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"


class ASRControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Mac 系统音频识别")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        # 进程管理
        self.process = None
        self.is_running = False
        self.model_loaded = False
        
        # 当前输出文件
        self.current_output_file = None
        
        # 刷新定时器
        self.refresh_timer = None
        
        # 创建界面
        self.create_widgets()
        
        # 检查后台进程
        self.check_background_process()
        
    def create_widgets(self):
        """创建所有界面组件"""
        
        # 标题区域
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            header_frame, 
            text="🎤 Mac 系统音频识别",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="FunASR paraformer-zh | 10 秒滑动窗口 | 支持 B 站视频/会议录音等系统声音",
            font=("Helvetica", 9),
            foreground="gray"
        )
        subtitle_label.pack()
        
        # 控制区域
        control_frame = ttk.LabelFrame(self.root, text="🔘 控制面板", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="⏸️ 已停止")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, font=("Helvetica", 12))
        status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # 启动按钮
        self.start_btn = ttk.Button(
            control_frame, 
            text="▶️ 开始识别",
            command=self.start_asr,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮
        self.stop_btn = ttk.Button(
            control_frame, 
            text="⏹️ 停止识别",
            command=self.stop_asr,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            control_frame,
            text="🔄 刷新状态",
            command=self.refresh_status,
            width=12
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # 文件信息区域
        info_frame = ttk.LabelFrame(self.root, text="📁 文件信息", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text="输出文件：").pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar(value="无")
        file_path_label = ttk.Label(
            info_frame, 
            textvariable=self.file_path_var,
            font=("Courier", 9),
            foreground="blue",
            wraplength=650,
            justify=tk.LEFT
        )
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 标签页容器
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: 实时日志
        self.tab_log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_log_frame, text="📝 实时日志")
        
        self.log_text = scrolledtext.ScrolledText(
            self.tab_log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            height=25,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: 实时转录内容
        self.tab_transcript_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_transcript_frame, text="📄 实时转录")
        
        self.transcript_text = scrolledtext.ScrolledText(
            self.tab_transcript_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            height=25,
            state=tk.DISABLED
        )
        self.transcript_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 底部进度条区域
        progress_frame = ttk.Frame(self.root, padding="5")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(progress_frame, text="进度：").pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=600
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 配置文本颜色标签
        self.tag_config()
        
    def tag_config(self):
        """配置日志文本样式"""
        self.log_text.tag_configure("info", foreground="black")
        self.log_text.tag_configure("success", foreground="green")
        self.log_text.tag_configure("warning", foreground="orange")
        self.log_text.tag_configure("error", foreground="red")
        
        self.transcript_text.tag_configure("normal", foreground="black")
        
    def add_log(self, message, tag="info"):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def update_transcript_file(self):
        """实时更新转录文件内容"""
        if self.current_output_file and self.current_output_file.exists():
            try:
                with open(self.current_output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.transcript_text.config(state=tk.NORMAL)
                self.transcript_text.delete(1.0, tk.END)
                self.transcript_text.insert(tk.END, content)
                self.transcript_text.see(tk.END)
                self.transcript_text.config(state=tk.DISABLED)
            except Exception as e:
                pass  # 忽略读取错误
                
    def check_background_process(self):
        """检查是否有后台进程在运行"""
        pid = self.get_pid()
        if pid and self.is_process_running(pid):
            self.is_running = True
            self.status_var.set(f"🟢 运行中 (PID: {pid})")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.add_log("检测到后台进程正在运行", "info")
            
    def get_pid(self):
        """读取 PID 文件"""
        if not PID_FILE.exists():
            return None
        try:
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError):
            return None
            
    def is_process_running(self, pid):
        """检查进程是否运行"""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
            
    def start_asr(self):
        """启动 ASR 服务"""
        if self.is_running:
            messagebox.showwarning("警告", "服务已经在运行中！")
            return
        
        TRANSCRIPTS_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_file = TRANSCRIPTS_DIR / f"{timestamp}.txt"
        
        cmd = [
            PYTHON_CMD,
            str(PROJECT_ROOT / "asr_core.py"),
            "--output", str(output_file)
        ]
        
        self.add_log("\n" + "="*50, "info")
        self.add_log("正在启动 ASR 服务...", "info")
        self.add_log(f"输出文件：{output_file}", "info")
        self.add_log("等待模型加载（首次约 2-3 分钟）...\n", "warning")
        
        self.status_var.set("⏳ 加载中...")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.file_path_var.set(str(output_file))
        self.current_output_file = output_file
        
        # 确保在 Tab 1（日志页面）
        self.notebook.select(0)
        
        try:
            # 启动子进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 更新 PID 文件
            with open(PID_FILE, 'w') as f:
                f.write(str(self.process.pid))
                
            self.add_log(f"✅ 服务已启动 (PID: {self.process.pid})", "success")
            self.is_running = True
            
            # 读取输出流
            self.read_process_output()
            
        except Exception as e:
            self.add_log(f"❌ 启动失败：{str(e)}", "error")
            self.stop_btn.config(state=tk.DISABLED)
            self.progress_bar.stop()
            
    def read_process_output(self):
        """读取进程输出"""
        if self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    line = line.strip()
                    if not line:
                        self.root.after(100, self.read_process_output)
                        return
                    
                    # 解析日志内容
                    if "可以录制系统声音了" in line or "FunASR 模型已加载完成" in line:
                        self.add_log(line, "success")
                        self.status_var.set(f"🟢 运行中 (PID: {self.process.pid})")
                        self.progress_bar.stop()
                        self.model_loaded = True
                        
                        # 切换到 Tab 2（转录内容）
                        self.root.after(1000, lambda: self.notebook.select(1))
                        
                        # 启动文件内容刷新
                        self.start_transcript_refresh()
                        
                    elif "错误" in line or "Error" in line or "Exception" in line:
                        self.add_log(line, "error")
                    elif "音量" in line:
                        self.add_log(line, "info")
                    elif "rtf_avg" in line or "|███████" in line:
                        # 进度条和性能统计，不显示
                        pass
                    else:
                        self.add_log(line, "info")
                    
                    self.root.after(100, self.read_process_output)
                else:
                    self.root.after(100, self.read_process_output)
            except Exception as e:
                self.add_log(f"读取输出错误：{str(e)}", "error")
        else:
            # 进程已结束
            if self.process:
                returncode = self.process.poll()
                self.add_log(f"\n服务已停止 (退出码：{returncode})", "info")
            self.stop_asr_internal()
            
    def start_transcript_refresh(self):
        """启动转录文件内容刷新"""
        if self.model_loaded:
            self.update_transcript_file()
            self.root.after(2000, self.start_transcript_refresh)  # 每 2 秒刷新一次
            
    def stop_asr(self):
        """停止 ASR 服务"""
        if not messagebox.askyesno("确认", "确定要停止识别服务吗？"):
            return
            
        self.add_log("\n正在停止服务...", "warning")
        self.stop_asr_internal()
        
    def stop_asr_internal(self):
        """内部停止逻辑"""
        # 终止进程
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                self.add_log("✅ 进程已优雅终止", "success")
            except:
                try:
                    self.process.kill()
                    self.add_log("✅ 进程已被强制终止", "success")
                except:
                    self.add_log("⚠️ 进程终止失败", "warning")
            finally:
                self.process = None
        
        # 清理 PID 文件
        if PID_FILE.exists():
            try:
                os.remove(PID_FILE)
            except:
                pass
                
        # 重置界面
        self.is_running = False
        self.model_loaded = False
        self.status_var.set("⏸️ 已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        # 清空转录内容
        self.transcript_text.config(state=tk.NORMAL)
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.config(state=tk.DISABLED)
        
        # 回到 Tab 1
        self.notebook.select(0)
        
    def refresh_status(self):
        """刷新状态"""
        pid = self.get_pid()
        if pid and self.is_process_running(pid):
            self.is_running = True
            self.status_var.set(f"🟢 运行中 (PID: {pid})")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.add_log("🔄 服务正在运行", "info")
        else:
            self.is_running = False
            self.status_var.set("⏸️ 已停止")
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if PID_FILE.exists():
                try:
                    os.remove(PID_FILE)
                except:
                    pass
            self.add_log("🔄 服务已停止", "info")
            
    def on_closing(self):
        """窗口关闭时处理"""
        if self.is_running:
            if messagebox.askyesno("确认", "有识别任务正在运行，确定要退出吗？"):
                self.stop_asr_internal()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    # 确保 transcripts 目录存在
    TRANSCRIPTS_DIR.mkdir(exist_ok=True)
    
    # 创建应用
    root = tk.Tk()
    app = ASRControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
