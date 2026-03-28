# Project Overview and Execution Plan

## Document Role
- This file keeps only the project goal, stage judgment, active lines of work, and next steps needed for takeover.
- Detailed per-round experiment logs and old long-form history should not keep flowing back into this file.
- Current archive snapshots:
  - `docs/archive/01_project_overview_and_plan_snapshot_20260326.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260328.md`

## Project Goal Summary
- Based on `initial_design.md`, the project goal remains an industrial voice-conversion system that balances high offline quality with low online latency.
- The core control-chain design state remains:
  - `z_art`
  - `e_evt`
  - `F0 / vuv / aper / E`
  - tightly constrained `r_res`
- The main principles are unchanged:
  - the no-residual backbone must stand on its own first
  - the system must not collapse into a neural codec hidden behind an interpretable shell
  - streaming end-to-end closure comes after offline backbone validation

## Current Repository Layout
- `initial_design.md`: primary design document
- `initial_design_judg.md`: risk and de-romanticization review
- `manage.py`: unified command entry
- `python.exe`: fixed project interpreter
- `src/v5vc/`: main source tree for Stage3, Stage5, teacher-first, and streaming-student work
- `configs/`: configuration files and templates
- `reports/`: training, evaluation, export artifacts, and structured experiment outputs
- `docs/`: active docs and numbered reports
- `docs/archive/`: archived snapshots from older stages

## Current Stage Assessment
- The strongest current Stage3 reference remains generation-side work around `acoustic_directional_targetstate_bridge_v1`.
- The old `Stage5 no-res downstream` route is no longer the default route worth re-running by inertia.
- The `student_control_packet -> minimal Stage5 adapter` path already reached real `decoded.wav` smoke level, but obvious buzz already gave a harder fail-fast negative conclusion.
- Stage3 now has a formal packet-aware checkpoint selector, and Stage3 checkpoint choice must no longer collapse training-trajectory validation, post-hoc full-checkpoint evaluation, and packet-aware screening into one "best checkpoint" label.
- The active corrected-manifold Stage5 winner is now `wfta003`, and it should not be retired by broad anti-thrash wording that was meant for already dead pure-buzz families.
- Paired Stage3 still lacks a valid frame bridge and alignment contract, so paired training cannot be treated as ready.

## Current Main Lines

### Line A: Continue teacher-label and target-state generation-side completion
- Current reference:
  - `acoustic_directional_targetstate_bridge_v1`
- Current action:
  - continue generation-side bridge and target-state completion
  - do not go back to old `acoustic_contextual` micro-patches
  - do not overinterpret loss-side imitation improvements as readiness improvements

### Line B: Re-identify the correct handoff family instead of recycling the old Stage5 route
- The highest-priority current candidate is still `Stage3 student-control packet v1`.
- Before opening a new Stage5 route, require:
  - `proxy-acoustic / proxy-audio` cheap screen
  - named-control readiness negative gate
- For Stage3 checkpoint choice inside this line:
  - use packet-aware selection for downstream packet and handoff screening
  - keep post-hoc full-checkpoint teacher-loss evaluation as a separate signal
- Current gate reading:
  - `e_evt / z_art` are ready
  - `F0 / vuv / aper / E` are still not handoff-ready

### Line C: Finish paired Stage3 wiring and alignment prerequisites before paired training
- Current prerequisites include:
  - `source_semantic_parity_sidecar` must attach `source_record_id`
  - target teacher labels must obey formal split alignment constraints
- Current hard limitation:
  - source waveform and target teacher frame sequences are not naturally aligned

## Current Maintenance Rules
- Active documents must stay in English ASCII.
- All repository text files must stay UTF-8 without BOM on disk.
- Use only `.\python.exe ...` for Python commands.
- Long historical context belongs in `docs/archive/`, not back in active docs.
- Enable `skip_existing` only after verifying artifact identity and reuse safety.
- Important experiment and asset changes must land in traceable summary artifacts such as final summaries and machine-readable JSON.

## Current Recommended Next Steps
1. Continue generation-side completion around `acoustic_directional_targetstate_bridge_v1`.
2. Keep handoff candidates behind cheap screen and readiness gate before opening a new Stage5 adapter route.
3. Keep the current `wfta003` corrected-manifold line active, but only for a clearly different localization-oriented probe rather than more blind same-family weight shrinking.
4. Finish frame bridge and alignment contract work before any paired Stage3 training decision.
5. Treat `C-prime / v2-core` as a strategic contract backlog, while keeping the immediate named-control blocker statement focused on `F0 / vuv / aper / E`.
6. Use the new packet-aware selector for downstream-facing Stage3 checkpoint ranking, and label post-hoc full-checkpoint eval results explicitly instead of calling every selector output the same "best checkpoint".
7. Keep writing long-lived conclusions back to `docs/01_project_overview_and_plan.md` and `docs/02_pitfalls_log.md`, while leaving local experiment detail in numbered reports.

## Key Reference Reports
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/375_stage3_teacher_label_target_state_contract_completion_report.md`
- `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
- `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- `docs/447_repo_health_and_compliance_audit_20260328.md`
- `docs/475_stage5_corrected_manifold_vnc01_maskfix_wfta003_followup_report.md`
- `docs/476_root_1md_strategy_memo_independent_assessment.md`
- `docs/477_stage3_packet_aware_checkpoint_selector_integration_and_selection_drift_report.md`
