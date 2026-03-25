# 350. source semantic parity sidecar 时长元数据修复报告

## 结论
- `paired_parallel_source_semantic_parity_sidecar`
  之前错误地信任了
  pair spec
  里的
  `source_audio.duration_sec`，
  导致 source-side parity
  的时长和帧数都漂移到了错误区间。
- 现在已经改成：
  - 直接读取真实
    source/target wav
    元数据
  - 再计算
    `source_duration_sec / target_duration_sec / source_estimated_frame_count`
- 修复后：
  - parity sidecar
    的
    `source_estimated_frame_count`
    已从旧的
    `1068/968`
    变成真实的
    `657/660`
  - `source_to_target_duration_ratio`
    也从伪造的
    `1.436329`
    回到真实的
    `0.930744`
- 这说明：
  - 旧 sidecar
    不是“source 真的更长”，
    而是
    pair spec
    的 source duration metadata
    已漂移。

## 一、本轮代码改动
- 更新：
  - `src/v5vc/event_semantics.py`
- 关键修复：
  1. `group_parallel_pair_rows_by_source_record_id(...)`
     不再把
     pair spec
     的
     `duration_sec`
     当真值，
     而是直接读取：
     - `source_audio_path`
     - `target_audio_path`
     对应 wav
     的真实时长
  2. parity row
     现在同时保留：
     - `source_duration_sec`
       真实 wav 时长
     - `target_duration_sec`
       真实 wav 时长
     - `source_duration_sec_pair_spec`
     - `target_duration_sec_pair_spec`
     - `source_duration_metadata_drift_sec`
     - `target_duration_metadata_drift_sec`
  3. summary
     新增：
     - `source_duration_metadata_drift_sec_stats`
     - `target_duration_metadata_drift_sec_stats`
  4. markdown summary
     也会把上述 drift
     统计写出来

## 二、执行命令
- 已执行：
```powershell
.\python.exe -m py_compile `
  src/v5vc/event_semantics.py `
  src/v5vc/streaming_student/training_data_entry.py `
  src/v5vc/cli.py
```

- 已重建：
```powershell
.\python.exe manage.py build-paired-parallel-source-semantic-parity-sidecar `
  --pair-spec-path data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --pair-spec-path data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --target-event-semantic-sidecar-path data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar-path data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl `
  --data-output-dir data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar `
  --report-output-dir reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar
```

## 三、关键结果
- 新 summary：
  - `reports/data/round1_1_paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar_summary.json`
- 当前关键值：
  - `source_estimated_frame_count_stats.mean = 658.5`
  - `source_to_target_duration_ratio_stats.mean = 0.930744`
  - `source_duration_metadata_drift_sec_stats.mean = 1.304977`
  - `target_duration_metadata_drift_sec_stats.mean = 0.0`
- 新 row
  也已写出明确 drift：
  - `107`
    - `source_duration_sec = 2.39`
    - `source_duration_sec_pair_spec = 3.881224`
    - `source_duration_metadata_drift_sec = 1.491224`
    - `source_estimated_frame_count = 657`
  - `132`
    - `source_duration_sec = 2.4`
    - `source_duration_sec_pair_spec = 3.51873`
    - `source_duration_metadata_drift_sec = 1.11873`
    - `source_estimated_frame_count = 660`

## 四、当前判断
- 现在可以正式写死：
  1. 旧的 source parity sidecar
     里那组
     `source_duration_sec / source_estimated_frame_count`
     不是可信 ground truth
  2. 后续所有
     paired source-side semantic
     资产，
     不能再依赖
     pair spec
     内嵌的 source duration metadata
  3. 真实 source-side parity
     资产已经修正到与 wav
     一致，
     但这不等于
     source 和 target teacher
     已经帧对齐

## 五、下一步
1. 保留这次修复后的
   source parity asset
   作为 paired Stage3
   的唯一可信 source-side 语义底座
2. 下一步应继续核对：
   - source 真实时长
   与
   target teacher
   的真实帧长差距
3. 不要再把
   “pair spec 说 source 更长”
   当作事实使用
