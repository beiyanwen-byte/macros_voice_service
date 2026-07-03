# Mac System Audio Recognition Tool / macOS 系统音频识别工具

基于 FunASR paraformer-zh 模型的 Web 语音识别服务，**将系统播放的声音实时转换为文字**。

## 🚀 快速开始 / Quick Start

### 前置要求 / Prerequisites

**macOS Big Sur (10.11) 或更高版本**  
**Python 3.10+**  
**Homebrew**（用于安装构建工具）

### 1. 安装构建工具 (首次运行必需)

```bash
# macOS 需要 cmake 来编译部分 Python 包
brew install cmake
```

### 2. 启动服务 / Start Service

```bash
cd asr_project
./start.sh
```

脚本会自动：
- ✅ 创建虚拟环境（如果不存在）
- ✅ 安装所有必需的 Python 依赖
- ✅ 启动 Web 服务器

### 3. 浏览器访问 / Open Browser

打开浏览器访问：**`http://localhost:5000`**

### 4. 操作步骤 / Steps

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 点击 **"🔽 加载模型"** | 首次约 60 秒，之后自动缓存 |
| 2 | 按钮变亮后点击 **"▶️ 开始识别"** | 立即开始，无需等待 |
| 3 | 播放音频（B 站/会议/播客） | 日志区实时显示识别结果 |
| 4 | 点击 **"⏹️ 停止"** | Web 界面优雅停止 |
| 5 | Ctrl+C 或运行 `./stop.sh` | 完全退出服务器进程 |

---

## 🛠️ 手动安装 (可选)

如果 `start.sh` 失败，可以手动安装：

```bash
cd asr_project

# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or venv\Scripts\activate  # Windows

# 2. 安装 PyTorch CPU 版本
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# 3. 安装其他依赖
pip install flask sounddevice pydub numpy "numpy<2.0"

# 4. 安装 FunASR (可能需要先安装 cmake)
brew install cmake
pip install funasr==1.1.9

# 5. 启动服务
python3 app.py
```

---

## 🎧 音频配置 / Audio Configuration

要识别**系统播放的声音**，需配置 **BlackHole 虚拟声卡**：

1. 下载 BlackHole: https://github.com/ExistentialAudio/BlackHole/releases
2. 安装 BlackHole 2ch 版本
3. 在「音频 MIDI 设置」中创建多输出设备（勾选 BlackHole + 内建输出）
4. 在系统声音设置中选择该多输出设备

---

## 💻 技术规格 / Technical Specifications

| 参数 | 值 |
|------|-----|
| **模型** | paraformer-zh (FunASR 1.1.9) |
| **PyTorch** | 2.2.2 (macOS CPU 版本) |
| **采样率** | 16kHz |
| **内存占用** | ~1.3GB |
| **CPU 占用** | 0-75% (识别时) |

---

## 📁 文件结构 / File Structure

```
asr_project/
├── app.py                  # Web 服务主程序
├── asr_core.py             # ASR 核心引擎
├── start.sh                # 启动脚本
├── stop.sh                 # 停止脚本
├── requirements.txt        # Python 依赖
├── transcripts/            # 识别结果目录
│   └── 2026-XX-XX_XXXX.txt
└── venv/                   # Python 虚拟环境
```

---

## ❓ 常见问题 / FAQ

**Q: `./start.sh` 卡在 "Installing dependencies..."**  
A: 首次安装会下载 PyTorch (~800MB)，需要几分钟。请耐心等待。

**Q: "llvmlite" 构建失败**  
A: 需要安装 cmake：`brew install cmake`

**Q: "No module named 'flask'"**  
A: 确保已激活虚拟环境或使用 `./venv/bin/python3 app.py`

**Q: 字之间有空格？**  
A: FunASR 1.1.9 的输出格式限制，二期可升级。

---

**项目位置**: `asr_project/`  
**GitHub**: `https://github.com/beiyanwen-byte/macros_voice_service`
