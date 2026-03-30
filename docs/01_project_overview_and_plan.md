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
- The Stage3 post-hoc teacher-loss selector now has an explicit preferred CLI name, while the older `select-streaming-student-best-checkpoint` command remains only as a legacy alias.
- Stage3 also now has a combined selector-comparison CLI, so future checkpoint-family reviews can materialize selector disagreement directly instead of stitching two selector directories by hand.
- The combined selector-comparison artifact now also emits a decision summary that separates teacher-loss reference choice, handoff-facing packet candidate choice, and the conservative route-opening conclusion.
- The active corrected-manifold Stage5 winner is now `wfta003`, and it should not be retired by broad anti-thrash wording that was meant for already dead pure-buzz families.
- Paired Stage3 still lacks a valid frame bridge and alignment contract, so paired training cannot be treated as ready.
- Stage3 F0 representation is confirmed structurally blocked: coarse_log_f0 collapses to near-constant output in the current explicit_named_control_family_v1 architecture regardless of loss weight tuning. A structural decision is required before F0 can become a genuine handoff control.
- External reference review now supports a concrete recovery route:
  - do not insist on waveform-only implicit F0 discovery
  - formalize a Stage3 pitch-provider interface
  - integrate the in-repo deterministic extractor first
  - evaluate RMVPE second behind the same contract
- Step A is now implemented and smoke-validated:
  - `deterministic_extractor_v1` is wired through training, checkpoint eval, proxy export, and downstream packet export
  - the current strong F0 smoke metrics validate contract plumbing, not final runtime readiness
- Step B is now also implemented at wiring level:
  - `rmvpe_v1` is wired through the same Stage3 contract
  - current naive direct injection is not yet contract-compatible and fails the small packet screen
- Provider-only audit is now completed:
  - `deterministic_extractor_v1` is a clean positive control at the raw provider level
  - `rmvpe_v1` still fails raw provider-only readiness-like screening on `8/8` validation records
  - simple anchor and lag sweeps do not rescue RMVPE into a usable contract
- RMVPE diagnosis is now further narrowed:
  - hybrid `rmvpe_f0 + deterministic_vuv` still does not clear readiness-like screening
  - jointly voiced RMVPE F0 is often reasonable
  - the dominant remaining mismatch appears to be voiced-support contract drift rather than octave error or raw F0 magnitude collapse
- RMVPE voicing calibration is now also probed:
  - threshold sweep slightly changes the tradeoff but does not clear readiness
  - simple binary VUV postprocess presets are effectively no-ops on the audited validation slice
  - the current thresholded RMVPE route should not open a new packet-smoke cycle
- A confidence-aware RMVPE provider probe now also exists:
  - `rmvpe_confidence_v1` feeds unthresholded RMVPE F0 plus sampled confidence
  - provider-side evidence is stronger than old thresholded RMVPE
  - but one-step packet smoke still fails `F0` readiness on `0/3`
- A short controlled `rmvpe_confidence_v1` training loop and packet-aware selector pass are now also completed:
  - sampled validation improved and chose step `4`
  - packet-aware screening across steps `1` to `6` still found `f0_ready_count = 0/3` for every checkpoint
  - packet-facing best step `3` is only the least-bad candidate, not a route-opening winner
- A follow-up richer contract probe is now also completed:
  - `rmvpe_split_confidence_v1` keeps hard `VUV` and sampled confidence separate
  - the new probe passes supervision and one-step training smoke
  - sample3 packet readiness is still unchanged at `f0_ready_count = 0/3`
- A consumer-side confidence-gated correction probe is now also completed:
  - `provider_confidence_gate_mode = hard_vuv_times_confidence_v1`
  - the gate reduces correction magnitude substantially
  - sample3 packet readiness is still unchanged at `f0_ready_count = 0/3`
- The deterministic explicit-provider line has now progressed beyond bootstrap:
  - `deterministic_extractor_v1` with `f0_correction_enabled = false` reaches `f0_ready_count = 3/3`, `vuv_ready_count = 3/3`, and `aper_ready_count = 2/3` on the current sample3 packet screen
  - this makes `ENERGY`, not `F0`, the dominant remaining blocker on that line
- Deterministic energy-focus probes are now also bounded:
  - scratch energy-focused training can raise `energy_ready_count` to `2/3`, but only by giving back `F0` and `APER`
  - warm-starting from the packet-best deterministic checkpoint does not preserve the earlier `F0` opening under the same energy-focused objective
  - the current scalar-loss route is therefore exhausted for joint `F0 / VUV / APER / ENERGY` opening on this scaffold
