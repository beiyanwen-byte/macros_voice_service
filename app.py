#!/usr/bin/env python3
"""
ASR Web GUI - 替代 Tkinter 的稳定方案
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request

# Import ASREngine from core module
from asr_core import ASREngine

PROJECT_ROOT = Path(__file__).parent
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

# 全局状态
state = {
    'model_loaded': False,
    'is_recording': False,
    'engine': None,
    'process': None,
    'log_buffer': [],
    'output_file': None
}

lock = threading.Lock()

def add_log(msg, level="INFO"):
    """添加日志到缓冲区"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    with lock:
        state['log_buffer'].append({
            'time': timestamp,
            'level': level,
            'msg': msg
        })
        # 只保留最近 100 条
        if len(state['log_buffer']) > 100:
            state['log_buffer'] = state['log_buffer'][-100:]

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASR 语音识别 (Web)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .status-bar { display: flex; justify-content: space-between; padding: 10px 20px; background: #f8f9fa; border-bottom: 1px solid #eee; font-size: 14px; }
        .status-indicator { padding: 5px 12px; border-radius: 4px; font-weight: 500; }
        .status-ready { background: #d4edda; color: #155724; }
        .status-loading { background: #fff3cd; color: #856404; }
        .status-recording { background: #f8d7da; color: #721c24; }
        .controls { padding: 20px; display: flex; gap: 10px; justify-content: center; }
        .btn { padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; transition: all 0.2s; font-weight: 500; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-load { background: #6c757d; color: white; }
        .btn-load:hover:not(:disabled) { background: #5a6268; }
        .btn-start { background: #28a745; color: white; }
        .btn-start:hover:not(:disabled) { background: #218838; }
        .btn-stop { background: #dc3545; color: white; }
        .btn-stop:hover:not(:disabled) { background: #c82333; }
        .log-area { padding: 20px; background: #1e1e1e; height: 400px; overflow-y: auto; font-family: "Courier New", monospace; font-size: 13px; line-height: 1.6; }
        .log-entry { margin-bottom: 4px; }
        .log-time { color: #888; margin-right: 8px; }
        .log-info { color: #fff; }
        .log-success { color: #4caf50; font-weight: bold; }
        .log-warning { color: #ff9800; }
        .log-error { color: #f44336; }
        .footer { padding: 15px; text-align: center; color: #666; font-size: 12px; background: #f8f9fa; border-top: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 ASR 语音识别</h1>
            <p>FunASR paraformer-zh | macOS 系统音频转文字</p>
        </div>
        
        <div class="status-bar">
            <span id="status-text">状态：就绪</span>
            <span id="recording-time"></span>
        </div>
        
        <div class="controls">
            <button id="btn-load" class="btn btn-load" onclick="loadModel()">🔽 加载模型</button>
            <button id="btn-start" class="btn btn-start" onclick="startRecording()" disabled>▶️ 开始识别</button>
            <button id="btn-stop" class="btn btn-stop" onclick="stopRecording()" disabled>⏹️ 停止</button>
        </div>
        
        <div class="log-area" id="log-container">
            <!-- 日志将在这里显示 -->
        </div>
        
        <div class="footer">
            输出目录：<code id="output-dir"></code> | 
            最后更新：<span id="last-update">-</span>
        </div>
    </div>

    <script>
        let recordingStartTime = null;
        let timerInterval = null;

        function updateStatus(text, className) {
            const el = document.getElementById('status-text');
            el.textContent = '状态：' + text;
            el.className = 'status-indicator ' + className;
        }

        function addLog(time, level, msg) {
            const container = document.getElementById('log-container');
            const entry = document.createElement('div');
            entry.className = 'log-entry log-' + level.toLowerCase();
            entry.innerHTML = '<span class="log-time">[' + time + ']</span>' + msg;
            container.appendChild(entry);
            container.scrollTop = container.scrollHeight;
            
            // 限制显示条数
            while (container.children.length > 100) {
                container.removeChild(container.firstChild);
            }
            
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }

        async function loadModel() {
            document.getElementById('btn-load').disabled = true;
            updateStatus('加载中...', 'status-loading');
            
            try {
                const res = await fetch('/api/load');
                const data = await res.json();
                
                if (data.success) {
                    updateStatus('已加载', 'status-ready');
                    document.getElementById('btn-start').disabled = false;
                    addLog(data.time, 'SUCCESS', '✅ 模型加载完成！');
                } else {
                    updateStatus('加载失败', 'status-error');
                    addLog(data.time, 'ERROR', '❌ ' + data.message);
                }
            } catch (err) {
                addLog(new Date().toLocaleTimeString(), 'ERROR', '❌ 网络错误：' + err.message);
            } finally {
                document.getElementById('btn-load').disabled = false;
            }
        }

        async function startRecording() {
            // 不本地置灰，由轮询自动更新
            try {
                const res = await fetch('/api/start', { method: 'POST' });
                const data = await res.json();
                
                // 显示提示
                if (data.success) {
                    addLog(data.time, 'SUCCESS', '✅ ' + data.message);
                } else {
                    addLog(data.time, 'ERROR', '❌ ' + data.message);
                }
                // 按钮状态由 pollStatusAndLogs 自动更新
            } catch (err) {
                addLog(new Date().toLocaleTimeString(), 'ERROR', '❌ 网络错误：' + err.message);
            }
        }

        async function stopRecording() {
            try {
                const res = await fetch('/api/stop', { method: 'POST' });
                const data = await res.json();
                
                // 显示提示
                if (data.success) {
                    addLog(data.time, 'SUCCESS', '✅ ' + data.message);
                } else {
                    addLog(data.time, 'ERROR', '❌ ' + data.message);
                }
                // 按钮状态由 pollStatusAndLogs 自动更新
            } catch (err) {
                addLog(new Date().toLocaleTimeString(), 'ERROR', '❌ 网络错误：' + err.message);
            }
        }

        // 根据后端状态更新按钮
        function updateButtons(state) {
            const btnLoad = document.getElementById('btn-load');
            const btnStart = document.getElementById('btn-start');
            const btnStop = document.getElementById('btn-stop');
            
            // 正在录制 → 禁用加载和开始，启用停止
            if (state.is_recording) {
                btnLoad.disabled = true;
                btnStart.disabled = true;
                btnStop.disabled = false;
                updateStatus('正在录制', 'status-recording');
                
                // 启动计时器（如果还没启动）
                if (!timerInterval && recordingStartTime === null) {
                    recordingStartTime = Date.now();
                    timerInterval = setInterval(() => {
                        const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
                        const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
                        const secs = (elapsed % 60).toString().padStart(2, '0');
                        document.getElementById('recording-time').textContent = '⏱️ ' + mins + ':' + secs;
                    }, 1000);
                }
            } else {
                // 未录制 → 启用加载和开始，禁用停止
                btnLoad.disabled = false;
                btnStart.disabled = !state.model_loaded;
                btnStop.disabled = true;
                
                // 清除计时器
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                    recordingStartTime = null;
                    document.getElementById('recording-time').textContent = '';
                }
                
                // 根据模型状态更新提示
                if (state.model_loaded) {
                    updateStatus('已加载', 'status-ready');
                } else {
                    updateStatus('未加载', 'status-loading');
                }
            }
        }

        // 轮询状态和日志
        async function pollStatusAndLogs() {
            try {
                // 1. 先获取状态
                const statusRes = await fetch('/api/status');
                const statusData = await statusRes.json();
                
                // 检测录制状态变化（用于清理日志缓存）
                const wasRecording = document.body.dataset.recording === 'true';
                document.body.dataset.recording = statusData.is_recording;
                
                // 如果从录制状态退出，清除日志去重缓存（防止 ID 复用导致的显示问题）
                if (wasRecording && !statusData.is_recording) {
                    console.log('Recording stopped, clearing log cache...');
                    sessionStorage.removeItem('asr_seen_logs');
                }
                
                updateButtons(statusData);
                
                // 2. 再获取日志
                const logsRes = await fetch('/api/logs');
                const logsData = await logsRes.json();
                
                if (logsData.logs && logsData.logs.length > 0) {
                    // 使用 sessionStorage 存储已显示的日志 key（时间戳 + 内容）
                    const seenLogs = new Set(JSON.parse(sessionStorage.getItem('asr_seen_logs') || '[]'));
                    let hasNewLogs = false;
                    
                    for (const log of logsData.logs) {
                        // 使用"时间戳 + 消息内容"作为唯一标识
                        const logKey = `${log.time}|${log.level}|${log.msg}`;
                        
                        if (!seenLogs.has(logKey)) {
                            seenLogs.add(logKey);
                            addLog(log.time, log.level, log.msg);
                            hasNewLogs = true;
                        }
                    }
                    
                    // 定期清理旧记录（只保留最近 500 条）
                    if (hasNewLogs && seenLogs.size > 500) {
                        const arr = Array.from(seenLogs).slice(-500);
                        seenLogs.clear();
                        arr.forEach(k => seenLogs.add(k));
                    }
                    
                    // 保存回 sessionStorage
                    if (seenLogs.size > 0) {
                        sessionStorage.setItem('asr_seen_logs', JSON.stringify(Array.from(seenLogs)));
                    }
                }
            } catch (err) {
                console.error('Poll error:', err);
            }
        }

        // 初始化
        document.getElementById('output-dir').textContent = '/Users/tanyanwen/asr_project/transcripts';
        
        // 立即执行一次，然后每 500ms 轮询
        pollStatusAndLogs();
        setInterval(pollStatusAndLogs, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    return jsonify({
        'model_loaded': state['model_loaded'],
        'is_recording': state['is_recording']
    })

@app.route('/api/load')
def api_load():
    if state['model_loaded']:
        return jsonify({'success': True, 'message': '模型已加载', 'time': datetime.now().strftime('%H:%M:%S')})
    
    def do_load():
        try:
            from asr_core import ASREngine
            
            def log_cb(msg, level):
                add_log(f"[ASR] {msg}", level.upper())
            
            with lock:
                state['engine'] = ASREngine(log_callback=log_cb)
            
            if state['engine'].load_model():
                with lock:
                    state['model_loaded'] = True
                add_log("✅ 模型加载完成！", "SUCCESS")
            else:
                add_log("❌ 模型加载失败", "ERROR")
        except Exception as e:
            add_log(f"❌ 异常：{e}", "ERROR")
    
    thread = threading.Thread(target=do_load, daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'message': '正在加载...', 'time': datetime.now().strftime('%H:%M:%S')})

@app.route('/api/start', methods=['POST'])
def api_start():
    if not state['model_loaded']:
        return jsonify({'success': False, 'message': '请先加载模型', 'time': datetime.now().strftime('%H:%M:%S')})
    
    if state['is_recording']:
        return jsonify({'success': False, 'message': '已在录制中', 'time': datetime.now().strftime('%H:%M:%S')})
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    output_file = str(TRANSCRIPTS_DIR / f"{timestamp}.txt")
    
    def do_record():
        """后台线程：直接调用引擎进行识别"""
        try:
            engine = state['engine']
            
            # 定义识别结果回调
            def on_transcript(line):
                add_log(f"[RESULT] {line}", "INFO")
            
            # 开始识别（阻塞调用，在后台线程运行）
            engine.start_recognition(output_file=output_file, transcript_callback=on_transcript)
            
            # 等待识别完成（engine.running 为 False 时结束）
            while state['is_recording']:
                time.sleep(0.5)
            
            add_log("✅ 识别结束", "SUCCESS")
            
        except Exception as e:
            add_log(f"❌ 识别异常：{e}", "ERROR")
            with lock:
                state['is_recording'] = False
    
    # 启动后台线程
    with lock:
        state['is_recording'] = True
        state['output_file'] = output_file
    
    thread = threading.Thread(target=do_record, daemon=True)
    thread.start()
    
    add_log(f"🎤 开始录制：{output_file}", "SUCCESS")
    
    return jsonify({'success': True, 'message': '开始录制', 'time': datetime.now().strftime('%H:%M:%S')})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    if not state['is_recording']:
        return jsonify({'success': False, 'message': '未在录制', 'time': datetime.now().strftime('%H:%M:%S')})
    
    try:
        engine = state['engine']
        
        # 优雅停止（等待最后一次识别完成）
        add_log("⏳ 正在停止识别...", "INFO")
        engine.stop_recognition(wait=True)
        
        add_log("✅ 已停止", "SUCCESS")
        
    except Exception as e:
        add_log(f"❌ 停止异常：{e}", "ERROR")
    finally:
        with lock:
            state['is_recording'] = False
    
    return jsonify({'success': True, 'message': '已停止', 'time': datetime.now().strftime('%H:%M:%S')})

@app.route('/api/logs')
def api_logs():
    with lock:
        logs = [{'id': i+1, **log} for i, log in enumerate(state['log_buffer'])]
    return jsonify({'logs': logs})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ASR Web GUI 启动中...")
    print("=" * 60)
    print(f"访问地址：http://localhost:5000")
    print(f"输出目录：{TRANSCRIPTS_DIR}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
