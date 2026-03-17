# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline96_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 4
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 96, "packages_per_step": 8, "validation_interval": 24, "checkpoint_interval": 24, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}}

## Checkpoints
- step=24 loss_total=0.469644 delta_vs_previous=None delta_vs_first=0.0
- step=48 loss_total=0.441292 delta_vs_previous=-0.028352 delta_vs_first=-0.028352
- step=72 loss_total=0.435399 delta_vs_previous=-0.005893 delta_vs_first=-0.034245
- step=96 loss_total=0.432645 delta_vs_previous=-0.002754 delta_vs_first=-0.036999

## Pairwise Reviews
- step24 -> step48: avg_delta=-0.028352 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_115: 0.360101 -> 0.322465 (delta=-0.037636)
  - target::chapter3_3_firefly_199: 0.42061 -> 0.384878 (delta=-0.035732)
  - target::chapter3_3_firefly_162: 0.451954 -> 0.416348 (delta=-0.035606)
  - target::chapter3_30_firefly_137: 0.462724 -> 0.427377 (delta=-0.035347)
  - target::chapter4_7_firefly_105: 0.452978 -> 0.41804 (delta=-0.034938)
  - target::chapter3_29_firefly_141: 0.461532 -> 0.426967 (delta=-0.034565)
  - target::chapter3_3_firefly_114: 0.439414 -> 0.405035 (delta=-0.034379)
  - target::chapter3_3_firefly_215: 0.437194 -> 0.40337 (delta=-0.033824)
  - target::chapter3_29_firefly_130: 0.390839 -> 0.357358 (delta=-0.033481)
  - target::chapter3_3_firefly_245: 0.420089 -> 0.386859 (delta=-0.03323)
  least_improved_records:
  - target::chapter3_29_firefly_113: 0.499633 -> 0.484245 (delta=-0.015388)
  - target::chapter3_5_firefly_102: 0.493025 -> 0.476501 (delta=-0.016524)
  - target::chapter3_2_firefly_131: 0.495105 -> 0.477728 (delta=-0.017377)
  - target::chapter3_20_firefly_184: 0.544495 -> 0.525844 (delta=-0.018651)
  - target::chapter3_4_firefly_140: 0.585569 -> 0.566266 (delta=-0.019303)
  - target::chapter3_3_firefly_174: 0.499528 -> 0.479829 (delta=-0.019699)
  - target::chapter3_29_firefly_103: 0.466595 -> 0.445721 (delta=-0.020874)
  - target::chapter3_6_firefly_106: 0.431282 -> 0.408969 (delta=-0.022313)
  - target::chapter3_3_firefly_171: 0.524567 -> 0.502156 (delta=-0.022411)
  - target::chapter3_22_firefly_114: 0.466458 -> 0.443152 (delta=-0.023306)
- step48 -> step72: avg_delta=-0.005894 improved=64/66 worsened=2/66
  top_improved_records:
  - target::chapter3_2_firefly_131: 0.477728 -> 0.466635 (delta=-0.011093)
  - target::chapter3_30_firefly_101: 0.454674 -> 0.443815 (delta=-0.010859)
  - target::chapter3_4_firefly_140: 0.566266 -> 0.555812 (delta=-0.010454)
  - target::chapter3_5_firefly_102: 0.476501 -> 0.46641 (delta=-0.010091)
  - target::chapter3_30_firefly_117: 0.445152 -> 0.435454 (delta=-0.009698)
  - target::chapter3_20_firefly_184: 0.525844 -> 0.51637 (delta=-0.009474)
  - target::chapter3_30_firefly_132: 0.442114 -> 0.432905 (delta=-0.009209)
  - target::chapter3_3_firefly_174: 0.479829 -> 0.470965 (delta=-0.008864)
  - target::chapter3_2_firefly_164: 0.442937 -> 0.434075 (delta=-0.008862)
  - target::chapter3_26_firefly_107: 0.474168 -> 0.465438 (delta=-0.00873)
  top_worsened_records:
  - target::chapter3_3_firefly_207: 0.430987 -> 0.433185 (delta=0.002198)
  - target::chapter3_3_firefly_162: 0.416348 -> 0.41778 (delta=0.001432)
  - target::chapter3_2_firefly_137: 0.425816 -> 0.42315 (delta=-0.002666)
  - target::chapter3_22_firefly_114: 0.443152 -> 0.440479 (delta=-0.002673)
  - target::chapter3_6_firefly_106: 0.408969 -> 0.40614 (delta=-0.002829)
  - target::chapter3_3_firefly_215: 0.40337 -> 0.400272 (delta=-0.003098)
  - target::chapter3_6_firefly_103: 0.367486 -> 0.364229 (delta=-0.003257)
  - target::chapter3_3_firefly_182: 0.451591 -> 0.447955 (delta=-0.003636)
  - target::chapter4_7_firefly_105: 0.41804 -> 0.414386 (delta=-0.003654)
  - target::chapter3_3_firefly_246: 0.369579 -> 0.365909 (delta=-0.00367)
