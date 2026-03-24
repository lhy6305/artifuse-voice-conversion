# 2026-03-24 Stage5 `contractv2_normfix` waveform objective 复查报告

## 结论
- 本轮已补读并固化：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_round1_1/`
    这份今天
    `11:01`
    生成、
    但此前尚未登记到正式 `docs/`
    的 probe 结果。
- 当前结论非常直接：
  - 即使
    `contractv2_normfix`
    已把 validation
    数值拉回并略优于旧 baseline，
    当前 waveform objective
    依然允许
    `template-buzz + envelope-following`
    假解；
  - 因而
    “validation 变好”
    和
    “最新人工验证仍是 buzz”
    并不矛盾。
- 当前下一步不该再优先折返：
  - source 修补
  - target reference
  - inference 小热修
- 更合理的默认主线应转为：
  - 在
    `contractv2_normfix`
    上做
    **objective-side minimal smoke**
  - 第一优先候选是：
    - `active_template_weight = 0.05`
    - `frame_delta_weight = 6.0`

## 一、这轮补登记的 probe 是什么
- runtime 产物目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_contractv2_normfix_round1_1/`
- 关键输入：
  - checkpoint：
    `contractv2_normfix`
    `best_validation`
    `step72`
  - dataset index：
    `offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - split：
    `validation`
  - `sample_count = 12`
  - decode 语义：
    - predicted gate `on`
    - smooth3
    - `post_ola_envelope`
- 这条 probe
  与此前
  `docs/259-274`
  的关系不是重复，
  而是：
  - 把同类 objective 诊断
    正式迁移到
    当前最新
    `contractv2_normfix`
    主线，
    看它是否仍然存在
    同类 collapse。

## 二、当前 probe 给出的关键事实

### 1. baseline 仍然输给 fixed-template oracle
- aggregate
  `weighted_wave_objective`
  排名：
  - `oracle_active_frame_target_rms = 0.141467`
  - `oracle_sine_target_rms = 0.147455`
  - `baseline_decode_route = 0.149037`
- 也就是：
  - 当前真正听到的
    baseline decode route，
    在现有正式
    `waveform + STFT + rms_guard`
    加权目标下，
    仍排在两个
    fixed-template counterexample
    后面。
- 这已经足够说明：
  - `contractv2_normfix`
    并没有把
    objective permissiveness
    一并修掉。

### 2. baseline 仍表现出很强 template 化
- aggregate：
  - `baseline decoded_frame_template_cosine_mean = 0.993590`
  - `oracle_active_frame_target_rms = 0.923083`
  - `oracle_sine_target_rms = 0.925485`
- 同时：
  - `baseline decoded_frame_rms_to_aligned_frame_rms_corr = 0.874109`
  - 两个 oracle
    都接近
    `0.9985`
- 这说明当前 baseline
  的典型形态仍是：
  - 短时帧极度贴同一模板
  - 但包络跟随反而不如
    “固定模板 + target RMS”
    这种反例路线

### 3. 仅换成 short-window MRSTFT 也不够
- sidecar 排序里，
  baseline 仍落后于 oracle：
  - `loss_mrstft_short_256_512_1024`
    baseline
    最差
  - `loss_frame_unit_rms_l1`
    baseline
    最差
  - `loss_frame_unit_rms_logspec_l1`
    baseline
    最差
- 所以当前不能再把问题写成：
  - “只要把 single-resolution STFT
    换成 MRSTFT
    就会自然转正”

### 4. 纯 transition-delta 有帮助，但单独还不稳
- `transition_delta_flip_thresholds`
  显示：
  - 对
    `oracle_sine_target_rms`
    来说，
    `flip_lambda_min ≈ 0.119767`
  - 对
    `oracle_active_frame_target_rms`
    来说，
    `flip_lambda_min ≈ 0.519276`
- 但 per-record
  `transition_combo`
  最好也只是：
  - `delta_lambda = 1.5`
  - `flux_lambda = 0.0`
  - `total_wins = 17 / 24`
- 这说明：
  - `frame_delta`
    是当前最先能把 aggregate
    拉回 baseline 前面的信号，
  - 但若只靠它，
    仍然存在明显 residual hard case。

### 5. active-template 单独做主轴仍不够稳
- `active_template_candidate_grid_summary`
  最好组合是：
  - `template_lambda = 0.25`
  - `zero_jitter_lambda = 4.0`
  - `total_wins = 21 / 24`
- 这比 transition-only
  更强，
  但还没完全扫平残留。
- 当前 residual
  还剩：
  - `target::chapter3_29_firefly_113`
  - `target::chapter3_2_firefly_212`

### 6. 当前最强 objective 候选是 `active_template + frame_delta`
- `active_template_delta_candidate_grid_summary`
  最佳组合：
  - `template_lambda = 0.05`
  - `delta_lambda = 6.0`
  - `total_wins = 24 / 24`
- `active_template_delta_targeted_summary`
  同时给出：
  - `residual_count = 0`
- 这说明在当前 probe
  里，
  第一个把两类 fixed-template oracle
  全面压回去的最小组合，
  不是：
  - active-template 单独
  - 也不是 flux 补项
  - 而是：
    - 小权重
      `active_template`
    - 大权重
      `frame_delta`
      的联用

## 三、这对当前实验线意味着什么

### 1. `contractv2_normfix` 的主要价值已被确认
- 它解决了：
  - consumer-side
    分布错位
  - validation
    显著落后旧主线
    的问题
- 但它没有解决：
  - waveform objective
    对 template collapse
    的宽容

### 2. 当前 user-line 仍是 buzz，不再需要额外靠前端理由解释
- 先前已经排掉：
  - source 电平过低
  - target reference
    不够 clean
  - inference 小热修
    作为主因
- 现在这份最新 objective probe
  又补上一条：
  - 当前最新
    `contractv2_normfix`
    主线下，
    objective permissiveness
    仍然客观存在
- 所以当前更合理的总解释是：
  - front-side
    已经基本清障，
  - remaining buzz
    更像是
    decoder/objective
    主线问题。

### 3. `chapter3_17_firefly_133` 是当前 transition-side hard case
- 当前
  `transition_targeted_hard_failure_summary`
  里，
  重复 hard failure
  只剩：
  - `target::chapter3_17_firefly_133`
- 它更像后续局部诊断入口，
  不是当前第一步就该阻塞整个 objective smoke
  的理由。

## 四、当前推荐的下一步

### 推荐主动作
1. 在
   `contractv2_normfix`
   dataset index
   上，
   跑一轮最小
   objective smoke
2. 只改：
   - `active_template_weight = 0.05`
   - `frame_delta_weight = 6.0`
3. 其余全部先保持：
   - `contract_v2_normfix`
     package
   - decoder head
   - checkpoint family
   - predicted gate
   - reconstruction apply mode
   不动

### 为什么先这样做
- 因为这条动作满足三个条件：
  1. 完全对齐当前最新 probe
     给出的最强候选
  2. 只改 objective，
     不把变量又扩回
     contract / decoder head
  3. 能最快回答：
     - 这条 objective 候选
       是否开始把
       validation 侧和可听侧
       一起拉离 buzz

### 当前明确不建议先做的
- 不建议现在先回去继续修：
  - source 输入
  - target reference
  - inference-only
    小热修
- 不建议现在就同时改：
  - waveform head
  - GAN
  - 多分辨率大重构
- 不建议把
  `chapter3_17_firefly_133`
  这个 hard case
  先升格成主线阻塞

## 一句话结论
- 当前最新
  `contractv2_normfix`
  主线已经被 objective probe
  再次证实：
  - validation 数值回升
    不等于
    waveform objective
    已经摆脱
    template-buzz
- 下一步最合理的接班动作，
  是在不改 contract
  和 decoder head
  的前提下，
  先做一轮
  `active_template(0.05) + frame_delta(6.0)`
  的 objective smoke，
  让问题继续沿
  decoder/objective
  主线收敛。
