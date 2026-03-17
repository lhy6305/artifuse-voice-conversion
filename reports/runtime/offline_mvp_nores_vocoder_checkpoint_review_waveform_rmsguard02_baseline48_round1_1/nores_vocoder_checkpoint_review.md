# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 4
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 48, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260317, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2}}

## Checkpoints
- step=12 loss_total=0.907863 delta_vs_previous=None delta_vs_first=0.0
- step=24 loss_total=0.75061 delta_vs_previous=-0.157253 delta_vs_first=-0.157253
- step=36 loss_total=0.69899 delta_vs_previous=-0.05162 delta_vs_first=-0.208873
- step=48 loss_total=0.655545 delta_vs_previous=-0.043445 delta_vs_first=-0.252318

## Pairwise Reviews
- step12 -> step24: avg_delta=-0.157253 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_29_firefly_130: 0.841857 -> 0.6571 (delta=-0.184757)
  - target::chapter3_20_firefly_135: 0.885504 -> 0.70833 (delta=-0.177174)
  - target::chapter3_30_firefly_117: 0.948322 -> 0.772222 (delta=-0.1761)
  - target::chapter3_3_firefly_199: 0.854724 -> 0.680481 (delta=-0.174243)
  - target::chapter3_30_firefly_101: 0.984399 -> 0.810176 (delta=-0.174223)
  - target::chapter3_3_firefly_162: 0.930165 -> 0.75697 (delta=-0.173195)
  - target::chapter4_7_firefly_105: 0.906512 -> 0.73435 (delta=-0.172162)
  - target::chapter3_30_firefly_137: 0.935456 -> 0.765994 (delta=-0.169462)
  - target::chapter3_20_firefly_133: 0.911686 -> 0.74479 (delta=-0.166896)
  - target::chapter3_17_firefly_133: 0.928411 -> 0.762 (delta=-0.166411)
  least_improved_records:
  - target::chapter3_5_firefly_102: 0.875591 -> 0.749468 (delta=-0.126123)
  - target::chapter3_4_firefly_140: 0.999691 -> 0.867306 (delta=-0.132385)
  - target::chapter3_3_firefly_213: 0.900651 -> 0.762348 (delta=-0.138303)
  - target::chapter3_3_firefly_174: 0.894038 -> 0.754419 (delta=-0.139619)
  - target::chapter3_3_firefly_171: 0.92121 -> 0.781352 (delta=-0.139858)
  - target::chapter3_29_firefly_113: 0.902836 -> 0.762666 (delta=-0.14017)
  - target::chapter3_3_firefly_234: 0.911456 -> 0.76985 (delta=-0.141606)
  - target::chapter3_4_firefly_112: 0.983612 -> 0.84196 (delta=-0.141652)
  - target::chapter3_20_firefly_184: 0.998109 -> 0.856109 (delta=-0.142)
  - target::chapter3_30_firefly_147: 0.955711 -> 0.811629 (delta=-0.144082)
- step24 -> step36: avg_delta=-0.05162 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_246: 0.675453 -> 0.605109 (delta=-0.070344)
  - target::chapter3_3_firefly_199: 0.680481 -> 0.61196 (delta=-0.068521)
  - target::chapter3_3_firefly_115: 0.647482 -> 0.57911 (delta=-0.068372)
  - target::chapter3_3_firefly_162: 0.75697 -> 0.68932 (delta=-0.06765)
  - target::chapter3_3_firefly_210: 0.695537 -> 0.628156 (delta=-0.067381)
  - target::chapter3_3_firefly_114: 0.720451 -> 0.653458 (delta=-0.066993)
  - target::chapter3_3_firefly_245: 0.68172 -> 0.614817 (delta=-0.066903)
  - target::chapter3_2_firefly_163: 0.683481 -> 0.62148 (delta=-0.062001)
  - target::chapter3_3_firefly_212: 0.703974 -> 0.64243 (delta=-0.061544)
  - target::chapter3_29_firefly_130: 0.6571 -> 0.596961 (delta=-0.060139)
  least_improved_records:
  - target::chapter3_20_firefly_184: 0.856109 -> 0.823343 (delta=-0.032766)
  - target::chapter3_4_firefly_140: 0.867306 -> 0.833653 (delta=-0.033653)
  - target::chapter3_2_firefly_131: 0.729622 -> 0.694956 (delta=-0.034666)
  - target::chapter3_3_firefly_174: 0.754419 -> 0.715703 (delta=-0.038716)
  - target::chapter3_3_firefly_171: 0.781352 -> 0.741849 (delta=-0.039503)
  - target::chapter3_30_firefly_147: 0.811629 -> 0.771986 (delta=-0.039643)
  - target::chapter3_4_firefly_112: 0.84196 -> 0.799845 (delta=-0.042115)
  - target::chapter3_3_firefly_234: 0.76985 -> 0.726568 (delta=-0.043282)
  - target::chapter3_2_firefly_183: 0.773311 -> 0.729727 (delta=-0.043584)
  - target::chapter3_2_firefly_178: 0.756557 -> 0.712083 (delta=-0.044474)
