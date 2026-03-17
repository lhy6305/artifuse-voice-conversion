# 离线 MVP Scaffold 状态

## 当前已具备的命令
### 1. 基线评估
- 命令：
  - `.\python.exe manage.py evaluate-round1-baseline --experiment-metrics reports/experiments/EXP-20260314-001-offline-mvp-baseline.metrics.json`
- 当前作用：
  - 对 round1 manifest 做基线门槛检查。
  - 强制保留 `z_art / e_evt / r_res / latency` 的槽位。
- 当前输出：
  - `reports/eval/round1_baseline/baseline_eval.json`
  - `reports/eval/round1_baseline/baseline_eval.md`

### 2. 训练 dry-run
- 命令：
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-20260314-001-offline-mvp-baseline --dry-run`
- 当前作用：
  - 不启动真实训练。
  - 真实读取一小批音频与文本。
  - 构建词表、batch，并跑一遍 `torch` 前向。
- 当前输出：
  - `reports/training/offline_mvp/EXP-20260314-001-offline-mvp-baseline.train_plan.json`
  - `reports/training/offline_mvp/EXP-20260314-001-offline-mvp-baseline.train_plan.md`

### 3. 单步训练验证
- 命令：
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-20260314-002-offline-mvp-step1`
- 当前作用：
  - 真实读取一小批目标与源音频。
  - 跑通无残差模型前向、首版损失、反向传播和优化器 step。
  - 输出 checkpoint、step log 和训练计划，并回写实验 metrics。
- 当前输出：
  - `reports/training/offline_mvp/EXP-20260314-002-offline-mvp-step1.train_plan.json`
  - `reports/training/offline_mvp/EXP-20260314-002-offline-mvp-step1.train_plan.md`
  - `reports/training/offline_mvp/checkpoints/EXP-20260314-002-offline-mvp-step1.step1.pt`
  - `reports/training/offline_mvp/logs/EXP-20260314-002-offline-mvp-step1.step1.json`
  - `reports/experiments/EXP-20260314-002-offline-mvp-step1.metrics.json`

### 4. 多步训练验证
- 命令：
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-20260314-003-offline-mvp-multistep`
- 当前作用：
  - 读取训练 manifest 并切出固定验证子集。
  - 运行 3 step 真实训练。
  - 每 step 落 step log、checkpoint，并在固定验证切片上做一次 loss 检查。
- 当前输出：
  - `reports/training/offline_mvp/EXP-20260314-003-offline-mvp-multistep.train_plan.json`
  - `reports/training/offline_mvp/EXP-20260314-003-offline-mvp-multistep.train_plan.md`
  - `reports/training/offline_mvp/logs/EXP-20260314-003-offline-mvp-multistep.step1.json`
  - `reports/training/offline_mvp/logs/EXP-20260314-003-offline-mvp-multistep.step2.json`
  - `reports/training/offline_mvp/logs/EXP-20260314-003-offline-mvp-multistep.step3.json`
  - `reports/training/offline_mvp/checkpoints/EXP-20260314-003-offline-mvp-multistep.step1.pt`
  - `reports/training/offline_mvp/checkpoints/EXP-20260314-003-offline-mvp-multistep.step2.pt`
  - `reports/training/offline_mvp/checkpoints/EXP-20260314-003-offline-mvp-multistep.step3.pt`
  - `reports/experiments/EXP-20260314-003-offline-mvp-multistep.metrics.json`

### 5. 带时间打印的小规模训练验证
- 命令：
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-20260314-005-offline-mvp-timed-stdout`
- 当前作用：
  - 在小规模训练阶段验证时间打印规范。
  - 将开始时间、结束时间、总耗时和 step 耗时同时写入计划、step log 和实验 metrics。
  - 验证标准输出会打印 `run_started_at / step_started / step_completed / run_completed`。
