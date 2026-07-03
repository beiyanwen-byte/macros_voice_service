# 📦 依赖关系完整说明

本文档详细说明 ASR 语音识别工具的所有依赖及其关系。

---

## 🔑 核心依赖栈（ABI 兼容组合）

这是整个系统的基石，**必须严格保持版本一致**：

```
┌─────────────────────────────────────────┐
│          NumPy ABI Compatibility         │
└─────────────────────────────────────────┘
              ↓ (关键约束)
┌─────────────────────────────────────────┐
│ numpy==1.26.4                           │
│   └── ⚠️ 不能升级到 2.x!                 │
│      PyTorch 2.2.2 仅支持 NumPy 1.x     │
├─────────────────────────────────────────┤
│ scipy==1.12.0                           │
│   └── 需要 numpy>=1.23,<1.27            │
├─────────────────────────────────────────┤
│ numba==0.59.1                           │
│   └── ⚠️ 关键修复！                      │
│      0.60+ 与 numpy 1.26.4 有 ABI 冲突    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ torch==2.2.2 (CPU)                     │
│   └── macOS CPU 最高支持版本             │
│   └── 不支持 NumPy 2.x                   │
└─────────────────────────────────────────┘
```

### ❌ 禁止操作

```bash
# 这些命令会破坏系统！
pip install --upgrade numpy       # ❌ 升级到 2.x → ABI 错误
pip install --upgrade scipy       # ❌ 可能引入不兼容版本
pip install numba>=0.60           # ❌ "numpy.dtype size changed" 错误
```

---

## 🎯 直接依赖（由 pip install 直接安装）

### AI/ML 核心框架

| 包名 | 版本 | 用途 | 备注 |
|------|------|------|------|
| **torch** | 2.2.2 | Deep Learning | CPU-only, macOS 兼容 |
| **torchaudio** | 2.2.2 | Audio Processing | 音频 I/O 和处理 |
| **funasr** | 1.1.9 | Speech Recognition | ASR 主模型 |

### 音频处理

| 包名 | 版本 | 用途 |
|------|------|------|
| librosa | >=0.10.0 | 音频特征提取 |
| sounddevice | >=0.4.6 | 实时音频捕获 |
| pydub | >=0.25.0 | 音频格式转换 |

### Web 框架

| 包名 | 版本 | 用途 |
|------|------|------|
| flask | >=2.0.0 | Web 服务 |

### 模型管理

| 包名 | 版本 | 用途 |
|------|------|------|
| modelscope | >=1.9.0 | 阿里云 ModelScope |
| omegaconf | >=2.3.0 | 配置管理 |
| transformers | >=4.30.0 | HuggingFace 工具 |

### 文本处理

| 包名 | 版本 | 用途 |
|------|------|------|
| sentencepiece | >=0.2.0 | 分词器 |
| jieba | >=0.42.0 | 中文分词 |
| jaconv | >=0.4.0 | 日文假名转换 |
| jamo | >=0.4.0 | 韩文处理 |

### 工具库

| 包名 | 版本 | 用途 |
|------|------|------|
| hydra-core | >=1.3.0 | 实验配置 |
| kaldiio | >=2.17.0 | Kaldi 文件格式 |
| tensorboardX | >=2.6.0 | TensorBoard 记录 |
| editdistance | >=0.8.0 | 编辑距离计算 |
| pytorch-wpe | >=0.0.1 | 语音增强 |
| torch-complex | - | Complex 运算支持 |

---

## 🔗 间接依赖（自动安装）

以下包作为上述库的依赖自动安装，但显式列出确保完整性：

### librosa 的依赖

```python
librosa (0.11.0)
├── audioread (3.1.0)        ← 音频文件读取
├── decorator (5.3.1)        ← 装饰器
├── joblib (1.5.3)           ← 并行计算
├── lazy_loader (0.5)        ← 懒加载
├── msgpack (1.2.1)          ← 序列化
├── pooch (1.9.0)            ← 数据集下载
├── scikit-learn (1.9.0)     ← 机器学习
├── scipy (1.12.0)           ← 科学计算 (已在核心栈)
└── soxr (1.1.0)             ← 重采样
```

### scikit-learn 的依赖

```python
scikit-learn (1.9.0)
├── narwhals (2.23.0)        ← DataFrame API
├── numpy (1.26.4)           ← 已在核心栈
├── scipy (1.12.0)           ← 已在核心栈
└── threadpoolctl (3.6.0)    ← 线程池控制
```

### huggingface_hub 的依赖

