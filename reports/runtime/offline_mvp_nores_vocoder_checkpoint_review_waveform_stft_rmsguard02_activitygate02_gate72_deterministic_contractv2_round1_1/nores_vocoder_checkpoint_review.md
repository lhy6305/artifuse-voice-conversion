# Stage5 No-Residual Vocoder Checkpoint Review

- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json
- checkpoint_count: 6
- dataset: {"train_package_count": 592, "validation_package_count": 66}
- runtime: {"device": "cuda:0"}
- training: {"num_steps": 72, "packages_per_step": 4, "validation_interval": 12, "checkpoint_interval": 12, "sampler_mode": "shuffle", "seed": 20260318, "deterministic": true, "learning_rate": 0.001, "max_grad_norm": 5.0, "loss_weights": {"harmonic": 1.0, "noise": 1.0, "periodic_gate": 0.2, "noise_gate": 0.2, "activity_gate": 0.2, "waveform": 0.5, "stft": 0.5, "rms_guard": 0.2, "active_template": 0.0, "frame_delta": 0.0, "use_predicted_activity_gate": true, "reconstruction_frame_gain_apply_mode": "pre_overlap_add"}}

## Checkpoints
- step=12 loss_total=0.986235 delta_vs_previous=None delta_vs_first=0.0
- step=24 loss_total=0.818536 delta_vs_previous=-0.167699 delta_vs_first=-0.167699
- step=36 loss_total=0.734092 delta_vs_previous=-0.084444 delta_vs_first=-0.252143
- step=48 loss_total=0.689489 delta_vs_previous=-0.044603 delta_vs_first=-0.296746
- step=60 loss_total=0.669387 delta_vs_previous=-0.020102 delta_vs_first=-0.316848
- step=72 loss_total=0.658881 delta_vs_previous=-0.010506 delta_vs_first=-0.327354

## Pairwise Reviews
- step12 -> step24: avg_delta=-0.167699 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 0.911389 -> 0.707365 (delta=-0.204024)
  - target::chapter3_3_firefly_114: 0.89674 -> 0.699336 (delta=-0.197404)
  - target::chapter3_3_firefly_246: 0.840323 -> 0.645244 (delta=-0.195079)
  - target::chapter3_3_firefly_199: 0.893088 -> 0.701595 (delta=-0.191493)
  - target::chapter3_3_firefly_115: 0.780292 -> 0.589831 (delta=-0.190461)
  - target::chapter3_3_firefly_245: 0.879618 -> 0.691862 (delta=-0.187756)
  - target::chapter3_30_firefly_137: 0.989838 -> 0.802692 (delta=-0.187146)
  - target::chapter3_3_firefly_215: 0.918207 -> 0.731919 (delta=-0.186288)
  - target::chapter3_29_firefly_130: 0.866682 -> 0.680708 (delta=-0.185974)
  - target::chapter3_3_firefly_162: 1.043381 -> 0.85899 (delta=-0.184391)
  least_improved_records:
  - target::chapter3_2_firefly_131: 0.976322 -> 0.838814 (delta=-0.137508)
  - target::chapter3_29_firefly_103: 1.029232 -> 0.891075 (delta=-0.138157)
  - target::chapter3_4_firefly_140: 1.105595 -> 0.964537 (delta=-0.141058)
  - target::chapter3_3_firefly_171: 1.036031 -> 0.894133 (delta=-0.141898)
  - target::chapter3_29_firefly_113: 0.994113 -> 0.851315 (delta=-0.142798)
  - target::chapter4_7_firefly_119: 0.996451 -> 0.852592 (delta=-0.143859)
  - target::chapter3_20_firefly_184: 1.109681 -> 0.965474 (delta=-0.144207)
  - target::chapter3_26_firefly_107: 1.088842 -> 0.944263 (delta=-0.144579)
  - target::chapter3_3_firefly_234: 1.038731 -> 0.893937 (delta=-0.144794)
  - target::chapter3_5_firefly_102: 0.966267 -> 0.81879 (delta=-0.147477)
