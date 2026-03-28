# 451 Stage3 timingfocus and warm-start probe report

## 结论
- 单阶段 `timingfocus` 是目前最温和的 loss-side 权重候选：
  - `12-step` 略优于 `vuvbalancedgate12`
  - `12-step packet` 基本持平
  - 但拉到 `24-step` 后，packet 仍然和 `evtfocus` 路线一样明显退化
- 两阶段 warm-start 是本轮最有价值的新信号：
  - `timingfocus12 -> baseline12` 的 validation 明显优于 `baseline24`
  - 说明“前半程定向拉齐、后半程回到 baseline”这条训练范式是成立的
  - 但 packet 仍未达到可替换 `baseline24` 的程度，尤其 energy readiness 和部分 f0 指标仍退
- 因此本轮结束时：
  - 不切换当前 packet-facing reference，仍保留 `vuvbalancedgate24`
  - 保留 warm-start 入口能力，作为后续主线实验基础设施

## 本轮改动
- 更新：
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `src/v5vc/cli.py`
- 新增：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_timingfocus_v1.json`
- 能力补充：
  - `run-streaming-student-training-loop` 新增 `--init-checkpoint`
  - 新 loop 仅加载 init checkpoint 的 `model_state_dict`
  - optimizer / loss schedule 重新开始，适合做两阶段 warm-start

## A. timingfocus 单阶段

### 1. `timingfocus12`
- 配置：
  - `configs/streaming_student_loss_weights_vuv_balanced_gate_timingfocus_v1.json`
- 通道权重：
  - `5:1.08,6:1.08,7:1.12`
- 资产：
  - `reports/training/streaming_student_loop_vuvbalancedgate_timingfocus12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_timingfocus12_round1_1/`
- 相对 `vuvbalancedgate12`，validation 小幅正向：
  - `loss_total: 1.524679 -> 1.523894`
  - `loss_total_semantic_disabled_reference: 1.40554 -> 1.405033`
  - `loss_teacher_event: 0.441675 -> 0.44149`
  - `loss_teacher_event_prior: 0.510075 -> 0.508282`
- packet 基本持平：
  - baseline12 与 timingfocus12 都是
    - `f0=0 / vuv=1 / aper=2 / energy=3 / all_records_auto_reject=true`

### 2. `timingfocus24`
- 资产：
  - `reports/training/streaming_student_loop_vuvbalancedgate_timingfocus24_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_vuvbalancedgate_timingfocus24best_round1_1/`
- 相对 `vuvbalancedgate24`，validation 仍略好：
  - baseline24 final
    - `loss_total = 0.919927`
    - `loss_total_semantic_disabled_reference = 0.832382`
    - `loss_teacher_event = 0.325852`
    - `loss_teacher_event_prior = 0.392491`
  - timingfocus24 final
    - `loss_total = 0.919286`
    - `loss_total_semantic_disabled_reference = 0.832012`
    - `loss_teacher_event = 0.325423`
    - `loss_teacher_event_prior = 0.391635`
  - timingfocus24 best
    - `step18`
    - `loss_total = 0.913462`
- 但 packet 仍明显退化：
  - baseline24 summary
    - `f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
  - timingfocus24best summary
    - `f0=0 / vuv=1 / aper=3 / energy=1 / all_records_auto_reject=true`
- 三条代表记录都表现为同类退化：
  - `target::chapter3_3_firefly_162`
    - `vuv_reference_mae: 0.107152 -> 0.127376`
    - `f0_proxy_reference_corr: 0.495445 -> 0.493158`
    - `f0_calibrated_log2_mae: 0.17472 -> 0.176837`
    - `aper_calibrated_reference_mae: 0.095282 -> 0.103497`
  - `target::chapter3_3_firefly_138`
    - `vuv_reference_mae: 0.207186 -> 0.226799`
    - `f0_proxy_reference_corr: 0.187293 -> 0.180496`
    - `f0_calibrated_log2_mae: 0.431756 -> 0.430847`
    - `aper_calibrated_reference_mae: 0.137007 -> 0.150733`
  - `target::chapter3_4_firefly_106`
    - `vuv_reference_mae: 0.255081 -> 0.282374`
    - `f0_proxy_reference_corr: 0.608869 -> 0.591957`
    - `f0_calibrated_log2_mae: 0.370633 -> 0.385449`
    - `aper_calibrated_reference_mae: 0.12198 -> 0.142962`

