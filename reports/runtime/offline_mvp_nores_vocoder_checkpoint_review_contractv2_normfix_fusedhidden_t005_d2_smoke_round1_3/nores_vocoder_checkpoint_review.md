# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_fusedhidden_t005_d2_smoke_round1_3/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 2
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 4, "packages_per_step": 4, "validation_interval": 2, "checkpoint_interval": 2, "sampler_mode": "shuffle", "seed": 20260324, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "fused_hidden_template": 0.05, "fused_hidden_delta": 2.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=2 loss_total=1.400002 delta_vs_previous=None delta_vs_first=0.0
- step=4 loss_total=1.22959 delta_vs_previous=-0.170412 delta_vs_first=-0.170412

## Pairwise Reviews
- step2 -> step4: avg_delta=-0.170412 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.383194 -> 1.141237 (delta=-0.241957)
  - target::chapter3_3_firefly_115: 1.278369 -> 1.038022 (delta=-0.240347)
  - target::chapter3_6_firefly_106: 1.378634 -> 1.142578 (delta=-0.236056)
  - target::chapter3_3_firefly_246: 1.333151 -> 1.105813 (delta=-0.227338)
  least_improved_records:
  - target::chapter3_20_firefly_184: 1.504163 -> 1.387684 (delta=-0.116479)
  - target::chapter3_4_firefly_112: 1.470651 -> 1.347022 (delta=-0.123629)
  - target::chapter3_29_firefly_141: 1.408768 -> 1.28026 (delta=-0.128508)
  - target::chapter3_4_firefly_140: 1.471886 -> 1.343316 (delta=-0.12857)

## Overall Review
- step2 -> step4: avg_delta=-0.170412 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 1.383194 -> 1.141237 (delta=-0.241957)
  - target::chapter3_3_firefly_115: 1.278369 -> 1.038022 (delta=-0.240347)
  - target::chapter3_6_firefly_106: 1.378634 -> 1.142578 (delta=-0.236056)
  - target::chapter3_3_firefly_246: 1.333151 -> 1.105813 (delta=-0.227338)
  least_improved_records:
  - target::chapter3_20_firefly_184: 1.504163 -> 1.387684 (delta=-0.116479)
  - target::chapter3_4_firefly_112: 1.470651 -> 1.347022 (delta=-0.123629)
  - target::chapter3_29_firefly_141: 1.408768 -> 1.28026 (delta=-0.128508)
  - target::chapter3_4_firefly_140: 1.471886 -> 1.343316 (delta=-0.12857)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
