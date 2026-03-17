# 方案决策记录

## 2026-03-14 预处理方案确认
本页记录已经由用户明确确认、可直接进入实现的方案。后续若有变更，只追加新条目，不覆盖历史决策。

### 1. 文本数据的训练/推理定位
- 已确认结论：
  - 当前系统推理阶段不把文本作为必选输入。
  - 文本进入训练和数据处理流程，不进入当前 MVP 的运行时强依赖。
- 当前实施范围：
  - 用于数据清洗和规范化。
  - 用于后续对齐、CTC/ASR 辅助监督、事件边界和内容评估。
- 不在当前阶段实施的内容：
  - 文本驱动推理。
  - 需要运行时额外提供文本输入的链路。

### 2. 目标说话人文本清洗策略
- 已确认结论：
  - 去除特殊符号，仅保留主要标点。
- 当前实施口径：
  - 保留主要停顿和语气相关标点。
  - 对特殊符号做删除或归一化。
  - 原始文本保留在 manifest 中，清洗结果另存字段，不覆盖原始标签。
- 当前实现目标：
  - 给出可追溯的清洗映射。
  - 后续如需调整规则，可重跑而不破坏原始数据。

### 3. 源录音切分策略
- 已确认结论：
  - 按“存在明显内容”的部分切成小片段。
  - 每段前后保留少量静音缓冲，防止误裁切。
  - 判断源录音是否存在底噪，若存在，按底噪阈值做响度裁切或静音替换。
  - 将明显突变或峰值片段单独切出供用户试听。
- 当前实施口径：
  - 原始大文件保留不动。
  - 切分结果输出到独立目录。
  - 峰值片段与训练候选片段分开存放。

### 4. 目标说话人音频格式筛选策略
- 已确认结论：
  - 目标音频当前阶段只保留主流格式部分进入训练副本。
  - 非主流采样率或双声道样本暂时隔离，不进入第一版训练副本。
- 当前实施口径：
  - 原始数据保持不动。
  - manifest 中明确区分：
    - 主流样本
    - 隔离样本
  - 后续如需纳入隔离样本，再单独出补充方案。

### 5. 当前可直接推进的实现项
1. 文本规范化脚本。
2. 目标数据样本筛选与标准化 manifest。
3. 源录音内容段检测和切分。
4. 峰值/突变片段导出与试听清单。

### 6. 当前仍需后续再议的事项
1. 主要标点的最终集合是否继续细化。
2. 底噪门限和静音替换参数是否需要按试听样本调参。
3. 隔离样本未来是否二次重采样后纳入训练副本。

## 2026-03-14 峰值片段人工复核结论
### 1. 已确认处置
- `peak_005_0001221975_top_peak.wav`
  - 结论：删除。
  - 原因：麦克风吹气瞬态。
- `peak_008_0001665045_abrupt_rise.wav`
  - 结论：round1 删除。
  - 原因：咳嗽瞬态。
- `peak_010_0002051985_abrupt_rise.wav`
  - 结论：不整段按异常丢弃，只排除开头短非人声瞬态区间。
  - 当前实现：排除 `2051.385s` 到 `2051.770s`。
- `peak_011_0002370615_top_peak.wav`
  - 结论：保留。
  - 原因：激动导致的破音，但属于纯人声。
- `peak_014_0003049665_top_peak.wav`
  - 结论：round1 删除。
  - 原因：离麦克风距离明显不稳定。
- `peak_015_0003614595_abrupt_rise.wav`
  - 结论：round1 删除。
  - 原因：叹气瞬态。
- 未提到的其余 peaks：
  - 结论：按正常说话人声处理。

### 2. 源片段边界规则确认
- 已确认结论：
  - 在代码层面增加边界静区约束。
- 当前实施口径：
  - 片段时长至少 `0.5s`。
  - 片段起止边界必须落在低于阈值的静区中。
  - 边界相连静区长度至少 `0.5s`。
