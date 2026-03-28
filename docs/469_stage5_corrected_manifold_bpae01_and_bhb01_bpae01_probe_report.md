# 2026-03-28 Stage5 corrected-manifold `bpae01` 与 `bhb01+bpae01` probe 报告

## 结论
- 我沿着
  `docs/468_stage5_corrected_manifold_base_logits_minimal_penalty_probe_report.md`
  的下一步判断，
  继续把更结构性的
  `waveform_decoder_base_logits -> aper * noise_E`
  product-jump 约束
  (`bpae01`)
  回投到当前 corrected-manifold anchor：
  - 单项 `bpae01`
  - 最小双项组合 `bhb01 + bpae01`
- 结果已经足够清楚：
  - `bpae01`
    在 corrected-manifold 上几乎复现了
    `bta01`
    的轨迹
  - `bhb01 + bpae01`
    又几乎复现了
    `bhb01`
    的轨迹
  - 两者都没有突破当前 anchor 的
    `decoded_post_ola_gate auto_reject = 14/24`
- 更具体地说：
  - anchor：
    `14/24`
  - `bpae01 step8`：
    `14/24`
  - `bhb01 + bpae01 step4`：
    `14/24`
  - `bhb01 + bpae01 step8`：
    `15/24`
- 同时几条新候选都延续了同一模式：
  - centroid / high-band
    持续下降
  - 但 `waveform_frame_logits / waveform_frames`
    template 持续上升
  - `decoded_no_gate auto_reject`
    维持在 `18/24`
  - diagnosis
    始终是
    `needs_more_localization`
- 因而当前可以正式收口为：
  - corrected-manifold 上的
    单项 `base_logits` penalty
    与最小双项 penalty
    都已经到头
  - 它们能重塑 operating region，
    但不能把系统从当前 template-heavy localization basin
    再往前推出
  - 下一步不该继续做
    `bta01 / bhb01 / bpae01`
    及其相近组合的小扫，
    而应切到：
    - 更强的结构性 `base_logits` probe
    - 或更高阶的 interface constraint

## 一、实验对象
- 当前 anchor checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- 数据集：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 共用 recipe：
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

## 二、`bpae01`：单项 product-jump 约束
- 训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bpae01_round1_1/`
- 额外 loss：
  - `waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr = 0.1`
- validation：
  - `step4 = 1.339955`
  - `step8 = 1.293838`
- 读法：
  - 比 anchor 的 `1.311899`
    略好
  - 但明显不如 `bhb01`
    的 `1.253358`

### 1. handoff probe
- `step4`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bpae01_step4_round1_1/`
- `step8`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bpae01_step8_round1_1/`

### 2. aggregate 对比
- anchor `fbmcrs + residualshape step8`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973165`
  - `centroid_gap = 4679.957520`
  - `high_band_gap = 0.354575`
  - `decoded_no_gate auto_reject = 16/24`
  - `waveform_frames_template = 0.985322`
- `bpae01 step4`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973447`
  - `centroid_gap = 4554.479492`
  - `high_band_gap = 0.344546`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.985866`
- `bpae01 step8`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.974096`
  - `centroid_gap = 4462.347168`
  - `high_band_gap = 0.335406`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.986232`

### 3. 读法
- `bpae01`
  在 corrected-manifold 上
  没有表现出 old output-head 线里那种“独立于 active-template 的新性格”，
  反而与 `bta01`
  数值上几乎重合。
- 它和 `bta01`
  一样：
  - 继续降低 centroid / high-band
  - 继续加重 template
  - 继续让 no-gate
    退回 `18/24`
- 这意味着：
  - 当前 corrected-manifold 里的
    product-jump 约束
    并没有被转译成新的 localization 改善
  - 它更像只是把模型重新压进一个
    与 `bta01`
    极相近的 dark-template basin

