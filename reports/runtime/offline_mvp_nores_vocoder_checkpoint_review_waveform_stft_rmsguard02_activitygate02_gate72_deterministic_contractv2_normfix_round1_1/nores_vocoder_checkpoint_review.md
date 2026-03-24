# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 6
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 72, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260318, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=12 loss_total=0.977894 delta_vs_previous=None delta_vs_first=0.0
- step=24 loss_total=0.776948 delta_vs_previous=-0.200946 delta_vs_first=-0.200946
- step=36 loss_total=0.671027 delta_vs_previous=-0.105921 delta_vs_first=-0.306867
- step=48 loss_total=0.606769 delta_vs_previous=-0.064258 delta_vs_first=-0.371125
- step=60 loss_total=0.572388 delta_vs_previous=-0.034381 delta_vs_first=-0.405506
- step=72 loss_total=0.554104 delta_vs_previous=-0.018284 delta_vs_first=-0.42379

## Pairwise Reviews
- step12 -> step24: avg_delta=-0.200946 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 0.897401 -> 0.664835 (delta=-0.232566)
  - target::chapter3_3_firefly_245: 0.897374 -> 0.671211 (delta=-0.226163)
  - target::chapter3_3_firefly_114: 0.91642 -> 0.692215 (delta=-0.224205)
  - target::chapter3_3_firefly_246: 0.849083 -> 0.625263 (delta=-0.22382)
  - target::chapter3_2_firefly_163: 0.927528 -> 0.706684 (delta=-0.220844)
  - target::chapter3_3_firefly_210: 0.91432 -> 0.69548 (delta=-0.21884)
  - target::chapter3_3_firefly_199: 0.886704 -> 0.668029 (delta=-0.218675)
  - target::chapter4_7_firefly_119: 0.970143 -> 0.75497 (delta=-0.215173)
  - target::chapter3_3_firefly_212: 0.929609 -> 0.714973 (delta=-0.214636)
  - target::chapter3_3_firefly_115: 0.771619 -> 0.557872 (delta=-0.213747)
  least_improved_records:
  - target::chapter3_4_firefly_140: 1.102399 -> 0.929926 (delta=-0.172473)
  - target::chapter3_20_firefly_184: 1.113473 -> 0.940458 (delta=-0.173015)
  - target::chapter3_29_firefly_103: 0.978098 -> 0.798582 (delta=-0.179516)
  - target::chapter3_21_firefly_116: 1.044488 -> 0.863504 (delta=-0.180984)
  - target::chapter3_2_firefly_131: 0.969312 -> 0.788173 (delta=-0.181139)
  - target::chapter3_3_firefly_174: 1.008087 -> 0.823123 (delta=-0.184964)
  - target::chapter3_4_firefly_112: 1.08592 -> 0.900322 (delta=-0.185598)
  - target::chapter3_4_firefly_126: 1.020239 -> 0.833759 (delta=-0.18648)
  - target::chapter3_30_firefly_147: 1.033937 -> 0.847052 (delta=-0.186885)
  - target::chapter3_30_firefly_145: 0.992443 -> 0.80482 (delta=-0.187623)
- step24 -> step36: avg_delta=-0.105921 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_30_firefly_117: 0.796096 -> 0.670612 (delta=-0.125484)
  - target::chapter3_30_firefly_137: 0.772825 -> 0.647467 (delta=-0.125358)
  - target::chapter3_3_firefly_162: 0.800161 -> 0.674841 (delta=-0.12532)
  - target::chapter3_29_firefly_141: 0.799454 -> 0.675461 (delta=-0.123993)
  - target::chapter3_20_firefly_172: 0.818128 -> 0.694537 (delta=-0.123591)
  - target::chapter3_30_firefly_101: 0.826727 -> 0.705473 (delta=-0.121254)
  - target::chapter3_30_firefly_136: 0.793383 -> 0.672196 (delta=-0.121187)
  - target::chapter4_7_firefly_105: 0.746831 -> 0.626266 (delta=-0.120565)
  - target::chapter3_20_firefly_135: 0.731684 -> 0.612691 (delta=-0.118993)
  - target::chapter3_26_firefly_114: 0.829911 -> 0.71109 (delta=-0.118821)
  least_improved_records:
  - target::chapter3_5_firefly_102: 0.794918 -> 0.719465 (delta=-0.075453)
  - target::chapter3_6_firefly_106: 0.706716 -> 0.630329 (delta=-0.076387)
  - target::chapter3_3_firefly_115: 0.557872 -> 0.472777 (delta=-0.085095)
  - target::chapter3_29_firefly_113: 0.803249 -> 0.717856 (delta=-0.085393)
  - target::chapter3_3_firefly_174: 0.823123 -> 0.736907 (delta=-0.086216)
  - target::chapter3_3_firefly_171: 0.856533 -> 0.767812 (delta=-0.088721)
  - target::chapter3_6_firefly_103: 0.664835 -> 0.575626 (delta=-0.089209)
  - target::chapter3_3_firefly_234: 0.853855 -> 0.76393 (delta=-0.089925)
  - target::chapter3_3_firefly_213: 0.752746 -> 0.660725 (delta=-0.092021)
  - target::chapter3_2_firefly_131: 0.788173 -> 0.695523 (delta=-0.09265)