- step72 -> step96: avg_delta=-0.002753 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_162: 0.41778 -> 0.411012 (delta=-0.006768)
  - target::chapter3_29_firefly_103: 0.440619 -> 0.435063 (delta=-0.005556)
  - target::chapter3_21_firefly_116: 0.441475 -> 0.436666 (delta=-0.004809)
  - target::chapter4_7_firefly_119: 0.433274 -> 0.428482 (delta=-0.004792)
  - target::chapter3_5_firefly_102: 0.46641 -> 0.461682 (delta=-0.004728)
  - target::chapter3_2_firefly_212: 0.454529 -> 0.449816 (delta=-0.004713)
  - target::chapter3_20_firefly_184: 0.51637 -> 0.511743 (delta=-0.004627)
  - target::chapter3_30_firefly_117: 0.435454 -> 0.430862 (delta=-0.004592)
  - target::chapter3_29_firefly_113: 0.477072 -> 0.472776 (delta=-0.004296)
  - target::chapter3_2_firefly_165: 0.453077 -> 0.44879 (delta=-0.004287)
  least_improved_records:
  - target::chapter3_30_firefly_145: 0.484728 -> 0.484274 (delta=-0.000454)
  - target::chapter3_3_firefly_246: 0.365909 -> 0.36532 (delta=-0.000589)
  - target::chapter3_30_firefly_147: 0.516319 -> 0.515598 (delta=-0.000721)
  - target::chapter3_3_firefly_212: 0.412306 -> 0.411218 (delta=-0.001088)
  - target::chapter3_30_firefly_137: 0.42117 -> 0.420045 (delta=-0.001125)
  - target::chapter3_29_firefly_136: 0.441673 -> 0.440531 (delta=-0.001142)
  - target::chapter3_29_firefly_142: 0.424981 -> 0.423837 (delta=-0.001144)
  - target::chapter3_17_firefly_133: 0.436631 -> 0.435223 (delta=-0.001408)
  - target::chapter3_29_firefly_141: 0.422302 -> 0.420884 (delta=-0.001418)
  - target::chapter4_7_firefly_105: 0.414386 -> 0.412864 (delta=-0.001522)

## Overall Review
- step24 -> step96: avg_delta=-0.036999 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.487763 -> 0.440829 (delta=-0.046934)
  - target::chapter3_30_firefly_117: 0.477389 -> 0.430862 (delta=-0.046527)
  - target::chapter3_3_firefly_115: 0.360101 -> 0.31524 (delta=-0.044861)
  - target::chapter3_3_firefly_245: 0.420089 -> 0.375676 (delta=-0.044413)
  - target::chapter3_20_firefly_135: 0.426367 -> 0.382646 (delta=-0.043721)
  - target::chapter3_3_firefly_199: 0.42061 -> 0.376964 (delta=-0.043646)
  - target::chapter3_30_firefly_137: 0.462724 -> 0.420045 (delta=-0.042679)
  - target::chapter3_29_firefly_130: 0.390839 -> 0.348768 (delta=-0.042071)
  - target::chapter3_20_firefly_172: 0.470681 -> 0.429084 (delta=-0.041597)
  - target::chapter3_30_firefly_136: 0.475259 -> 0.434217 (delta=-0.041042)
  least_improved_records:
  - target::chapter3_29_firefly_113: 0.499633 -> 0.472776 (delta=-0.026857)
  - target::chapter3_22_firefly_114: 0.466458 -> 0.438488 (delta=-0.02797)
  - target::chapter3_6_firefly_106: 0.431282 -> 0.403066 (delta=-0.028216)
  - target::chapter3_2_firefly_131: 0.495105 -> 0.46511 (delta=-0.029995)
  - target::chapter3_5_firefly_102: 0.493025 -> 0.461682 (delta=-0.031343)
  - target::chapter3_29_firefly_103: 0.466595 -> 0.435063 (delta=-0.031532)
  - target::chapter3_3_firefly_174: 0.499528 -> 0.467663 (delta=-0.031865)
  - target::chapter3_4_firefly_140: 0.585569 -> 0.553632 (delta=-0.031937)
  - target::chapter3_4_firefly_112: 0.527392 -> 0.495417 (delta=-0.031975)
  - target::chapter3_3_firefly_171: 0.524567 -> 0.492189 (delta=-0.032378)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
