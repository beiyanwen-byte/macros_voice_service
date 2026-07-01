# ASR CLI 工具 / Command Line Interface

## ⚠️ 重要提示 / Important Note

**推荐优先使用 Web 界面** (`app.py`)：更美观、支持远程访问、实时日志显示  
**CLI 仅作为备用方案**，适合服务器环境或脚本自动化

---

## 使用方法 / Usage

### 启动识别 / Start Recognition

```bash
cd asr_project
python3 asr.py start
```

**输出示例 / Output:**
```
============================================================
🚀 Mac System Audio Recognition Tool (CLI Mode)
============================================================
[INFO] 正在初始化 FunASR...
[INFO] 加载 paraformer-zh 模型 (首次约 60 秒)...
[INFO] ✅ 模型加载完成！
[INFO] 🎤 开始录制：2026-07-01_2207.txt
[INFO] 等待停止信号... (Ctrl+C 停止)

[RESULT] [22:08:06] 给自己的信息加上一道门对你要在开口之前先想一想...
```

### 停止识别 / Stop Recognition

```bash
# 方法 1: Ctrl+C (在运行终端中)
# 方法 2: 另开终端发送停止命令
python3 asr.py stop
```

### 检查状态 / Check Status

```bash
python3 asr.py status
```

**返回示例 / Output:**
```json
{
  "is_recording": false,
  "model_loaded": true,
  "output_file": "/Users/username/asr_project/transcripts/2026-07-01_2207.txt"
}
```

---

## 完整示例 / Complete Example

```bash
# 1. 启动服务
python3 asr.py start

# 2. 播放 B 站视频或其他音频
# ... 等待识别结果 ...

# 3. 停止服务 (Ctrl+C 或另一终端)
python3 asr.py stop
```

---

## 配置文件 / Configuration

部分参数可在 `asr_core.py` 中调整：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `volume_threshold` | 0.04 | 音量阈值（低于此值跳过识别） |
| `window_size` | 10 | 滑动窗口大小（秒） |
| `sample_rate` | 16000 | 采样率 (Hz) |

**修改示例:**
```python
# asr_core.py
class ASREngine:
    def __init__(self, volume_threshold=0.04, window_size=10):
        self.volume_threshold = volume_threshold
        self.window_size = window_size
```

---

## 常见问题 / FAQ

**Q: CLI 模式下如何看实时日志？**  
A: 直接查看终端输出。Web 模式的日志会显示在浏览器中，更友好。

**Q: CLI 能后台运行吗？**  
A: 可以配合 `nohup`：
```bash
nohup python3 asr.py start > asr.log 2>&1 &
```

**Q: 为什么推荐 Web 模式？**  
A: 
- ✅ 美观的图形界面
- ✅ 支持手机远程访问
- ✅ 实时日志滚动显示
- ✅ 按钮状态自动管理
- ✅ 优雅停止机制

---

**更多详情见**: [README.md](README.md)
