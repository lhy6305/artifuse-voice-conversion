# 2026-03-21 Stage5 原设计门槛复核报告

## 结论
- 当前不建议继续在本轮
  Stage5
  局部环节
  扫更多方案。
- 更合理的下一步不是：
  - 继续扩
    `postenv`
    周边小题
  - 继续追
    training-side
    apply mode
    的短程 smoke
  - 或重开
    clean-only /
    reverb-like
    子线
- 更合理的下一步是：
  - 回到
    `initial_design.md`
    的原设计门槛，
  - 先复核
    当前 Stage5
    no-res route
    到底有没有真正接近：
    - “无残差主干可懂、稳定、基本自然”
    - “控制变量不是名义输入，而是真在起作用”

先说人话：
- 最近几轮实验不是没推进，
  而是局部题已经基本收干净了。
- 现在再继续在同一小圈里扫，
  更像在打磨边角，
  不是在回答
  Stage5
  最重要的问题。

## 复核基准：原设计到底要求什么

### 1. Stage5 的原始核心门槛
- `initial_design.md`
  在
  `4.4 / 5.2 / 6.7 / 推荐实施路线图 / MVP`
  中反复强调：
  - 先训练
    无残差声码器
  - 仅凭
    `z_art + e_evt + F0 + vuv + aper + E`
    就要做到：
    - 可懂
    - 稳定
    - 基本自然
  - 然后才谈
    `r_res`
    接入和联合微调
- 这说明：
  当前 Stage5
  最重要的不是
  某个 decode-side
  小参数还可不可以再抠一点，
  而是：
  - no-res 主干到底立没立住

### 2. 风险文档强调的真正高风险
- `initial_design_judg.md`
  明确提醒：
  - 无残差主干能力
    是系统核心门槛
  - 中间控制变量
    可能根本没被真正使用
  - 如果缺少正式消融，
    只靠听感无法证明：
    - `z_art`
      是否主导元音/浊音骨架
    - `e_evt`
      是否主导辅音事件
    - `r_res`
      是否被限制为补偿角色
- 所以对 Stage5
  来说，
  真正的大问题仍然是：
  - 主干能力
  - 控制变量使用性
  - 而不是
    当前已经收口的局部 decode 细调

## 当前 Stage5 已经做到的部分

### 1. no-res scaffold 与 dataset-level 训练路线已成立
- `docs/177_nores_vocoder_scaffold_bootstrap_report.md`
  已把：
  - teacher-first
    consumer scaffold
  - no-res source-filter scaffold
  正式落地
- `docs/184_nores_vocoder_fullsplit_training_baseline_report.md`
  与
  `docs/185_stage5_gpu_seed_reproducibility_and_long_horizon_baseline_report.md`
  已证明：
  - full-split dataset loop
    成立
  - GPU-backed
    seeded proxy baseline
    成立

### 2. waveform bootstrap route 已成立
- `docs/189_stage5_waveform_stft_bootstrap_decoder_report.md`
  已把：
  - minimal waveform decoder
  - aligned waveform L1
  - single-resolution log-STFT
  接到
  dataset-level loop
- `docs/192_stage5_waveform_rmsguard02_baseline48_and_deterministic_reproducibility_fix_report.md`
  与
  `docs/194_stage5_waveform_checkpoint_selection_and_late_stop_policy_report.md`
  又把：
  - RMS guard
  - deterministic mode
  - checkpoint selector
  补齐了

### 3. 当前最佳 no-res waveform route 已经能导出、能听、能治理
- `docs/195_stage5_waveform_step72_audio_export_bootstrap_report.md`
  已建立：
  - `step72`
    可导出
    `decoded.wav`
    与
    `aligned_target.wav`
- `docs/204_stage5_decoded_primary_listening_contract_report.md`
  已把：
  - 主听入口
    固定为
    `decoded.wav`
- `docs/223_stage5_low_activity_waveform_rms_generalization_and_governance_promotion_report.md`
  与
  `docs/230_stage5_step72_glitch_smoothing_ablation_report.md`
  到
  `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`
  则说明：
  - 当前 Stage5
    已具备：
    - low-activity
      probe
    - export-side
      decode 修正
    - GUI 听审
    - `postenv`
      默认治理

## 当前还没完成，或仍明显缺证据的部分

### 1. 当前 Stage5 还不是原设计里的完整条件声码器
- `docs/177_nores_vocoder_scaffold_bootstrap_report.md`
  已明确：
  - 当前 teacher path
    仍缺
    `f0_hz`
  - 噪声支路
    仍缺
    `r_res`
- 这意味着：
  当前路线更准确的说法仍然是：
  - Stage5 no-res bootstrap route
