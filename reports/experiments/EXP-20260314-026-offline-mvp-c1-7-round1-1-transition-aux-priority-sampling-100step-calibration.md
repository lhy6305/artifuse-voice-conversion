# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-026-offline-mvp-c1-7-round1-1-transition-aux-priority-sampling-100step-calibration
- date: 2026-03-15T00:12:00
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_sampling_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar with clause spans and utterance structure types
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep the independent clause-transition auxiliary loss from `EXP-025`, but raise the appearance density of transition-rich target records during early and mid training via targeted sampling
- hypothesis: if the auxiliary loss is valid but underpowered because transition-rich records do not appear densely enough in the current uniform sampler, priority interleave on `clause_count >= 4 OR multi_terminal` should improve the unresolved `step50` dependency dip more effectively than more loss-constant tweaking

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and upgraded `C1` sidecar were both reused unchanged; priority pool count is `234 / 592` under `clause_count >= 4 OR multi_terminal`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 1.357745`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.732196`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; aggressive priority interleave is the first sampling change that materially moves the route-C trajectory, producing the best main validation so far, but it worsens the punctuation-only challenge gap and pushes the `step50` dependency dip deeper instead of fixing it.
- failures: no execution failure; methodologically the target remains unmet because `step50 zero_e_evt.delta_target_loss_total = -0.933602` and `step50 zero_z_art.delta_target_loss_total = -0.300652` are both worse than `EXP-025`, while final `target_special_eval.delta_loss_total = 0.101163` regresses sharply despite `target_validation.loss_total = 2.648178`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-026-offline-mvp-c1-7-round1-1-transition-aux-priority-sampling-100step-calibration.metrics.json
