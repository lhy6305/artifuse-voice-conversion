# AI Work Sessions Index

- generated_at: 2026-03-21T18:10:58
- session_count: 14
- active_session_count: 2
- conflict_count: 0
- conflicted_session_count: 0

## Write Root Conflicts
- none

## planned
- none

## active
- user_line_minimal_runtime: owner=codex-b lane=user_line objective=continue terminal-user minimal source-to-target runtime hardening
  write_roots=['F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_runs', 'F:/proj_dev/tmp/workdir4/scripts/run_teacher_first_single_target_vc_demo.ps1']
- user_line_runtime_risk_and_gate_isolation_20260321: owner=codex-main lane=user_line objective=implement gate-isolation decoder diagnostics and runtime risk warnings for teacher-first single-target user line
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/teacher_first_vc_demo.py', 'F:/proj_dev/tmp/workdir4/src/v5vc/cli.py', 'F:/proj_dev/tmp/workdir4/docs/01_project_overview_and_plan.md', 'F:/proj_dev/tmp/workdir4/docs/02_pitfalls_log.md', 'F:/proj_dev/tmp/workdir4/docs/250_user_line_context_restore_and_decoder_behavior_takeover_report.md', 'F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']

## blocked
- none

## completed
- experiment_line_decode_applymode_hardening_20260321: owner=codex-main lane=experiment_line objective=completed Stage5 decode-side apply-mode semantics hardening for training-path explicitness
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/offline_vocoder_training.py', 'F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_next_question_assessment_20260321: owner=codex-main lane=experiment_line objective=completed ranked next-question assessment for experiment line and recommended freezing low-information sublines
  write_roots=['F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_stage5_decode: owner=codex-a lane=experiment_line objective=completed Stage5 decode-side governance after postenv default promotion
  write_roots=['F:/proj_dev/tmp/workdir4/reports/audio', 'F:/proj_dev/tmp/workdir4/scripts/launch_stage5_step72_glitch_smooth3_postenv_validation12_audit.ps1']
- experiment_line_stage5_milestone_acceptance_design_20260321: owner=codex-main lane=experiment_line objective=duplicate registry entry resolved in favor of experiment_line_stage5_milestone_acceptance_kickoff_20260321
  write_roots=['F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
  depends_on=['experiment_line_stage5_milestone_acceptance_kickoff_20260321']
- experiment_line_stage5_milestone_acceptance_kickoff_20260321: owner=codex-main lane=experiment_line objective=completed Stage5 no-res milestone acceptance kickoff with fixed listening bundle, script entry, and GUI smoke
  write_roots=['F:/proj_dev/tmp/workdir4/scripts/launch_stage5_nores_milestone_acceptance_audit.ps1', 'F:/proj_dev/tmp/workdir4/reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session', 'F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_stage5_milestone_acceptance_tooling_20260321: owner=codex-main lane=experiment_line objective=completed Stage5 no-res milestone acceptance tooling hardening with dedicated GUI mode and fixed result materializer
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/audio_audit_gui.py', 'F:/proj_dev/tmp/workdir4/src/v5vc/stage5_nores_milestone_acceptance_report.py', 'F:/proj_dev/tmp/workdir4/reports/templates/stage5_nores_milestone_acceptance_report_template.md', 'F:/proj_dev/tmp/workdir4/scripts/launch_stage5_nores_milestone_acceptance_audit.ps1', 'F:/proj_dev/tmp/workdir4/scripts/materialize_stage5_nores_milestone_acceptance_result_report.ps1', 'F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_stage5_milestone_review_20260321: owner=codex-main lane=experiment_line objective=completed Stage5 original-design milestone review and redirected next-step recommendation from local tweak scanning back to no-res milestone acceptance
  write_roots=['F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_takeover_restore_20260321: owner=codex-main lane=experiment_line objective=restored experiment-line state after postenv promotion and documented current handoff boundary
  write_roots=['F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_training_applymode_plumbing_20260321: owner=codex-main lane=experiment_line objective=completed training-side reconstruction apply-mode CLI plumbing without changing the default training semantics
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/cli.py', 'F:/proj_dev/tmp/workdir4/src/v5vc/offline_vocoder_training.py', 'F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- experiment_line_training_applymode_probe_20260321: owner=codex-main lane=experiment_line objective=completed minimal controlled A/B probe for training-side reconstruction apply mode with no strong short-horizon signal
  write_roots=['F:/proj_dev/tmp/workdir4/reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1', 'F:/proj_dev/tmp/workdir4/docs', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- user_line_applicability_probe_20260321: owner=codex-main lane=user_line objective=completed applicability diagnosis for teacher-first single-target review bundle buzzing failure with decoder-behavior probe
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/teacher_first_vc_demo.py', 'F:/proj_dev/tmp/workdir4/src/v5vc/cli.py', 'F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe', 'F:/proj_dev/tmp/workdir4/docs/01_project_overview_and_plan.md', 'F:/proj_dev/tmp/workdir4/docs/02_pitfalls_log.md', 'F:/proj_dev/tmp/workdir4/docs/250_user_line_context_restore_and_decoder_behavior_takeover_report.md', 'F:/proj_dev/tmp/workdir4/reports/collab/ai_work_sessions']
- user_line_review_bundle_20260321: owner=codex-main lane=user_line objective=completed terminal-user batch export and listening bundle on top of the teacher-first single-target runtime
  write_roots=['F:/proj_dev/tmp/workdir4/src/v5vc/teacher_first_vc_demo.py', 'F:/proj_dev/tmp/workdir4/src/v5vc/cli.py', 'F:/proj_dev/tmp/workdir4/scripts/run_teacher_first_single_target_vc_review_bundle.ps1', 'F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_review_bundles']
