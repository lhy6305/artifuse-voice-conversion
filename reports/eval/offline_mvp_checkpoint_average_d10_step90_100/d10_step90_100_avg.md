# offline MVP checkpoint averaging

- output_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d10_step90_100/d10_step90_100_avg.pt
- checkpoint_count: 2
- source_steps: [90, 100]
- mode: uniform_mean

## source checkpoints
- F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step90.pt
- F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step100.pt

## notes
- Floating-point tensors are averaged elementwise across checkpoints.
- Non-floating tensors and non-tensor metadata are copied from the first checkpoint after equality validation.
