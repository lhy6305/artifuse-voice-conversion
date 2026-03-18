# 194. Stage5 waveform checkpoint selection 与 late-stop 制度化报告

## 背景
- `docs/193_stage5_waveform_rmsguard02_baseline96_deterministic_tail_review_report.md`
  已确认:
  - `step96`
    是当前
    best-by-loss
  - `step72`
    更像稳妥的
    late-stop 候选
- 但这时
  仍然存在一个工程缺口:
  - 结论还主要靠
    人工阅读 report
  - 没有可复用的
    Stage5 checkpoint selector

## 本轮目标
1. 给 Stage5
   no-res waveform route
   补一个专用
   checkpoint selection
   入口
2. 把以下三类角色
   显式拆开:
   - best validation checkpoint
   - best RMS checkpoint
   - stable late-stop checkpoint
3. 在当前
   deterministic `96-step`
   结果上
   验证这套制度

## 本轮代码落地

### 1. `src/v5vc/nores_vocoder_checkpoint_selection.py`
- 新增
  Stage5 专用 selector
- 输入:
  - dataset-loop
    `summary.json`
- 输出:
  - `best_validation_checkpoint`
  - `best_rms_checkpoint`
  - `late_candidates`
  - `selected_stable_late_stop`

### 2. 选择规则
- `best_validation_checkpoint`:
  - 直接取
    最低 validation
    `loss_total`
- `best_rms_checkpoint`:
  - 取
    `decoded_to_target_rms_ratio`
    最接近 `1.0`
  - 若并列，
    再看
    validation `loss_total`
- `selected_stable_late_stop`:
  - 只在
    late window
    内选择
  - 同时要求:
    - 处于 validation guard 内
    - pairwise worsened ratio
      不超过阈值
    - RMS ratio deviation
      不超过阈值
  - 在满足条件的候选里，
    默认取
    最晚 step

### 3. `src/v5vc/cli.py`
- 新增命令:
  - `select-offline-mvp-nores-vocoder-checkpoint`
- 关键参数:
  - `--late-step-ratio`
  - `--validation-guard-ratio`
  - `--max-pairwise-worsened-ratio`
  - `--max-rms-ratio-deviation`

## 本轮选择命令

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline96_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_baseline96_deterministic_round1_1 --late-step-ratio 0.5 --validation-guard-ratio 1.03 --max-pairwise-worsened-ratio 0.2 --max-rms-ratio-deviation 0.03
```

## 结果

### 选择策略
- late window:
  - `step >= 48`
- validation guard:
  - `<= 1.03x`
    best validation
  - threshold:
    - `0.635001`
- pairwise worsened ratio
  上限:
  - `0.2`
- RMS ratio deviation
  上限:
  - `0.03`

### 选择结果
- best validation checkpoint:
  - `step96`
  - `loss_total = 0.616506`
- best RMS checkpoint:
  - `step48`
  - `decoded_to_target_rms_ratio = 0.981499`
- selected stable late-stop:
  - `step72`
  - `loss_total = 0.625926`
  - `decoded_to_target_rms_ratio = 0.979730`
  - pairwise:
    - `48 -> 72`
      `66 / 66`
      improved

### late candidate 判定
- `step48`
  未通过:
  - 不在 validation guard 内
- `step72`
  通过:
  - 在 validation guard 内
  - `worsened_ratio = 0.0`
  - `rms_ratio_deviation = 0.020270`
- `step96`
  未通过:
  - `worsened_ratio = 0.363636`
  - `rms_ratio_deviation = 0.051881`

## 当前判断

### 1. 现在可以把 `96` 与 `72` 的角色差异制度化，而不是只靠报告口头解释
- `96`
  是:
  - best-by-loss
- `72`
  是:
  - stable late-stop
- 这两者
  现在已经能由
  统一 selector
  稳定输出

### 2. `48` 虽然 RMS 最贴近 1.0，但不该自动升格成默认晚停点
- 因为它
  不在当前
  validation guard
  以内
- 所以:
  - best RMS
    不等于
    best late-stop

### 3. 当前 Stage5 waveform route 已具备更清晰的治理口径
- 以后汇报时
  不再只说:
  - best checkpoint
- 而应拆成:
  - best-by-loss
  - best-by-RMS
  - stable late-stop

先说人话:
- 这一步相当于
  给当前 Stage5
  加了一个
  “自动裁判”。
- 以后不用再每次
  手工看一堆表
  才能说清楚
  到底该拿
  `96`
  还是
  `72`。

## 当前产物
- selector 输出:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_baseline96_deterministic_round1_1`

## 下一步建议
1. 当前若要给
   waveform route
   选默认 checkpoint，
   优先采用:
   - stable late-stop
     `step72`
2. 若后续新增
   multi-resolution /
   adversarial objective，
   应继续沿用
   这种三分口径:
   - best validation
   - best RMS
   - stable late-stop
3. 在当前 proxy/bootstrap
   形态下，
   不建议再继续做
   更长 deterministic horizon
   来替代
   selection 制度

## 一句话结论
- 本轮已把
  Stage5 waveform route
  的 checkpoint 选择
  从“人工读报告判断”
  推进到
  “可重复执行的 selector”：
  - `step96 = best validation`
  - `step48 = best RMS`
  - `step72 = stable late-stop`
- 其中真正适合作为
  当前默认晚停点的，
  是 `step72`，
  而不是简单取
  最低平均 loss
  的 `step96`。
