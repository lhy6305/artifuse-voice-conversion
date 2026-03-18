# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline96_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 4
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 96, "packages_per_step": 4, "validation_interval": 24, "checkpoint_interval": 24, "sampler_mode": "shuffle", "seed": 20260317, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2}}

## Checkpoints
- step=24 loss_total=0.749261 delta_vs_previous=None delta_vs_first=0.0
- step=48 loss_total=0.656366 delta_vs_previous=-0.092895 delta_vs_first=-0.092895
- step=72 loss_total=0.625926 delta_vs_previous=-0.03044 delta_vs_first=-0.123335
- step=96 loss_total=0.616506 delta_vs_previous=-0.00942 delta_vs_first=-0.132755

## Pairwise Reviews
- step24 -> step48: avg_delta=-0.092896 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_162: 0.756216 -> 0.621624 (delta=-0.134592)
  - target::chapter3_29_firefly_130: 0.65578 -> 0.539852 (delta=-0.115928)
  - target::chapter3_3_firefly_207: 0.738359 -> 0.623123 (delta=-0.115236)
  - target::chapter3_3_firefly_215: 0.700971 -> 0.58606 (delta=-0.114911)
  - target::chapter3_2_firefly_170: 0.723838 -> 0.614085 (delta=-0.109753)
  - target::chapter3_29_firefly_141: 0.774085 -> 0.664397 (delta=-0.109688)
  - target::chapter4_7_firefly_105: 0.733234 -> 0.62488 (delta=-0.108354)
  - target::chapter3_4_firefly_109: 0.769021 -> 0.661323 (delta=-0.107698)
  - target::chapter3_30_firefly_137: 0.764619 -> 0.657778 (delta=-0.106841)
  - target::chapter3_20_firefly_135: 0.707148 -> 0.600483 (delta=-0.106665)
  least_improved_records:
  - target::chapter3_2_firefly_131: 0.727713 -> 0.682489 (delta=-0.045224)
  - target::chapter3_5_firefly_102: 0.748025 -> 0.688358 (delta=-0.059667)
  - target::chapter3_29_firefly_113: 0.761364 -> 0.700187 (delta=-0.061177)
  - target::chapter3_4_firefly_140: 0.866096 -> 0.801892 (delta=-0.064204)
  - target::chapter3_2_firefly_164: 0.721978 -> 0.654549 (delta=-0.067429)
  - target::chapter3_20_firefly_184: 0.85502 -> 0.786383 (delta=-0.068637)
  - target::chapter3_3_firefly_213: 0.760294 -> 0.685828 (delta=-0.074466)
  - target::chapter3_2_firefly_212: 0.739091 -> 0.663097 (delta=-0.075994)
  - target::chapter3_30_firefly_147: 0.810165 -> 0.734147 (delta=-0.076018)
  - target::chapter4_7_firefly_119: 0.712502 -> 0.634808 (delta=-0.077694)
- step48 -> step72: avg_delta=-0.03044 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.713614 -> 0.677058 (delta=-0.036556)
  - target::chapter3_30_firefly_117: 0.674379 -> 0.638675 (delta=-0.035704)
  - target::chapter3_30_firefly_137: 0.657778 -> 0.623428 (delta=-0.03435)
  - target::chapter3_30_firefly_132: 0.668071 -> 0.633873 (delta=-0.034198)
  - target::chapter4_7_firefly_105: 0.62488 -> 0.590885 (delta=-0.033995)
  - target::chapter3_26_firefly_114: 0.688108 -> 0.654777 (delta=-0.033331)
  - target::chapter3_26_firefly_107: 0.717922 -> 0.684628 (delta=-0.033294)
  - target::chapter3_3_firefly_115: 0.549147 -> 0.515909 (delta=-0.033238)
  - target::chapter3_30_firefly_136: 0.67045 -> 0.637365 (delta=-0.033085)
  - target::chapter3_3_firefly_245: 0.591396 -> 0.558439 (delta=-0.032957)
  least_improved_records:
  - target::chapter3_3_firefly_207: 0.623123 -> 0.601272 (delta=-0.021851)
  - target::chapter3_3_firefly_162: 0.621624 -> 0.597543 (delta=-0.024081)
  - target::chapter3_6_firefly_106: 0.650644 -> 0.625811 (delta=-0.024833)
  - target::chapter3_2_firefly_165: 0.645895 -> 0.619004 (delta=-0.026891)
  - target::chapter3_21_firefly_116: 0.702061 -> 0.675169 (delta=-0.026892)
  - target::chapter3_3_firefly_246: 0.580082 -> 0.552921 (delta=-0.027161)
  - target::chapter3_3_firefly_234: 0.68259 -> 0.655388 (delta=-0.027202)
  - target::chapter3_6_firefly_103: 0.661679 -> 0.634405 (delta=-0.027274)
  - target::chapter3_22_firefly_114: 0.687093 -> 0.659719 (delta=-0.027374)
  - target::chapter3_20_firefly_184: 0.786383 -> 0.758712 (delta=-0.027671)
