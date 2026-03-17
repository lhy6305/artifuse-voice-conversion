# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline192_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 4
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 192, "packages_per_step": 8, "validation_interval": 48, "checkpoint_interval": 48, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2}}

## Checkpoints
- step=48 loss_total=0.441292 delta_vs_previous=None delta_vs_first=0.0
- step=96 loss_total=0.432645 delta_vs_previous=-0.008647 delta_vs_first=-0.008647
- step=144 loss_total=0.428461 delta_vs_previous=-0.004184 delta_vs_first=-0.012831
- step=192 loss_total=0.425898 delta_vs_previous=-0.002563 delta_vs_first=-0.015394

## Pairwise Reviews
- step48 -> step96: avg_delta=-0.008647 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_5_firefly_102: 0.476501 -> 0.461682 (delta=-0.014819)
  - target::chapter3_30_firefly_117: 0.445152 -> 0.430862 (delta=-0.01429)
  - target::chapter3_20_firefly_184: 0.525844 -> 0.511743 (delta=-0.014101)
  - target::chapter3_30_firefly_101: 0.454674 -> 0.440829 (delta=-0.013845)
  - target::chapter3_4_firefly_140: 0.566266 -> 0.553632 (delta=-0.012634)
  - target::chapter3_2_firefly_131: 0.477728 -> 0.46511 (delta=-0.012618)
  - target::chapter3_26_firefly_107: 0.474168 -> 0.461692 (delta=-0.012476)
  - target::chapter3_2_firefly_212: 0.462162 -> 0.449816 (delta=-0.012346)
  - target::chapter3_3_firefly_174: 0.479829 -> 0.467663 (delta=-0.012166)
  - target::chapter3_30_firefly_132: 0.442114 -> 0.430303 (delta=-0.011811)
  least_improved_records:
  - target::chapter3_3_firefly_207: 0.430987 -> 0.429955 (delta=-0.001032)
  - target::chapter3_3_firefly_246: 0.369579 -> 0.36532 (delta=-0.004259)
  - target::chapter3_22_firefly_114: 0.443152 -> 0.438488 (delta=-0.004664)
  - target::chapter4_7_firefly_105: 0.41804 -> 0.412864 (delta=-0.005176)
  - target::chapter3_3_firefly_215: 0.40337 -> 0.398088 (delta=-0.005282)
  - target::chapter3_3_firefly_162: 0.416348 -> 0.411012 (delta=-0.005336)
  - target::chapter3_2_firefly_137: 0.425816 -> 0.420132 (delta=-0.005684)
  - target::chapter3_6_firefly_106: 0.408969 -> 0.403066 (delta=-0.005903)
  - target::chapter3_29_firefly_141: 0.426967 -> 0.420884 (delta=-0.006083)
  - target::chapter3_3_firefly_212: 0.417326 -> 0.411218 (delta=-0.006108)
- step96 -> step144: avg_delta=-0.004184 improved=65/66 worsened=1/66
  top_improved_records:
  - target::chapter3_26_firefly_107: 0.461692 -> 0.453853 (delta=-0.007839)
  - target::chapter3_29_firefly_141: 0.420884 -> 0.413344 (delta=-0.00754)
  - target::chapter3_20_firefly_184: 0.511743 -> 0.504408 (delta=-0.007335)
  - target::chapter3_21_firefly_116: 0.436666 -> 0.429383 (delta=-0.007283)
  - target::chapter3_26_firefly_114: 0.443365 -> 0.43632 (delta=-0.007045)
  - target::chapter3_29_firefly_136: 0.440531 -> 0.433549 (delta=-0.006982)
  - target::chapter3_20_firefly_145: 0.412258 -> 0.405514 (delta=-0.006744)
  - target::chapter3_29_firefly_142: 0.423837 -> 0.41727 (delta=-0.006567)
  - target::chapter3_30_firefly_117: 0.430862 -> 0.424345 (delta=-0.006517)
  - target::chapter3_30_firefly_137: 0.420045 -> 0.413587 (delta=-0.006458)
  top_worsened_records:
  - target::chapter3_3_firefly_162: 0.411012 -> 0.414939 (delta=0.003927)
  - target::chapter3_6_firefly_106: 0.403066 -> 0.40304 (delta=-2.6e-05)
  - target::chapter3_3_firefly_246: 0.36532 -> 0.365018 (delta=-0.000302)
  - target::chapter3_3_firefly_207: 0.429955 -> 0.429413 (delta=-0.000542)
  - target::chapter3_3_firefly_199: 0.376964 -> 0.376261 (delta=-0.000703)
  - target::chapter3_2_firefly_137: 0.420132 -> 0.419238 (delta=-0.000894)
  - target::chapter3_2_firefly_164: 0.431418 -> 0.429925 (delta=-0.001493)
  - target::chapter3_5_firefly_102: 0.461682 -> 0.45913 (delta=-0.002552)
  - target::chapter3_2_firefly_170: 0.415872 -> 0.413157 (delta=-0.002715)
  - target::chapter3_2_firefly_163: 0.389491 -> 0.386738 (delta=-0.002753)