## B. 两阶段 warm-start

### 1. 设计
- 路线：
  - 先用 `timingfocus12` 学到更好的 early semantic fit
  - 再回到 baseline loss weights 继续训练 12 步
- 实现方式：
  - 新 loop 使用 `--init-checkpoint`
  - 初始化 checkpoint：
    - `reports/training/streaming_student_loop_vuvbalancedgate_timingfocus12_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate_timingfocus12_round1_1.step12.pt`
- 续跑资产：
  - `reports/training/streaming_student_loop_timingfocus12warm_baseline12_round1_1/`
  - `reports/runtime/streaming_student_downstream_control_packet_timingfocus12warm_baseline12_round1_1/`

### 2. validation
- 相对 `baseline24`，warm-start validation 明显更强：
  - baseline24 final
    - `loss_total = 0.919927`
    - `loss_total_semantic_disabled_reference = 0.832382`
    - `loss_teacher_event = 0.325852`
    - `loss_teacher_event_prior = 0.392491`
  - warm-start final/best
    - `loss_total = 0.833233`
    - `loss_total_semantic_disabled_reference = 0.741754`
    - `loss_teacher_event = 0.340539`
    - `loss_teacher_event_prior = 0.388945`
- 解读：
  - 总 loss 和 semantic-disabled reference 都有显著下降
  - `teacher_event` 单项略高于 baseline24
  - `teacher_event_prior` 略低于 baseline24
  - 说明 warm-start 的主收益更像“整体收敛形态改善”，不是单一 event 项直降

### 3. packet
- readiness summary：
  - baseline24：`f0=0 / vuv=1 / aper=3 / energy=3 / all_records_auto_reject=true`
  - warm-start：`f0=0 / vuv=1 / aper=3 / energy=1 / all_records_auto_reject=true`
- 代表记录：
  - `target::chapter3_3_firefly_162`
    - `vuv_reference_mae: 0.107152 -> 0.106564`
    - `f0_proxy_reference_corr: 0.495445 -> 0.432845`
    - `f0_calibrated_log2_mae: 0.17472 -> 0.186373`
    - `aper_calibrated_reference_mae: 0.095282 -> 0.103936`
  - `target::chapter3_3_firefly_138`
    - `vuv_reference_mae: 0.207186 -> 0.20369`
    - `f0_proxy_reference_corr: 0.187293 -> 0.144777`
    - `f0_calibrated_log2_mae: 0.431756 -> 0.429963`
    - `aper_calibrated_reference_mae: 0.137007 -> 0.148242`
  - `target::chapter3_4_firefly_106`
    - `vuv_reference_mae: 0.255081 -> 0.248215`
    - `f0_proxy_reference_corr: 0.608869 -> 0.555656`
    - `f0_calibrated_log2_mae: 0.370633 -> 0.4098`
    - `aper_calibrated_reference_mae: 0.12198 -> 0.140709`
- 解读：
  - `vuv_reference_mae` 三条都变好
  - 但 `f0_proxy_reference_corr` 三条都显著下降
  - `aper_calibrated_reference_mae` 三条都变差
  - `energy_ready_count` 从 `3` 降到 `1`
- 因此 warm-start 仍然不能替换 `baseline24` 作为 packet-facing reference。

## 最终判断
- 权重线和 warm-start 线共同说明：
  - 仅靠 Stage3 teacher-supervised loss 的改善，仍然不足以保证 packet-facing named controls 变好
  - warm-start 比单阶段权重更值得保留，因为它第一次给出了“明显更好的 validation 且 packet 没有全面崩坏”的结构化信号
  - 但当前 packet 退化仍超出可接受范围
- 当前主线状态：
  - packet-facing reference 继续保持 `vuvbalancedgate24`
  - 可继续探索的下一个方向不再是扩大通道权重，而应围绕 warm-start 范式本身继续收窄：
    - 更短的加权 warm phase
    - 更保守的 phase2 学习率/步数
    - 或显式把 packet-facing cheap screen 纳入 checkpoint 选择
