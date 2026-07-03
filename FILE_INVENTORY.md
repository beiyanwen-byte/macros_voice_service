# 📁 ASR 项目文件分类清单

**最后更新**: 2026-07-03  
**目的**: 明确每个文件的用途，便于维护和清理

---

## ✅ **必需文件（核心功能）**

这些文件是系统运行所必需的，**绝对不能删除**。

### 1. Python 源代码 (`.py`)

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| **app.py** | 15KB | Web 服务主程序 | Flask 后端 + HTML 前端，**当前主要入口** |
| **asr_core.py** | 9.3KB | ASR 核心引擎 | FunASR 封装、音频捕获、流式识别逻辑 |
| **asr.py** | 4.5KB | CLI 命令行工具 | 备选启动方式（无需 Web 界面），**保留但可选** |

### 2. Shell 脚本 (`.sh`)

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| **start.sh** | 3.6KB | 启动脚本 | **必须！**自动检测/创建 venv，安装依赖，启动服务 |
| **stop.sh** | 2.4KB | 停止脚本 | **必须！**优雅关闭服务，PID 追踪 |
| **restart.sh** | 0.2KB | 重启脚本 | ❌ **已废弃**（内容过时，用 `./stop.sh && ./start.sh` 替代） |

### 3. 配置文件 (`.txt`)

| 文件名 | 大小 | 用途 | 说明 |
|--------|------|------|------|
| **requirements.txt** | 1.4KB | Python 依赖清单 | **必须！**pip install 的输入文件 |
| **.gitignore** | 0.3KB | Git 忽略规则 | **必须！**排除 venv/, transcripts/, *.pyc 等 |

### 4. 文档文件 (`.md`)

| 文件名 | 大小 | 用途 | 优先级 |
|--------|------|------|--------|
| **README.md** | 3.4KB | 项目简介（中英双语） | ⭐⭐⭐ 用户首先看到的文档 |
| **DEPLOYMENT_GUIDE.md** | 8.4KB | 完整部署与使用指南 | ⭐⭐⭐ 新用户必读 |
| **DEPENDENCIES.md** | 8.2KB | 依赖关系详解 | ⭐⭐ 开发者和维护者参考 |
| **ASR_CLI.md** | 2.5KB | CLI 模式使用说明 | ⭐ 仅当用户使用 asr.py 时需要 |

---

## 🔄 **辅助文件（有用但非必需）**

这些文件对开发和维护有帮助，但删除后不影响系统运行。

### 1. 开发与维护文档

| 文件名 | 大小 | 用途 | 建议 |
|--------|------|------|------|
| **PROJECT_EXPERIENCE_SUMMARY.md** | 11KB | 开发经验总结 | ✅ 保留（记录技术决策和踩坑过程） |
| **FILE_INVENTORY.md** | - | 本文档 | ✅ 保留（方便后续维护） |

### 2. 日志和输出文件

