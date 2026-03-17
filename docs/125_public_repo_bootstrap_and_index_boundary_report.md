# 125. `public repo bootstrap and index boundary` 报告

## 背景
本轮不是实验推进，
而是为项目建立一个可公开同步到 GitHub 的工作仓库，
用于实时备份当前进展。

目标边界已经明确:
- 可以公开:
  - 代码
  - 配置
  - 方案文档
  - 阶段评估
  - 中间模型 / checkpoint
- 不公开:
  - 原始音频
  - 分段音频
  - 代理审听音频
  - 本地运行环境与私有凭证

因此这轮的核心不是“完善对外说明”，
而是把:
- 公开仓库边界
- Git 忽略边界
- 索引检查口径

直接固化到仓库根目录和流程里。

## 本轮已完成事项
### 1. 根目录已初始化 Git 仓库
- 已执行:
  - `git init -b main`
- 当前默认分支:
  - `main`

### 2. 已配置 GitHub 远端
- `origin`:
  - `https://github.com/lhy6305/artifuse-voice-conversion.git`

### 3. 已新增建仓基础文件
- `.gitignore`
- `LICENSE`
- `README.md`
- `NOTICE`

这些文件的用途是:
- 定义公开边界
- 防止误收音频和本地环境文件
- 给 GitHub 仓库一个最小可读入口

## `.gitignore` 的当前边界
### 已明确忽略
- 全部常见音频扩展名:
  - `*.wav`
  - `*.mp3`
  - `*.flac`
  - `*.ogg`
  - `*.m4a`
  - `*.aac`
  - `*.wma`
  - `*.opus`
- 已知高风险目录:
  - `data_convert/dataset_firefly_raw/`
  - `data_prep/**/audio/`
  - `data_prep/**/segments/`
  - `reports/audio/`
- 本地运行环境:
  - `python.exe`
  - `codex_perm_cleanup_static.exe`
  - `tmp/`
  - `__pycache__/`
  - 常见 Python cache / venv

### 仍允许进入仓库
- `configs/`
- `src/`
- `docs/`
- `reports/` 下非音频评估与报告
- `reports/training/` 与 `reports/experiments/` 的中间模型 / checkpoint / metrics
- `data_prep/` 下非音频、非分段的结构化产物

## 许可证口径
当前 `LICENSE` 采用的是:
- 保留所有权利
- 公开可见
- 不授予第三方复用权

这更符合本仓库当前用途:
- 公开备份
- 自用
- 不面向外部协作或二次开发

## 敏感文件与索引边界核验
### 当前磁盘状态
用户在根目录放置了一个敏感文件:
- `ssh-key-private`

本轮检查刻意只核对 Git 状态，
不读取其内容。

### 核验结果
1. `git check-ignore` 显示:
   - `ssh-key-private` 已被 `.gitignore` 命中
2. `git status --short --ignored` 显示:
   - 该文件状态为 `!!`
   - 即:
     - 已忽略
     - 未跟踪
3. `git ls-files` 当前为空
   - 说明索引中没有任何已跟踪文件
4. `git rev-list --count --all = 0`
   - 说明当前仓库还没有任何提交历史

### 直接结论
- 当前敏感文件未进入索引
- 当前敏感文件未进入提交历史
- 当前仓库不存在任何已提交、已可上传的内容

## 当前阶段正式口径
1. 这个 Git 仓库已经可以作为公开备份仓使用。
2. 其默认公开边界是:
   - 代码 / 文档 / 评估 / 方案 / 中间模型
   - 不含原始或派生音频
3. 任何新放入根目录的敏感文件，
   都必须先确认:
   - 被 `.gitignore` 命中
   - 未进入 `git ls-files`
   - 未被提交

## 后续规范
### 提交前检查
每次首次 `git add` 或扩大 `.gitignore` 边界后，
至少检查:
- `git status --short --ignored`
- `git ls-files`

### 若新增敏感文件
先检查:
- 是否被忽略
- 是否已经被加入索引

### 若新增音频相关目录
先决定它属于:
- 原始 / 分段 / 代理音频
  - 默认继续忽略
- 结构化标注 / 指标 / 计划
  - 可继续保留

## 结论
这轮的结果不是实验结论，
而是项目的公开备份边界已经落地:
- 仓库已初始化
- 远端已配置
- 根目录建仓文件已补齐
- 敏感文件未进入索引或历史

因此后续可以在这个仓库上继续日常增量备份，
同时维持“公开代码与方案、排除音频与私密文件”的默认制度。
