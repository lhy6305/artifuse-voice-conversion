# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_baseline_smoke_round1_2/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 2
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=2 loss_total=1.400019 delta_vs_previous=None delta_vs_first=0.0
- step=4 loss_total=1.229178 delta_vs_previous=-0.170841 delta_vs_first=-0.170841

## Pairwise Reviews
- step2 -> step4: avg_delta=-0.170841 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.383233 -> 1.140958 (delta=-0.242275)
  - target::chapter3_3_firefly_115: 1.27837 -> 1.037904 (delta=-0.240466)
  - target::chapter3_6_firefly_106: 1.378674 -> 1.142251 (delta=-0.236423)
  - target::chapter3_3_firefly_246: 1.333189 -> 1.105453 (delta=-0.227736)
  - target::chapter3_3_firefly_114: 1.375539 -> 1.151908 (delta=-0.223631)
  - target::chapter3_29_firefly_113: 1.424397 -> 1.2021 (delta=-0.222297)
  - target::chapter3_3_firefly_245: 1.36396 -> 1.142412 (delta=-0.221548)
  - target::chapter4_7_firefly_119: 1.391535 -> 1.17032 (delta=-0.221215)
  - target::chapter3_3_firefly_213: 1.406148 -> 1.186303 (delta=-0.219845)
  - target::chapter3_3_firefly_210: 1.370908 -> 1.151431 (delta=-0.219477)
  least_improved_records:
  - target::chapter3_20_firefly_184: 1.504169 -> 1.387328 (delta=-0.116841)
  - target::chapter3_4_firefly_112: 1.470652 -> 1.346537 (delta=-0.124115)
  - target::chapter3_4_firefly_140: 1.471909 -> 1.342966 (delta=-0.128943)
  - target::chapter3_29_firefly_141: 1.408763 -> 1.279697 (delta=-0.129066)
  - target::chapter3_4_firefly_109: 1.385744 -> 1.2548 (delta=-0.130944)
  - target::chapter3_30_firefly_132: 1.391911 -> 1.260755 (delta=-0.131156)
  - target::chapter3_30_firefly_101: 1.446633 -> 1.315325 (delta=-0.131308)
  - target::chapter3_21_firefly_116: 1.445053 -> 1.313334 (delta=-0.131719)
  - target::chapter3_30_firefly_117: 1.40863 -> 1.276431 (delta=-0.132199)
  - target::chapter3_30_firefly_136: 1.395457 -> 1.263117 (delta=-0.13234)

## Overall Review
- step2 -> step4: avg_delta=-0.170841 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.383233 -> 1.140958 (delta=-0.242275)
  - target::chapter3_3_firefly_115: 1.27837 -> 1.037904 (delta=-0.240466)
  - target::chapter3_6_firefly_106: 1.378674 -> 1.142251 (delta=-0.236423)
  - target::chapter3_3_firefly_246: 1.333189 -> 1.105453 (delta=-0.227736)
  - target::chapter3_3_firefly_114: 1.375539 -> 1.151908 (delta=-0.223631)
  - target::chapter3_29_firefly_113: 1.424397 -> 1.2021 (delta=-0.222297)
  - target::chapter3_3_firefly_245: 1.36396 -> 1.142412 (delta=-0.221548)
  - target::chapter4_7_firefly_119: 1.391535 -> 1.17032 (delta=-0.221215)
  - target::chapter3_3_firefly_213: 1.406148 -> 1.186303 (delta=-0.219845)
  - target::chapter3_3_firefly_210: 1.370908 -> 1.151431 (delta=-0.219477)
  least_improved_records:
  - target::chapter3_20_firefly_184: 1.504169 -> 1.387328 (delta=-0.116841)
  - target::chapter3_4_firefly_112: 1.470652 -> 1.346537 (delta=-0.124115)
  - target::chapter3_4_firefly_140: 1.471909 -> 1.342966 (delta=-0.128943)
  - target::chapter3_29_firefly_141: 1.408763 -> 1.279697 (delta=-0.129066)
  - target::chapter3_4_firefly_109: 1.385744 -> 1.2548 (delta=-0.130944)
  - target::chapter3_30_firefly_132: 1.391911 -> 1.260755 (delta=-0.131156)
  - target::chapter3_30_firefly_101: 1.446633 -> 1.315325 (delta=-0.131308)
  - target::chapter3_21_firefly_116: 1.445053 -> 1.313334 (delta=-0.131719)
  - target::chapter3_30_firefly_117: 1.40863 -> 1.276431 (delta=-0.132199)
  - target::chapter3_30_firefly_136: 1.395457 -> 1.263117 (delta=-0.13234)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