- 当前输出：
  - `reports/training/offline_mvp/EXP-20260314-005-offline-mvp-timed-stdout.train_plan.json`
  - `reports/training/offline_mvp/EXP-20260314-005-offline-mvp-timed-stdout.train_plan.md`
  - `reports/training/offline_mvp/logs/EXP-20260314-005-offline-mvp-timed-stdout.step1.json`
  - `reports/training/offline_mvp/logs/EXP-20260314-005-offline-mvp-timed-stdout.step2.json`
  - `reports/training/offline_mvp/logs/EXP-20260314-005-offline-mvp-timed-stdout.step3.json`
  - `reports/experiments/EXP-20260314-005-offline-mvp-timed-stdout.metrics.json`

### 6. hybrid 正式 split 小规模训练验证
- 命令：
  - `.\python.exe manage.py materialize-round1-split`
  - `.\python.exe manage.py train-offline-mvp --experiment-id EXP-20260314-006-offline-mvp-hybrid-split`
- 当前作用：
  - 将用户已确认的 `hybrid_stratified_blocked` 物化为正式 split 目录。
  - 让训练入口从正式 split 读取 train/validation，而不是再用尾部切片。
- 当前输出：
  - `data_prep/round1/splits/hybrid_stratified_blocked/`
  - `reports/training/offline_mvp/EXP-20260314-006-offline-mvp-hybrid-split.train_plan.json`
  - `reports/experiments/EXP-20260314-006-offline-mvp-hybrid-split.metrics.json`

### 7. target special_eval 独立评估
- 命令：
  - `.\python.exe manage.py evaluate-round1-special-eval --experiment-metrics reports/experiments/EXP-20260314-006-offline-mvp-hybrid-split.metrics.json`
- 当前作用：
  - 独立检查 `target_special_eval` 是否与主验证集分离。
  - 确认它是否仍保持 `no_text_voice` challenge slice 的预期属性。
- 当前输出：
  - `reports/eval/round1_special_eval/special_eval.json`
  - `reports/eval/round1_special_eval/special_eval.md`
  - 回写 `reports/experiments/EXP-20260314-006-offline-mvp-hybrid-split.metrics.json`

### 8. offline MVP 控制消融评估
- 命令：
  - `.\python.exe manage.py evaluate-offline-mvp-ablations --experiment-metrics reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`
- 当前作用：
  - 在正式 `hybrid_stratified_blocked` validation split 上评估 `none / zero_z_art / zero_e_evt`。
  - 检查 `z_art / e_evt` 是否真的进入控制融合，而不是名义存在。
- 当前输出：
  - `reports/eval/offline_mvp_ablations/ablation_eval.json`
  - `reports/eval/offline_mvp_ablations/ablation_eval.md`
  - 回写 `reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`

### 9. offline MVP target_special_eval 模型级评估
- 命令：
  - `.\python.exe manage.py evaluate-offline-mvp-special-eval --experiment-metrics reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`
- 当前作用：
  - 对 `target_validation` 与 `target_special_eval` 分别跑模型前向和 loss。
  - 检查 punctuation-only challenge slice 在当前 checkpoint 上是否表现出异常退化。
- 当前输出：
  - `reports/eval/offline_mvp_special_eval/special_eval_model.json`
  - `reports/eval/offline_mvp_special_eval/special_eval_model.md`
  - 回写 `reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`

### 10. offline MVP checkpoint 系列消融汇总
- 命令：
  - `.\python.exe manage.py evaluate-offline-mvp-checkpoint-series --config configs/offline_mvp_train_smallscale_seeded_shuffle.json --experiment-metrics reports/experiments/EXP-20260314-009-offline-mvp-seeded-shuffle.metrics.json`
- 当前作用：
  - 基于实验 metrics 中记录的 `checkpoint_paths`，自动汇总 step5/10/15/20 的消融结果。
  - 检查 `z_art / e_evt` 的 loss 敏感度是否随训练推进而增强。
