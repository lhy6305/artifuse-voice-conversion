# 2026-03-23 Stage5 active-template residual listening bundle 报告

## 结论
- 本轮在继续保留
  `docs/271`
  的 residual/stationary 结论之外，
  先把一版可复查试听包
  真正落出来了。
- 当前 residual-focused bundle
  已覆盖：
  - `target::chapter3_2_firefly_155`
  - `target::chapter3_2_firefly_212`
- 主听源设置为：
  - `decoded_pitch_matched`
  - reference:
    `aligned_target`

先说人话：
- 这一步的价值
  不是新的 loss 结论，
  而是：
  - 先把 residual 试听入口
    固化出来，
    避免又回到
    “数值结论推进很久，
    但没有及时听”
    的坑里

## 本轮工程动作

### 1. 修掉 residual listening bundle 导出回归
- 文件：
  - `src/v5vc/nores_vocoder_audio_export.py`
- 修正内容：
  - 给
    `compute_nores_vocoder_losses`
    补上当前训练侧新增的
    `reconstruction_frame_gain_apply_mode`
    参数
- 当前处理口径：
  - 直接复用
    `DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE`
  - 不额外改变现有 CLI
    用户接口

### 2. 实际导出 residual-focused bundle
- 命令口径：
  - checkpoint:
    `best_validation`
  - split:
    `validation`
  - records:
    - `target::chapter3_2_firefly_155`
    - `target::chapter3_2_firefly_212`
  - listening source:
    `decoded_pitch_matched`
  - pitch-match reference:
    `aligned_target`
  - predicted activity gate:
    - on
    - smooth3
    - `post_ola_envelope`

## 当前产物

### 1. 导出目录
- [offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1)

### 2. 主清单
- [nores_vocoder_audio_export.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1/nores_vocoder_audio_export.md)
- [proxy_audio_export.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1/proxy_audio_export.md)

### 3. GUI-compatible manifest
- [proxy_audio_export.json](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_audio_export_active_template_residual_round1_1/proxy_audio_export.json)

### 4. 已导出的试听文件
- `target::chapter3_2_firefly_155`
  - aligned target
  - decoded
  - decoded pitch matched
  - audit proxy
- `target::chapter3_2_firefly_212`
  - aligned target
  - decoded
  - decoded pitch matched
  - audit proxy

## 当前判断
- 当前实验线若继续推进，
  这版 residual bundle
  已足够作为：
  - residual-specific
    人耳回查入口
- 当前最重要的工程含义是：
  - 以后不要把
    “等后面再统一导试听包”
    当默认策略
  - residual 一旦收紧到
    2-3 条记录，
    就应该尽快把 bundle
    真正落盘

## 对下一步的直接含义
1. 下一步继续做
   stationary-friendly residual
   补充项诊断时，
   应直接配套回听：
   - `chapter3_2_firefly_155`
   - `chapter3_2_firefly_212`
2. 如果后续再出现新的 residual
   名单变化，
   优先扩这份 bundle，
   而不是重新临时手工导出

## 一句话结论
- residual-specific 试听包已经落盘，
  当前不用再担心因为导出链路没准备好，
  重演上次“数值先走太远、回听跟不上”的坑。