| 路径 | 用途 | 清理建议 |
|------|------|---------|
| **transcripts/** | 转录结果目录 | 🗑️ 定期清理测试文件（保留最近几个） |
| **transcripts/*.txt** | 具体转录文件 | 🗑️ 删除示例文件或移动到备份目录 |
| **.DS_Store** | macOS 系统文件 | 🗑️ 删除（添加至 .gitignore） |

### 3. IDE 配置

| 路径 | 用途 | 建议 |
|------|------|------|
| **.idea/** | IntelliJ IDEA 配置 | ✅ 保留（如果使用 JetBrains IDE） |
| **.idea/.gitignore** | IDE Git 配置 | ✅ 保留 |

---

## ❌ **无用文件（可以安全删除）**

以下文件已经过时或不必要，**可以删除**。

| 文件名 | 原因 | 操作 |
|--------|------|------|
| **restart.sh** | 功能已被 `stop.sh + start.sh` 替代，且硬编码路径 | `rm restart.sh` |
| **=0.10.0** 等临时文件 | pip 命令解析错误产生的空文件 | `rm =*` |
| **.asr.pid / .asr_pid** | PID 跟踪文件（运行时生成） | `rm .asr.pid`（已在 .gitignore 中） |
| **transcripts/2026-07-03_*.txt** | 测试期间生成的转录文件 | 🗑️ 选择性删除 |
| **.DS_Store** | macOS 系统隐藏文件 | `find . -name ".DS_Store" -delete` |

---

## 📦 **大型目录（选择性清理）**

| 目录 | 大小 | 用途 | 清理建议 |
|------|------|------|---------|
| **venv/** | 1.4GB | Python 虚拟环境 | 🔄 可删除后用 `./start.sh` 重建（适合迁移到新机器） |
| **__pycache__/** | ~10MB | Python 字节码缓存 | 🗑️ 可删除（Python 会自动重建） |
| **.git/** | 520KB | Git 版本库 | ✅ 必须保留（除非不需要版本控制） |

---

## 🎯 **推荐的最小文件集**

如果你只想保留最核心的文件（用于发布或分发），只需要：

```bash
# 必需的最小集合
app.py              # Web 服务
asr_core.py         # ASR 引擎
start.sh            # 启动脚本
stop.sh             # 停止脚本
requirements.txt    # 依赖清单
.gitignore          # Git 规则

# 基础文档
README.md           # 项目说明
DEPLOYMENT_GUIDE.md # 部署指南

# 可选（CLI 模式）
asr.py              # 命令行工具（可选）
```

**总计约**: 35KB（不含 venv 和 transcripts）

---

## 🧹 **清理脚本**

### 1. 完全清理（删除所有派生文件）

```bash
cd /Users/tanyanwen/asr_project

# 删除虚拟环境（重新构建）
rm -rf venv

# 删除字节码缓存
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 删除 macOS 系统文件
find . -name ".DS_Store" -delete

# 删除测试转录文件
rm -f transcripts/2026-07-03_*.txt

# 删除临时文件
rm -f =* .asr.pid .asr_pid

# 删除废弃脚本
rm -f restart.sh

echo "✅ 清理完成！保留核心代码和文档。"
```

### 2. 轻度清理（只删除临时文件）

```bash
cd /Users/tanyanwen/asr_project

# 仅删除明显无用的文件
rm -f restart.sh =* .asr.pid .asr_pid .DS_Store
find . -name "*.pyc" -delete

echo "✅ 轻度清理完成！"
```

### 3. 保留历史数据（推荐）

如果你想保留一些转录文件作为示例：

```bash
cd /Users/tanyanwen/asr_project/transcripts

# 保留最新的 3 个文件
ls -t *.txt | tail -n +4 | xargs rm -f 2>/dev/null || true

echo "✅ 保留了最近的转录文件。"
```

---

## 📊 **文件分类汇总**

| 类别 | 文件数 | 总大小 | 说明 |
|------|--------|--------|------|
| ✅ **必需** | 10 | ~50KB | 核心代码 + 关键文档 |
| 🔄 **辅助** | 4 | ~20KB | 开发文档 + IDE 配置 |
| ❌ **无用** | 5+ | ~2KB | 可安全删除 |
| 📦 **大型** | 3 | >1GB | venv, __pycache__, .git |

---

## 🔍 **快速检查命令**

```bash
# 1. 查看所有文件
find . -type f | grep -v "venv\|.git\|__pycache__" | sort

# 2. 检查文件大小分布
du -ah --max-depth=1 | sort -h

# 3. 查找重复或大文件
find . -type f -size +1M | head -10

# 4. 验证核心文件存在
ls -l app.py asr_core.py start.sh stop.sh requirements.txt README.md DEPLOYMENT_GUIDE.md
```

---

## 📝 **维护建议**

### 每次发布前检查

- [ ] 删除 `transcripts/` 中的测试文件
- [ ] 删除 `.DS_Store`
- [ ] 确认 `restart.sh` 不存在（已废弃）
- [ ] 更新 `README.md` 版本号
- [ ] 提交并推送最新更改

### 定期检查

- [ ] 每季度检查 `requirements.txt` 是否有安全漏洞（`pip-audit`）
- [ ] 每年评估是否升级 PyTorch/FunASR 版本
- [ ] 清理过时的日志文件和测试转录

---

**制定人**: Peter  
**审核状态**: ✅ 已完成全面检查  
**下一步**: 执行轻度清理 → 提交 Git → 推送远程仓库