## 三、`bhb01 + bpae01`：最小双项组合
- 训练目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_bpae01_round1_1/`
- 额外 losses：
  - `waveform_decoder_base_logits_high_band_excess = 0.1`
  - `waveform_decoder_base_logits_aper_noise_energy_abs_zero_lag_corr = 0.1`
- validation：
  - `step4 = 1.373217`
  - `step8 = 1.325066`
- 读法：
  - 比 anchor 还差
  - 也明显差于单独 `bhb01`

### 1. handoff probe
- `step4`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_bpae01_step4_round1_1/`
- `step8`：
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_bhb01_bpae01_step8_round1_1/`

### 2. aggregate 对比
- `bhb01 + bpae01 step4`：
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `template = 0.973540`
  - `centroid_gap = 4500.911621`
  - `high_band_gap = 0.339426`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.985898`
- `bhb01 + bpae01 step8`：
  - `decoded_post_ola_gate auto_reject = 15/24`
  - `template = 0.974491`
  - `centroid_gap = 4310.210938`
  - `high_band_gap = 0.320430`
  - `decoded_no_gate auto_reject = 18/24`
  - `waveform_frames_template = 0.986386`

### 3. 读法
- 这条组合没有叠出“结构 + 亮度”的协同，
  反而基本复现了
  `bhb01`
  的样子：
  - centroid / high-band
    继续做到最好一档
  - 但 template 更高
  - post-gate auto-reject
    仍没有优于 anchor，
    且 `step8`
    轻微反弹到 `15/24`
- 这说明：
  - 当前 corrected-manifold 问题
    不是“只差把 brightness penalty
    和 product-jump penalty
    叠在一起”
  - 两者叠加只是在当前 basin
    内继续重排，不会自动带来
    localization 突破

## 四、与本轮其它 corrected-manifold 候选的关系
- `bta01 step8`：
  - `post auto_reject = 14/24`
  - `centroid_gap = 4460.122559`
  - `high_band_gap = 0.335132`
  - `frames_template = 0.986218`
- `bpae01 step8`：
  - `post auto_reject = 14/24`
  - `centroid_gap = 4462.347168`
  - `high_band_gap = 0.335406`
  - `frames_template = 0.986232`
- `bhb01 step8`：
  - `post auto_reject = 15/24`
  - `centroid_gap = 4311.048340`
  - `high_band_gap = 0.320379`
  - `frames_template = 0.986569`
- `bhb01 + bpae01 step8`：
  - `post auto_reject = 15/24`
  - `centroid_gap = 4310.210938`
  - `high_band_gap = 0.320430`
  - `frames_template = 0.986386`

### 当前最重要的结构性事实
- `bpae01`
  与 `bta01`
  几乎同构
- `bhb01 + bpae01`
  与 `bhb01`
  几乎同构
- 这说明当前 corrected-manifold 主瓶颈
  已经不是这些 penalty 名义上针对的单一 coupling，
  而是更上游、更整体的
  `base_logits` operating region

## 五、当前判断
- 这轮之后可以把下面这些路线
  一并视为“已完成最小 corrected-manifold 验证”：
  - `bta01`
  - `bhb01`
  - `bpae01`
  - `bhb01 + bpae01`
- 它们都提供了相同方向的信息：
  - 明显优于 plain `corr24 step8`
    的早期 buzz basin
  - 但全部卡在
    `needs_more_localization`
    这一级
- 因而下一步应转向：
  - corrected-manifold 版
    `base_logits` 结构 probe，
    先确认当前 template-heavy localization
    具体由哪类 coupling 主导
  - 或更高阶的 interface-local 约束，
    而不是继续做同类权重和小组合扫描

## 一句话结论
- 在 corrected-manifold 上，`bpae01` 没有打开新方向，只是近似复现 `bta01`；`bhb01 + bpae01` 也没有产生协同，只是近似复现 `bhb01`。因此本轮已经足够证明：单项与最小双项 `base_logits` penalty 都推不穿当前 `14/24` handoff 门槛，下一步必须转去 probe 或更强结构约束。
