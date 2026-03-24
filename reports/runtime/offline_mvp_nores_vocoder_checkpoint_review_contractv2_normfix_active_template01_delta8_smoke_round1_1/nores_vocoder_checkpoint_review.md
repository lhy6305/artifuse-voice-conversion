# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template01_delta8_smoke_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 2
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.1, "frame_delta": 8.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=2 loss_total=8.939874 delta_vs_previous=None delta_vs_first=0.0
- step=4 loss_total=8.753729 delta_vs_previous=-0.186145 delta_vs_first=-0.186145

## Pairwise Reviews
- step2 -> step4: avg_delta=-0.186145 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 9.045584 -> 8.783285 (delta=-0.262299)
  - target::chapter3_3_firefly_115: 5.643844 -> 5.388645 (delta=-0.255199)
  - target::chapter3_6_firefly_106: 9.759427 -> 9.504422 (delta=-0.255005)
  - target::chapter3_3_firefly_246: 5.595184 -> 5.356038 (delta=-0.239146)
  least_improved_records:
  - target::chapter3_20_firefly_184: 9.769758 -> 9.644711 (delta=-0.125047)
  - target::chapter3_21_firefly_116: 9.790571 -> 9.652974 (delta=-0.137597)
  - target::chapter3_4_firefly_112: 8.589658 -> 8.449662 (delta=-0.139996)
  - target::chapter3_3_firefly_207: 9.338195 -> 9.193357 (delta=-0.144838)

## Overall Review
- step2 -> step4: avg_delta=-0.186145 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 9.045584 -> 8.783285 (delta=-0.262299)
  - target::chapter3_3_firefly_115: 5.643844 -> 5.388645 (delta=-0.255199)
  - target::chapter3_6_firefly_106: 9.759427 -> 9.504422 (delta=-0.255005)
  - target::chapter3_3_firefly_246: 5.595184 -> 5.356038 (delta=-0.239146)
  least_improved_records:
  - target::chapter3_20_firefly_184: 9.769758 -> 9.644711 (delta=-0.125047)
  - target::chapter3_21_firefly_116: 9.790571 -> 9.652974 (delta=-0.137597)
  - target::chapter3_4_firefly_112: 8.589658 -> 8.449662 (delta=-0.139996)
  - target::chapter3_3_firefly_207: 9.338195 -> 9.193357 (delta=-0.144838)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
