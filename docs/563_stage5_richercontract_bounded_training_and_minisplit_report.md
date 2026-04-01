# 563 Stage5 Richer-Contract Bounded Training And Minisplit Report

## Summary
- Date: `2026-04-01`
- Goal: continue past smoke-only verification and run the first bounded richer-contract Stage5 training comparison with machine-side checkpoint and speech-emergence follow-up
- Result:
  - ran a 20-step same-architecture richer-contract comparison between random init and partial-init warm-start
  - then tightened the setup into a `3 train / 2 validation` richer-contract minisplit and ran a 40-step warm-start holdout check
  - machine-side speech-emergence probes were replayed on the selected checkpoints
- Main conclusion:
  - richer-contract warm-start is the better active route than richer-contract random init, but only slightly on loss and more meaningfully on machine-side decode shape
  - moving from the duplicated loop-smoke split to a held-out minisplit still improves validation and some alignment-facing speech-emergence metrics
  - the route is still not listening-ready because RMS overshoot and strong frame-template collapse remain large

## Same-Architecture 20-Step Comparison
- Dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_loopsmoke_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Shared structure:
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_scale = 0.5`
  - `use_waveform_decoder_input_adapter = true`
  - `use_noise_hidden_residual_adapter = true`
  - `noise_hidden_residual_mode = delta_direct_v1`
- Random-init run:
  - `reports/runtime/stage5_richercontract_dataset_training_randominit_bmcresid20_r1_1/`
  - best validation checkpoint: `step20`
  - best validation loss: `0.516383`
- Warm-start run:
  - `reports/runtime/stage5_richercontract_dataset_training_warmstart_bmcresid20_r1_1/`
  - init checkpoint:
    - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
  - best validation checkpoint: `step20`
  - best validation loss: `0.512735`
  - skipped mismatched init keys:
    - `periodic_encoder.0.weight`
    - `noise_encoder.0.weight`
- Immediate reading:
  - warm-start beats random-init only slightly on loop loss
  - but that is enough to keep warm-start as the preferred richer-contract route

## Full5 Speech-Emergence Comparison After 20 Steps
- Random-init probe:
  - `reports/runtime/stage5_richercontract_speechemergence_randominit_bmcresid20_r1_1/`
- Warm-start probe:
  - `reports/runtime/stage5_richercontract_speechemergence_warmstart_bmcresid20_r1_1/`
- Baseline aggregate comparison:
  - random-init:
    - `decoded_zero_crossing_rate = 0.507160`
    - `decoded_spectral_centroid_hz = 11298.665039`
    - `decoded_spectral_high_band_energy_ratio = 0.820886`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.335935`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.372204`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.811409`
  - warm-start:
    - `decoded_zero_crossing_rate = 0.392033`
    - `decoded_spectral_centroid_hz = 8860.710938`
    - `decoded_spectral_high_band_energy_ratio = 0.676641`
    - `predicted_activity_to_aligned_frame_rms_corr = 0.368539`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.401708`
    - `decoded_frame_template_cosine_gap_vs_aligned = 0.852499`
- Reading:
  - warm-start is clearly less extreme in high-frequency whiteness than random-init
  - warm-start also improves frame-RMS alignment correlations
  - but template-collapse metrics remain severe, so this is still not a human-audit trigger

## Held-Out Minisplit Run
- Minisplit dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_minisplit_r1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Train ids:
  - `target::chapter3_26_firefly_114`
  - `target::chapter4_7_firefly_105`
  - `target::no_text_voice/chapter3_18_firefly_101`
- Validation ids:
  - `target::chapter3_30_firefly_132`
  - `target::no_text_voice/chapter3_21_firefly_108`
- Warm-start run:
  - `reports/runtime/stage5_richercontract_minisplit_warmstart40_r1_1/`
  - best validation checkpoint: `step39`
  - best validation loss: `0.443589`
  - validation trend:
    - `step20 = 0.478746`
    - `step30 = 0.451651`
    - `step39 = 0.443589`
    - `step40 = 0.444436`
- Reading:
  - unlike the duplicated loop-smoke setup, this run keeps improving on held-out packages
  - therefore the richer-contract route is not merely memorizing the same 5-package loop-smoke index

## Held-Out Minisplit Speech-Emergence
- Probe:
  - `reports/runtime/stage5_richercontract_speechemergence_minisplit_warmstart40_r1_1/`
- Baseline aggregate on validation split:
  - `decoded_zero_crossing_rate = 0.379961`
  - `decoded_spectral_centroid_hz = 8688.796875`
  - `decoded_spectral_high_band_energy_ratio = 0.683286`
  - `decoded_to_aligned_rms_ratio = 2.963793`
  - `predicted_activity_to_aligned_frame_rms_corr = 0.449751`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.479959`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.844697`
- Relative to the full5 warm-start 20-step checkpoint:
  - better:
    - lower `decoded_zero_crossing_rate`
    - lower `decoded_spectral_centroid_hz`
    - stronger activity/RMS alignment correlations
    - slightly lower frame-template gap
  - worse:
    - larger `decoded_to_aligned_rms_ratio`
    - no clear high-band-ratio improvement

## Decision
- Keep:
  - richer-contract warm-start as the active route
  - held-out minisplit validation as a more meaningful bounded check than duplicated train=validation loop smoke
- Do not claim yet:
  - that speech emergence is solved
  - that the current checkpoint family is ready for human listening audit
- Next valid machine step:
  - continue the richer-contract warm-start route with explicit RMS / high-band control, because that is the most obvious remaining machine-side failure after the first held-out improvement
