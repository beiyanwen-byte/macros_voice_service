# 🚀 ASR 语音识别工具 - 部署与使用指南

**macOS System Audio Recognition Tool**  
基于 FunASR paraformer-zh 模型，将系统播放的声音实时转换为文字。

---

## 📋 快速开始

### 前置要求

| 项目 | 要求 | 说明 |
|------|------|------|
| **操作系统** | macOS Big Sur (10.11) 或更高版本 | 已在 macOS 10.15, 12, 13 测试 |
| **Python** | Python 3.10+ | `python3 --version` 检查 |
| **Homebrew** | 可选（用于 ffmpeg） | `brew install ffmpeg` 可提升音频加载速度 |

### 一键启动

```bash
cd asr_project
./start.sh
```

**脚本会自动完成以下操作**：
1. ✅ 检查/创建虚拟环境 (`venv/`)
2. ✅ 激活虚拟环境
3. ✅ 升级 pip
4. ✅ 安装所有必需依赖（含 PyTorch CPU 版，~800MB）
5. ✅ 启动 Web 服务

**预计耗时**：首次运行约 3-5 分钟（下载依赖），后续启动 <5 秒

---

## 🌐 使用方法

### 1. 打开 Web 界面

浏览器访问：**http://localhost:5000**

### 2. 操作流程

| 步骤 | 操作 | 预期结果 | 耗时 |
|------|------|---------|------|
| **1** | 点击 "🔽 加载模型" | 显示加载日志 | ~60 秒（首次下载模型 990MB） |
| **2** | 等待按钮变亮 | 状态变为"已加载" | - |
| **3** | 点击 "▶️ 开始识别" | 立即开始录制 | <1 秒 |
| **4** | 播放音频 | 实时显示转录 | 实时 |
| **5** | 点击 "⏹️ 停止" | 保存文件并退出 | <1 秒 |

### 3. 输出文件

位置：`transcripts/YYYY-MM-DD_HHMM.txt`

格式示例：
```
[16:09:24] 就 是 大 家 看 到 这 个 你 default 进 去 是 chat model
[16:09:35] 是 吧 然 后 你 也 可 以 做 一 些 这 个 呃 行 业 里 叫 honest engineer
[16:09:44] 个 呃 工 作 流 然 后 在 工 作 流 上 设 定 不 同 的 步 骤
```

> **注意**：FunASR 1.1.9 字之间有空格属正常现象（模型版本限制）。

---

## 🔧 依赖关系详解

### 核心依赖栈（已验证兼容组合）

| 包名 | 版本 | 用途 | 兼容性说明 |
|------|------|------|-----------|
| **torch** | 2.2.2 | AI 推理框架 | macOS CPU 最高支持版本 |
| **torchaudio** | 2.2.2 | 音频处理 | 与 torch 2.2.2 配套 |
| **numpy** | **1.26.4** | 数值计算 | ⚠️ **不能升级到 2.x**（与 torch 2.2.2 不兼容） |
| **scipy** | **1.12.0** | 科学计算 | 兼容 numpy 1.26.4 |
| **numba** | **0.59.1** | JIT 编译 | ⚠️ **关键修复**：0.60+ 有 ABI 冲突 |
| **funasr** | 1.1.9 | 语音识别模型 | 稳定版本 |
| **librosa** | >=0.10.0 | 音频特征提取 | 依赖 numba/scipy |
| **modelscope** | >=1.9.0 | 模型下载 | 阿里云 ModelScope |

### 其他依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| flask | >=2.0.0 | Web 框架 |
| sounddevice | >=0.4.6 | 系统音频捕获 |
| pydub | >=0.25.0 | 音频格式转换 |
| omegaconf | >=2.3.0 | 配置文件解析 |
| transformers | >=4.30.0 | HuggingFace 工具 |
| hydra-core | >=1.3.0 | 实验配置管理 |
| kaldiio | >=2.17.0 | Kaldi 文件格式支持 |
| sentencepiece | >=0.2.0 | 分词器 |
| jieba / jaconv / jamo | - | 中日文文本处理 |

### ❌ 禁止操作的依赖

```bash
# ❌ 不要执行以下操作：
pip install --upgrade numpy       # 会升级到 2.x，与 torch 不兼容
pip install --upgrade scipy       # 可能引入版本冲突
pip install numba==0.60.0         # ABI 不兼容，导致 "numpy.dtype size changed" 错误
pip install numba>=0.60           # 同上
```

---

## 🔍 故障排查

### 问题 1: `numpy.dtype size changed` 错误

**症状**：
```
numpy.dtype size changed, may indicate binary incompatibility. 
Expected 96 from C header, got 88 from PyObject
```

**原因**: `numba 0.60+` 与 `numpy 1.26.4` 的 C 扩展 ABI 不兼容。

**解决**：
```bash
# 删除旧环境并重新创建
rm -rf venv
./start.sh
```

如果仍有问题，手动安装兼容版本：
```bash
./venv/bin/pip uninstall -y numba
./venv/bin/pip install numba==0.59.1 --only-binary=:all:
```

---

### 问题 2: `No module named 'omegaconf'` 或类似缺失