- step72 -> step96: avg_delta=-0.00942 improved=42/66 worsened=24/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.677058 -> 0.64876 (delta=-0.028298)
  - target::chapter3_30_firefly_117: 0.638675 -> 0.61074 (delta=-0.027935)
  - target::chapter3_3_firefly_162: 0.597543 -> 0.570003 (delta=-0.02754)
  - target::chapter3_30_firefly_132: 0.633873 -> 0.607534 (delta=-0.026339)
  - target::chapter3_20_firefly_135: 0.567605 -> 0.541783 (delta=-0.025822)
  - target::chapter3_30_firefly_137: 0.623428 -> 0.598952 (delta=-0.024476)
  - target::chapter3_29_firefly_142: 0.610926 -> 0.586459 (delta=-0.024467)
  - target::chapter3_29_firefly_136: 0.634509 -> 0.610155 (delta=-0.024354)
  - target::chapter3_20_firefly_133: 0.614073 -> 0.589806 (delta=-0.024267)
  - target::chapter3_30_firefly_136: 0.637365 -> 0.613134 (delta=-0.024231)
  top_worsened_records:
  - target::chapter3_3_firefly_234: 0.655388 -> 0.664743 (delta=0.009355)
  - target::chapter3_29_firefly_113: 0.670883 -> 0.679736 (delta=0.008853)
  - target::chapter4_7_firefly_119: 0.602722 -> 0.611523 (delta=0.008801)
  - target::chapter3_3_firefly_171: 0.666493 -> 0.674779 (delta=0.008286)
  - target::chapter3_2_firefly_131: 0.650029 -> 0.657656 (delta=0.007627)
  - target::chapter3_5_firefly_102: 0.660654 -> 0.667865 (delta=0.007211)
  - target::chapter3_3_firefly_212: 0.584129 -> 0.58993 (delta=0.005801)
  - target::chapter3_2_firefly_206: 0.60132 -> 0.607121 (delta=0.005801)
  - target::chapter3_30_firefly_147: 0.702298 -> 0.707697 (delta=0.005399)
  - target::chapter3_3_firefly_197: 0.59503 -> 0.600198 (delta=0.005168)

## Overall Review
- step24 -> step96: avg_delta=-0.132755 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_162: 0.756216 -> 0.570003 (delta=-0.186213)
  - target::chapter3_30_firefly_137: 0.764619 -> 0.598952 (delta=-0.165667)
  - target::chapter3_20_firefly_135: 0.707148 -> 0.541783 (delta=-0.165365)
  - target::chapter3_29_firefly_141: 0.774085 -> 0.609386 (delta=-0.164699)
  - target::chapter3_4_firefly_109: 0.769021 -> 0.60766 (delta=-0.161361)
  - target::chapter4_7_firefly_105: 0.733234 -> 0.572673 (delta=-0.160561)
  - target::chapter3_29_firefly_136: 0.770465 -> 0.610155 (delta=-0.16031)
  - target::chapter3_30_firefly_117: 0.770718 -> 0.61074 (delta=-0.159978)
  - target::chapter3_30_firefly_101: 0.808665 -> 0.64876 (delta=-0.159905)
  - target::chapter3_4_firefly_105: 0.773126 -> 0.613424 (delta=-0.159702)
  least_improved_records:
  - target::chapter3_2_firefly_131: 0.727713 -> 0.657656 (delta=-0.070057)
  - target::chapter3_5_firefly_102: 0.748025 -> 0.667865 (delta=-0.08016)
  - target::chapter3_29_firefly_113: 0.761364 -> 0.679736 (delta=-0.081628)
  - target::chapter3_2_firefly_164: 0.721978 -> 0.62539 (delta=-0.096588)
  - target::chapter3_2_firefly_212: 0.739091 -> 0.639716 (delta=-0.099375)
  - target::chapter4_7_firefly_119: 0.712502 -> 0.611523 (delta=-0.100979)
  - target::chapter3_3_firefly_213: 0.760294 -> 0.658377 (delta=-0.101917)
  - target::chapter3_30_firefly_147: 0.810165 -> 0.707697 (delta=-0.102468)
  - target::chapter3_6_firefly_106: 0.729486 -> 0.626437 (delta=-0.103049)
  - target::chapter3_3_firefly_234: 0.768846 -> 0.664743 (delta=-0.104103)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