- step24 -> step36: avg_delta=-0.084444 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_246: 0.645244 -> 0.524098 (delta=-0.121146)
  - target::chapter3_6_firefly_103: 0.707365 -> 0.589417 (delta=-0.117948)
  - target::chapter3_29_firefly_130: 0.680708 -> 0.565154 (delta=-0.115554)
  - target::chapter3_3_firefly_215: 0.731919 -> 0.621728 (delta=-0.110191)
  - target::chapter3_3_firefly_115: 0.589831 -> 0.481159 (delta=-0.108672)
  - target::chapter3_3_firefly_199: 0.701595 -> 0.593161 (delta=-0.108434)
  - target::chapter3_30_firefly_137: 0.802692 -> 0.697232 (delta=-0.10546)
  - target::chapter3_29_firefly_136: 0.81049 -> 0.706073 (delta=-0.104417)
  - target::chapter3_29_firefly_142: 0.777593 -> 0.675144 (delta=-0.102449)
  - target::chapter3_3_firefly_114: 0.699336 -> 0.597343 (delta=-0.101993)
  least_improved_records:
  - target::chapter3_3_firefly_234: 0.893937 -> 0.8465 (delta=-0.047437)
  - target::chapter3_3_firefly_171: 0.894133 -> 0.845352 (delta=-0.048781)
  - target::chapter3_3_firefly_174: 0.845524 -> 0.787879 (delta=-0.057645)
  - target::chapter3_29_firefly_113: 0.851315 -> 0.790422 (delta=-0.060893)
  - target::chapter3_3_firefly_138: 0.842572 -> 0.779539 (delta=-0.063033)
  - target::chapter3_3_firefly_207: 0.822515 -> 0.757226 (delta=-0.065289)
  - target::chapter3_20_firefly_184: 0.965474 -> 0.900002 (delta=-0.065472)
  - target::chapter3_2_firefly_178: 0.820685 -> 0.752799 (delta=-0.067886)
  - target::chapter3_2_firefly_183: 0.864548 -> 0.796499 (delta=-0.068049)
  - target::chapter3_2_firefly_155: 0.835844 -> 0.767714 (delta=-0.06813)
- step36 -> step48: avg_delta=-0.044603 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_30_firefly_101: 0.75729 -> 0.693307 (delta=-0.063983)
  - target::chapter3_30_firefly_117: 0.732794 -> 0.671337 (delta=-0.061457)
  - target::chapter3_3_firefly_246: 0.524098 -> 0.465161 (delta=-0.058937)
  - target::chapter3_30_firefly_137: 0.697232 -> 0.6393 (delta=-0.057932)
  - target::chapter3_29_firefly_142: 0.675144 -> 0.617551 (delta=-0.057593)
  - target::chapter3_2_firefly_206: 0.665763 -> 0.608224 (delta=-0.057539)
  - target::chapter3_3_firefly_245: 0.592592 -> 0.535479 (delta=-0.057113)
  - target::chapter3_29_firefly_130: 0.565154 -> 0.508347 (delta=-0.056807)
  - target::chapter3_3_firefly_199: 0.593161 -> 0.536536 (delta=-0.056625)
  - target::chapter3_2_firefly_164: 0.694498 -> 0.638143 (delta=-0.056355)
  least_improved_records:
  - target::chapter3_29_firefly_103: 0.802788 -> 0.78088 (delta=-0.021908)
  - target::chapter4_7_firefly_119: 0.781913 -> 0.756961 (delta=-0.024952)
  - target::chapter3_22_firefly_114: 0.826652 -> 0.799795 (delta=-0.026857)
  - target::chapter3_3_firefly_234: 0.8465 -> 0.818036 (delta=-0.028464)
  - target::chapter3_6_firefly_106: 0.672597 -> 0.642655 (delta=-0.029942)
  - target::chapter3_20_firefly_135: 0.74646 -> 0.715645 (delta=-0.030815)
  - target::chapter3_20_firefly_145: 0.810186 -> 0.779132 (delta=-0.031054)
  - target::chapter3_20_firefly_133: 0.780673 -> 0.74915 (delta=-0.031523)
  - target::chapter3_4_firefly_106: 0.760661 -> 0.72877 (delta=-0.031891)
  - target::chapter3_3_firefly_115: 0.481159 -> 0.449044 (delta=-0.032115)
- step48 -> step60: avg_delta=-0.020101 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_3_firefly_114: 0.54175 -> 0.507514 (delta=-0.034236)
  - target::chapter3_3_firefly_207: 0.717544 -> 0.684446 (delta=-0.033098)
  - target::chapter3_3_firefly_210: 0.574316 -> 0.541584 (delta=-0.032732)
  - target::chapter3_2_firefly_137: 0.637005 -> 0.604644 (delta=-0.032361)
  - target::chapter3_2_firefly_163: 0.616479 -> 0.585081 (delta=-0.031398)
  - target::chapter3_2_firefly_170: 0.673967 -> 0.643127 (delta=-0.03084)
  - target::chapter3_3_firefly_212: 0.608897 -> 0.578425 (delta=-0.030472)
  - target::chapter3_6_firefly_103: 0.544104 -> 0.513936 (delta=-0.030168)
  - target::chapter3_3_firefly_182: 0.68974 -> 0.659959 (delta=-0.029781)
  - target::chapter3_3_firefly_197: 0.665636 -> 0.63675 (delta=-0.028886)
  least_improved_records:
  - target::chapter3_4_firefly_140: 0.845462 -> 0.840786 (delta=-0.004676)
  - target::chapter3_20_firefly_184: 0.851443 -> 0.845204 (delta=-0.006239)
  - target::chapter3_2_firefly_131: 0.723282 -> 0.715033 (delta=-0.008249)
  - target::chapter3_26_firefly_107: 0.83689 -> 0.828253 (delta=-0.008637)
  - target::chapter3_4_firefly_126: 0.780884 -> 0.770892 (delta=-0.009992)
  - target::chapter3_20_firefly_145: 0.779132 -> 0.768405 (delta=-0.010727)
  - target::chapter3_26_firefly_114: 0.799533 -> 0.787549 (delta=-0.011984)
  - target::chapter3_29_firefly_103: 0.78088 -> 0.768631 (delta=-0.012249)
  - target::chapter3_4_firefly_112: 0.830081 -> 0.817775 (delta=-0.012306)
  - target::chapter3_4_firefly_106: 0.72877 -> 0.716341 (delta=-0.012429)