- step36 -> step48: avg_delta=-0.043445 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_162: 0.68932 -> 0.61729 (delta=-0.07203)
  - target::chapter3_3_firefly_207: 0.687495 -> 0.618411 (delta=-0.069084)
  - target::chapter3_2_firefly_170: 0.672233 -> 0.609259 (delta=-0.062974)
  - target::chapter3_21_firefly_116: 0.760514 -> 0.698101 (delta=-0.062413)
  - target::chapter3_29_firefly_141: 0.721406 -> 0.660676 (delta=-0.06073)
  - target::chapter3_29_firefly_103: 0.708488 -> 0.649234 (delta=-0.059254)
  - target::chapter3_22_firefly_114: 0.743499 -> 0.685276 (delta=-0.058223)
  - target::chapter3_3_firefly_182: 0.694154 -> 0.636238 (delta=-0.057916)
  - target::chapter3_20_firefly_172: 0.734849 -> 0.677196 (delta=-0.057653)
  - target::chapter3_4_firefly_109: 0.715604 -> 0.658444 (delta=-0.05716)
  least_improved_records:
  - target::chapter3_2_firefly_131: 0.694956 -> 0.685205 (delta=-0.009751)
  - target::chapter3_2_firefly_164: 0.66723 -> 0.656584 (delta=-0.010646)
  - target::chapter3_5_firefly_102: 0.702402 -> 0.691583 (delta=-0.010819)
  - target::chapter3_29_firefly_113: 0.715107 -> 0.703438 (delta=-0.011669)
  - target::chapter3_3_firefly_213: 0.704523 -> 0.688962 (delta=-0.015561)
  - target::chapter3_3_firefly_245: 0.614817 -> 0.594332 (delta=-0.020485)
  - target::chapter3_3_firefly_246: 0.605109 -> 0.583613 (delta=-0.021496)
  - target::chapter3_3_firefly_210: 0.628156 -> 0.606605 (delta=-0.021551)
  - target::chapter3_2_firefly_206: 0.658222 -> 0.635673 (delta=-0.022549)
  - target::chapter3_6_firefly_106: 0.676658 -> 0.654078 (delta=-0.02258)

## Overall Review
- step12 -> step48: avg_delta=-0.252318 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_162: 0.930165 -> 0.61729 (delta=-0.312875)
  - target::chapter3_29_firefly_130: 0.841857 -> 0.541607 (delta=-0.30025)
  - target::chapter3_20_firefly_135: 0.885504 -> 0.598776 (delta=-0.286728)
  - target::chapter4_7_firefly_105: 0.906512 -> 0.623448 (delta=-0.283064)
  - target::chapter3_30_firefly_137: 0.935456 -> 0.654793 (delta=-0.280663)
  - target::chapter3_3_firefly_215: 0.868123 -> 0.58877 (delta=-0.279353)
  - target::chapter3_29_firefly_141: 0.937217 -> 0.660676 (delta=-0.276541)
  - target::chapter3_2_firefly_170: 0.885725 -> 0.609259 (delta=-0.276466)
  - target::chapter3_30_firefly_117: 0.948322 -> 0.67189 (delta=-0.276432)
  - target::chapter3_4_firefly_109: 0.933296 -> 0.658444 (delta=-0.274852)
  least_improved_records:
  - target::chapter3_5_firefly_102: 0.875591 -> 0.691583 (delta=-0.184008)
  - target::chapter3_2_firefly_131: 0.876741 -> 0.685205 (delta=-0.191536)
  - target::chapter3_29_firefly_113: 0.902836 -> 0.703438 (delta=-0.199398)
  - target::chapter3_4_firefly_140: 0.999691 -> 0.798963 (delta=-0.200728)
  - target::chapter3_3_firefly_213: 0.900651 -> 0.688962 (delta=-0.211689)
  - target::chapter3_2_firefly_164: 0.868794 -> 0.656584 (delta=-0.21221)
  - target::chapter3_20_firefly_184: 0.998109 -> 0.781915 (delta=-0.216194)
  - target::chapter3_30_firefly_147: 0.955711 -> 0.733928 (delta=-0.221783)
  - target::chapter3_6_firefly_106: 0.875942 -> 0.654078 (delta=-0.221864)
  - target::chapter3_3_firefly_174: 0.894038 -> 0.668935 (delta=-0.225103)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
