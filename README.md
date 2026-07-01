# Mac 系统音频识别工具 / Mac System Audio Recognition Tool

基于 FunASR paraformer-zh 模型的语音识别工具，**将系统播放的声音实时转换为文字**。
Voice recognition tool based on FunASR paraformer-zh model, **converting system audio to text in real-time**.

## 🎯 功能特性 / Features

- ✅ **系统内录**：支持 B 站视频、会议录音、在线课程等所有系统播放的音频
  - **System Audio Capture**: Supports all system audio including Bilibili videos, meetings, online courses
- ✅ **图形界面**：双击启动，一键开始/停止，无需命令行操作
  - **GUI Interface**: Double-click to start, one-click start/stop, no command line needed
- ✅ **实时显示**：双标签页设计，模型加载时看日志，完成后看转录内容
  - **Real-time Display**: Dual-tab design for logs and transcript content
- ✅ **自动检测**：静音过滤，避免垃圾输出
  - **Auto Detection**: Silence filtering to avoid garbage output
- ✅ **文件保存**：按时间戳自动保存转录结果
  - **File Saving**: Automatically saves transcripts with timestamps

---

## 🚀 快速开始 / Quick Start

### 方式 1: 图形界面（推荐）/ GUI Mode (Recommended)

```bash
cd asr_project
python3 gui_controller.py
```

**操作步骤 / Steps：**
1. 点击 **"▶️ 开始识别"** / Click "▶️ Start Recognition"
2. 等待模型加载（首次约 2-3 分钟）/ Wait for model loading (~2-3 min first time)
3. 界面自动切换到 **实时转录** 页面 / Auto-switch to transcript tab
4. 播放 B 站视频或其他音频即可看到文字 / Play any audio to see results
5. 点击 **"⏹️ 停止识别"** 结束 / Click "⏹️ Stop" to finish

### 方式 2: 命令行模式 / Command Line Mode

```bash
# 启动服务 / Start service
python3 asr.py start

# 查看状态 / Check status
python3 asr.py status

# 停止服务 / Stop service
python3 asr.py stop
```

---

## 🎧 音频配置 / Audio Configuration (重要 / Important)

要识别**系统播放的声音**（而非麦克风），需配置 **BlackHole 虚拟声卡** / To capture **system audio** (not microphone), configure **BlackHole Virtual Audio Device**:

1. 打开「音频 MIDI 设置」 / Open "Audio MIDI Setup"
2. 创建**多输出设备**：勾选 **BlackHole 2ch** + **内建输出** / Create **Multi-Output Device**: Check BlackHole 2ch + Built-in Output
3. 在系统声音设置中选择该多输出设备 / Select this device in System Sound Settings

**测试方法 / Test Method**: 播放 B 站视频，检查 ASR 是否能识别出字幕内容 / Play a Bilibili video and check if subtitles are recognized

---

## 📁 输出文件 / Output Files

转录结果自动保存到 `transcripts/` 目录 / Transcripts automatically saved to `transcripts/` directory:

```
transcripts/
├── 2026-06-28_1450.txt   # 每次启动生成新文件 / New file per session
└── ...
```

**文件格式示例 / Format Example:**
```txt
# 识别开始时间：2026-06-28 14:50:22
# 输出文件：asr_project/transcripts/2026-06-28_1450.txt
# 音频设备：BlackHole 2ch

[14:50:35] 这个不同的这个呃反思甚至批判啊就是我们在提示策略里面去设计一些这样的东西也可以做出一些不同的这个 agent 其中
[14:50:45] 又以这个 lanlanguagent tree search 啊这个 LATS 待会儿我们也可以去讲一讲它呢它可以算是我们在学习 tree of thoughts 啊
```

---

## 🔬 技术原理 / Technical Principles

### 语音识别流程 / Speech Recognition Pipeline

```
声音 → 数字信号 → 特征提取 → 深度学习模型 → 文字输出
Sound → Digital Signal → Feature Extraction → Deep Learning Model → Text Output
```

#### **步骤详解 / Step-by-Step Breakdown:**

1. **音频捕获 / Audio Capture** (16kHz 采样率，单声道)
   - BlackHole 虚拟声卡截获系统音频 / BlackHole captures system audio
   - 模拟声波 → 数字信号 (每秒 16000 个样本点) / Analog → Digital (16000 samples/sec)

2. **预处理 / Preprocessing** (10 秒滑动窗口)
   - 计算 RMS 音量值 / Calculate RMS volume
   - 音量 < 0.04 → 跳过识别（静音过滤）/ Volume < 0.04 → Skip (silence filter)
   - 分帧处理（每帧 25ms，重叠 10ms）/ Frame splitting (25ms frames, 10ms overlap)

3. **特征提取 / Feature Extraction**
   - 转换为 MFCC 或 Fbank 频谱特征 / Convert to MFCC/Fbank spectral features
   - 每帧 ≈ 80 维向量 / Each frame ≈ 80-dimensional vector

4. **模型推理 / Model Inference** (FunASR paraformer-zh)
   ```
   编码器 Encoder：多尺度卷积 + Transformer 自注意力
     - Multi-scale convolutions + Transformer self-attention
   
   双向解码器 Decoder：前后文联合预测
     - Bidirectional prediction using context from both directions
   
   CTC 解码：解决音字不对齐问题
     - CTC decoding handles sound-character misalignment
   ```