- 当前实现参数：
  - 边界阈值 `-38.0 dBFS`
  - 最小静区长度 `500 ms`

## 2026-03-14 round1 正式训练/验证拆分方案确认
### 1. 已确认结论
- 用户已确认采用 `hybrid_stratified_blocked` 作为 round1 正式拆分方案。

### 2. 当前实施口径
- 目标侧：
  - 主分布 `<root>` 中取 `62` 条作为常规验证集。
  - `no_text_voice` 的 `8` 条不混入常规验证集，单独作为 `special_eval / challenge eval`。
- 源侧：
  - 采用跨时间轴的 blocked holdout。
  - 取 `54` 条作为验证集，其余作为训练集。

### 3. 当前落盘产物
- 正式 split 目录：
  - `data_prep/round1/splits/hybrid_stratified_blocked/`
- 关键文件：
  - `target_train.jsonl`
  - `target_validation.jsonl`
  - `target_special_eval.jsonl`
  - `source_train.jsonl`
  - `source_validation.jsonl`
  - `split_summary.json`
  - `split_assignment.json`

### 4. 当前执行范围
- offline MVP 训练入口默认读取上述正式 split。
- 当前小规模训练已验证正式 split 生效。
- `target_special_eval.jsonl` 已接入独立数据级评估与模型级评估命令。

## 2026-03-14 `no_text_voice` 人耳复核结论
### 1. 已确认结论
- 用户补充确认：
  - 目标音频的 `no_text_voice` 子集里没有任何一个完整音节。
  - 该子集内容本质上是喘气等非完整语音片段。

### 2. 当前解释口径
- `target_special_eval` 不能用于内容保持或正常发音质量的主结论。
- 该集合只适合作为：
  - punctuation-only / near-nonverbal challenge slice
  - 极短非完整发声片段的压力测试

### 3. 对当前评估的影响
- 数据级评估仍然保留，用于确认 split 隔离与子集属性。
- 模型级评估仍然保留，但必须单独汇报，不与常规 validation 混合平均。
- 后续若需要内容级 special eval，必须另找包含完整音节或短词的独立目标子集。

## 2026-03-14 默认训练采样方案确认
### 1. 已确认结论
- 用户已确认：
  - 后续默认训练采样方案切换为基于固定 seed 的 shuffled 采样。

### 2. 当前实施口径
- 默认训练模板使用：
  - `seed = 20260314`
  - `shuffle_train_records = true`
- 训练计划、step log 和实验 metrics 必须继续显式记录：
  - `seed`
  - `target_sampler_seed`
  - `source_sampler_seed`
  - `sampler_mode`

### 3. 当前解释口径
- 该决策的主要依据不是当前单次小规模对比里主 validation loss 最低。
- 该决策的主要依据是：
  - 可复现性更强。
  - `z_art / e_evt` 的控制学习趋势更早、更清晰。
  - 更符合当前阶段“优先验证控制主链成立”的目标。

### 4. 当前保留项
- 顺序采样能力继续保留，作为：
  - 对照实验能力
  - 排障回退手段
  - 非默认采样方案

## 2026-03-14 大规模训练进入路线确认
### 1. 已确认结论
- 用户已确认：
  - 不走 `100 step` 中等规模校准 run。
  - 直接进入 `500 step` 的 `large_scale` 训练。

### 2. 当前实施口径
- 训练配置：
  - `configs/offline_mvp_train_large_scale_seeded_500.json`
- 核心参数：
  - `run_stage = large_scale`
  - `prerequisite_experiment_id = EXP-20260314-010-offline-mvp-default-seeded-template`
  - `num_steps = 500`
  - `validation_interval = 25`
  - `checkpoint_interval = 25`
  - `seed = 20260314`
  - `shuffle_train_records = true`

### 3. 当前边界
- 用户已明确表示：
  - 若速度不可接受，将人工叫停并反馈。
- 当前实现仍需保持：
  - 时间打印
  - checkpoint 周期写盘
  - validation 周期检查
  - 实验 metrics 持续落盘

