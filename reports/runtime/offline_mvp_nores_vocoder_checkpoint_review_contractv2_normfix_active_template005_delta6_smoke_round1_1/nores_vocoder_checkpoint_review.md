# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 2
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.05, "frame_delta": 6.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=2 loss_total=7.041812 delta_vs_previous=None delta_vs_first=0.0
- step=4 loss_total=6.86659 delta_vs_previous=-0.175222 delta_vs_first=-0.175222

## Pairwise Reviews
- step2 -> step4: avg_delta=-0.175222 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 7.115327 -> 6.860875 (delta=-0.254452)
  - target::chapter3_3_firefly_115: 4.535323 -> 4.282968 (delta=-0.252355)
  - target::chapter3_6_firefly_106: 7.650619 -> 7.403933 (delta=-0.246686)
  - target::chapter3_3_firefly_246: 4.51659 -> 4.280645 (delta=-0.235945)
  - target::chapter3_3_firefly_114: 5.387632 -> 5.154127 (delta=-0.233505)
  - target::chapter3_3_firefly_245: 5.746354 -> 5.515317 (delta=-0.231037)
  - target::chapter3_3_firefly_213: 5.91861 -> 5.688975 (delta=-0.229635)
  - target::chapter3_29_firefly_113: 7.612059 -> 7.383845 (delta=-0.228214)
  - target::chapter3_2_firefly_164: 7.047827 -> 6.821538 (delta=-0.226289)
  - target::chapter4_7_firefly_119: 7.257349 -> 7.031742 (delta=-0.225607)
  least_improved_records:
  - target::chapter3_20_firefly_184: 7.690628 -> 7.573891 (delta=-0.116737)
  - target::chapter3_4_firefly_112: 6.79704 -> 6.668206 (delta=-0.128834)
  - target::chapter3_4_firefly_140: 7.68001 -> 7.548008 (delta=-0.132002)
  - target::chapter3_21_firefly_116: 7.689305 -> 7.556668 (delta=-0.132637)
  - target::chapter3_3_firefly_207: 7.343291 -> 7.209125 (delta=-0.134166)
  - target::chapter3_29_firefly_141: 7.665534 -> 7.531105 (delta=-0.134429)
  - target::chapter3_30_firefly_132: 7.968328 -> 7.83256 (delta=-0.135768)
  - target::chapter3_4_firefly_109: 6.99815 -> 6.862354 (delta=-0.135796)
  - target::chapter3_30_firefly_101: 8.111631 -> 7.975706 (delta=-0.135925)
  - target::chapter3_30_firefly_117: 7.341496 -> 7.205014 (delta=-0.136482)

## Overall Review
- step2 -> step4: avg_delta=-0.175222 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 7.115327 -> 6.860875 (delta=-0.254452)
  - target::chapter3_3_firefly_115: 4.535323 -> 4.282968 (delta=-0.252355)
  - target::chapter3_6_firefly_106: 7.650619 -> 7.403933 (delta=-0.246686)
  - target::chapter3_3_firefly_246: 4.51659 -> 4.280645 (delta=-0.235945)
  - target::chapter3_3_firefly_114: 5.387632 -> 5.154127 (delta=-0.233505)
  - target::chapter3_3_firefly_245: 5.746354 -> 5.515317 (delta=-0.231037)
  - target::chapter3_3_firefly_213: 5.91861 -> 5.688975 (delta=-0.229635)
  - target::chapter3_29_firefly_113: 7.612059 -> 7.383845 (delta=-0.228214)
  - target::chapter3_2_firefly_164: 7.047827 -> 6.821538 (delta=-0.226289)
  - target::chapter4_7_firefly_119: 7.257349 -> 7.031742 (delta=-0.225607)
  least_improved_records:
  - target::chapter3_20_firefly_184: 7.690628 -> 7.573891 (delta=-0.116737)
  - target::chapter3_4_firefly_112: 6.79704 -> 6.668206 (delta=-0.128834)
  - target::chapter3_4_firefly_140: 7.68001 -> 7.548008 (delta=-0.132002)
  - target::chapter3_21_firefly_116: 7.689305 -> 7.556668 (delta=-0.132637)
  - target::chapter3_3_firefly_207: 7.343291 -> 7.209125 (delta=-0.134166)
  - target::chapter3_29_firefly_141: 7.665534 -> 7.531105 (delta=-0.134429)
  - target::chapter3_30_firefly_132: 7.968328 -> 7.83256 (delta=-0.135768)
  - target::chapter3_4_firefly_109: 6.99815 -> 6.862354 (delta=-0.135796)
  - target::chapter3_30_firefly_101: 8.111631 -> 7.975706 (delta=-0.135925)
  - target::chapter3_30_firefly_117: 7.341496 -> 7.205014 (delta=-0.136482)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