- step36 -> step48: avg_delta=-0.064259 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter4_7_firefly_105: 0.626266 -> 0.542222 (delta=-0.084044)
  - target::chapter3_3_firefly_162: 0.674841 -> 0.594082 (delta=-0.080759)
  - target::chapter3_22_firefly_114: 0.717408 -> 0.63873 (delta=-0.078678)
  - target::chapter3_30_firefly_137: 0.647467 -> 0.570657 (delta=-0.07681)
  - target::chapter3_17_firefly_129: 0.679896 -> 0.603562 (delta=-0.076334)
  - target::chapter3_3_firefly_199: 0.55008 -> 0.474203 (delta=-0.075877)
  - target::chapter3_20_firefly_172: 0.694537 -> 0.619181 (delta=-0.075356)
  - target::chapter3_26_firefly_114: 0.71109 -> 0.636298 (delta=-0.074792)
  - target::chapter3_29_firefly_141: 0.675461 -> 0.600705 (delta=-0.074756)
  - target::chapter3_4_firefly_105: 0.682769 -> 0.608319 (delta=-0.07445)
  least_improved_records:
  - target::chapter3_2_firefly_131: 0.695523 -> 0.653233 (delta=-0.04229)
  - target::chapter3_29_firefly_113: 0.717856 -> 0.673671 (delta=-0.044185)
  - target::chapter3_3_firefly_115: 0.472777 -> 0.427402 (delta=-0.045375)
  - target::chapter3_5_firefly_102: 0.719465 -> 0.67298 (delta=-0.046485)
  - target::chapter3_30_firefly_147: 0.746207 -> 0.697894 (delta=-0.048313)
  - target::chapter3_20_firefly_184: 0.83417 -> 0.784736 (delta=-0.049434)
  - target::chapter3_3_firefly_174: 0.736907 -> 0.68696 (delta=-0.049947)
  - target::chapter3_6_firefly_106: 0.630329 -> 0.57961 (delta=-0.050719)
  - target::chapter3_3_firefly_171: 0.767812 -> 0.715481 (delta=-0.052331)
  - target::chapter3_3_firefly_234: 0.76393 -> 0.708527 (delta=-0.055403)
- step48 -> step60: avg_delta=-0.03438 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter4_7_firefly_105: 0.542222 -> 0.486594 (delta=-0.055628)
  - target::chapter3_20_firefly_172: 0.619181 -> 0.565017 (delta=-0.054164)
  - target::chapter3_29_firefly_130: 0.467589 -> 0.414342 (delta=-0.053247)
  - target::chapter3_30_firefly_137: 0.570657 -> 0.517413 (delta=-0.053244)
  - target::chapter3_20_firefly_133: 0.583446 -> 0.530765 (delta=-0.052681)
  - target::chapter3_30_firefly_101: 0.634708 -> 0.582282 (delta=-0.052426)
  - target::chapter3_30_firefly_117: 0.603014 -> 0.550988 (delta=-0.052026)
  - target::chapter3_4_firefly_105: 0.608319 -> 0.557608 (delta=-0.050711)
  - target::chapter3_20_firefly_135: 0.541783 -> 0.491708 (delta=-0.050075)
  - target::chapter3_17_firefly_133: 0.590714 -> 0.540775 (delta=-0.049939)
  least_improved_records:
  - target::chapter3_5_firefly_102: 0.67298 -> 0.660318 (delta=-0.012662)
  - target::chapter3_3_firefly_174: 0.68696 -> 0.67273 (delta=-0.01423)
  - target::chapter3_3_firefly_171: 0.715481 -> 0.698177 (delta=-0.017304)
  - target::chapter3_29_firefly_113: 0.673671 -> 0.655833 (delta=-0.017838)
  - target::chapter3_30_firefly_147: 0.697894 -> 0.679843 (delta=-0.018051)
  - target::chapter3_3_firefly_234: 0.708527 -> 0.690096 (delta=-0.018431)
  - target::chapter3_2_firefly_183: 0.673158 -> 0.654158 (delta=-0.019)
  - target::chapter3_2_firefly_131: 0.653233 -> 0.633375 (delta=-0.019858)
  - target::chapter3_6_firefly_106: 0.57961 -> 0.558996 (delta=-0.020614)
  - target::chapter3_2_firefly_178: 0.648385 -> 0.627363 (delta=-0.021022)
