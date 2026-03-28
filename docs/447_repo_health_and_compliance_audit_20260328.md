# 仓库健康度与规范性自检报告

## 基本信息
- 日期：2026-03-28
- 范围：全仓静态扫描，覆盖 `docs/`、`configs/`、`scripts/`、`src/`、`reports/`、`data_prep/`、根目录规范文件。
- 入口文档：
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `README.md`
  - `initial_design.md`
  - `initial_design_judg.md`
- 特殊说明：
  - 根目录 `ssh-key-private` 按任务要求视为预期存在，不计为风险。
  - 本次未执行长时训练、重推理或音频业务链路复跑；代码风险判断以静态审查、入口可执行性验证和仓库资产扫描为主。

## 扫描方法
- 使用 `UTF-8` 读取规范与设计文档。
- 递归统计全仓文件规模、类型分布、目录分布、tracked/ignored 边界。
- 检查 `.gitignore`、`.gitattributes`、CLI 入口与核心模块组织。
- 运行静态可执行性校验：
  - `.\python.exe -m compileall`
  - `.\python.exe manage.py --help`
- 运行编码规范扫描：
  - Python `read_text/write_text/open` 显式编码检查
  - 风险模式检索：`except Exception`、`shell=True`、`TODO/FIXME` 等
- 重点人工审查：
  - Stage3 paired / split / teacher-label 路径
  - Stage5 dataset package 复用逻辑
  - checkpoint 选择与实验产物复用路径
  - 目录组织、文档体量、路径长度与 Git 工具行为

## 仓库快照
- 全仓文件数：`101,218`
- 顶层目录文件数：
  - `reports/`: `91,646`
  - `data_prep/`: `7,339`
  - `data_convert/`: `1,345`
  - `docs/`: `452`
  - `src/`: `243`
  - `configs/`: `160`
  - `scripts/`: `17`
- 主要文件类型：
  - `.json`: `38,858`
  - `.pt`: `29,104`
  - `.md`: `24,535`
  - `.wav`: `6,194`
  - `.lab`: `1,961`
  - `.py`: `84`
- Git 跟踪概况：
  - tracked 文件总数：`6,788`
  - `docs/`: `452/452` tracked
  - `reports/`: `5,989/91,646` tracked
  - `data_prep/`: `80/7,339` tracked
  - `src/`: `82/243` tracked
- 代码体量指标：
  - `src/v5vc/teacher_first_vc_demo.py`: `7,020` 行
  - `src/v5vc/cli.py`: `6,567` 行
  - `src/v5vc/offline_vocoder_training.py`: `6,116` 行
  - 超过 `100` 行的函数：`120`
  - 超过 `120` 字符的源码行：`840`
  - `reset_managed_directory()` 重复定义次数：`38`
- 文档体量指标：
  - `docs/02_pitfalls_log.md`: `2,485` 行
  - `docs/01_project_overview_and_plan.md`: `1,872` 行

## 结论总览
- 结论：仓库整体可运行、编码规范执行度较高、Git 保留恢复资产的策略也基本成型，但健康度并不理想。
- 最主要的问题不在“有没有代码”，而在：
  - 部分关键路径仍存在可直接污染训练/验证结论的复用与 split 校验漏洞；
  - 代码和文档存在明显单文件膨胀；
  - `reports/` 路径和命名过长，已经开始反噬 Git 工具稳定性；
  - 目录中残留较多 ignored 缓存与巨量产物，本地工作区注意力成本过高。

## 高优先级问题

### 1. paired Stage3 路径没有对 teacher-label split 做硬校验，存在训练/验证污染风险
- 位置：
  - `src/v5vc/streaming_student/data.py:155`
  - `src/v5vc/streaming_student/data.py:370`
- 现象：
  - `load_streaming_student_paired_records_by_split()` 直接把 `train_pair_spec_path` 和 `validation_pair_spec_path` 送入 `attach_streaming_student_paired_contract_metadata()`。
  - `attach_streaming_student_paired_contract_metadata()` 只检查 `target_record_id` 是否能在 `teacher_index_map` 找到，但没有像 target-only 路径那样校验 `teacher_row["split_name"]` 是否与当前 `split_name` 一致。
- 风险：
  - 只要 pair spec 写错，就可能把训练样本的 teacher label 混入验证，或把验证标签混入训练。
  - 这类错误不会在当前代码里被阻断，只会被当作合法 paired contract 继续下游执行，直接污染 loss、validation、checkpoint 选择和后续判断。
- 判断：高风险、需优先修。

### 2. Stage3 -> Stage5 最小桥接在 `skip_existing=True` 时按“文件存在”直接复用，可能静默复用错误 package
- 位置：
  - `src/v5vc/streaming_student/stage5_handoff.py:29`
  - 关键逻辑：`src/v5vc/streaming_student/stage5_handoff.py:70`
