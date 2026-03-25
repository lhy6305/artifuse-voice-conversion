# 346. Stage5 source semantic parity stage5 metadata plumbing 报告

## 结论
- `paired_parallel_source_semantic_parity_sidecar`
  已正式接入
  Stage5 package / index metadata。
- 当前状态是：
  - 资产存在
  - metadata 接通
  - 但 forward consumer
    仍未启用
- 这一步的意义是：
  - 以后若继续做
    source-aware semantic route，
    不会再混淆成
    “sidecar 根本没进 package”

## 一、本轮做了什么
- `offline_mvp.data`
  新增：
  - parity sidecar
    load / infer / overview
- `offline_vocoder_training`
  新增：
  - dataset builder
    读取
    `--source-semantic-parity-sidecar`
  - package payload / summary
    写入：
    - `source_semantic_parity_sidecar`
    - `source_semantic_parity_overview`
  - dataset index
    写入：
    - `source_semantic_parity_sidecar_path`
    - `source_semantic_parity_summary`
- `cli.py`
  新增：
  - `build-offline-mvp-nores-vocoder-dataset-packages --source-semantic-parity-sidecar`

## 二、关键实现约束
- source parity attach
  必须按：
  - `source_record_id`
- 不能按：
  - `target_record_id`
  - `pair record_id`
- 原因是：
  - 这份 sidecar
    的主键就是
    source 侧记录
  - 它表示的是：
    source frame axis
    上的 parity semantic

## 三、验证命令
- 已执行：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --train-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_train_pairs.jsonl `
  --validation-pair-spec data_prep/round1_1/stage5_paired_source_to_target_overfit_smoke/parallel_validation_pairs.jsonl `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_sourceparityplumb_smoke_round1_1 `
  --device cpu `
  --selection-mode file_order `
  --skip-full-pass-verify `
  --target-event-semantic-sidecar data_prep/round1_1/target_event_semantic_sidecar/target_event_semantic_sidecar.jsonl `
  --target-event-timing-semantic-sidecar data_prep/round1_1/target_event_timing_semantic_sidecar/target_event_timing_semantic_sidecar.jsonl `
  --source-semantic-parity-sidecar data_prep/round1_1/paired_parallel_source_semantic_parity_sidecar/paired_parallel_source_semantic_parity_sidecar.jsonl
```

## 四、验证结果
- smoke package build：
  - `train_packages = 2`
  - `validation_packages = 2`
- dataset index
  已记录：
  - `source_semantic_parity_sidecar_path`
  - `summary.train.source_semantic_parity_summary.present_count = 2`
  - `summary.validation.source_semantic_parity_summary.present_count = 2`
- `107`
  package
  已记录：
  - `source_semantic_parity_sidecar_present = true`
  - `source_semantic_parity_overview.parity_contract_version = paired_parallel_source_semantic_parity_sidecar_v1`
  - `source_semantic_parity_overview.parity_status = matched_target_semantic_and_timing`
  - `source_semantic_parity_overview.semantic_ready_for_source_side_bootstrap = true`

## 五、当前阶段判断
- 现在可以明确拆开三层问题：
  1. source-side parity
     资产是否存在
  2. metadata
     是否接通
  3. consumer / supervision
     是否有效
- 也就是说：
  - 如果下一轮
    source-aware route
    仍失败，
  - 就不应再怀疑：
    - path 没传到底
    - attach key
      用错

## 六、下一步
1. 不要立刻回到
   target-only
   semantic/timing
   变体
2. 下一轮更合理的是：
   - 评估
     source parity
     该接到
     Stage5 consumer
     还是更上游 supervision
3. 当前更推荐先做：
   - source-parity aware
     consumer 设计草案
   - 但继续保持
     “不是 source-native semantic”
     的边界说明