- 当前输出：
  - `reports/eval/offline_mvp_checkpoint_series/checkpoint_series_eval.json`
  - `reports/eval/offline_mvp_checkpoint_series/checkpoint_series_eval.md`
  - 回写 `reports/experiments/EXP-20260314-009-offline-mvp-seeded-shuffle.metrics.json`

### 11. offline MVP special_eval checkpoint 系列汇总
- 命令：
  - `.\python.exe manage.py evaluate-offline-mvp-special-eval-series --config configs/offline_mvp_train_large_scale_seeded_500.json --experiment-metrics reports/experiments/EXP-20260314-011-offline-mvp-large-scale-500.metrics.json --steps 25 100 250 500`
- 当前作用：
  - 对选定 checkpoint 的 `target_validation` 与 `target_special_eval` 做同口径模型级对比。
  - 专门用于分析 challenge slice 行为是否随训练阶段发生翻转。
- 当前输出：
  - `reports/eval/offline_mvp_special_eval_series_exp011/special_eval_series.json`
  - `reports/eval/offline_mvp_special_eval_series_exp011/special_eval_series.md`
  - 各 step 子目录下的 `special_eval_model.json/.md`

## 当前已验证结论
- round1 数据入口完整可用。
- 目标文本覆盖完整，且仅进入训练侧，不进入当前运行时硬依赖。
- 当前 offline MVP 仍保持：
  - `r_res` 关闭
  - 训练侧使用文本
  - 运行时不要求文本
- 当前 dry-run 已验证：
  - source batch 真实可加载
  - target batch 真实可加载
  - 词表可建立
  - 无残差模型前向可输出 `z_art / event_logits / acoustic`
- 当前单步训练已验证：
  - 首版损失函数可计算
  - 反向传播可执行
  - 优化器 step 可执行
  - checkpoint 与 step log 可落盘
  - 实验 metrics 可自动回写
- 当前多步训练已验证：
  - `num_steps / validation_interval / checkpoint_interval` 已生效
  - 训练 batch 会按 manifest 顺序轮转
  - 固定验证切片会按周期执行
  - 训练历史与验证历史会同时进入训练计划和实验 metrics
- 当前时间与门禁已验证：
  - 训练计划、step log、实验 metrics 都会记录时间
  - 训练命令标准输出会打印时间
  - `run_stage = large_scale` 时必须引用成功的小规模实验
  - 缺少 `prerequisite_experiment_id` 时，大规模训练会被受控失败直接拦截
- 当前正式 split 已验证：
  - 训练入口会优先读取 `data.split_dir`
  - 当前默认 split 为 `hybrid_stratified_blocked`
  - 当前训练/验证计数为 `554 / 62 / 8 / 483 / 54`
- 当前 special_eval 已验证：
  - `target_special_eval` 与常规 `target_validation` 完全分离
  - 当前 8 条全部来自 `no_text_voice`
  - 当前 8 条 `clean text` 全为标点，属于 stress slice，不是普通内容验证
- 当前控制消融已验证：
  - `z_art / e_evt` 已不再是空连线
  - `zero_e_evt` 会明显拉高目标侧和源侧验证损失
  - `zero_z_art` 在 3 step checkpoint 上仅表现为输出变化
  - `zero_z_art` 在 20 step checkpoint 上已开始表现出稳定的正向 loss 退化
- 当前模型级 special_eval 已验证：
  - `target_special_eval` 的总 loss 低于常规 validation，主要因为片段更短、更简单
  - `target_special_eval` 的 `text_aux` loss 明显更高，符合 punctuation-only challenge slice 预期
  - 控制输出统计与常规 validation 接近，当前没有看到“special slice 上控制直接崩坏”
  - 结合人耳复核，当前 special slice 本质上是非完整发声集合，不应用于内容保持主结论