5. **后处理 / Post-processing**
   - Beam Search 束搜索最优句子路径 / Beam Search finds optimal sentence path
   - Language Model 语言模型纠正歧义 / LM resolves ambiguity

---

## 💾 资源占用与缓存分析 / Resource & Cache Analysis

### 运行时资源占用 / Runtime Resource Usage

| 类型 | 占用量 | 说明 |
|------|-------|------|
| **内存 / Memory** | ~800MB | FunASR 模型常驻内存 (固定值) / Model loaded in RAM (fixed) |
| **CPU 占用** | 0-75% | 仅识别时高，空闲时<5% / High only during inference, <5% idle |
| **磁盘缓存** | ~2GB | 模型文件（一次下载永久复用）/ Model files (download once, reuse forever) |
| **运行时缓冲** | <1MB | 10 秒音频 ≈ 640KB (识别后立即释放) / 10s audio buffer ≈ 640KB (released after processing) |

### 详细分析 / Detailed Breakdown

#### **内存层面 / Memory Level:**
```python
# 模型加载后：~800MB（固定值，不会随时间增长）
# After model load: ~800MB (fixed, does not grow over time)
model = AutoModel(model="paraformer-zh", device="cpu")

# 音频缓冲区：每 10 秒 ≈ 160,000 samples × 4 bytes = 640KB
# Audio buffer: per 10s ≈ 160,000 samples × 4 bytes = 640KB
audio_buffer = []  # 每次识别后清空 / Cleared after each recognition
```

#### **磁盘层面 / Disk Level:**
```
/Users/tanyanwen/.cache/modelscope/          # 模型缓存 (~2GB，一次下载永久使用)
    └── speech_seaco_paraformer_large_...    

asr_project/transcripts/                      # 输出文件（累积性增长，但可控）
    ├── 2026-06-28_1450.txt  (~5KB per minute of audio)
    └── ...
```

### ⭐ 核心结论 / Key Takeaway

✅ **不会产生持续增长的缓存！** / **No continuously growing cache!**

- **模型缓存**: 一次下载，永久复用 / Model cache: Download once, reuse forever
- **音频缓冲**: 识别后立即释放 / Audio buffer: Released immediately after processing
- **唯一增长的是 `transcripts/` 目录下的 txt 文件**（可手动管理）/ Only `transcripts/*.txt` files grow (manually manageable)

---

## ⚙️ 技术细节 / Technical Specifications

| 参数 / Parameter | 值 / Value | 说明 / Description |
|------------------|-----------|-------------------|
| **模型 / Model** | paraformer-zh | 中文优化版本 / Chinese-optimized |
| **采样率 / Sample Rate** | 16kHz | 单声道 / Mono |
| **滑动窗口 / Window Size** | 10 秒 | 保证句子完整性 / Ensures sentence completeness |
| **音量阈值 / Volume Threshold** | 0.04 | 低于此值跳过识别 / Skip if below threshold |
| **Python 环境** | QwenPaw venv | 独立虚拟环境 / Isolated environment |

---

## ❓ 常见问题 / FAQ

**Q: 为什么每个字之间有空格？ / Why spaces between characters?**  
A: FunASR 1.1.9 版本的输出格式限制。二期可升级到带标点版本。/ Output format limitation of FunASR 1.1.9. Can upgrade to punctuated version in future.

**Q: 系统没有声音时会输出乱码吗？ / Does it output garbage when silent?**  
A: 已添加音量阈值过滤（默认 0.04）。如果仍有问题可调整 `volume_threshold`。/ Volume threshold filtering added (default 0.04). Can adjust if needed.

**Q: 可以识别英文吗？ / Does it support English?**  
A: 当前版本专注于中文。如需多语言支持，需切换到 multilingual 模型。/ Currently Chinese-focused. Need multilingual model for multi-language support.

**Q: 程序会占用大量磁盘空间吗？ / Will the program use lots of disk space?**  
A: 不会。模型缓存一次性 2GB 后不再增长，唯一增长的是 txt 输出文件（可手动清理）。/ No. Model cache is one-time 2GB. Only txt output files grow (can be manually cleaned).

**Q: 支持哪些场景？ / What scenarios are supported?**  
A: **任何系统播放的音频**：B 站/YouTube 视频、在线会议、网络课程、播客、本地播放器 / **Any system audio**: Bilibili/YouTube videos, online meetings, courses, podcasts, local players

---

## 📝 使用场景举例 / Use Case Examples

```bash
# 场景 1: 学习 B 站课程 / Scenario 1: Study Bilibili courses
1. 打开 B 站课程视频 / Open Bilibili course video
2. 启动 ASR (gui_controller.py) / Launch ASR
3. 获得完整字幕记录 / Get complete transcript

# 场景 2: 会议记录 / Scenario 2: Meeting notes
1. 加入线上会议 / Join online meeting
2. 启动 ASR / Launch ASR
3. 自动转录会议内容 / Automatic meeting transcription

# 场景 3: 播客整理 / Scenario 3: Podcast organization
1. 播放播客节目 / Play podcast episode
2. 启动 ASR / Launch ASR
3. 获取文字稿用于后续整理 / Get text for further processing
```

---

**项目位置 / Project Location**: `asr_project/`  
**GitHub**: `https://github.com/beiyanwen-byte/macros_voice_service`