## 2026-03-14 `方案 D / A1` 首轮执行结果确认
### 1. 已确认事实
- 用户已确认按方案 `D` 推进。
- 已先执行 `A1`：
  - `A1 dry-run`
  - 真实 `500 step` large-scale 实验
  - final ablation
  - checkpoint-series
  - final special-eval

### 2. 当前结论口径
- `A1` 当前这组参数不升级为默认方案。
- 继续保留默认 large-scale 配置为：
  - `configs/offline_mvp_train_large_scale_seeded_500.json`
- `A1` 本轮的主要结论是：
  - `e_evt` 后期依赖略有回升；
  - 但整体验证损失明显恶化；
  - 且 `z_art` 后期贡献被压弱。

### 3. 当前归档位置
- 设计草案：
  - `docs/17_e_evt_constraint_a1_draft.md`
- 首轮实跑报告：
  - `docs/18_e_evt_constraint_a1_run_report.md`
- 对应实验：
  - `EXP-20260314-013-offline-mvp-evt-a1-large-scale`

## 2026-03-14 `方案 B` 路线确认
### 1. 已确认结论
- 用户已确认：
  - 不再继续 `A2`
  - 直接转向方案 `B`
  - 源侧当前不做手工全文本标注
  - `B1` 采用不对称监督：
    - 目标侧使用文本与标点停顿线索
    - 源侧继续保持纯音频监督

### 2. 当前已落盘的启动产物
- `B1` supervision inventory 代码入口：
  - `src/v5vc/b1_supervision_inventory.py`
- sidecar：
  - `data_prep/round1/b1_supervision/target_supervision_inventory.jsonl`
  - `data_prep/round1/b1_supervision/source_supervision_inventory.jsonl`
- 报告：
  - `reports/data/b1_supervision_inventory/b1_supervision_inventory.md`
  - `docs/20_b_route_bootstrap_report.md`

### 3. 当前口径
- 方案 `B` 当前先从离线可落的 `B1-offline-minimal` 启动更稳。
- 但是否直接进入 `B1-offline-minimal` 训练接入，还是先只搭 `B2` 长线接口，仍应由用户拍板。

## 2026-03-14 `B1-offline-minimal` 首轮实现确认
### 1. 已确认事实
- `B1-offline-minimal` 已完成首轮代码接入与小规模真实训练验证。
- 当前配置文件：
  - `configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json`
- 对应实验：
  - `EXP-20260314-014-offline-mvp-b1-smallscale`

### 2. 当前结论口径
- `B1` 已证明可以稳定接入现有 offline MVP。
- 当前还不能说它已经整体优于旧 seeded-shuffle 小规模基线。
- 当前可以说：
  - 它没有破坏主流程；
  - 且在 20 step 小规模下，`z_art / e_evt` 消融敏感度更强。

## 2026-03-14 `B1.1-A -> C` 推进确认
### 1. 已确认结论
- 用户已确认：
  - 按既定顺序继续推进：
    - 先做 `B1.1-A`
    - 若证据仍不够，再继续 `C`

### 2. 当前阶段结论
- `B1.1-A` 已完成 `100 step` 小规模校准。
- 当前结论是：
  - `B1.1-A` 没有把训练拖坏；
  - 但未在主验证集上形成比 `B1` 更明确的增益；
  - 因此按既定顺序继续推进到 `C1`。

### 3. 当前已落盘产物
- `B1.1-A` 报告：
  - `docs/24_b1_1a_run_report.md`
- `C1` 弱事件提示启动报告：
  - `docs/25_c1_weak_event_hints_bootstrap_report.md`
- `C1` sidecar：
  - `data_prep/round1/c1_weak_event_hints/target_weak_event_hints.jsonl`

### 3. 当前归档位置
- 启动报告：
  - `docs/20_b_route_bootstrap_report.md`
- 首轮实现与验证报告：
  - `docs/21_b1_offline_minimal_report.md`
