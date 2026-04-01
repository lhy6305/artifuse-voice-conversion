# 569 Stage5 WavePCA16 Upper-Bound Bounded Training And Regularizer Report

## Summary
- Date: `2026-04-01`
- Goal: move the new `wavepca16` analysis-only upper-bound route beyond smoke and test it on bounded Stage5 training, held-out minisplit validation, and the previously useful `rms_guard + bhb01` regularizer continuation
- Result:
  - ran a `full5` loop-smoke warm-start 20-step route
  - ran a held-out `3 train / 2 validation` warm-start 40-step route
  - replayed speech-emergence probes on both
  - then ran a held-out `rms_guard = 0.2 + waveform_decoder_base_logits_high_band_excess = 0.1` continuation and probed both `step20` and `step40`
- Main conclusion:
  - `wavepca16` materially improves structure-facing machine diagnostics and control usage, so the compact waveform-geometry code is not a fake upper bound
  - but the default Stage5 objective still drives this route into a bright/high-band operating point
  - the richer-contract regularizer recipe does not transfer cleanly: it tames brightness and RMS, but it also destroys waveform-to-target frame-RMS alignment on the `wavepca16` route

## A. Full5 Loop-Smoke Warm-Start 20
- Run:
  - `reports/runtime/stage5_wavepca16_dataset_training_warmstart_bmcresid20_r1_1/`
- Dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_wavepca16_loopsmoke_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Initialization:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Structure:
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 0.5`
  - `use_waveform_decoder_input_adapter = true`
  - `use_noise_hidden_residual_adapter = true`
  - `noise_hidden_residual_mode = delta_direct_v1`
- Best validation checkpoint:
  - `step20`
  - `loss_total = 0.574284`

## B. Full5 Speech-Emergence Read
- Probe:
  - `reports/runtime/stage5_wavepca16_speechemergence_warmstart_bmcresid20_r1_1/`
- Baseline aggregate:
  - `decoded_zero_crossing_rate = 0.472139`
  - `decoded_spectral_centroid_hz = 10329.085938`
  - `decoded_spectral_high_band_energy_ratio = 0.776409`
  - `decoded_to_aligned_rms_ratio = 2.175221`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.441763`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.498083`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.378867`
- Control-usage impact ranking top slice:
  - `conditioning_zero = 0.027236`
  - `z_art_zero = 0.014647`
  - `noise_proxies_zero = 0.011975`
  - `event_probs_zero = 0.011963`
  - `periodic_proxies_zero = 0.004301`
- Reading:
  - this route is still too bright and high-band heavy for listening
  - but unlike the earlier richer-contract line, it clearly uses `z_art` and `event_probs` much more strongly
  - the very low `decoded_frame_template_cosine_gap_vs_aligned` is the first machine sign that Stage5 is no longer stuck in the same old shared-template basin

## C. Held-Out Minisplit Warm-Start 40
- Minisplit dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_wavepca16_minisplit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Train ids:
  - `target::chapter3_26_firefly_114`
  - `target::chapter4_7_firefly_105`
  - `target::no_text_voice/chapter3_18_firefly_101`
- Validation ids:
  - `target::chapter3_30_firefly_132`
  - `target::no_text_voice/chapter3_21_firefly_108`
- Run:
  - `reports/runtime/stage5_wavepca16_minisplit_warmstart40_r1_1/`
- Best validation checkpoint:
  - `step40`
  - `loss_total = 0.534152`
- Validation trend:
  - `step20 = 0.613390`
  - `step30 = 0.563901`
  - `step39 = 0.536310`
  - `step40 = 0.534152`

## D. Held-Out Minisplit Speech-Emergence
- Probe:
  - `reports/runtime/stage5_wavepca16_speechemergence_minisplit_warmstart40_r1_1/`
- Baseline aggregate on held-out validation:
  - `decoded_zero_crossing_rate = 0.468720`
  - `decoded_spectral_centroid_hz = 10186.308594`
  - `decoded_spectral_high_band_energy_ratio = 0.759900`
  - `decoded_to_aligned_rms_ratio = 3.075386`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.290653`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.509279`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.429025`
- Relative to the richer-contract held-out baseline from `563`:
  - better:
    - `decoded_frame_rms_to_aligned_frame_rms_corr: 0.479959 -> 0.509279`
    - `decoded_frame_template_cosine_gap_vs_aligned: 0.844697 -> 0.429025`
    - control usage is no longer mostly proxy-only
  - worse:
    - `decoded_zero_crossing_rate: 0.379961 -> 0.468720`
    - `decoded_spectral_centroid_hz: 8688.796875 -> 10186.308594`
    - `decoded_spectral_high_band_energy_ratio: 0.683286 -> 0.759900`
    - `decoded_to_aligned_rms_ratio: 2.963793 -> 3.075386`
    - `predicted_activity_to_aligned_frame_rms_corr: 0.449751 -> 0.290653`
- Reading:
  - the upper-bound route really is carrying more frame-specific geometry
  - but the current Stage5 objective does not land that geometry in a perceptually healthy operating region

## E. Held-Out `rms_guard = 0.2 + bhb01`
- Run:
  - `reports/runtime/stage5_wavepca16_minisplit_warmstart40_rmsguard02_bhb01_r1_1/`
- Validation-best checkpoint:
  - `step39`
  - `loss_total = 0.676287`
- Step40 speech-emergence:
  - `reports/runtime/stage5_wavepca16_speechemergence_minisplit_warmstart40_rmsguard02_bhb01_r1_1/`
  - `decoded_zero_crossing_rate = 0.396713`
  - `decoded_spectral_centroid_hz = 7319.660156`
  - `decoded_spectral_high_band_energy_ratio = 0.489306`
  - `decoded_to_aligned_rms_ratio = 0.776896`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.284960`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.084554`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.452800`
- Extra step20 speech-emergence:
  - `reports/runtime/stage5_wavepca16_speechemergence_minisplit_warmstart40_rmsguard02_bhb01_step20_r1_1/`
  - `decoded_zero_crossing_rate = 0.438649`
  - `decoded_spectral_centroid_hz = 8879.244141`
  - `decoded_spectral_high_band_energy_ratio = 0.620007`
  - `decoded_to_aligned_rms_ratio = 1.253765`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.240850`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.158907`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.457121`
- Reading:
  - the regularizer pair does lower brightness and RMS sharply on the upper-bound route
  - but it also collapses `decoded_frame_rms_to_aligned_frame_rms_corr`
  - unlike the richer-contract branch, this regularizer pair is not a clean next route here

## Decision
- Keep:
  - `wavepca16` as the strongest current evidence that the missing ingredient is upstream waveform-geometry representation
  - the held-out minisplit `wavepca16` route as the current machine proof that structure-facing metrics can move in the right direction
- Do not keep:
  - the assumption that the richer-contract regularizer recipe will transfer unchanged to the upper-bound route
  - the idea that lower brightness alone means a better upper-bound checkpoint
- Next valid step:
  - move from analysis-only `wavepca16` toward a producer-side learned waveform-code contract and supervise that upstream predictor directly
  - do not spend the next cycle on another Stage5-local regularizer sweep before that producer-side learning path exists
