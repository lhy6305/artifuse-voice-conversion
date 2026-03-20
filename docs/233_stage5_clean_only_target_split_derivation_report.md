# Stage5 clean-only target split 派生报告

## 本次动作

已基于当前推荐拆分
`hybrid_stratified_blocked`
和最新
`reverb_like`
标注 sidecar，
派生出一套可直接用于
clean-only
对照实验的 split：

- `data_prep/round1_1/splits/hybrid_stratified_blocked_target_clean_no_reverb/`

其中包含：

- `target_train.jsonl`
- `target_validation.jsonl`
- `target_special_eval.jsonl`
- `source_train.jsonl`
- `source_validation.jsonl`
- `split_summary.json`
- `split_summary.md`

## 派生规则

- 仅根据
  `data_prep/round1_1/annotations/target_quality_annotations_chapter3_5_3_6_reverb.jsonl`
  中的
  `reverb_like`
  标注，
  从 target train / validation
  里剔除对应记录
- source 侧保持不变
- `target_special_eval`
  保持不变，
  因为本轮标注没有命中其中记录

## 影响范围

- target train
  - 原始 `592`
  - 移除 `14`
  - clean-only 后 `578`
  - 被移除时长约 `85.458914s`
- target validation
  - 原始 `66`
  - 移除 `3`
  - clean-only 后 `63`
  - 被移除时长约 `15.749977s`
- target special eval
  - 原始 `8`
  - 移除 `0`
  - 维持 `8`

## 当前意义

这套 split 的价值不是立刻宣判
“必须 clean-only 重训”，
而是把下一步真正需要的对照资产补齐：

1. 可以直接做
   target clean-only
   训练对照，
   不再需要临时人工筛样
2. 可以先测
   “去掉章节级混响样本后，
   clean-only 目标域是否真有收益”
3. 只有当这组对照实验显式优于当前主线，
   才值得进一步讨论是否把
   `reverb_like`
   样本从正式训练集里长期排除

## 当前建议

下一步如果继续推进实验，
最合理的是做一组最小对照：

- baseline:
  当前正式
  `hybrid_stratified_blocked`
- variant:
  `hybrid_stratified_blocked_target_clean_no_reverb`

优先看：

- target validation
  是否在 clean-only 目标域上更稳
- 当前 low-activity / glitch
  结论是否保持
- 是否出现泛化变窄
  或 robustness 下滑