- step60 -> step72: avg_delta=-0.010506 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_106: 0.616894 -> 0.585396 (delta=-0.031498)
  - target::chapter3_6_firefly_103: 0.513936 -> 0.483068 (delta=-0.030868)
  - target::chapter3_29_firefly_113: 0.736321 -> 0.709811 (delta=-0.02651)
  - target::chapter3_3_firefly_213: 0.62393 -> 0.601814 (delta=-0.022116)
  - target::chapter3_2_firefly_164: 0.613557 -> 0.592858 (delta=-0.020699)
  - target::chapter3_3_firefly_114: 0.507514 -> 0.488363 (delta=-0.019151)
  - target::chapter3_3_firefly_171: 0.786704 -> 0.767791 (delta=-0.018913)
  - target::chapter3_3_firefly_234: 0.794033 -> 0.777334 (delta=-0.016699)
  - target::chapter3_2_firefly_206: 0.579348 -> 0.563608 (delta=-0.01574)
  - target::chapter3_3_firefly_138: 0.709567 -> 0.69419 (delta=-0.015377)
  least_improved_records:
  - target::chapter3_3_firefly_162: 0.716272 -> 0.715538 (delta=-0.000734)
  - target::chapter3_29_firefly_141: 0.66031 -> 0.656848 (delta=-0.003462)
  - target::chapter3_2_firefly_170: 0.643127 -> 0.638243 (delta=-0.004884)
  - target::chapter3_4_firefly_112: 0.817775 -> 0.812718 (delta=-0.005057)
  - target::chapter3_20_firefly_172: 0.759632 -> 0.754513 (delta=-0.005119)
  - target::chapter3_30_firefly_132: 0.661088 -> 0.65594 (delta=-0.005148)
  - target::chapter3_3_firefly_115: 0.425154 -> 0.419838 (delta=-0.005316)
  - target::chapter3_21_firefly_116: 0.770213 -> 0.764815 (delta=-0.005398)
  - target::chapter3_3_firefly_215: 0.549519 -> 0.544102 (delta=-0.005417)
  - target::chapter3_20_firefly_184: 0.845204 -> 0.839612 (delta=-0.005592)

## Overall Review
- step12 -> step72: avg_delta=-0.327354 improved=66/66 worsened=0/66
  top_improved_records:
  - target::chapter3_6_firefly_103: 0.911389 -> 0.483068 (delta=-0.428321)
  - target::chapter3_3_firefly_114: 0.89674 -> 0.488363 (delta=-0.408377)
  - target::chapter3_3_firefly_246: 0.840323 -> 0.432829 (delta=-0.407494)
  - target::chapter3_29_firefly_130: 0.866682 -> 0.478303 (delta=-0.388379)
  - target::chapter3_3_firefly_199: 0.893088 -> 0.509021 (delta=-0.384067)
  - target::chapter3_30_firefly_137: 0.989838 -> 0.613959 (delta=-0.375879)
  - target::chapter3_3_firefly_215: 0.918207 -> 0.544102 (delta=-0.374105)
  - target::chapter3_3_firefly_245: 0.879618 -> 0.50982 (delta=-0.369798)
  - target::chapter3_29_firefly_142: 0.958853 -> 0.59216 (delta=-0.366693)
  - target::chapter3_3_firefly_210: 0.899392 -> 0.534009 (delta=-0.365383)
  least_improved_records:
  - target::chapter3_3_firefly_234: 1.038731 -> 0.777334 (delta=-0.261397)
  - target::chapter3_26_firefly_107: 1.088842 -> 0.820677 (delta=-0.268165)
  - target::chapter3_3_firefly_171: 1.036031 -> 0.767791 (delta=-0.26824)
  - target::chapter4_7_firefly_119: 0.996451 -> 0.726602 (delta=-0.269849)
  - target::chapter3_20_firefly_184: 1.109681 -> 0.839612 (delta=-0.270069)
  - target::chapter3_2_firefly_131: 0.976322 -> 0.704999 (delta=-0.271323)
  - target::chapter3_4_firefly_140: 1.105595 -> 0.833266 (delta=-0.272329)
  - target::chapter3_29_firefly_103: 1.029232 -> 0.75513 (delta=-0.274102)
  - target::chapter3_20_firefly_145: 1.038046 -> 0.760811 (delta=-0.277235)
  - target::chapter3_26_firefly_114: 1.060503 -> 0.780639 (delta=-0.279864)

## Notes
- This review is derived from the dataset-loop summary validation_history payload.
- Checkpoint-level loss_total tracks validation-package averages already recorded by the Stage5 loop.
- Per-record review compares validation package loss_total across checkpoints to see whether gains are broad-based or concentrated.