- Deterministic energy-freeze isolation is now also probed:
  - a strict trainable-prefix allowlist can preserve packet-facing `F0 / VUV / APER` across all screened checkpoints
  - but `ENERGY` remains unchanged at `0/3`
  - this shows the remaining blocker is not only shared-update interference; the current scaffold also lacks enough isolated energy-specific capacity
- Deterministic dedicated energy-branch isolation is now also probed:
  - a new isolated `dedicated_energy_branch_v1` improves packet-facing `ENERGY` error while still preserving `F0 / VUV / APER`
  - packet-best `avg_energy_stage5_norm_calibrated_reference_mae` improves from `0.707125` to `0.550192`
  - but `energy_ready_count` still stays `0/3`, so the branch is not yet strong enough to open the route
- Deterministic Stage5-scale energy objective routing is now also probed:
  - a new `teacher_energy_stage5_state` loss supervises `ENERGY` on the same normalized scale used by the packet gate
  - the loss wiring works, but packet-best `avg_energy_stage5_norm_calibrated_reference_mae` only moves from `0.550192` to `0.550175`
  - so simple gate-scale alignment does not materially improve readiness on the current isolated branch
- Deterministic dedicated energy-branch widening is now also probed:
  - widening the isolated energy branch hidden dimension from `96` to `192` keeps `F0 / VUV / APER` stable
  - but the best energy value in the widened family is still worse than the earlier dedicated-branch result
  - later checkpoints fall back to the old `0.707125` plateau, so naive widening is not the right next move