**原因**: 某些依赖未正确安装。

**解决**：
```bash
cd asr_project
source venv/bin/activate
pip install omegaconf transformers modelscope tensorboardX
```

---

### 问题 3: 端口 5000 被占用

**症状**: `Address already in use Port 5000 is in use`

**解决**：
```bash
# macOS AirPlay Receiver 占用端口
sudo lsof -i :5000            # 查找进程
sudo kill -9 <PID>            # 强制停止
# 或暂时关闭 AirPlay Receiver（系统设置 -> 通用 -> AirPlay 接收器）
```

---

### 问题 4: 模型下载超时

**原因**: 网络问题导致 ModelScope 下载失败。

**解决**：
1. 检查网络连接
2. 手动下载模型（高级用户）
3. 重试多次（`./start.sh` 会自动重试）

---

### 问题 5: 没有声音（无法捕获系统音频）

**原因**: 未配置 BlackHole 虚拟声卡。

**解决**：
1. 下载 BlackHole: https://github.com/ExistentialAudio/BlackHole/releases
2. 安装 **BlackHole 2ch** 版本
3. 打开「音频 MIDI 设置」
4. 创建「多输出设备」，勾选：
   - ✅ BlackHole 2ch
   - ✅ 内建输出（同时听到声音）
5. 系统声音设置中选择该「多输出设备」

---

## 📦 文件系统结构

```
asr_project/
├── app.py                  # Web 服务主程序（Flask）
├── asr_core.py             # ASR 核心引擎（FunASR 封装）
├── start.sh                # 启动脚本（自动配置）
├── stop.sh                 # 停止脚本（优雅关闭）
├── requirements.txt        # Python 依赖清单
├── DEPLOYMENT_GUIDE.md     # 本文档
├── README.md               # 项目说明（中英双语）
├── transcripts/            # 转录结果目录
│   ├── 2026-07-03_1608.txt
│   └── YYYY-MM-DD_HHMM.txt
├── venv/                   # Python 虚拟环境（自动生成）
│   ├── bin/
│   ├── lib/
│   └── ...
└── .gitignore              # Git 忽略规则
```

---

## 🔒 安全与隐私

- ✅ **完全离线运行**: 所有音频处理和识别都在本地完成
- ✅ **无数据上传**: 不会将音频或转录结果发送到任何远程服务器
- ✅ **模型缓存**: 模型下载到 `~/.cache/modelscope/`，仅首次使用时下载
- ⚠️ **权限注意**: 如需录制系统音频，需授予「录音机」权限

---

## 💻 性能指标

| 指标 | 值 | 说明 |
|------|-----|------|
| **内存占用** | ~1.3 GB | 单进程架构优化（原 2.6GB） |
| **CPU 占用** | 0%（待机）→ 75%（识别中） | macOS MacBook Pro M1/M2 |
| **模型大小** | 990 MB | paraformer-zh |
| **首次启动时间** | ~60 秒 | 含模型下载（网速影响） |
| **后续启动时间** | ~15 秒 | 从缓存加载 |
| **识别延迟** | ~5 秒 | 滑动窗口长度 |

---

## 🛠️ 高级使用

### 手动控制虚拟环境

```bash
# 激活环境
source venv/bin/activate

# 查看已安装的包
pip list

# 更新某个包（谨慎操作！）
pip install --upgrade flask   # Flask 可以安全升级

# 退出环境
deactivate
```

### 命令行工具（备选）

```bash
# 直接运行 CLI 版本（无需 Web 界面）
source venv/bin/activate
python3 asr.py
```

### 后台运行服务

```bash
# 使用 nohup 后台运行
nohup ./venv/bin/python3 app.py > server.log 2>&1 &

# 查看进程
ps aux | grep "app.py"

# 停止服务
kill $(lsof -t -i:5000)
```

### Docker 部署（计划中）

未来版本将提供 Docker 镜像，简化跨平台部署。

---

## 📝 更新日志

### v1.2.0 (2026-07-03)
- ✅ 修复 NumPy/SciPy/Numba ABI 兼容性问题
- ✅ 锁定 `numba==0.59.1`，解决 `numpy.dtype size changed` 错误
- ✅ 优化 `start.sh` 安装顺序，添加回退机制
- ✅ 内存占用从 2.6GB 降至 1.3GB（单进程架构）
- ✅ 添加完整部署指南

### v1.1.0 (2026-06-28)
- ✅ 迁移至 Flask Web 界面
- ✅ 实现懒加载模型（按需触发）
- ✅ 支持优雅停止机制

### v1.0.0 (2026-06-25)
- ✅ 初始版本发布
- ✅ 基于 FunASR paraformer-zh
- ✅ 系统音频捕获（BlackHole）

---

## 🙏 致谢

- **FunASR**: https://github.com/alibaba-damo-academy/FunASR
- **ModelScope**: https://modelscope.cn
- **BlackHole**: https://github.com/ExistentialAudio/BlackHole

---

## 📄 许可证

MIT License - 详见项目根目录 LICENSE 文件。

---

**最后更新**: 2026-07-03  
**维护者**: Peter  
**GitHub**: https://github.com/beiyanwen-byte/macros_voice_service
