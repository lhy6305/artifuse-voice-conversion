# Stage5 chapter3_5 / chapter3_6 混响标注落盘报告

## 本次动作

已根据你的人工试听结论，
把 `chapter3_5` 与 `chapter3_6` 的 target 样本整体标记为
`reverb_like`。

标注资产落在：

- `data_prep/round1_1/annotations/target_quality_annotations_chapter3_5_3_6_reverb.jsonl`

同时补了摘要：

- `reports/data/round1_1_target_quality_annotations/target_quality_annotation_summary.json`
- `reports/data/round1_1_target_quality_annotations/target_quality_annotation_summary.md`

## 标注范围

- `chapter3_5`
  - `6` 条
- `chapter3_6`
  - `11` 条
- 合计
  - `17` 条

## 采用的标注策略

这次没有直接改写现有
`target_train.jsonl / target_validation.jsonl`
  的 schema，
而是单独新增 sidecar 标注文件。

这样做的原因是：

1. 不会破坏现有训练/导出/分析入口对 manifest 结构的假设。
2. 后续若要按
   `reverb_like`
   做筛样、做 challenge bucket、
   或做对照训练，
   可以直接复用这份 sidecar。
3. 当前这条标签来源于人工听审，
   不是自动声学检测，
   单独 sidecar 更符合证据性质。

## 当前建议

- 默认保留这些样本，
  不因本次标注立即删样本重训。
- 后续若要做更严格的数据治理，
  先把这份 sidecar 接入：
  - challenge eval
  - robustness bucket
  - selective ablation
- 如果未来要做
  “clean-only train”
  对照实验，
  就以这份 sidecar 作为剔除清单起点。
