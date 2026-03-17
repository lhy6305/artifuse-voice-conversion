# 191. 仓库恢复性与忽略规则评估报告

## 任务目标
- 评估当前仓库的忽略规则，
  尤其是:
  - `.gitignore`
  - `.git/info/exclude`
- 判断它们是否符合
  “发生意外丢失时，
   尽量保留最大可恢复状态”
  的目标

## 本轮检查范围
- 根目录:
  - `.gitignore`
  - `.gitattributes`
- Git 本地补充忽略:
  - `.git/info/exclude`
- 现有规范与历史口径:
  - `docs/00_context_bootstrap.md`
  - `docs/125_public_repo_bootstrap_and_index_boundary_report.md`
- 运行产物结构:
  - `reports/runtime/`

## 观察到的事实

### 1. `.git/info/exclude` 当前没有项目级有效规则
- 只有默认注释
- 所以当前真正起作用的
  忽略边界
  主要来自:
  - 根目录 `.gitignore`

### 2. `.gitattributes` 当前基本合理
- 文本文件统一按文本处理
- 常见二进制与媒体文件
  统一按 binary 标注
- 这会减少:
  - 行尾漂移
  - 大二进制误判为文本
- 本轮未发现
  需要调整的地方

### 3. 旧 `.gitignore` 对“恢复性”不够合理
旧规则的主要问题有两类:

#### A. 全局忽略 `*.pt`
- 会把 runtime / training
  下正式训练 checkpoint
  一起挡掉
- 但这些 checkpoint
  恰恰是意外丢失后
  最难重建、
  恢复价值最高的产物之一

#### B. `reports/runtime/**`
仅放行 `*.summary.json/md`
- 这会误伤很多
  体积不大、
  但恢复价值很高的正式元数据，例如:
  - `offline_mvp_nores_vocoder_dataset_index.json`
  - `nores_vocoder_checkpoint_review.json`
  - train-step / scaffold / train-target 的正式 json/md
- 结果会变成:
  - 文档里写了实验结论
  - 但真正能支撑恢复和复核的
    元数据没有入库

### 4. `reports/runtime/` 内部并不是“全部都该保留”
- 当前运行产物里:
  - `.json` 约 `2509` 个
  - `.md` 约 `2057` 个
  - `.pt` 约 `2079` 个
- 其中最大头的是:
  - `reports/runtime/**/packages/**`
    下面的 package 级 payload
- 这部分虽然多，
  但大多数是:
  - teacher contract
  - scaffold
  - train_targets
  的批量导出副本
- 它们可以由:
  - 代码
  - split
  - dataset index
  - 正式 summary
  再次重建，
  不适合整体放入仓库

### 5. 正式 checkpoint 的体量是可接受的
- 当前 Stage5 正式 checkpoint
  多数在:
  - 约 `0.3 MB`
  - 到 `0.8 MB`
- 这类体量
  对“保留关键恢复状态”
  来说是合理的

## 结论
- 旧 `.gitignore`
  对“公开边界”尚可，
  但对
  “最大可恢复目标”
  不够合理
- 主要原因不是
  忽略得太少，
  而是:
  - 把高恢复价值的
    checkpoint 和元数据
    一起忽略掉了

所以本轮结论是:
- 规则不完全合理
- 已直接修正

## 本轮修正

### 1. 保留正式 checkpoint
- 对以下目录
  放行:
  - `reports/training/**/checkpoints/*.pt`
  - `reports/runtime/**/checkpoints/*.pt`

### 2. 保留正式恢复元数据
- 对以下 runtime 元数据
  放行:
  - `offline_mvp_nores_vocoder_dataset_index.json/md`
  - `nores_vocoder_checkpoint_review.json/md`
  - `offline_mvp_nores_vocoder_train_step.json/md`
  - `offline_mvp_nores_vocoder_scaffold.json/md`
  - `offline_mvp_nores_vocoder_train_targets.json/md`
  - `teacher_vocoder_input_scaffold.json/md`
  - `teacher_downstream_control_contract.json/md`
  - `teacher_runtime_summary.json/md`
  - 所有正式 `summary.json/md`

### 3. 继续忽略可重建 package payload
- 明确继续忽略:
  - `reports/runtime/**/packages/**`
- 这样保住的是:
  - 恢复状态必需的索引、摘要、评审、checkpoint
- 丢掉的是:
  - 批量可重建的包体副本

## 规范落盘
- 已把上述策略
  写入:
  - `docs/00_context_bootstrap.md`
  的
  `### 11. Git 忽略与恢复边界`

## 当前建议
1. 后续新增 `.gitignore`
   规则时，
   默认先问自己:
   - 这条规则会不会误伤
     checkpoint
     或正式恢复元数据
2. 以后若新增
   大体量运行产物，
   优先采用:
   - “忽略批量可重建件”
   - “保留少量关键恢复件”
   的结构化策略
3. 不再把
   `reports/runtime/**`
   这类粗粒度全目录忽略
   当成默认安全做法

## 一句话结论
- 这次检查的结果不是
  “当前忽略规则已经完全合理”，
  而是:
  - 它对恢复性不够友好
  - 但问题已经被修正
- 现在新的边界更符合
  本项目的真实目标:
  - 敏感音频和可重建大包体
    继续忽略
  - 正式恢复元数据与关键 checkpoint
    保留入库
