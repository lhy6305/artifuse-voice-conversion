# Experiment Record Template

## Metadata
- experiment_id: EXP-20260314-022-offline-mvp-c1-4-round1-1-evt-a2-dimonly-100step-calibration
- date: 2026-03-14T22:57:04
- owner: codex
- code_ref:
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_4_round1_1_evt_a2_dimonly_smallscale_100_seeded_shuffle.json

## Data
- target_manifest: data_prep/round1_1/manifests/target_train.jsonl
- source_manifest: data_prep/round1_1/manifests/source_train.jsonl
- data_filters: materialized split `hybrid_stratified_blocked`, `target_text_feature_version = b1_1_stats_v2`, rebuilt `round1.1` weak-event sidecar, `round1.1 / C1.4` recipe unchanged except `event_dimension_weights`
- known_exclusions: `42` recovered lexical target samples remain inside the `round1.1` main manifest; `5` `no_text_voice` records remain isolated outside the main training manifest

## Objective
- baseline_or_change: keep `round1.1 / C1.4` and sampler unchanged, but apply the minimal `A2` stability test by enabling only event-dimension reweighting
- hypothesis: if the mid-training dependency dip mainly comes from event dimensions being too weakly emphasized inside the existing loss, dimension-only reweighting may improve `step50` stability without the broader regressions seen in `A1`

## Model Scope
- offline_or_streaming: offline
- uses_text_in_training: true
- uses_text_in_runtime: false
- r_res_enabled: false

## Checks
- data_integrity: passed, `round1.1` split and sidecar were reused unchanged; final counts remain `target_train = 592`, `target_validation = 66`, `target_special_eval = 8`, `source_train = 483`, `source_validation = 54`
- z_art_ablation: passed, `zero_z_art.delta_target_loss_total = 0.899777`
- e_evt_ablation: passed, `zero_e_evt.delta_target_loss_total = 1.803449`
- r_res_ablation: not applicable in current offline no-residual scope
- latency: not measured in this experiment

## Results
- summary: `100 step` run completed cleanly; compared with `EXP-021`, minimal `A2` makes final `special_eval` slightly better and raises final `e_evt` dependence a little more, but formal full-validation is slightly worse and the `step50` dependency dip remains effectively unchanged.
- failures: no execution failure; methodologically the key target was not met because `step50 zero_e_evt.delta_target_loss_total` stays strongly negative at `-0.846723` and `step50 zero_z_art.delta_target_loss_total` stays negative at `-0.265417`.
- follow_up: metrics file -> F:/proj_dev/tmp/workdir4/reports/experiments/EXP-20260314-022-offline-mvp-c1-4-round1-1-evt-a2-dimonly-100step-calibration.metrics.json
