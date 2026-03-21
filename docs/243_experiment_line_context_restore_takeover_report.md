# 2026-03-21 实验线上下文恢复与接班报告

## 目的
- 在上次对话因上下文过长中断后，
  只针对实验线恢复当前真实状态。
- 避免把当前停点误判回：
  - `postenv` focused human audit 仍待完成
  - 或旧听审脚本仍是唯一需要继续的事项

## 本轮实际读取与核对范围
1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/236_stage5_step72_decode_gate_smooth3_postenv_validation_report.md`
5. `docs/240_stage5_step72_glitch_smooth3_postenv_human_audit_reactivation_report.md`
6. `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`
7. `docs/242_multi_ai_parallel_collaboration_assessment_and_registry_report.md`
8. 边界参考：
   - `docs/238_teacher_first_single_target_terminal_user_line_bootstrap_report.md`
   - `docs/239_teacher_first_single_target_multisource_smoke_and_wrapper_report.md`
9. 代码与产物：
   - `src/v5vc/cli.py`
   - `src/v5vc/nores_vocoder_audio_export.py`
   - `src/v5vc/offline_vocoder_training.py`
   - `src/v5vc/teacher_first_vc_demo.py`
   - `scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1`
   - `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/audio_audit_review.json`
   - `reports/collab/ai_work_sessions/ai_work_sessions_index.md`

## 当前真实状态恢复结论

### 1. 实验线已经不再停在“待听审”
- `docs/240`
  记录的是：
  - 听审入口恢复可启动
  - 但当时正式 review
    尚未落盘
- 当前磁盘真实状态已经继续推进到：
  - `docs/241`
  - 以及正式产物
    `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/audio_audit_review.json`
- 当前 review
  已完成：
  - `record_count = 10`
  - `completed_count = 10`
  - `overall_pick / best_boundary / most_stable / best_rhythm`
    均为
    `打平 10`
- 所以实验线当前真实停点应写成：
  - `postenv` focused human audit
    已完成
  - Stage5 decode-side 默认 apply mode
    已提升为
    `post_ola_envelope`

### 2. 当前代码默认值已与上述结论对齐
- `src/v5vc/nores_vocoder_audio_export.py`
  当前正式平滑默认常量为：
  - `DEFAULT_PREDICTED_ACTIVITY_GATE_SMOOTHING_FRAMES = 3`
- `src/v5vc/cli.py`
  中：
  - `export-offline-mvp-nores-vocoder-audio`
    默认
    `--predicted-activity-gate-smoothing-frames = 3`
  - `export-offline-mvp-nores-vocoder-audio`
    默认
    `--predicted-activity-gate-apply-mode = post_ola_envelope`
- 同文件中：
  - `run-offline-mvp-teacher-first-vc-demo`
    也已同步默认
    `post_ola_envelope`
- `scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1`
  当前仍与短路径 probe / session
  目录口径一致，
  且保留 bundle 缺失时的自动重建能力

### 3. 当前实验线真正需要警惕的不是“听审没做完”，而是两个边界
- 协作边界：
  - `reports/collab/ai_work_sessions/ai_work_sessions_index.md`
    一度仍把
    `experiment_line_stage5_decode`
    记成
    `active`
  - 但从实验内容看，
    该 objective
    已在
    `docs/241`
    完成
- 代码边界：
  - `src/v5vc/offline_vocoder_training.py`
    里的
    `reconstruct_waveform_from_frames(...)`
    低层默认值仍是：
    `frame_gain_apply_mode = "pre_overlap_add"`
  - 当前主线 CLI
    都会显式传
    `post_ola_envelope`，
    所以正式 decode / export
    不受影响
  - 但这不等于：
    - 所有低层调用
      都已全局切成
      `postenv`

## 当前接班判断

### 1. 这次接班不应再回到旧问题
- 不应再把下一棒写成：
  - 继续
    `step72__decode_gate_smooth3`
    vs
    `step72__decode_gate_smooth3_postenv`
    focused human audit
- 不应再把
  `docs/240`
  的中间态，
  误当成当前最终状态

### 2. 当前更准确的实验线起点
- Stage5 decode-side
  的
  `smooth3 + post_ola_envelope`
  已是正式默认
- 旧的
  `pre_overlap_add`
  当前只应视为：
  - 显式回退口径
  - 历史复现口径

### 3. 当前更合理的下一步
- 若继续实验线，
  应先定义：
  - `postenv`
    默认提升之后，
    下一道真正要回答的
    decode-side / governance
    问题是什么
- 在该问题被明确前，
  不要重开旧听审
  或扩做已经收口的
  `smooth3`
  vs
  `postenv`
  对照

## 多 AI 协作处理
- 本轮已按
  `docs/242`
  先登记恢复会话，
  并避开现有
  `reports/audio`
  write root
- 当前更合理的 registry
  状态应是：
  - 已完成的旧实验线会话
    标记为
    `completed`
  - 新一轮真正继续实验线时，
    再以新的 objective
    和新的 write roots
    重新登记

## 一句话结论
- 当前实验线已经从
  “`postenv` 待听审”
  正式推进到
  “`postenv` 听审完成且默认已提升”；
  下次接班不应再回到旧听审，
  而应从新的 decode-side 治理问题重新立题。
