# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template025_smoke_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 2
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.25, "frame_delta": 0.0, "fused_hidden_template": 0.0, "fused_hidden_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=2 loss_total=1.472526 delta_vs_previous=None delta_vs_first=0.0
- step=4 loss_total=1.263878 delta_vs_previous=-0.208648 delta_vs_first=-0.208648

## Pairwise Reviews
- step2 -> step4: avg_delta=-0.208648 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.468593 -> 1.186139 (delta=-0.282454)
  - target::chapter3_6_firefly_106: 1.45151 -> 1.184689 (delta=-0.266821)
  - target::chapter3_3_firefly_115: 1.40421 -> 1.141359 (delta=-0.262851)
  - target::chapter3_29_firefly_113: 1.52442 -> 1.265439 (delta=-0.258981)
  least_improved_records:
  - target::chapter3_30_firefly_137: 1.448398 -> 1.280624 (delta=-0.167774)
  - target::chapter3_3_firefly_207: 1.470226 -> 1.301898 (delta=-0.168328)
  - target::chapter3_30_firefly_101: 1.502666 -> 1.334201 (delta=-0.168465)
  - target::chapter3_30_firefly_136: 1.453936 -> 1.28366 (delta=-0.170276)

## Overall Review
- step2 -> step4: avg_delta=-0.208648 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.468593 -> 1.186139 (delta=-0.282454)
  - target::chapter3_6_firefly_106: 1.45151 -> 1.184689 (delta=-0.266821)
  - target::chapter3_3_firefly_115: 1.40421 -> 1.141359 (delta=-0.262851)
  - target::chapter3_29_firefly_113: 1.52442 -> 1.265439 (delta=-0.258981)
  least_improved_records:
  - target::chapter3_30_firefly_137: 1.448398 -> 1.280624 (delta=-0.167774)
  - target::chapter3_3_firefly_207: 1.470226 -> 1.301898 (delta=-0.168328)
  - target::chapter3_30_firefly_101: 1.502666 -> 1.334201 (delta=-0.168465)
  - target::chapter3_30_firefly_136: 1.453936 -> 1.28366 (delta=-0.170276)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