- step60 -> step72: avg_delta=-0.018284 improved=42/66 worsened=24/66
  top_improved_records:
  - target::chapter3_6_firefly_106: 0.558996 -> 0.489489 (delta=-0.069507)
  - target::chapter3_6_firefly_103: 0.472553 -> 0.405621 (delta=-0.066932)
  - target::chapter3_29_firefly_113: 0.655833 -> 0.596121 (delta=-0.059712)
  - target::chapter3_3_firefly_213: 0.57584 -> 0.522804 (delta=-0.053036)
  - target::chapter3_2_firefly_164: 0.563896 -> 0.512288 (delta=-0.051608)
  - target::chapter3_3_firefly_171: 0.698177 -> 0.648221 (delta=-0.049956)
  - target::chapter3_3_firefly_114: 0.487754 -> 0.440091 (delta=-0.047663)
  - target::chapter3_3_firefly_234: 0.690096 -> 0.644716 (delta=-0.04538)
  - target::chapter3_2_firefly_178: 0.627363 -> 0.582427 (delta=-0.044936)
  - target::chapter3_3_firefly_197: 0.558367 -> 0.513434 (delta=-0.044933)
  top_worsened_records:
  - target::chapter3_3_firefly_115: 0.392721 -> 0.419536 (delta=0.026815)
  - target::chapter3_21_firefly_116: 0.64867 -> 0.664602 (delta=0.015932)
  - target::chapter3_29_firefly_141: 0.55112 -> 0.56533 (delta=0.01421)
  - target::chapter3_20_firefly_172: 0.565017 -> 0.578041 (delta=0.013024)
  - target::chapter3_20_firefly_135: 0.491708 -> 0.504309 (delta=0.012601)
  - target::chapter3_30_firefly_132: 0.576427 -> 0.586327 (delta=0.0099)
  - target::chapter3_4_firefly_109: 0.553531 -> 0.562001 (delta=0.00847)
  - target::chapter3_30_firefly_137: 0.517413 -> 0.525216 (delta=0.007803)
  - target::chapter3_30_firefly_136: 0.554081 -> 0.561327 (delta=0.007246)
  - target::chapter3_4_firefly_105: 0.557608 -> 0.564602 (delta=0.006994)

## Overall Review
- step12 -> step72: avg_delta=-0.42379 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 0.897401 -> 0.405621 (delta=-0.49178)
  - target::chapter3_3_firefly_114: 0.91642 -> 0.440091 (delta=-0.476329)
  - target::chapter4_7_firefly_105: 0.956249 -> 0.486002 (delta=-0.470247)
  - target::chapter3_3_firefly_199: 0.886704 -> 0.424994 (delta=-0.46171)
  - target::chapter3_3_firefly_246: 0.849083 -> 0.387428 (delta=-0.461655)
  - target::chapter3_2_firefly_163: 0.927528 -> 0.471235 (delta=-0.456293)
  - target::chapter3_3_firefly_162: 1.011668 -> 0.55544 (delta=-0.456228)
  - target::chapter3_30_firefly_137: 0.979602 -> 0.525216 (delta=-0.454386)
  - target::chapter3_3_firefly_210: 0.91432 -> 0.460319 (delta=-0.454001)
  - target::chapter3_2_firefly_206: 0.951572 -> 0.501765 (delta=-0.449807)
  least_improved_records:
  - target::chapter3_5_firefly_102: 0.984966 -> 0.637011 (delta=-0.347955)
  - target::chapter3_2_firefly_131: 0.969312 -> 0.620207 (delta=-0.349105)
  - target::chapter3_3_firefly_115: 0.771619 -> 0.419536 (delta=-0.352083)
  - target::chapter3_20_firefly_184: 1.113473 -> 0.754448 (delta=-0.359025)
  - target::chapter3_3_firefly_174: 1.008087 -> 0.633381 (delta=-0.374706)
  - target::chapter3_4_firefly_140: 1.102399 -> 0.726627 (delta=-0.375772)
  - target::chapter3_29_firefly_103: 0.978098 -> 0.599453 (delta=-0.378645)
  - target::chapter3_21_firefly_116: 1.044488 -> 0.664602 (delta=-0.379886)
  - target::chapter3_30_firefly_147: 1.033937 -> 0.639165 (delta=-0.394772)
  - target::chapter3_3_firefly_171: 1.046492 -> 0.648221 (delta=-0.398271)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
