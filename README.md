# Mac 系统音频识别工具 / Mac System Audio Recognition Tool

基于 FunASR paraformer-zh 模型的 Web 语音识别服务，**将系统播放的声音实时转换为文字**。
Web-based voice recognition service using FunASR paraformer-zh model, **converting system audio to text in real-time**.

## 🎯 功能特性 / Features

- ✅ **系统内录**：支持 B 站视频、会议录音、在线课程等所有系统播放的音频
  - **System Audio Capture**: Supports all system audio including Bilibili videos, meetings, online courses
- ✅ **Web 界面**：浏览器访问 `http://localhost:5000`，支持手机远程访问
  - **Web Interface**: Access via browser at `http://localhost:5000`, works on mobile devices
- ✅ **单进程架构**：模型只加载一次，点击开始即识别（无需等待 60 秒）
  - **Single-Process Architecture**: Model loaded once, instant start (no 60s wait)
- ✅ **内存优化**：1.3GB 内存占用（相比双进程节省 50%）
  - **Memory Optimized**: Only 1.3GB RAM usage (50% less than dual-process)
- ✅ **优雅停止**：点击停止后等待最后一次识别完成再退出
  - **Graceful Stop**: Waits for last recognition to complete before exit

---

## 🚀 快速开始 / Quick Start

### 1. 启动 Web 服务 / Start Web Service

```bash
cd asr_project
python3 app.py
```

**看到提示 / See:**
```
🚀 ASR Web GUI 启动中...
============================================================
访问地址：http://localhost:5000
输出目录：<your-project-path>/transcripts
============================================================
```

### 2. 浏览器访问 / Open Browser

打开浏览器访问：**`http://localhost:5000`**

### 3. 操作步骤 / Steps

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 点击 **"🔽 加载模型"** | 首次约 60 秒，之后自动缓存 |
| 2 | 按钮变亮后点击 **"▶️ 开始识别"** | 立即开始，无需等待 |
| 3 | 播放音频（B 站/会议/播客） | 日志区实时显示识别结果 |
| 4 | 点击 **"⏹️ 停止"** | 优雅停止，自动保存文件 |

---

## 🎧 音频配置 / Audio Configuration (重要 / Important)

要识别**系统播放的声音**（而非麦克风），需配置 **BlackHole 虚拟声卡**：

### 方法一：手动配置 (一次性)

1. 打开「**音频 MIDI 设置**」 (/Applications/Utilities/Audio MIDI Setup.app)
2. 点击左下角 **+** → **创建多输出设备** / Click **+** → **Create Multi-Output Device**
3. 勾选 **BlackHole 2ch** + **内建输出** (Built-in Output)
4. 在系统声音设置中选择该多输出设备

### 方法二：使用 SoundSource (推荐)

