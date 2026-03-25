# 343. Stage5 target event timing semantic metadata plumbing 报告

## 结论
- 已把
  `target_event_timing_semantic_sidecar`
  接进
  Stage5 dataset package / index
  的 metadata 链。
- 当前还没有做新的
  time-aware consumer
  训练；
  这一步只负责：
  - attach
  - summarize
  - validate
- 结果是：
  - timing sidecar
    现在不再只是数据目录里的独立资产
  - 它已经能随
    Stage5 package
    一起被正式消费与审计

## 一、本轮代码改动
- 更新：
  - `src/v5vc/offline_mvp/data.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增能力：
  1. `offline_mvp.data`
     增加：
     - `load_target_event_timing_semantic_sidecar_map(...)`
     - `infer_target_event_timing_semantic_sidecar_path(...)`
     - `build_record_timing_semantic_overview(...)`
  2. Stage5 package builder
     增加：
     - `--target-event-timing-semantic-sidecar`
  3. package / index / summary / markdown
     均会记录：
     - `target_event_timing_semantic_sidecar_present`
     - `target_timing_semantic_overview`
     - `timing_semantic_sidecar_summary`

## 二、验证
- 已执行：
  - `.\python.exe -m py_compile src/v5vc/offline_mvp/data.py src/v5vc/offline_vocoder_training.py src/v5vc/cli.py`
  - 结果：
    - `py_compile_ok`
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_timingplumb_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify `
  --target-event-semantic-sidecar data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl
```
- 结果：
  - `train_packages = 2`
  - `validation_packages = 2`
  - `duration_sec = 3.027572`

## 三、关键验证结果
- dataset index
  已明确记录：
  - `target_event_timing_semantic_sidecar_path`
  - `timing_semantic_sidecar_summary`
- smoke index 结果：
  - `present_count = 2`
  - `timing_contract_version_counts = {'target_event_timing_semantic_sidecar_v1': 2}`
  - `timing_alignment_type_counts = {'weak_punctuation_lexical_progress_v1': 2}`
  - `timeline_event_count_mean = 3.0`
- 具体到
  `chapter3_17_firefly_107`
  这个 package，
  已能看到：
  - `timeline_event_count = 4`
  - `clause_region_count = 2`
  - `pause_boundary_event_count = 1`
  - `terminal_boundary_event_count = 1`
  - `weak_time_alignment_ready_for_target_side_bootstrap = true`

## 四、当前阶段判断
- 这一步拿到的不是：
  - 听感成功
  - 或 consumer 成功
- 它拿到的是：
  1. timing asset
     已正式并入
     Stage5 package contract
  2. 下一轮如果要试
     time-aware consumer，
     可以直接从 package
     读取标准 timing metadata
  3. 可以把：
     - 资产层是否存在
     - metadata 是否接通
     - consumer 是否有效
     这三层问题明确拆开

## 五、下一步
1. 下一步应在这条 metadata 链基础上，
   设计第一版
   time-aware semantic consumer
2. 仍保持边界：
   - target-side only
   - weak timing only
   - 不把这份 sidecar
     误称为完整
     design-state
     `e_evt`