- step144 -> step192: avg_delta=-0.002563 improved=64/66 worsened=2/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.435325 -> 0.428412 (delta=-0.006913)
  - target::chapter3_3_firefly_174: 0.463712 -> 0.456815 (delta=-0.006897)
  - target::chapter3_4_firefly_140: 0.550788 -> 0.54485 (delta=-0.005938)
  - target::chapter3_2_firefly_164: 0.429925 -> 0.424191 (delta=-0.005734)
  - target::chapter3_2_firefly_131: 0.460454 -> 0.454861 (delta=-0.005593)
  - target::chapter3_2_firefly_178: 0.455087 -> 0.450034 (delta=-0.005053)
  - target::chapter3_2_firefly_165: 0.445759 -> 0.44101 (delta=-0.004749)
  - target::chapter3_3_firefly_171: 0.488241 -> 0.483498 (delta=-0.004743)
  - target::chapter3_6_firefly_106: 0.40304 -> 0.398484 (delta=-0.004556)
  - target::chapter3_20_firefly_184: 0.504408 -> 0.500136 (delta=-0.004272)
  top_worsened_records:
  - target::chapter4_7_firefly_119: 0.424759 -> 0.425456 (delta=0.000697)
  - target::chapter3_22_firefly_114: 0.43435 -> 0.434752 (delta=0.000402)
  - target::chapter3_3_firefly_114: 0.395325 -> 0.395185 (delta=-0.00014)
  - target::chapter4_7_firefly_105: 0.408336 -> 0.408176 (delta=-0.00016)
  - target::chapter3_3_firefly_207: 0.429413 -> 0.429233 (delta=-0.00018)
  - target::chapter3_29_firefly_103: 0.430551 -> 0.430163 (delta=-0.000388)
  - target::chapter3_21_firefly_116: 0.429383 -> 0.428915 (delta=-0.000468)
  - target::chapter3_30_firefly_136: 0.428931 -> 0.428335 (delta=-0.000596)
  - target::chapter3_5_firefly_102: 0.45913 -> 0.458417 (delta=-0.000713)
  - target::chapter3_17_firefly_133: 0.429359 -> 0.428503 (delta=-0.000856)

## Overall Review
- step48 -> step192: avg_delta=-0.015395 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.454674 -> 0.428412 (delta=-0.026262)
  - target::chapter3_20_firefly_184: 0.525844 -> 0.500136 (delta=-0.025708)
  - target::chapter3_26_firefly_107: 0.474168 -> 0.450672 (delta=-0.023496)
  - target::chapter3_3_firefly_174: 0.479829 -> 0.456815 (delta=-0.023014)
  - target::chapter3_2_firefly_131: 0.477728 -> 0.454861 (delta=-0.022867)
  - target::chapter3_30_firefly_117: 0.445152 -> 0.422454 (delta=-0.022698)
  - target::chapter3_2_firefly_178: 0.471542 -> 0.450034 (delta=-0.021508)
  - target::chapter3_4_firefly_140: 0.566266 -> 0.54485 (delta=-0.021416)
  - target::chapter3_20_firefly_145: 0.423688 -> 0.402751 (delta=-0.020937)
  - target::chapter3_2_firefly_212: 0.462162 -> 0.441646 (delta=-0.020516)
  least_improved_records:
  - target::chapter3_3_firefly_207: 0.430987 -> 0.429233 (delta=-0.001754)
  - target::chapter3_3_firefly_162: 0.416348 -> 0.412615 (delta=-0.003733)
  - target::chapter3_3_firefly_246: 0.369579 -> 0.36401 (delta=-0.005569)
  - target::chapter3_22_firefly_114: 0.443152 -> 0.434752 (delta=-0.0084)
  - target::chapter3_2_firefly_137: 0.425816 -> 0.416664 (delta=-0.009152)
  - target::chapter3_3_firefly_114: 0.405035 -> 0.395185 (delta=-0.00985)
  - target::chapter4_7_firefly_105: 0.41804 -> 0.408176 (delta=-0.009864)
  - target::chapter3_3_firefly_199: 0.384878 -> 0.37487 (delta=-0.010008)
  - target::chapter3_6_firefly_106: 0.408969 -> 0.398484 (delta=-0.010485)
  - target::chapter3_3_firefly_215: 0.40337 -> 0.392279 (delta=-0.011091)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
