# 2026-03-21 用户线上下文恢复与 decoder behavior 接班报告

## 结论
- 本次接班只继续用户线，
  明确忽略实验线未提交内容。
- 当前用户线不是回到
  “最小闭环入口还没做”，
  而是已经推进到：
  - `run-offline-mvp-teacher-first-vc-demo`
    可运行
  - review bundle
    可批量导出
  - self-check
    可做成功/失败回归
  - applicability probe
    已能比较 scaffold 分布
- 当前真正未收口的问题是：
  - 为什么 review bundle
    虽然稳定导出，
    但听感会塌成高频 buzzing
- 本轮已把仓库里“写到一半但未挂 CLI”
  的 decoder behavior probe
  补成正式命令，
  并完成第一轮实际运行。
- 当前新结论是：
  - buzzing
    更像是
    当前 user-line 控制进入
    Stage5 checkpoint
    后的 decoder 行为严重脱离训练内分布
  - 而不只是：
    - 路径拼接错
    - 文件读错
    - scaffold 特征轻微偏移

## 本次恢复时确认到的用户线状态

### 1. 已有正式入口
- CLI：
  - `run-offline-mvp-teacher-first-vc-demo`
  - `self-check-offline-mvp-teacher-first-vc-demo`
  - `build-offline-mvp-teacher-first-vc-review-bundle`
  - `analyze-offline-mvp-teacher-first-vc-applicability`
- PowerShell：
  - `scripts/run_teacher_first_single_target_vc_demo.ps1`
  - `scripts/self_check_teacher_first_single_target_vc_demo.ps1`
  - `scripts/run_teacher_first_single_target_vc_review_bundle.ps1`

### 2. 当前默认口径
- decode apply mode
  已沿正式主线提升为：
  - `post_ola_envelope`
- 依据文档：
  - `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`

### 3. 当前活跃用户线会话
- 续登记会话：
  - `reports/collab/ai_work_sessions/user_line_applicability_probe_20260321.md`
- 本次接班说明已写入会话卡：
  - takeover restored in current session
  - only user-line applicability diagnosis continues
  - experiment-line changes ignored

## 本轮补齐的正式入口

### 1. 新增 CLI
- `analyze-offline-mvp-teacher-first-vc-decoder-behavior`

### 2. 目的
- 用与当前用户线相同的
  Stage5 checkpoint
  和 decode 设置，
  直接比较：
  - user-line 输入导出的 decoded 行为
  - Stage5 train package
    内分布样本的 decoded 行为
- 它比
  scaffold-level applicability probe
  更进一步，
  回答的是：
  - “问题是不是主要在 decoder 侧放大出来”

## 本轮运行

### 命令
```powershell
.\python.exe manage.py analyze-offline-mvp-teacher-first-vc-decoder-behavior `
  --input-audio data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav `
  --input-audio data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav `
  --input-audio data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav `
  --output-dir reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_probe `
  --device cpu `
  --chunk-ms 33.333333
```

### 输出
- 目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_probe/`
- 关键文件：
  - `teacher_first_vc_decoder_behavior_probe.json`
  - `teacher_first_vc_decoder_behavior_probe.md`

## 当前诊断结果

### 1. scaffold-level 偏移不是唯一主因
- 早一轮 applicability probe
  已显示：
  - 常规 segment
    与 peak case
    的 scaffold 偏移不算失控
  - 高静音 case
    偏移更大，
    但也主要是控制分布变化

### 2. decoder-level 指标出现了极端反常
- 参考
  Stage5 train package
  内分布样本的 decoded 指标大致稳定在：
  - `decoded_spectral_centroid_hz ≈ 3009.70`
  - `decoded_spectral_bandwidth_hz ≈ 4765.82`
  - `decoded_spectral_rolloff95_hz ≈ 20946.90`
  - `decoded_spectral_high_band_energy_ratio ≈ 0.064544`
- 但用户线三条 case
  全部落到：
  - `decoded_spectral_centroid_hz ≈ 3283~3303`
  - `decoded_spectral_bandwidth_hz ≈ 5201~5243`
  - `decoded_spectral_rolloff95_hz ≈ 22796~22799`
  - `decoded_spectral_high_band_energy_ratio ≈ 0.4776~0.4795`
- 也就是：
  - 高频能量占比
    比参考内分布高了一个数量级以上
  - 这与“高频 buzzing”
    的主观症状高度一致

### 3. 更准确的工程判断
- 当前 user-line
  `teacher-first / single-target`
  路径已经证明：
  - 工程上能跑通
  - 不是简单命令失败问题
- 但它还没有证明：
  - 当前 teacher control +
    single-target conditioning
    对 Stage5 no-res checkpoint
    仍处在可接受适用范围内
- 当前更像是：
  - checkpoint 在训练内分布 package 上
    行为稳定
  - 但喂入用户线 control/scaffold 后，
    decoded 端会系统性滑向过强高频能量分布

## 当前建议的下一步
1. 不要把当前 review bundle
   继续当作“终端用户可直接听质量”的正向展示材料。
2. 若继续用户线，
   下一题应优先围绕：
   - 如何给 user-line
     加适用性边界或异常告警
   - 如何让 user-line conditioning / control
     更接近 Stage5 训练内分布
3. 在新的缓解方案落地前，
   当前用户线更适合定位为：
   - 工程闭环已成立
   - 质量适用性仍待治理

## 文档入口
- `docs/237_teacher_first_single_target_terminal_user_line_design.md`
- `docs/238_teacher_first_single_target_terminal_user_line_bootstrap_report.md`
- `docs/239_teacher_first_single_target_multisource_smoke_and_wrapper_report.md`
- `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`

## 一句话结论
- 本次接班后，
  用户线状态已经恢复清楚：
  入口不是 blocker，
  当前 blocker
  是
  Stage5 checkpoint
  对 user-line 控制的适用性；
  buzzing
  更像是 decoder-side
  的系统性失配，
  不是简单拼接错误。
