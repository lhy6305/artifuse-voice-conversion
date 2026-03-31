# 540 Stage5 Waveform-Handoff Contract-Alignment Bugfix Report

## Summary
- This round did not open a new training family.
- It audited the apparent `539` handoff-vs-export divergence and found an implementation mismatch:
  - `stage5_waveform_handoff_probe.py` was still reconstructing decoded routes with the old training-side Hann overlap-add helper
  - real export was already using `reconstruct_waveform_from_frames_with_contract(...)`
  - the active `539` route comparison was therefore mixing:
    - handoff probe decoded routes under Hann reconstruction
    - real export decoded routes under rectangular reconstruction
- After fixing the probe to accept `reconstruction_contract_mode` and rerunning `539` with `rectangular_overlap_count_norm`, the apparent divergence disappears for `decoded_no_gate`:
  - corrected handoff `decoded_no_gate` now exactly matches real export at:
    - `auto_reject_count = 3/5`
    - `review_required_count = 2/5`
    - `decoded_frame_template_cosine_mean = 0.985812`
    - `decoded_frame_adjacent_cosine_mean = 0.997886`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.464940`
    - `spectral_centroid_gap_hz = 4777.123535`
    - `spectral_high_band_energy_ratio_gap = 0.315689`
- The corrected conclusion is:
  - `539` still stands as the strongest current bounded result and a real partial opening
  - but the earlier "handoff decoded routes are already `0/5 auto_reject` while export remains `3/5 auto_reject`" reading was a contract-mismatch artifact
  - the next action should now move to subset-specific diagnosis of the remaining `3` auto-reject records, not further handoff-vs-export semantics debugging

## Bug Localization
- Pre-fix handoff probe behavior:
  - `stage5_waveform_handoff_probe.py` imported:
    - `reconstruct_waveform_from_frames`
  - that helper uses Hann overlap-add from training-side bootstrap semantics
- Real export behavior:
  - `nores_vocoder_audio_export.py` reconstructs decoded audio through:
    - `reconstruct_waveform_from_frames_with_contract(...)`
  - active export route explicitly passed:
    - `reconstruction_contract_mode = rectangular_overlap_count_norm`
- Therefore the old `539` comparison was not:
  - same checkpoint
  - same frame sequence
  - same reconstruction contract

## Code Changes
- `src/v5vc/stage5_waveform_handoff_probe.py`
  - now imports:
    - `DEFAULT_RECONSTRUCTION_CONTRACT_MODE`
    - `normalize_reconstruction_contract_mode`
    - `reconstruct_waveform_from_frames_with_contract`
  - `analyze_stage5_nores_waveform_handoff(...)` now accepts:
    - `reconstruction_contract_mode`
  - route reconstruction now uses the explicit contract-aware helper
  - output summary now records:
    - `decode_runtime.reconstruction_contract_mode`
- `src/v5vc/cli.py`
  - `analyze-stage5-nores-waveform-handoff` now accepts:
    - `--reconstruction-contract-mode`

## Corrected Probe Run

### Corrected `539` handoff replay under rectangular contract
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_producerinterface_rectcontract_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_producerinterface_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3 --reconstruction-contract-mode rectangular_overlap_count_norm`
- Output:
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_producerinterface_rectcontract_r1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_producerinterface_rectcontract_r1_1/stage5_waveform_handoff_probe.md`

## Corrected Reading
- Corrected handoff runtime:
  - `reconstruction_contract_mode = rectangular_overlap_count_norm`
- Corrected `decoded_no_gate` aggregate:
  - `auto_reject_count = 3/5`
  - `decoded_frame_template_cosine_mean = 0.985812`
  - `decoded_frame_adjacent_cosine_mean = 0.997886`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.464940`
  - `spectral_centroid_gap_hz = 4777.123535`
  - `spectral_high_band_energy_ratio_gap = 0.315689`
- These now match the real export manifest aggregate at the same checkpoint and route.
- Corrected gated handoff routes:
  - `decoded_pre_ola_gate`
    - `auto_reject_count = 2/5`
  - `decoded_post_ola_gate`
    - `auto_reject_count = 2/5`
- Reading:
  - the remaining gap is not between handoff decoded reconstruction and export decoded reconstruction
  - the remaining active question is now the residual failure subset itself

## Record-Level Correction
- Corrected `decoded_no_gate` record statuses:
  - `target::chapter3_26_firefly_114`
    - `auto_reject_obvious_buzz`
  - `target::chapter3_30_firefly_132`
    - `review_required`
  - `target::chapter4_7_firefly_105`
    - `auto_reject_obvious_buzz`
  - `target::no_text_voice/chapter3_18_firefly_101`
    - `auto_reject_obvious_buzz`
  - `target::no_text_voice/chapter3_21_firefly_108`
    - `review_required`
- This is the same split already reported by real export.

## Impact On `539`
- What remains valid from `539`:
  - producer-plus-interface widening is a real gain
  - real export improved from `5/5 auto_reject` to `3/5 auto_reject + 2/5 review_required`
  - `539` remains the strongest current bounded training recipe
- What is superseded:
  - the old handoff readout that all decoded routes were already `0/5 auto_reject`
  - the follow-up next-step wording that framed the main issue as handoff-vs-export divergence

## Decision
- Keep:
  - the `539` producer-plus-interface checkpoint as the active bounded frontier
  - rectangular reconstruction as the active real export contract
- Retire:
  - the stale `539` handoff interpretation produced before contract alignment
  - the idea that the next move is more route-semantics debugging between handoff and export on this checkpoint

## Recommended Next Action
- Move directly to remaining-failure localization on the corrected `539` frontier.
- The next bounded probe should focus on the `3` remaining auto-reject records:
  - `target::chapter3_26_firefly_114`
  - `target::chapter4_7_firefly_105`
  - `target::no_text_voice/chapter3_18_firefly_101`
- Good next targets are:
  - subset-specific source-filter review and per-record metric comparison against the `2` review-required records
  - path-level localization on the corrected rectangular route for those `3` failures
  - only after that, decide whether another training widening is justified
