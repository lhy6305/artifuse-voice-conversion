# 336. Stage5 MRSTFT `0.05` validation training-sync 导出与最小对照包报告

## 结论
- 在
  `335`
  已把 short-window MRSTFT
  低权重 sweep
  收敛到
  `0.05`
  之后，
  本轮继续补齐了：
  - baseline `0.00`
    validation training-sync export
  - MRSTFT `0.05`
    validation training-sync export
  - 两条 case 的最小听审对照包
- 当前已经具备下一步人工听审所需的最小材料，
  不再停留在纯数值判断。

## 一、导出对象

### baseline
- checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_activitygate000_baseline_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- export 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_activitygate000_validation_trainingsync_round1_1/`

### MRSTFT `0.05`
- checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- export 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_mrstft005_validation_trainingsync_round1_1/`

## 二、导出口径
- 两边均使用：
  - `--split-name validation`
  - `--sample-count 2`
  - `--activity-gate-weight 0.0`
  - `--use-predicted-activity-gate`
  - `--predicted-activity-gate-apply-mode pre_overlap_add`
- 目的：
  - 保持与当前 paired overfit24
    训练语义一致，
    避免 export-side
    再引入额外口径漂移

## 三、最小听审包
- 目录：
  - `reports/audio/stage5_paired_parallel_overfit24_mrstft005_compare_quick_audit_20260325/`
- 文件顺序：
  - case107：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `mrstft005_decoded`
  - case132：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `mrstft005_decoded`

## 四、为什么这一步值得做
- `335`
  已经说明：
  - `0.05`
    是当前唯一还值得保留的
    MRSTFT
    最小候选
- 但这仍只是共享指标层面的判断；
  是否真的值得留，
  还要看听感上它到底是：
  - 更接近 target
  - 还是只是频谱数值略变、
    听起来并无实质改善

## 五、当前阶段判断
- 当前 MRSTFT
  这条线已经从：
  - plumbing 修复
  - 低权重 sweep
  继续推进到：
  - 可直接听的
    baseline vs `0.05`
    最小对照
- 因而下一步若继续这条线，
  现在最值钱的问题只剩一个：
  - `mrstft005`
    在真实听感上，
    是否比 baseline
    更接近 target，
    且没有新增明显副作用

## 六、下一步
1. 若继续 MRSTFT
   这条线，
   优先听：
   - `reports/audio/stage5_paired_parallel_overfit24_mrstft005_compare_quick_audit_20260325/`
2. 只回答：
   - case107 / case132
     中，
     `mrstft005`
     是否优于 baseline
3. 若答案是否定，
   就把 short-window MRSTFT
   正式收口为：
   - plumbing 已补齐
   - `0.05`
     是量化最佳折中
   - 但听感若无收益，
     则不继续推进
