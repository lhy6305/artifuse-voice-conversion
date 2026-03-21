# 2026-03-20 Stage5 clean-only vs baseline 对照训练报告

## 结论
- 事前预测：
  `clean-only` 更可能只是局部更干净，但总体持平或略弱于当前基线。
- 实际结果：
  预测命中。
  `clean-only` 没有赢，且在同一验证面上的交叉评估里仍然小幅落后于 baseline。
- 当前决策：
  不把
  `hybrid_stratified_blocked_target_clean_no_reverb`
  升格为正式训练主线。
  当前正式主线仍保留原始
  `hybrid_stratified_blocked`
  target split，
  混响样本先保留 sidecar 标记，不触发删样本重训。

## 本次实跑
- clean-only dataset index:
  `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1_clean_no_reverb/offline_mvp_nores_vocoder_dataset_index.json`
- clean-only dataset loop:
  `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_clean_no_reverb_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- baseline dataset loop:
  `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- common-eval report:
  `reports/runtime/offline_mvp_nores_vocoder_clean_no_reverb_comparison_round1_1/clean_no_reverb_vs_baseline_common_eval.md`

## 同训练面结果
- baseline dataset loop:
  - train/validation packages:
    `592 / 66`
  - best checkpoint:
    `step72`
  - validation loss_total:
    `0.564671`
- clean-only dataset loop:
  - train/validation packages:
    `578 / 63`
  - best checkpoint:
    `step72`
  - validation loss_total:
    `0.570703`
- 直接看各自 loop summary，
  clean-only 比 baseline 差
  `+0.006032`。
  但这一步不是严格 apples-to-apples，
  因为 validation 面也一起从
  `66`
  裁到了
  `63`。

## 同验证面交叉评估
- 在原正式 baseline validation
  `66`
  条包上：
  - baseline checkpoint:
    `0.564671`
  - clean-only checkpoint:
    `0.567886`
  - delta:
    `+0.003215`
- 在 clean-only validation
  `63`
  条包上：
  - baseline checkpoint:
    `0.568566`
  - clean-only checkpoint:
    `0.570703`
  - delta:
    `+0.002137`

## 解释
- 这说明“删掉
  `chapter3_5 / chapter3_6`
  的 reverb_like target train 子集”
  至少在当前 Stage5 no-res vocoder 目标上，
  没有带来整体收益。
- 更合理的解释不是
  “混响样本一定有害”，
  而是这批样本当前更像是带来一点目标域多样性 / 鲁棒性，
  直接拿掉后并没有换来更好的整体对齐。
- 因此当前更合适的治理动作仍然是：
  先保留样本，
  用 sidecar 标注，
  后续只在更窄的 clean-only 假设验证中使用，
  不覆盖正式主线 split。

## 顺手修复
- 本次第一次重跑时，
  `clean-only` 派生 split 的 JSONL 被 PowerShell 写成了带 BOM 的 UTF-8，
  `load_jsonl()` 按
  `utf-8`
  读取会直接报
  `Unexpected UTF-8 BOM`。
- 已在
  `src/v5vc/manifest_builder.py`
  把 JSONL 读取编码改为
  `utf-8-sig`，
  让 loader 默认兼容 BOM。