下载安装 [SoundSource](https://rogueamoeba.com/soundsource/)：
1. 启用 BlackHole 作为多输出设备
2. 一键切换到系统内录模式

### 测试方法 / Test Method

播放 B 站视频，检查 Web 界面日志区是否有文字输出。

---

## 📁 输出文件 / Output Files

转录结果自动保存到 `transcripts/` 目录：

```
transcripts/
├── 2026-07-01_2207.txt    # 按时间戳命名 / Timestamp-based naming
├── 2026-07-01_2149.txt
└── ...
```

**文件格式示例 / Format Example:**
```txt
# 识别开始时间：2026-07-01 22:07:50
# 输出文件：asr_project/transcripts/2026-07-01_2207.txt
# 音频设备：Built-in Microphone

[22:08:06] 给自己的信息加上一道门对你要在开口之前先想一想这个话讲出去会有什么样的后果会不会让自己后悔

# 识别结束时间：2026-07-01 22:08:07
```

---

## ⚙️ Web API 文档 / Web API Reference

### 主要接口 / Main Endpoints

| 接口 | 方法 | 功能 | 返回示例 |
|------|------|------|----------|
| `/` | GET | 打开 Web 界面 | HTML 页面 |
| `/api/status` | GET | 获取当前状态 | `{"model_loaded": true, "is_recording": false}` |
| `/api/load` | GET | 加载模型 | `{"success": true, "message": "正在加载..."}` |
| `/api/start` | POST | 开始识别 | `{"success": true, "message": "开始录制"}` |
| `/api/stop` | POST | 停止识别 | `{"success": true, "message": "已停止"}` |
| `/api/logs` | GET | 获取日志 | `[{"id": 1, "time": "10:00:00", "level": "INFO", "msg": "..."}]` |

### 使用示例 / Usage Examples

#### 检查状态 / Check Status
```bash
curl http://localhost:5000/api/status
# {"is_recording": false, "model_loaded": true}
```

#### 开始识别 / Start Recording
```bash
curl -X POST http://localhost:5000/api/start
# {"success": true, "message": "开始录制", "time": "22:07:50"}
```

#### 停止识别 / Stop Recording
```bash
curl -X POST http://localhost:5000/api/stop
# {"success": true, "message": "已停止", "time": "22:08:07"}
```

---

## 🔄 架构对比 / Architecture Comparison

### 旧架构 (双进程，已废弃) vs 新架构 (单进程多线程)

| 维度 | 旧架构 ❌ | 新架构 ✅ | 改进 |
|------|----------|-----------|------|
| **模型加载** | 两次（主进程 + 子进程） | 一次（主进程） | ⬇️ 节省 60 秒 |
| **内存占用** | 2.6GB | 1.3GB | ⬇️ 减少 50% |
| **点击开始** | 等待 60 秒 | **立即启动** | ⚡ 用户体验提升 |
| **代码复杂度** | subprocess 管理 | 纯线程 | ✅ 更简洁 |
| **日志显示** | 无法实时显示 | 完整显示 | ✅ 调试友好 |

### 技术实现差异 / Technical Details

**旧架构问题:**
```python
# 每次开始都重新加载模型！
subprocess.Popen([
    "python3", "-u", "asr_recorder_v2.py", "--output", output_file
])
# ↓ 子进程内部再次加载模型 (60 秒)
engine.load_model()  # ❌ 重复加载
```

**新架构优势:**
```python
# 直接使用已加载的引擎
state['engine'].start_recognition(output_file=output_file)
# ↓ 后台线程直接运行识别循环
threading.Thread(target=engine._recognition_loop, daemon=True).start()
```

---

## 💾 资源占用 / Resource Usage

| 类型 | 占用量 | 说明 |
|------|-------|------|
| **内存 / Memory** | ~1.3GB | 模型常驻内存 (单进程优化) |
| **CPU 占用** | 0-75% | 仅识别时高，空闲时<5% |
| **磁盘缓存** | ~2GB | 模型文件 (一次下载永久复用) |
| **运行时缓冲** | <1MB | 10 秒音频 ≈ 640KB (识别后立即释放) |

### ⭐ 核心结论 / Key Takeaway

✅ **不会产生持续增长的缓存！**  
- **模型缓存**: 一次下载，永久复用  
- **音频缓冲**: 识别后立即释放  
- **唯一增长的是 `transcripts/` 目录下的 txt 文件**（可手动管理）

---

## ⚙️ 技术规格 / Technical Specifications

| 参数 | 值 | 说明 |
|------|-----|------|
| **模型 / Model** | paraformer-zh (FunASR 1.1.9) | 中文优化版本 |
| **PyTorch 版本** | 2.2.2 | macOS CPU 兼容版本 |
| **采样率 / Sample Rate** | 16kHz | 单声道 |
| **滑动窗口 / Window Size** | 10 秒 | 保证句子完整性 |
| **音量阈值 / Volume Threshold** | 0.04 | 静音过滤 |
| **Python 环境** | QwenPaw venv | 独立虚拟环境 |
| **Web 服务器** | Flask | 轻量级 Python Web 框架 |

---

## ❓ 常见问题 / FAQ

**Q: 为什么每个字之间有空格？**  
A: FunASR 1.1.9 版本的输出格式限制。二期可升级到带标点版本。

**Q: 系统没有声音时会输出乱码吗？**  
A: 已添加音量阈值过滤（默认 0.04）。如果仍有问题可调整 `volume_threshold`。

**Q: 可以识别英文或粤语吗？**  
A: 当前版本专注于中文。如需多语言支持，需切换到 multilingual 模型。

**Q: 可以通过手机访问吗？**  
A: 可以！确保手机和电脑在同一 WiFi 网络，访问 `http://<电脑 IP>:5000`。

**Q: 程序会占用大量磁盘空间吗？**  
A: 不会。模型缓存一次性 2GB 后不再增长，唯一增长的是 txt 输出文件（可手动清理）。

---

## 📝 使用场景举例 / Use Cases

```bash
# 场景 1: 学习 B 站课程 / Study Bilibili courses
1. 打开 B 站课程视频 / Open Bilibili course video
2. 浏览器访问 http://localhost:5000 / Access via browser
3. 点击开始识别 / Click Start
4. 获得完整字幕记录 / Get complete transcript

# 场景 2: 会议记录 / Meeting notes
1. 加入线上会议 / Join online meeting
2. 手机访问 Web 界面 / Access via phone browser
3. 实时查看会议纪要 / Real-time meeting notes

# 场景 3: 播客整理 / Podcast organization
1. 播放播客节目 / Play podcast episode
2. 后台运行识别 / Run recognition in background
3. 获取文字稿用于后续整理 / Get text for further processing
```

---

## 🔐 安全与隐私 / Security & Privacy

- ✅ **本地运行**：所有处理在本地完成，不上传云端
- ✅ **无数据收集**：不记录用户身份信息
- ✅ **开源透明**：GitHub 仓库公开审计

---

**项目位置 / Project Location**: `asr_project/`  
**GitHub**: `https://github.com/beiyanwen-byte/macros_voice_service`
