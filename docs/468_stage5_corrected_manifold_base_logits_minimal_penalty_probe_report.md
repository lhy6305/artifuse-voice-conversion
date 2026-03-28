# 2026-03-28 Stage5 corrected-manifold base-logits minimal penalty probe 报告

## 结论
- 我沿着 `docs/467_stage5_corrected_manifold_fbmcrs_residualshape_finetune_report.md`
  里确立的当前主 anchor
  `corr24 fbmcrs + residualshape step8`
  做了两条最小 base-logits 侧回投：
  - `waveform_decoder_base_logits_active_template = 0.1`
    (`bta01`)
  - `waveform_decoder_base_logits_high_band_excess = 0.1`
    (`bhb01`)
- 两条路都没有把当前 handoff 最优点
  `decoded_post_ola_gate auto_reject = 14/24`
  再往下压。
- `bta01`
  的性质是：
  - centroid / high-band 继续下降
  - 但 `waveform_frame_logits -> waveform_frames`
    template 继续上升
  - `decoded_no_gate auto_reject`
    从 anchor 的 `16/24`
    退到 `18/24`
  - 因而它只是“更像把问题压到更暗、更平滑的 template-heavy 区”，
    不是更好的主线。
- `bhb01`
  的性质是：
  - 训练 validation 明显改善，
    从 anchor 的 `1.311899`
    降到 `1.253358`
  - centroid / high-band
    是当前所有 corrected-manifold 候选里最好的一档
  - 但 handoff 上仍没有突破：
    - `step4` 只做到 `14/24`
    - `step8` 反而回到 `15/24`
  - 同时 template 继续上升，
    `waveform_frames_template`
    来到 `0.986569`
- 因而当前更准确的结论是：
  - 最小 `base_logits active_template / high_band`
    penalty 确实能继续改 operating region
  - 但仍不足以把 corrected-manifold
    从当前 `needs_more_localization`
    basin 里推出去
  - 下一步不该继续在这两个单项 penalty 上做同类小修，
    而应转去更结构性的 base-logits 约束
    （例如 lagcorr / product-jump 类，
    或更直接的 decoder/base-logits 结构形成 probe）

## 一、实验对象
- 当前 anchor checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- 数据集：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 共同 recipe：
  - `num_steps = 8`
  - `packages_per_step = 6`
  - `validation_interval = 4`
  - `checkpoint_interval = 4`
  - `learning_rate = 1e-4`
  - `waveform = 0.5`
  - `stft = 0.5`
  - `rms_guard = 0.2`
  - `activity_gate = 0.2`
  - `active_template = 0.05`
  - `frame_spectral_flux_zero_target_jitter = 4.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 二、`bta01`：base-logits active-template 最小回投
- 训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bta01_round1_1/`
- 额外 loss：
  - `waveform_decoder_base_logits_active_template = 0.1`
- 训练 summary：
  - `validation loss_total`
    - `step4 = 1.356444`
    - `step8 = 1.316418`
  - 比 anchor 的 `1.311899`
    略差

### 1. handoff probe
- `step4`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bta01_step4_round1_1/`
- `step8`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bta01_step8_round1_1/`

### 2. aggregate 对比
- anchor `fbmcrs + residualshape step8`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973165`
  - `centroid_gap = 4679.957520`
  - `high_band_gap = 0.354575`
  - `decoded_no_gate auto_reject = 16/24`
  - `waveform_frames_template = 0.985322`
- `bta01 step4`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973407`
  - `centroid_gap = 4556.524902`
  - `high_band_gap = 0.344742`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.985846`
- `bta01 step8`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.974083`
  - `centroid_gap = 4460.122559`
  - `high_band_gap = 0.335132`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.986218`

### 3. 读法
- `bta01`
  的确继续把 centroid / high-band
  压下来了，
  而且诊断仍是
  `needs_more_localization`
  而不是退回
  `buzz_present_by_waveform_frames_before_gate`。
- 但它没有继续减少 post-gate auto-reject，
  反而让 no-gate 更差，
  同时 logits / frames template
  比 anchor 更高。
- 这说明 `bta01`
  不是把系统推出当前 basin，
  而是把当前 basin
  重新塑形成更暗但更 template-heavy 的版本。

## 三、`bhb01`：base-logits high-band 最小回投
- 训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_round1_1/`
- 额外 loss：
  - `waveform_decoder_base_logits_high_band_excess = 0.1`
- 训练 summary：
  - `validation loss_total`
    - `step4 = 1.295280`
    - `step8 = 1.253358`
  - 明显优于 anchor 的 `1.311899`

### 1. handoff probe
- `step4`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_step4_round1_1/`
- `step8`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_step8_round1_1/`

### 2. aggregate 对比
- `bhb01 step4`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973619`
  - `centroid_gap = 4501.277832`
  - `high_band_gap = 0.339466`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.985966`
- `bhb01 step8`：
  - `decoded_post_ola_gate auto_reject = 15/24`
  - `template = 0.974703`
  - `centroid_gap = 4311.048340`
  - `high_band_gap = 0.320379`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.986569`

### 3. 读法
- `bhb01`
  是这轮里最值得保留的信息点：
  - 它在训练目标上明显有效
  - 它把 centroid / high-band
    压到了当前 corrected-manifold
    所有已跑候选里最低
- 但 handoff 结果说明：
  - 亮度下降
    不等于
    更好 localization
  - `step8`
    甚至从 `14/24`
    轻微反弹到 `15/24`
  - template 也继续增大
- 所以 `bhb01`
  不能直接升格成新 winner；
  它更像证明：
  - 当前剩余问题
    已经不只是 brightness
  - 单纯 base-logits high-band
    约束还不够把模型带离
    template-heavy operating region

## 四、与 plain corrected-manifold 的位置关系
- plain `corr24 step8`
  (`reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_round1_1/`)
  仍然是旧的早期 buzz basin：
  - `decoded_post_ola_gate auto_reject = 24/24`
  - `centroid_gap = 8774.619141`
  - `high_band_gap = 0.660415`
  - `waveform_frames_template = 0.949051`
  - diagnosis:
    `buzz_present_by_waveform_frames_before_gate`
- `fbmcrs + residualshape`
  及其 `bta01 / bhb01`
  变体都已经稳定处在另一个 basin：
  - `buzz_before_predicted_activity_gate = false`
  - diagnosis:
    `needs_more_localization`
  - centroid / high-band
    比 plain route
    明显更低
- 当前卡点不是“能否逃离纯 buzz 盆地”，
  而是“逃离之后能否进一步摆脱 template-heavy localization failure”。

## 五、当前判断
- 这轮 probe 已经足够说明：
  - `base_logits active_template`
    单独不够
  - `base_logits high_band`
    单独也不够
- 下一步更合理的方向应转向：
  - `waveform_decoder_base_logits`
    的更结构性约束，
    而不是继续叠同类单项惩罚
  - 优先级更高的候选包括：
    - lagcorr / zero-lag / product-jump
      一类已在 `docs/439-445`
      验证过会真实打到 output-head coupling 的约束
    - 或直接补
      corrected-manifold 版
      `base_logits` 结构 probe，
      先确认当前 template-heavy 区
      具体是哪个 coupling
      仍在支配

## 一句话结论
- `bta01` 与 `bhb01` 都证明了 corrected-manifold 当前主问题已经进入 base-logits operating region，但两条最小单项 penalty 都没能突破 `14/24` 这个 handoff 门槛；因此下一步应停止做 `active_template / high_band` 同类微扫，改做更结构性的 base-logits 约束或 probe。