- 现象：
  - `build_streaming_student_stage5_dataset_packages()` 里 `package_reused = bool(skip_existing and package_path.exists())`。
  - 复用时没有核对：
    - `noise_event_family`
    - `semantic_consumer_mode`
    - `target_contract_mode`
    - 对应 `packet_path` 是否变化
    - 旧 scaffold/package 是否由当前请求参数生成
- 风险：
  - 同一路径下旧 package 会被当作本轮参数下的新 package 使用。
  - summary 仍按本轮参数写出，导致“报告写的是 A，实际跑的是旧 B”。
  - 这会直接污染 Stage5 fail-fast 判断，尤其是当前仓库非常依赖最小 decoded smoke 作负结论门禁。
- 判断：高风险、需优先修。

## 中高优先级问题

### 3. Stage5 dataset package 的复用判定只校验“侧车是否存在”，没有校验内容身份，仍可能复用陈旧产物
- 位置：
  - `src/v5vc/offline_vocoder_training.py:3331`
  - `src/v5vc/offline_vocoder_training.py:3401`
- 现象：
  - `should_reuse_existing_stage5_training_package()` 会检查：
    - semantic/timing/parity sidecar 是否存在
    - semantic/contract/spectral mode 是否一致
    - `teacher_e_evt_bridge_mode` / `teacher_e_evt_target_shaping_mode`
  - 但不会检查：
    - sidecar 内容是否变化
    - `source_audio_path` / `target_audio_path` / `record_id`
    - `route_handoff_path` / `checkpoint_path` / `calibration_asset_path`
    - scaffold 源文件是否已更新
- 风险：
  - 只要文件路径不变、模式字符串不变，即便上游 sidecar 或 runtime 内容已更新，也可能沿用旧 package。
  - 这会让 dataset rebuild 看起来“已完成”，但实际仍基于旧资产，结论失真且难排查。
- 判断：中高风险。

## 中优先级问题

