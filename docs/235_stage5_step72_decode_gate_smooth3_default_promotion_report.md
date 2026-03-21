# 2026-03-20 Stage5 `step72__decode_gate_smooth3` 默认导出提升报告

## 结论
- 当前 Stage5 no-res vocoder 的正式 decode-side 默认值提升为：
  - `--predicted-activity-gate-smoothing-frames 3`
  - `--predicted-activity-gate-floor 0.0`
- 这次提升只影响
  `export-offline-mvp-nores-vocoder-audio`
  的默认导出行为，
  不改写已有 checkpoint，
  也不影响显式传参的旧实验回放。
- 如需回退到历史 hard-gate 基线，
  仍可显式传：
  - `--predicted-activity-gate-smoothing-frames 0`

## 提升依据
- 量化上，
  `docs/230_stage5_step72_glitch_smoothing_ablation_report.md`
  已确认：
  `smooth3`
  在 `validation12`
  上将
  `mean_fragmentation_score`
  从
  `1.497705`
  降到
  `1.196807`，
  将
  `mean_sample_delta_peak`
  从
  `0.162141`
  降到
  `0.079572`，
  同时只付出小幅
  `waveform_rms / alignment`
  代价。
- 主观上，
  `reports/audio/audio_audit_gui_stage5_step72_glitch_smooth3_validation12_session/audio_audit_review.json`
  的 aggregate 显示：
  - `overall_pick`
    对
    `decoded:offline_mvp_nores_vocoder_dataset_loop.step72__decode_gate_smooth3`
    计数为
    `11`
  - `best_boundary`
    计数为
    `11`
  - `most_stable`
    计数为
    `11`
- 这说明
  `smooth3`
  已经不是“只在局部窗口里看起来不错的候选”；
  它在已导出的 focused + validation12
  听审里都形成了稳定单向支持。

## 本次工程动作
- 新增常量：
  - `src/v5vc/nores_vocoder_audio_export.py`
    `DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES = 3`
- `src/v5vc/cli.py`
  中
  `export-offline-mvp-nores-vocoder-audio`
  的
  `--predicted-activity-gate-smoothing-frames`
  默认值从
  `0`
  提升为
  `3`
- 帮助文案同步改为明确口径：
  - 默认值代表当前 promoted Stage5 decode setting
  - 显式传
    `0`
    即可回退 legacy hard-gate export

## 为什么这次可以默认化
- 之前不默认化，
  主要是因为缺少 focused human audit。
- 现在这个前置条件已经补齐：
  - representative glitch windows
    上，
    `step72__decode_gate_smooth3`
    明确优于 baseline
  - 扩到
    `validation12`
    后，
    量化没有反转
  - 导出的人工 review
    也没有反转
- 所以继续把
  `smooth3`
  留在“每次靠额外参数手动打开”的状态，
  只会增加主线使用成本，
  并让默认导出继续停在已经被证明更差的 decode 行为上。

## 兼容性口径
- 历史报告和历史产物不回写。
- 任何需要严格复现旧 hard-gate 导出的实验，
  只需显式传：

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  ... `
  --use-predicted-activity-gate `
  --predicted-activity-gate-smoothing-frames 0
```

## 当前建议
- 后续所有新的 Stage5 human-audit / probe / ad-hoc export，
  默认都以
  `smooth3`
  作为 decode-side 主线。
- 只有在做历史基线复现或专门的 hard-gate 对照时，
  才显式传
  `0`。