```python
huggingface_hub (1.21.0)
├── filelock (3.29.0)        ← 文件锁
├── fsspec (2026.4.0)        ← 文件系统抽象
├── platformdirs (4.10.0)    ← 平台目录
├── requests (2.34.2)        ← HTTP 请求
└── tqdm (4.68.3)            ← 进度条
```

### Flask 的依赖

```python
Flask (3.1.3)
├── blinker (1.9.0)          ← 信号处理
├── click (8.4.2)            ← CLI 框架
├── itsdangerous (2.2.0)     ← 安全令牌
├── jinja2 (3.1.6)           ← 模板引擎
└── werkzeug (3.1.8)         ← WSGI 服务器
```

### modelscope 的依赖

```python
modelscope (1.38.0)
├── aliyun-python-sdk-core (2.16.0)  ← 阿里云 SDK
├── aliyun-python-sdk-kms (2.16.0)   ← KMS
└── cryptography (49.0.0)            ← 加密
```

---

## ✅ 完整性检查清单

运行以下命令验证所有必需包已安装：

```bash
# 1. 核心栈
python3 -c "import torch, numpy, scipy; print('✅ Core:', torch.__version__, numpy.__version__, scipy.__version__)"

# 2. NumPy ABI 检查
python3 -c "from numba import __version__; import numpy; print(f'✅ Numba {__version__} + NumPy {numpy.__version__}')"

# 3. ASR 组件
python3 -c "from funasr import AutoModel; print('✅ FunASR imported')"

# 4. 音频组件  
python3 -c "import librosa, sounddevice; print('✅ Audio:', librosa.__version__)"

# 5. Web 组件
python3 -c "from flask import Flask; print('✅ Flask imported')"

# 6. 关键间接依赖
python3 -c "import decorator, joblib, pooch, lazy_loader; print('✅ Indirect deps OK')"
```

### 预期输出示例

```
✅ Core: 2.2.2 1.26.4 1.12.0
✅ Numba 0.59.1 + NumPy 1.26.4
[transformers] Disabling PyTorch because PyTorch >= 2.4 is required but found 2.2.2
✅ FunASR imported
✅ Audio: 0.11.0
✅ Flask imported
✅ Indirect deps OK
```

---

## 🔄 依赖升级策略

### 可以安全升级

```bash
# Web 框架相关
pip install --upgrade flask werkzeug jinja2 click blinker

# 工具库相关
pip install --upgrade tqdm requests pytest

# 非核心依赖
pip install --upgrade omegaconf hydra-core
```

### ⚠️ 谨慎升级

```bash
# 需要先测试兼容性
pip install --upgrade librosa    # 检查是否引入了 numpy 2.x 依赖
pip install --upgrade scipy      # 确认 numpy 版本要求
```

### ❌ 禁止升级

```bash
# 以下升级会导致系统崩溃！
pip install --upgrade numpy torch torchaudio funasr numba
```

---

## 🛠️ start.sh 执行流程

```bash
#!/bin/bash
# start.sh 内部流程

1. 检测虚拟环境
   ├─ VIRTUAL_ENV 已激活？→ 使用当前 venv
   ├─ 项目目录有 venv？→ source venv/bin/activate
   └─ 否则 → python3 -m venv venv → activate

2. 升级 pip
   └─ pip install --upgrade pip --quiet

3. 安装核心栈（带回退机制）
   ├─ torch==2.2.2 + numpy==1.26.4 + scipy==1.12.0 + numba==0.59.1
   │   (尝试 --only-binary，失败则普通模式)
   
4. 安装主要依赖
   ├─ funasr, flask, sounddevice, librosa, modelscope 等
   
5. 安装间接依赖（确保完整性）
   ├─ decorator, joblib, pooch, lazy_loader 等
   
6. 启动 Web 服务
   └─ exec python3 app.py
```

---

## 📊 版本矩阵

| 组件 | 当前版本 | 最低版本 | 最高版本 | 升级风险 |
|------|----------|----------|----------|---------|
| Python | 3.12 | 3.10 | 3.12 | Low |
| torch | **2.2.2** | 2.0.0 | 2.2.2 | High |
| numpy | **1.26.4** | 1.21.0 | 1.26.4 | Critical |
| scipy | **1.12.0** | 1.7.0 | 1.12.0 | High |
| numba | **0.59.1** | 0.58.0 | 0.59.1 | Critical |
| funasr | 1.1.9 | 1.0.0 | 1.1.9 | Medium |
| librosa | 0.11.0 | 0.10.0 | 0.11.0 | Low |
| flask | 3.1.3 | 2.0.0 | latest | Low |

---

**最后更新**: 2026-07-03  
**维护者**: Peter