- 当前 seed/shuffle 与 checkpoint 系列已验证：
  - 训练入口已支持固定 seed 和可选 shuffle
  - 训练计划会显式记录 `seed / shuffle_train_records / sampler_mode`
  - 在 seeded-shuffle 实验中，`z_art / e_evt` 的 loss 退化会随 checkpoint 单调增大

## 当前单步训练结果
- 实验：`EXP-20260314-002-offline-mvp-step1`
- `loss_total = 51.73610305786133`
- `target.loss_total = 15.529247283935547`
- `source.loss_total = 36.20685577392578`
- `grad_norm = 28.910484313964844`
- `single_step_validation_enabled = true`

## 当前多步训练结果
- 实验：`EXP-20260314-003-offline-mvp-multistep`
- `num_steps = 3`
- 最新 train `loss_total = 55.10185241699219`
- 最新 validation `loss_total = 52.068878173828125`
- validation 历史：`52.80699 -> 52.43594 -> 52.06888`
- holdout 切片：目标 `8` 条，源 `8` 条
- checkpoint 数量：`3`

## 当前带时间小规模训练结果
- 实验：`EXP-20260314-005-offline-mvp-timed-stdout`
- run timing：`2026-03-14T15:41:57 -> 2026-03-14T15:41:58`
- total duration：`0.889291s`
- step1 / step2 / step3：`0.049911s / 0.028695s / 0.012485s`
- latest validation `loss_total = 50.49259948730469`

## 当前 hybrid split 小规模训练结果
- 实验：`EXP-20260314-006-offline-mvp-hybrid-split`
- split strategy：`materialized_split`
- split counts：目标 `554 train / 62 val / 8 special_eval`；源 `483 train / 54 val`
- total duration：`0.714648s`
- latest validation `loss_total = 51.20595169067383`
- 当前 validation 首批样本已切换为 hybrid split 中的正式验证记录

## 当前 ablation-ready 小规模训练结果
- 实验：`EXP-20260314-007-offline-mvp-ablation-ready`
- run timing：`2026-03-14T16:45:35 -> 2026-03-14T16:45:36`
- total duration：`0.744369s`
- split strategy：`materialized_split`
- latest validation `loss_total = 50.16659927368164`
- checkpoint：`reports/training/offline_mvp/checkpoints/EXP-20260314-007-offline-mvp-ablation-ready.step3.pt`

## 当前 target special_eval 结果
- `overall_ok = True`
- `target_special_eval_record_count = 8`
- `group_counts = {"no_text_voice": 8}`
- `punctuation_only_count = 8`
- 当前解释口径：
  - 这是 challenge-only stress slice
  - 不能替代常规目标验证集

## 当前控制消融结果
- `EXP-20260314-007-offline-mvp-ablation-ready`:
  - `zero_z_art.delta_target_loss_total = -0.008774`
  - `zero_z_art.delta_source_loss_total = -0.013562`
  - `zero_e_evt.delta_target_loss_total = 0.1936`
  - `zero_e_evt.delta_source_loss_total = 0.254943`
- `EXP-20260314-008-offline-mvp-longer-smallscale`:
  - `zero_z_art.delta_target_loss_total = 0.079066`
  - `zero_z_art.delta_source_loss_total = 0.114091`
  - `zero_e_evt.delta_target_loss_total = 1.015739`
  - `zero_e_evt.delta_source_loss_total = 1.504668`
- 当前解释口径：
  - `e_evt` 已持续体现出更强的控制贡献
  - `z_art` 不再只是“接入输出路径”，在更晚 checkpoint 上已经开始表现为可观测 loss 退化
  - 但当前仍属于小规模训练阶段，还不能把这组结果当作最终强结论