### 4. 报告与训练产物路径过长，已经开始影响 Git 工具稳定性
- 证据：
  - 最长绝对路径达到 `379` 字符。
  - `git ls-files --others --exclude-standard` 在当前工作区会对 `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/.../t_contract`、`t_scaffold` 等深层路径反复报 `No such file or directory` 警告。
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/` 内文件最大绝对路径长度达到 `288` 字符。
- 现象：
  - 文件名中同时编码了实验阶段、策略、参数、轮次、step、数据集等信息。
  - 目录层级和文件名都过长，Windows/Git 工具链已出现边界问题。
- 风险：
  - Git 工具行为不稳定，文件枚举和忽略判断容易异常。
  - 人工定位与脚本处理成本明显上升。
- 判断：中风险，属于文件组织规范问题。

### 5. 核心代码与主文档明显过大，已经不适合长期维护
- 现象：
  - `src/v5vc/cli.py` 6,567 行，其中 `build_parser()` 单函数 5,205 行，`main()` 1,207 行。
  - `src/v5vc/teacher_first_vc_demo.py` 7,020 行。
  - `src/v5vc/offline_vocoder_training.py` 6,116 行，其中 `compute_nores_vocoder_losses()` 单函数 929 行。
  - `docs/01_project_overview_and_plan.md` 1,872 行，`docs/02_pitfalls_log.md` 2,485 行。
- 风险：
  - 单文件注意力负担过大，review 与修改极易漏掉旁路影响。
  - CLI、训练逻辑、teacher-first user line、文档主索引都已超出“单人一次性可靠全读”的舒适范围。
- 判断：中风险，属于长期维护性问题。

### 6. 文档和实验报告目录仍然过于扁平，结构与命名虽然规则化，但不够直觉
- 现象：
  - `docs/` 直接平铺 `452` 个编号文档。
  - `reports/runtime/` 单目录树下已有 `72,929` 个文件。
  - `reports/training/` 也已有 `12,639` 个文件。
- 风险：
  - 编号规则能保证顺序，但不能保证主题可发现性。
  - 接手者需要先知道编号或关键词，才能定位历史结论。
  - “阶段 / 主题 / 路线 / 审计”没有形成稳定的二级分类层。
- 判断：中风险，属于目录结构规范问题。

### 7. 存在系统性复制的无保护目录清空工具，操作边界偏脆弱
- 现象：
  - `reset_managed_directory()` 在源码中重复定义 `38` 次，典型实现是：
    - 若路径存在则 `shutil.rmtree(path)`
    - 然后重新 `mkdir`
  - 多处输出目录都允许用户经 CLI 自定义。
- 风险：
  - 一旦传入路径错误或层级过高，清空会直接发生，没有统一的边界保护。
  - 复制粘贴式实现会让后续修安全边界时难以一次到位。
- 判断：中风险，属于代码组织与操作安全问题。

## 低优先级问题

### 8. ignored 缓存残留在源码与配置目录，工作区不够干净
- 现象：
  - `src/**/__pycache__/`
  - `configs/__pycache__/`
  - 根目录 `__pycache__/`
  - 均为 ignored，但实际存在。
- 风险：
  - 不会直接污染 Git 历史，但会抬高目录噪音和扫描成本。
  - 也说明“临时产物回收”没有完全执行到位。
- 判断：低风险，属于卫生问题。

### 9. `build_dataset_markdown()` 固定展示 validation 统计，train-only 输出会写出误导性摘要
- 位置：
  - `src/v5vc/streaming_student/stage5_handoff.py:414`
- 现象：
  - markdown 固定读取 `package_summary['validation']` 的维度统计。
  - 若当前构建的是 train split，文档仍以 validation 字段展示。
- 风险：
  - 不是训练逻辑错误，但会让人误读当前 dataset index 的实际内容。
- 判断：低风险，属于报告正确性问题。

## 正向检查结果
- 文本编码纪律总体执行良好：
  - Python 源码中 `read_text/write_text/open` 显式编码扫描未发现违规。
- 入口可执行性正常：
  - `.\python.exe manage.py --help` 正常返回。
  - `compileall` 对 `src/`、`manage.py`、`sandbox_clean_removed_item.py` 全部通过。
- Git 当前工作树在非 ignored 视角下是干净的：
  - `git status --short` 无未提交改动。
- `.gitignore` 设计理念与 `docs/00_context_bootstrap.md` 基本一致：
  - 保留代码、文档、summary、dataset index、少量 checkpoint；
  - 忽略原始音频、缓存、可执行文件和批量可重建 payload。

## 规范性判断

### 文件夹规范
- 结论：部分达标，部分失控。
- 正面：
  - `src/`、`configs/`、`scripts/`、`docs/`、`reports/`、`data_prep/` 角色边界总体清楚。
  - 根目录未长期混放大量一次性结果。
- 问题：
  - `reports/` 体量已经远超“单目录可维护”范围。
  - `docs/` 平铺过多编号文档，发现性不足。
  - ignored 缓存仍散落于源码/配置目录。

### 文件组织规范
- 结论：命名规则强，但局部过度编码。
- 正面：
  - 实验/报告文件名可追溯，参数语义较完整。
- 问题：
  - 文件名携带过多参数，导致路径过长、可读性下降、Git 工具受压。
  - 超大单文件和超长主文档明显违背“长期维护文件不能过大”的要求。

### Git 跟踪规范
- 结论：理念正确，执行边界基本成立，但工作区过深路径已影响工具行为。
- 正面：
  - tracked/ignored 资产边界与恢复优先级基本合理。
  - 大部分重产物留在 ignored 区。
- 问题：
  - Windows 深路径已经让 Git 枚举出现警告。
  - ignored 目录下残留体量巨大，日常工具扫描成本偏高。

### 代码规范
- 结论：基础规范较好，但结构性可维护性偏弱。
- 正面：
  - UTF-8 显式读写基本落实。
  - 无明显 shell 注入模式；`shell=True` 未发现。
  - CLI 总入口、Stage3/Stage5 路线划分总体清楚。
- 问题：
  - megafile、megafunction、重复 helper 明显过多。
  - 关键实验路径仍存在 split 校验缺口和 stale reuse 风险。

## 优先级建议
1. 先修 paired Stage3 的 split 硬校验，阻断 train/validation 污染入口。
2. 立刻修 `streaming_student/stage5_handoff.py` 的 `skip_existing` 复用判定，至少校验 packet path、noise_event_family、semantic_consumer_mode、target_contract_mode。
3. 收紧 `offline_vocoder_training.py` 的 package reuse invalidation，加入 source/target path、record_id、上游 scaffold/contract 指纹校验。
4. 缩短报告与训练产物路径：
   - 目录名改短；
   - 参数改写入 summary/json，不再全塞进路径。
5. 拆分三大单文件：
   - `cli.py`
   - `teacher_first_vc_demo.py`
   - `offline_vocoder_training.py`
6. 对 `docs/` 和 `reports/` 做二级主题目录化：
   - `docs/stage3/`
   - `docs/stage5/`
   - `docs/audit/`
   - `reports/runtime/<topic>/`
7. 清理 ignored cache：
   - `__pycache__/`
   - `configs/__pycache__/`

## 最终判断
- 仓库不是“失控状态”，但已经明显进入“继续堆功能会放大维护成本和误判风险”的阶段。
- 当前最危险的问题不是代码风格，而是：
  - split 边界未完全封死；
  - package 复用判定过松；
  - 产物路径和单文件规模正在侵蚀工具可靠性与人工审计能力。
- 如果不先补这几处边界，后续实验即使继续产出数字，也会越来越难证明这些数字是否可信。
