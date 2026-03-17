# round1 训练/验证拆分候选分析

- manifest_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/manifests

## 全量数据概况
- target.record_count: 666
- target.group_counts: {"<root>": 658, "no_text_voice": 8}
- target.duration_sec: {"min": 0.229002, "p50": 5.010998, "mean": 6.098379, "max": 25.493991}
- target.clean_char_count: {"min": 1.0, "p50": 20.0, "mean": 24.418919, "max": 85.0}
- source.record_count: 537
- source.start_sec: {"min": 20.11, "p50": 1649.41, "mean": 1708.173017, "max": 3666.91}
- source.duration_sec: {"min": 0.51, "p50": 1.05, "mean": 1.220391, "max": 3.51}

## 当前建议
- recommended_option: hybrid_stratified_blocked
- reason: 目标侧当前尾部 8 条全部来自 no_text_voice 子组，源侧当前尾部 8 条全部集中在录音尾部。推荐将目标主集做分布覆盖抽样，把 no_text_voice 作为单独 challenge eval，同时把源录音验证集改为跨时间轴的分段 blocked holdout。

## 方案 current_tail_holdout
- description: 当前实现：目标/源都取尾部 8 条作为固定验证切片。
- target.validation_count: 8
- target.special_eval_count: 0
- target.validation_groups: {"<root>": 8}
- source.validation_count: 8
- source.validation_start_sec: {"min": 3612.1, "p50": 3652.39, "mean": 3644.15125, "max": 3666.91}
- source.boundary_contacts: {"validation_record_count": 8, "adjacent_train_contacts": 1}
- pros:
  - 实现最简单，已在当前训练入口中验证可运行。
  - 源侧尾部切片连续，时间轴泄漏边界少。
- cons:
  - 目标侧 8 条全部来自 no_text_voice 子组，严重偏离主训练分布。
  - 源侧 8 条全部位于录音尾部，只覆盖极窄时间区域。
  - 验证样本过少，波动大，不适合作为正式评估拆分。

## 方案 random_split_seed20260314
- description: 目标/源都按 10% 做固定随机拆分，使用种子 20260314。
- target.validation_count: 67
- target.special_eval_count: 0
- target.validation_groups: {"<root>": 66, "no_text_voice": 1}
- source.validation_count: 54
- source.validation_start_sec: {"min": 23.77, "p50": 1496.02, "mean": 1600.843889, "max": 3607.03}
- source.boundary_contacts: {"validation_record_count": 54, "adjacent_train_contacts": 96}
- pros:
  - 分布覆盖通常优于尾部切片，验证集规模更接近正式训练需求。
  - 实现成本低，后续复现实验方便。
- cons:
  - 源侧来自同一长录音，随机拆分会把时间上相邻片段打散到 train/val，泄漏风险高。
  - 目标侧 no_text_voice 子组会混入常规验证集，难以区分主分布和特殊子组表现。

## 方案 hybrid_stratified_blocked
- description: 推荐方案：目标主集按时长/文本长度做均匀覆盖抽样，no_text_voice 8 条单独作为 challenge eval；源侧按时间轴做跨全局的 blocked holdout。
- target.validation_count: 66
- target.special_eval_count: 8
- target.validation_groups: {"<root>": 66}
- source.validation_count: 54
- source.validation_start_sec: {"min": 188.8, "p50": 1648.15, "mean": 1712.126111, "max": 3343.84}
- source.boundary_contacts: {"validation_record_count": 54, "adjacent_train_contacts": 12}
- pros:
  - 目标主验证集更接近主训练分布，同时保留 no_text_voice 独立观察位。
  - 源侧验证集跨越整段录音，分布覆盖明显优于尾部切片。
  - 相比随机拆分，源侧 blocked holdout 能减少相邻片段泄漏。
- cons:
  - 实现与维护成本高于随机拆分。
  - blocked holdout 仍不是严格按语义或场景分层，后续仍需用户确认是否采用。

## 产物
- `split_analysis_summary.json` / `split_analysis_summary.md`
- `options/*.json`

## 注意
- 本报告只生成候选方案，不修改正式训练 manifest。
- 方案最终选择必须由用户确认后再落地到实际训练拆分逻辑。