## 当前模型级 target_special_eval 结果
- `EXP-20260314-008-offline-mvp-longer-smallscale`
- `target_validation.loss_total = 14.974206`
- `target_special_eval.loss_total = 11.146732`
- `delta_loss_total = -3.827474`
- `delta_loss_text_aux = 0.642243`
- `target_validation.event_prob_mean = 0.490508`
- `target_special_eval.event_prob_mean = 0.490787`
- 当前解释口径：
  - special slice 更短、更简单，所以 acoustic 主损失更低
  - 但因为文本几乎只有标点，`text_aux` stress 明显更强
  - 加上人耳复核“没有完整音节”这一事实后，该 slice 更应解释为非完整发声压力测试
  - 当前 checkpoint 在该 slice 上没有显示出控制量整体崩坏

## 当前 seeded-shuffle 与 checkpoint-series 结果
- 实验：`EXP-20260314-009-offline-mvp-seeded-shuffle`
- `seed = 20260314`
- `sampler_mode = seeded_shuffle`
- `total duration = 1.250314s`
- validation `loss_total`: `49.157608 -> 45.160576 -> 40.778854 -> 35.849232`
- checkpoint-series：
  - `zero_z_art.delta_target_loss_total`: `0.048894 -> 0.096982 -> 0.150881 -> 0.207483`
  - `zero_e_evt.delta_target_loss_total`: `1.053401 -> 1.295615 -> 1.530421 -> 1.737457`
- 当前解释口径：
  - shuffled 训练与多 checkpoint 汇总已经具备可复现性
  - 当前更适合把它解释为“训练过程规范化能力已到位”
  - 用户已确认将 shuffled 采样切为默认训练方案
  - 默认方案决策报告见 `docs/12_default_sampler_decision_report.md`

## 当前默认模板 seeded-shuffle 验证结果
- 实验：`EXP-20260314-010-offline-mvp-default-seeded-template`
- 配置：`configs/offline_mvp_train_template.json`
- `sampler_mode = seeded_shuffle`
- `reproducibility.seed = 20260314`
- `reproducibility.target_sampler_seed = 20260314`
- `reproducibility.source_sampler_seed = 20260315`
- run timing：`2026-03-14T18:03:45 -> 2026-03-14T18:03:45`
- total duration：`0.82421s`
- validation `loss_total`: `52.288879 -> 51.498352 -> 50.715160`
- 当前结论：
  - 默认模板已真正切到 seeded-shuffle
  - 默认入口的时间打印、reproducibility 字段和 checkpoint 落盘均正常

## 当前 500 step large-scale 结果
- 实验：`EXP-20260314-011-offline-mvp-large-scale-500`
- 配置：`configs/offline_mvp_train_large_scale_seeded_500.json`
- `run_stage = large_scale`
- `prerequisite_experiment_id = EXP-20260314-010-offline-mvp-default-seeded-template`
- `sampler_mode = seeded_shuffle`
- total duration：`10.505491s`
- validation `loss_total`：
  - `30.473316 -> 16.476933 -> 9.352869 -> 5.409974 -> ... -> 3.321292`
- checkpoint 数量：`20`
- 当前结论：
  - 首个 large-scale 训练已跑通，速度可接受
  - `z_art` 在后期继续增强
  - `e_evt` 仍有效，但在后期的消融敏感度明显回落
  - special slice 从 `step25` 的“更容易”翻转成 `step100+` 的“更难”

## 当前边界
- 还没有验证集评估汇总、最佳模型选择与早停逻辑。
- 还没有 latency 实测逻辑。
- 当前 checkpoint 仅用于结构验证，还不能视为可用模型版本。
- 当前时间数据只来自小规模验证，不应用于完整训练耗时承诺。
- 旧 checkpoint 不兼容当前控制融合结构，不能混用做消融。

## 下一步
1. 基于 `docs/15_e_evt_early_late_analysis.md`，整理 `e_evt` 约束增强方向的方案报告。
2. 评估是否需要为 special slice 增加更贴近运行时的非文本指标。
3. 视需要开始数据层调查，确认事件标签是否过粗或易被主干替代。