- Deterministic Stage5-shape energy objective routing is now also probed:
  - Stage5-normalized temporal and correlation losses are wired correctly and do optimize during training
  - but every screened checkpoint still lands at `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
  - so generic Stage5 trajectory shaping is not enough; the next move should target dynamic range or calibration more directly
- Deterministic Stage5 dynamic-range energy objective routing is now also probed:
  - centered-shape and per-sample std losses slightly improve the packet-best isolated energy result to `0.550066`
  - but `energy_ready_count` still stays `0/3`
  - this is the first small positive signal inside the direct packet-facing objective family, not a route-opening result
- Deterministic Stage5 affine-calibrated energy objective routing is now also probed:
  - direct affine-calibrated Stage5 loss improves the isolated packet-best energy result further to `0.547625`
  - but `energy_ready_count` still stays `0/3`
  - a low-learning-rate follow-up at `2.5e-4` does not improve this and should not become the default continuation

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
  - keep the incumbent packet-facing reference at `vuvbalancedgate24.step24`
  - keep `warm6_18.step15` as the current packet-aware next-best non-reference candidate and teacher-loss leader in the current two-way role-aware comparison
  - use packet-aware selection for downstream packet and handoff screening
  - keep post-hoc full-checkpoint teacher-loss evaluation as a separate signal
  - prefer the explicit `posthoc-teacher-loss` selector name in new reports and commands
  - use the combined selector-comparison command when the checkpoint-family decision depends on reconciling both signals
  - cite the combined `decision_summary` block first when the conclusion needs a teacher-loss reference, a handoff-facing candidate, and a route-opening recommendation
- Current gate reading:
  - `e_evt / z_art` are ready
  - waveform-only `F0` remains structurally blocked in the old architecture: `coarse_log_f0` collapses to near-constant output (span 0.06 octaves vs target 2.6 octaves) regardless of loss weight or temporal loss tuning
  - under the deterministic explicit-provider nof0corr reference, `F0` and `VUV` are now open on the current sample3 packet screen and `APER` is partially open
  - `ENERGY` is the dominant remaining blocker on that explicit-provider line
  - Do not run further waveform-only F0 loss-weight or temporal-loss probes without a structural model change
- Current preferred structural recovery route for `F0`:
  - Step A: completed as `deterministic_extractor_v1`
  - Step B: completed bootstrap for `rmvpe_v1`, but current naive direct injection is not yet viable
  - Provider-only audit conclusion: RMVPE mismatch is not explained by simple lag alone
  - voiced-intersection conclusion: RMVPE F0 is often acceptable where voicing agrees; the next diagnosis must target provider-side VUV calibration
  - calibration conclusion: threshold sweep and simple VUV cleanup do not produce a viable current-contract RMVPE provider
  - confidence-aware bootstrap conclusion: `rmvpe_confidence_v1` is structurally more plausible than thresholded RMVPE, but still not packet-ready after one-step smoke
  - short-loop conclusion: the confidence-aware branch can reduce sampled teacher loss, but the current consumer and loss mix still do not convert it into packet-ready `F0`
  - split-confidence conclusion: separating hard `VUV` from provider confidence improves some `F0` MAE values but still does not improve packet readiness or `F0` correlation enough to matter
  - gated-correction conclusion: confidence-gating the correction branch reduces correction activity but still does not rescue packet-facing `F0`
  - deterministic nof0corr conclusion: explicit deterministic provider plus disabled `F0` correction is now the strongest packet-facing positive reference on sample3
  - deterministic energy-focus conclusion: the remaining blocker is co-optimizing `ENERGY` without damaging already-open `F0 / VUV / APER`
  - deterministic warm-start conclusion: better sampled validation and packet-best warm-starting still do not preserve packet-facing `F0` once the current energy-focused objective is applied
  - deterministic energy-freeze conclusion: preserving `F0 / VUV / APER` with a strict energy-head allowlist still leaves `ENERGY` completely unchanged, so the next escalation must add isolated energy capacity rather than more scalar tuning
  - deterministic energy-adapter conclusion: a dedicated isolated energy branch does improve packet-facing `ENERGY` error without harming already-open `F0 / VUV / APER`, but it still does not clear the packet gate
  - deterministic stage5-energy-objective conclusion: directly supervising normalized Stage5 energy does not materially improve the current isolated branch, so the next escalation should focus on stronger isolated capacity or more direct packet-facing objectives
  - deterministic energy-widening conclusion: naive widening of the isolated energy branch does not beat the earlier dedicated-branch result and is not a promising default continuation
  - deterministic energy-stage5-shape conclusion: adding Stage5 temporal and correlation losses is active at teacher-loss level but packet-facing `ENERGY` still collapses back to `0.707125`, so generic trajectory shaping is also not a promising continuation
  - deterministic energy-dynamic-range conclusion: centered-state and std losses finally beat the earlier isolated energy best slightly, but the gain is still sub-threshold and `ENERGY` remains fully closed at packet gate
  - deterministic energy-affine-calibrated conclusion: direct calibration-aware loss is now the best deterministic isolated-energy result so far, but the gain is still sub-threshold and a simple lr-half follow-up does not improve it
  - keep both providers behind one shared Stage3 contract for fair comparison

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
- Keep managed output paths inside the current Windows-safe path budget and prefer compact `ss_*` artifact roots for new Stage3 selector outputs.
- Long historical context belongs in `docs/archive/`, not back in active docs.
- Enable `skip_existing` only after verifying artifact identity and reuse safety.
- Important experiment and asset changes must land in traceable summary artifacts such as final summaries and machine-readable JSON.

## Current Recommended Next Steps
1. Continue generation-side completion around `acoustic_directional_targetstate_bridge_v1`.
2. Keep handoff candidates behind cheap screen and readiness gate before opening a new Stage5 adapter route.
3. Keep the current `wfta003` corrected-manifold line active, but only for a clearly different localization-oriented probe rather than more blind same-family weight shrinking.
4. Finish frame bridge and alignment contract work before any paired Stage3 training decision.
5. Treat `C-prime / v2-core` as a strategic contract backlog. The immediate named-control blocker is now split: `vuv / aper / E` are training-addressable; `F0` requires a structural decision (explicit pitch feature input vs accepting permanent gate closure).
6. Use the new packet-aware selector for downstream-facing Stage3 checkpoint ranking, and label post-hoc full-checkpoint eval results explicitly instead of calling every selector output the same "best checkpoint".
7. Keep writing long-lived conclusions back to `docs/01_project_overview_and_plan.md` and `docs/02_pitfalls_log.md`, while leaving local experiment detail in numbered reports.
8. For the current `F0` recovery route, keep the provider comparison order explicit:
   - completed bootstrap: in-repo deterministic extractor
   - completed bootstrap: RMVPE sidecar
   - completed diagnosis milestone: provider-only audit confirms deterministic positive control and RMVPE raw-contract failure
   - completed diagnosis milestone: hybrid-VUV and voiced-intersection audit shows the dominant issue is voiced-support mismatch, not octave drift
   - completed diagnosis milestone: RMVPE voicing-threshold and simple VUV-postprocess calibration do not rescue the current thresholded route
   - completed structural probe: confidence-aware RMVPE provider is wired and smoke-runnable, but still fails packet-level F0 readiness
   - completed short-loop probe: longer same-contract training still leaves all screened checkpoints at `f0_ready_count = 0/3`
   - completed split-confidence probe: confidence and hard `VUV` separation still leaves sample3 at `f0_ready_count = 0/3`
   - completed gated-correction probe: confidence-gated `F0/VUV` correction still leaves sample3 at `f0_ready_count = 0/3`
   - next action: stop the current RMVPE Stage3 family; if RMVPE continues later, require a larger consumer or objective redesign rather than more same-family smokes
9. For the deterministic explicit-provider line:
   - keep `deterministic_extractor_v1` plus `f0_correction_enabled = false` as the current packet-facing reference
   - treat `ENERGY` as the dominant remaining blocker on that line
   - do not continue scalar energy weight nudging by inertia
   - completed isolation probe: strict stagewise freeze preserves already-open `F0 / VUV / APER` but does not move `ENERGY`
   - completed dedicated-branch probe: isolated energy-specific capacity now improves packet-facing `ENERGY` error while preserving already-open `F0 / VUV / APER`, but still leaves `energy_ready_count = 0/3`
   - completed stage5-scale objective probe: energy supervision aligned to packet-gate normalization is wired and valid, but gives no meaningful packet-facing gain beyond the existing dedicated branch result
   - completed widening probe: naive branch widening to `192` does not beat the earlier dedicated-branch result and shows short-loop instability
   - completed Stage5-shape probe: generic Stage5 temporal and correlation losses are active but packet-facing `ENERGY` fully regresses to the old `0.707125` plateau
   - completed dynamic-range probe: centered-state and std losses slightly improve packet-best `ENERGY` to `0.550066`, but `energy_ready_count` still remains `0/3`
   - completed affine-calibrated probe: direct calibration-aware loss further improves packet-best `ENERGY` to `0.547625`, but `energy_ready_count` still remains `0/3`
   - completed lr-half follow-up: halving learning rate to `2.5e-4` does not improve the affine-calibrated result and should not become the default continuation
   - if this line continues, keep the dedicated energy-branch family and continue only with more explicit calibration-aware objectives instead of returning to shared scalar tuning, same-family scale alignment, naive width scaling, generic trajectory shaping, or blind lr-half retries
10. Do not keep third-party reference repositories as permanent root-level directories once their design lessons are captured on disk.

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
- `docs/478_stage3_selector_naming_hardening_and_legacy_alias_report.md`
- `docs/479_stage3_selector_comparison_cli_and_divergence_materialization_report.md`
- `docs/480_stage3_selector_comparison_decision_summary_hardening_report.md`
- `docs/481_stage3_packet_reference_vs_warm6_candidate_role_aware_comparison_report.md`
- `docs/482_windows_path_budget_and_artifact_naming_policy.md`
- `docs/483_stage3_selector_output_path_budget_remediation_report.md`
- `docs/484_stage3_f0_corrfocus_nogo_and_sigmoid_collapse_diagnosis_report.md`
- `docs/485_stage3_f0_unboundedf0_unit_mismatch_and_corrected_root_cause_report.md`
- `docs/486_stage3_f0_sigmoid_collapse_systematic_diagnosis_and_structural_escalation_report.md`
- `docs/487_stage3_rvc_reference_review_and_rmvpe_sidecar_plan_report.md`
- `docs/488_stage3_deterministic_pitch_provider_bootstrap_and_smoke_report.md`
- `docs/489_stage3_rmvpe_provider_bootstrap_and_contract_mismatch_smoke_report.md`
- `docs/490_stage3_provider_only_audit_and_rmvpe_contract_diagnosis_report.md`
- `docs/491_stage3_rmvpe_voiced_intersection_and_hybrid_vuv_diagnosis_report.md`
- `docs/492_stage3_rmvpe_voicing_threshold_and_vuv_postprocess_calibration_report.md`
- `docs/493_stage3_rmvpe_confidence_provider_bootstrap_and_packet_smoke_report.md`
- `docs/494_stage3_rmvpe_confidence_short_loop_and_packet_selector_report.md`
- `docs/495_stage3_rmvpe_split_confidence_probe_report.md`
- `docs/496_stage3_rmvpe_splitconf_gated_correction_probe_report.md`
- `docs/497_stage3_detpitch_nof0corr_energy_tradeoff_and_warmstart_nogo_report.md`
- `docs/498_stage3_detpitch_energyfreeze_isolation_probe_report.md`
- `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
- `docs/500_stage3_detpitch_energy_stage5_objective_routing_probe_report.md`
- `docs/501_stage3_detpitch_energy_adapter_widening_probe_report.md`
- `docs/502_stage3_detpitch_energy_stage5_shape_objective_probe_report.md`
- `docs/503_stage3_detpitch_energy_stage5_dynamic_range_objective_probe_report.md`
- `docs/504_stage3_detpitch_energy_stage5_affine_calibrated_objective_and_lrhalf_followup_report.md`
