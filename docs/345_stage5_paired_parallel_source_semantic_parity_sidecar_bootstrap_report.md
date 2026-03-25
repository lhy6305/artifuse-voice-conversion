# 345. Stage5 paired-parallel source semantic parity sidecar bootstrap 报告

## 结论
- 第一份
  `source-side / parity-aware`
  semantic bootstrap
  资产已正式生成。
- 这份资产不是：
  - source-native text semantic
  - source-native phone semantic
  - source forced alignment
- 它是：
  - 利用 paired parallel
    同内容 target 语义
  - 按 lexical ratio
    投影到 source frame 轴上的
    bootstrap parity sidecar

## 一、本轮做了什么
- 新增命令：
  - `build-paired-parallel-source-semantic-parity-sidecar`
- 新资产保留两类信息：
  - source-side
    `clause_region`
  - source-side
    `pause_boundary_window / terminal_boundary_window`
- 语义来源明确保持为：
  - paired target transfer
  - 而不是 source-native supervision

## 二、代码改动
- 更新：
  - `src/v5vc/event_semantics.py`
  - `src/v5vc/cli.py`
- 新 contract 常量：
  - `paired_parallel_source_semantic_parity_sidecar_v1`
  - `source_paired_parallel_bootstrap_semantics_v1`
  - `paired_parallel_target_to_source_same_content_v1`

## 三、执行命令
- 已执行：
```powershell
.\python.exe manage.py build-paired-parallel-source-semantic-parity-sidecar `
  --pair-spec-path data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --pair-spec-path data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --target-event-semantic-sidecar-path data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar-path data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl `
  --data-output-dir data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar `
  --report-output-dir reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar
```

## 四、产物位置
- 数据：
  - `data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar.jsonl`
- 摘要：
  - `reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar_summary.json`
  - `reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar_summary.md`

## 五、关键结果
- 当前 overfit smoke
  摘要：
  - `record_count = 2`
  - `parity_status_counts.matched_target_semantic_and_timing = 2`
  - `semantic_ready_for_source_side_bootstrap_count = 2`
  - `source_estimated_frame_count_stats.mean = 1018.0`
  - `source_to_target_duration_ratio_stats.mean = 1.436329`
- `107`
  的 source-side 投影：
  - source frames:
    `1068`
  - 两段 clause
    被投到：
    - `0..426`
    - `427..1067`
  - pause boundary
    落在：
    - `425..429`
  - terminal boundary
    落在：
    - `1065..1067`
- `132`
  的 source-side 投影：
  - source frames:
    `968`
  - 单 clause
    覆盖：
    - `0..967`
  - terminal boundary
    落在：
    - `965..967`

## 六、当前阶段判断
- 这一步已经补上：
  - 第一份可审计的
    source-side parity-aware
    semantic asset
- 但还没有完成：
  - source-native semantic
  - design-state
    `e_evt`
  - source-side consumer
- 所以正确表述应保持为：
  - parity bootstrap 已就位
  - 不是 source semantic 已完成

## 七、下一步
1. 先把这份
   parity sidecar
   接入
   Stage5 package / index metadata
2. 明确验证：
   - attach key
     使用
     `source_record_id`
   - 不误挂到
     `target_record_id`
3. metadata
   稳定后，
   再决定：
   - 是继续做
     source-aware consumer
   - 还是转向更上游的
     supervision route