- 还不能直接写成：
  - 原设计完整版
    Stage5 vocoder

### 2. 当前 loss recipe 仍是 bootstrap，不是原设计终稿
- `docs/189_stage5_waveform_stft_bootstrap_decoder_report.md`
  已明确：
  - 当前接入的是
    minimal decoder +
    waveform L1 +
    single-resolution log-STFT
- `docs/198_stage5_audio_audit_proxy_retuning_and_silence_gate_fix_report.md`
  与
  `docs/204_stage5_decoded_primary_listening_contract_report.md`
  也都明确：
  - 当前还不是
    final multi-resolution /
    adversarial vocoder
- 因而原设计里的：
  - MRSTFT
  - adversarial
  - feature matching
  - 以及更完整的辅助约束
  目前还没有落地成
  Stage5
  正式主配方

### 3. 当前主观验证仍偏局部治理，不等于已证明“基本自然”
- 当前 Stage5
  最强的一批证据，
  主要集中在：
  - low-activity
    leakage
  - glitch / fragmentation
  - decode-side
    smoothing /
    postenv
    治理
- 这些证据很有价值，
  但它们回答的更像是：
  - 局部边界稳不稳
  - leakage
    控得好不好
- 它们还没有正式回答：
  - 当前 no-res route
    是否已经在更广的
    validation
    面上达到：
    - 可懂
    - 基本自然
    - 可作为
      Phase A
      门槛通过

### 4. 当前我没有找到 Stage5 专属的正式“控制变量使用性”证据
- 现有仓库里，
  早期
  offline MVP /
  Student
  路线
  有成熟的
  `z_art / e_evt`
  ablation
  体系。
- 但在当前
  Stage5
  文档序列里，
  我没有找到一份正式报告能够直接回答：
  - 当前 no-res vocoder
    去掉或削弱
    `z_art`
    会怎样
  - 去掉或削弱
    `e_evt`
    会怎样
  - 当前模型到底是在用：
    - 周期骨架 /
      事件条件
    - 还是主要在吃
      更容易优化的别的统计路径
- 这部分目前更像：
  - 缺证据
  而不是：
  - 已证明没问题

这里要说清楚：
- 这不是说
  当前 Stage5
  一定没在用控制变量。
- 更准确的说法是：
  - 现在还没有看到
    足够正式的
    Stage5
    专属证据，
    能把这件事写成
    已验证通过

## 对“是否继续扫当前环节其他方案”的判断

## 不建议继续扫
- 理由不是
  当前局部 tweak
  不重要，
  而是：
  - `postenv`
    已正式默认化
  - training-side
    apply mode
    短程无强信号
  - clean-only /
    reverb-like
    已有负结论
- 也就是说，
  当前这几条最顺手的局部题，
  都已经接近：
  - 已收口
  - 或暂不值得升格

## 为什么不建议继续扫
- 因为继续扫这些题，
  最容易出现的是：
  - 新结果继续增加
  - 但真正回答的仍是小问题
- 同时原设计层面的关键缺口，
  例如：
  - no-res
    是否已达基本自然
  - 控制变量是否真在起作用
  反而仍旧悬空

## 推荐的下一步方案

### 方案 A：推荐方案
- 当前先停止
  Stage5
  局部 tweak
  扩写
- 下一题改成：
  - `Stage5 no-res 原设计门槛验收`
- 重点不是继续调参数，
  而是把以下两件事补成正式证据：
  1. 当前 best no-res route
     是否已在更广样本面上达到：
     - 可懂
     - 稳定
     - 基本自然
  2. 当前 Stage5
     条件控制是否有正式使用性证据，
     若没有，
     就把缺口明示出来

### 方案 B：若必须继续开实验
- 也不建议再开：
  - `postenv`
    周边对照
  - training apply mode
    短程 probe
  - clean-only
    复跑
- 更值得开的第一条实验应改成：
  - Stage5 条件使用性 /
    门槛验收
    相关题

## 我建议的具体执行顺序
1. 先把当前 Stage5
   口径正式写成：
   - local decode-side
     治理已阶段性收口
   - 原设计门槛尚未被完整证明
2. 下一轮若继续实验线，
   不再开
   apply-mode /
   clean-only
   类小题
3. 真正新的优先题，
   应围绕：
   - Stage5 no-res
     的 broad listening /
     intelligibility /
     basic naturalness
     验收
   - 或
     Stage5 条件控制使用性
     证据补齐

## 一句话结论
- 当前 Stage5
  最合理的下一步，
  不是继续在现有局部环节扫更多方案，
  而是回到原设计的主门槛：
  - no-res 主干到底有没有真正站住
  - 当前控制变量到底有没有被正式证明在起作用
