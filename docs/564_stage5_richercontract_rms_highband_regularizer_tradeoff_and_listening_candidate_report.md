# 564 Stage5 Richer-Contract RMS High-Band Regularizer Tradeoff And Listening Candidate Report

## Summary
- Date: `2026-04-01`
- Goal: continue the richer-contract held-out minisplit route by adding explicit `RMS / high-band` control and decide whether machine-side work still has clear headroom before human listening
- Result:
  - ran two 40-step held-out minisplit warm-start ablations:
    - `rms_guard = 0.2`
    - `rms_guard = 0.2 + waveform_decoder_base_logits_high_band_excess = 0.1`
  - then isolated `waveform_decoder_base_logits_high_band_excess = 0.1` in a shorter 20-step held-out run
  - replayed speech-emergence probes on the resulting checkpoints, including an extra `step20` probe from the combined regularizer run
- Main conclusion:
  - `rms_guard` alone is not a good richer-contract continuation route
  - `bhb01` alone over-darkens and does not solve RMS overshoot
  - the best machine-side balance now comes from the combined route, but not from its validation-best checkpoint
  - `rmsguard02 + bhb01 step20` is the first checkpoint in this richer-contract family that looks strong enough to justify a human listening audit

## Setup
- Dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_minisplit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Shared initialization:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Shared structure:
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `waveform_decoder_mode = fused_single`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 0.5`
  - `use_waveform_decoder_input_adapter = true`
  - `use_noise_hidden_residual_adapter = true`
  - `noise_hidden_residual_mode = delta_direct_v1`

## A. `rms_guard = 0.2` Alone
- Run:
  - `reports/runtime/stage5_richercontract_minisplit_warmstart40_rmsguard02_r1_2/`
- Best validation checkpoint:
  - `step39`
  - `loss_total = 0.608997`
- Speech-emergence:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart40_rmsguard02_r1_2/`
  - baseline aggregate:
    - `decoded_zero_crossing_rate = 0.485224`
    - `decoded_spectral_centroid_hz = 10801.873047`
    - `decoded_spectral_high_band_energy_ratio = 0.831506`
    - `decoded_to_aligned_rms_ratio = 1.040854`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.447818`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.459417`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.711111`
- Reading:
  - `rms_guard` does fix the worst RMS overshoot
  - but it also pushes the route back toward a brighter, noisier operating region
  - held-out validation also degrades sharply versus the plain richer-contract baseline `0.443589`

## B. `rms_guard = 0.2 + bhb01`
- Run:
  - `reports/runtime/stage5_richercontract_minisplit_warmstart40_rmsguard02_bhb01_r1_1/`
- Validation-best checkpoint:
  - `step36`
  - `loss_total = 0.612045`
- Validation-best speech-emergence:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart40_rmsguard02_bhb01_r1_1/`
  - baseline aggregate:
    - `decoded_zero_crossing_rate = 0.394263`
    - `decoded_spectral_centroid_hz = 8580.947266`
    - `decoded_spectral_high_band_energy_ratio = 0.62557`
    - `decoded_to_aligned_rms_ratio = 0.857144`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.449026`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.448392`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.707669`
- Extra machine-selection probe:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart40_rmsguard02_bhb01_step20_r1_1/`
  - `step20` baseline aggregate:
    - `decoded_zero_crossing_rate = 0.42104`
    - `decoded_spectral_centroid_hz = 8381.073242`
    - `decoded_spectral_high_band_energy_ratio = 0.593995`
    - `decoded_to_aligned_rms_ratio = 1.167112`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.456053`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.471004`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.734923`
- Reading:
  - this combined route is the first one that improves almost all machine-facing failure dimensions at once
  - `step36` gives the strongest amplitude and template suppression
  - but `step20` is more balanced:
    - RMS overshoot is already close to controlled
    - activity and frame-RMS correlations stay stronger than at `step36`
    - centroid and high-band stay materially below the plain richer-contract baseline
  - therefore the validation-best checkpoint is not the machine-best checkpoint on this route

## C. `bhb01` Alone
- Short isolation run:
  - `reports/runtime/stage5_richercontract_minisplit_warmstart20_bhb01_r1_1/`
- Best validation checkpoint:
  - `step20`
  - `loss_total = 0.479047`
- Speech-emergence:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart20_bhb01_r1_1/`
  - baseline aggregate:
    - `decoded_zero_crossing_rate = 0.155458`
    - `decoded_spectral_centroid_hz = 1835.744751`
    - `decoded_spectral_high_band_energy_ratio = 0.055249`
    - `decoded_to_aligned_rms_ratio = 3.637033`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.443477`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.462033`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.813308`
- Reading:
  - `bhb01` alone does not solve the richer-contract route
  - it collapses the decode into an over-dark operating region while leaving RMS overshoot severe
  - this is useful as a negative control:
    - the improvement in the combined route is not just “high-band lower is always better”
    - the `rms_guard` term is doing real stabilization work there

## D. Comparison Against The Plain Richer-Contract Baseline
- Plain held-out richer-contract baseline:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart40_r1_1/`
  - `decoded_zero_crossing_rate = 0.379961`
  - `decoded_spectral_centroid_hz = 8688.796875`
  - `decoded_spectral_high_band_energy_ratio = 0.683286`
  - `decoded_to_aligned_rms_ratio = 2.963793`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.449751`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.479959`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.844697`
- Best current machine-balance checkpoint:
  - `rmsguard02 + bhb01 step20`
  - relative reading:
    - better:
      - `decoded_to_aligned_rms_ratio`: `2.963793 -> 1.167112`
      - `decoded_spectral_centroid_hz`: `8688.796875 -> 8381.073242`
      - `decoded_spectral_high_band_energy_ratio`: `0.683286 -> 0.593995`
      - `decoded_frame_template_cosine_gap_vs_aligned`: `0.844697 -> 0.734923`
      - `predicted_activity_to_aligned_frame_rms_corr`: `0.449751 -> 0.456053`
    - slightly worse:
      - `decoded_zero_crossing_rate`: `0.379961 -> 0.42104`
      - `decoded_frame_rms_to_aligned_frame_rms_corr`: `0.479959 -> 0.471004`
- Reading:
  - the combined route does not dominate baseline on every scalar
  - but it is the first route that brings RMS overshoot, high-band energy, centroid, and template collapse into a much more credible joint region without sacrificing activity alignment

## E. Control-Usage Read
- All four checked routes still keep the same broad impact ordering near the top:
  - `conditioning_zero`
  - `event_probs_zero` or `noise_proxies_zero`
  - `z_art_zero`
- Meaning:
  - the route is still not fully “speech-structural control solved”
  - but the richer-contract regularized checkpoints are no longer purely stuck in the old bright-template failure mode
  - the remaining uncertainty is now more qualitative than obviously machine-localizable

## Decision
- Keep:
  - richer-contract warm-start as the base family
  - the combined `rmsguard02 + bhb01` route as the most promising new regularized branch
- Do not keep as default:
  - `rms_guard` alone
  - `bhb01` alone
- New listening candidate:
  - `reports/runtime/stage5_richercontract_minisplit_warmstart40_rmsguard02_bhb01_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step20.pt`
- Why this is now a listening candidate:
  - machine-side work no longer points to a single obvious missing regularizer
  - objective validation now mis-ranks the more balanced emergence checkpoint
  - deciding between the plain richer-contract baseline and the new combined regularized checkpoint now requires ears

## Next Step
- Prepare a focused human listening comparison between:
  - plain richer-contract held-out baseline `step39`
  - combined regularized richer-contract `step20`
- Do not keep optimizing this branch only by `loss_total` until that listening comparison is done.
