# offline MVP checkpoint averaging

- output_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_checkpoint_average_d7_step90_100/d7_step90_100_avg.pt
- checkpoint_count: 2
- source_steps: [90, 100]
- mode: uniform_mean

## source checkpoints
- F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step90.pt
- F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step100.pt

## notes
- Floating-point tensors are averaged elementwise across checkpoints.
- Non-floating tensors and non-tensor metadata are copied from the first checkpoint after equality validation.
