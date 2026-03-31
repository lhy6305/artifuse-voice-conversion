# Stage5 Dynamic Output-Head Smoke Report

## Summary
- Date: `2026-03-31`
- Goal: test a materially different local mechanism at the still-stable bottleneck `decoder_hidden -> waveform_decoder_base_logits` without reopening the broader producer/interface scope
- Result: the minimal dynamic output-head smoke is technically live, trains cleanly, and preserves the current `0/5 auto_reject + 5/5 review_required` machine frontier on full5 real `rectangular gateoff` export, but it does not yet change the structural diagnosis; the main bottleneck still localizes to `decoder_hidden -> waveform_decoder_base_logits`

## Code Changes
- Added a bounded dynamic residual basis head to the fused-single waveform decoder path in `src/v5vc/offline_vocoder_scaffold.py`
  - new scaffold flags:
    - `use_waveform_decoder_dynamic_basis`
    - `waveform_decoder_dynamic_basis_count`
    - `waveform_decoder_dynamic_basis_scale`
  - new helper:
    - `compute_waveform_decoder_base_logits(...)`
  - design:
    - keeps the legacy `waveform_decoder(...)` path as the base projection
    - adds a small gated mixture of zero-init residual basis projections
    - preserves exact old behavior at init
- Wired the new head through:
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/teacher_first_vc_demo.py`
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
  - `src/v5vc/cli.py`
- Also fixed a reconstruction compatibility bug in `build_nores_vocoder_scaffold_from_state_dict(...)`
  - old checkpoints without any dynamic-basis keys now fall back to a safe default basis count instead of tripping the new constructor on inferred count `0`

## Smoke Design
- Anchor checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Bounded train subset:
  - `hardpaircontrol4`
  - records: `114`, `132`, `105`, `101`
- New trainable scope only:
  - `waveform_decoder_dynamic_adapter`
  - `waveform_decoder_dynamic_gate`
  - `waveform_decoder_dynamic_basis`
- Run:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_dynamicheadsmokea_round1_1`
  - `4` steps from the `templatepush_b` frontier
  - partial init allowed because the new head introduces `14` missing parameters

## Training Result
- Train loss:
  - step1 `82.987533`
  - step4 `82.967005`
- Validation loss:
  - step1 `82.979120`
  - step4 `82.960579`
- Best checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_dynamicheadsmokea_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt`

## Full5 Real Export
- Artifact:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_dynamicheadsmokea_rectgateoff_round1_1`
- Decode contract:
  - `disable-predicted-activity-gate`
  - `predicted_activity_gate_floor = 0.0`
  - `predicted_activity_gate_smoothing_frames = 0`
  - `predicted_activity_gate_apply_mode = pre_overlap_add`
  - `reconstruction_contract_mode = rectangular_overlap_count_norm`
- Export status:
  - `0/5 auto_reject + 5/5 review_required`
- This matches the negative-gate status of `templatepush_b`; it does not open a new machine-side route, but it also does not regress back to the `1/5 auto_reject` continuation basin

## Source-Filter Reading
- Artifact:
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_dynamicheadsmokea_rect_r1_1`
- Aggregate signals:
  - `decoded_vuv_high_band_ratio_mean = 0.121464`
  - `aligned_vuv_high_band_ratio_mean = 0.099338`
  - `decoded_vuv_centroid_gap_hz_mean = 1325.292383`
  - `aligned_vuv_centroid_gap_hz_mean = 1243.492761`
  - `decoded_template_cosine_mean = 0.965387`
  - `decoded_vuv_high_band_ratio_nonpositive_count = 0`
- Relative to the current `templatepush_b` machine frontier from `543`:
  - `decoded_template_cosine_mean` improves slightly: `0.968295 -> 0.965387`
  - `decoded_vuv_high_band_ratio_mean` improves slightly: `0.111866 -> 0.121464`
- Machine-side reading:
  - the new head can move the existing buzz basin a little
  - the probe still labels the route `needs_more_localization`
  - nothing here is enough to claim speech structure

## Structure Reading
- Artifact:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_full5_dynamicheadsmokea_r1_1`
- Baseline collapse summary:
  - `fused_hidden_template_cosine_mean = 0.981582`
  - `waveform_frames_template_cosine_mean = 0.966311`
  - `decoded_frames_template_cosine_mean = 0.961908`
  - diagnosis: `collapse_not_localized_to_waveform_decoder`
- Upstream coupling localization:
  - strongest transition: `decoder_to_base_logits`
  - strongest transition score: `1.177872`
  - diagnosis: `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Projection geometry localization:
  - strongest transition: `decoder_to_base_logits`
  - strongest transition score: `1.496381`
  - `decoder_to_base_logits_template_distance_drop = -1.496381`
  - diagnosis: `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Relative to the previous `templatepush_b` structure reading from `545/546/547`:
  - the main localization does not move
  - `decoder_to_base_logits_template_distance_drop` is slightly worse than the `templatepush_b` frontier reading `-1.463558`
- Interpretation:
  - the new residual basis path is active enough to shift machine-side export metrics
  - but the current minimal dynamic head does not yet break the old projection bottleneck

## Current Conclusion
- This is a valid mechanism-level smoke, not a dead wiring exercise:
  - the new dynamic head trains
  - it reconstructs correctly through checkpoint, export, and probe paths
  - it preserves the best current negative-gate export status
  - it slightly improves machine-side template and vuv readings over `templatepush_b`
- But it is not yet a route-opening result:
  - full5 export is still only `review_required`
  - no human listening review has been done yet
  - the old structural bottleneck remains unchanged

## Next Action
- Do not broaden replay from this checkpoint yet
- The next bounded move should be a direct human A/B against `templatepush_b`
  - if listening still says both are the same pure buzz basin, retire this minimal dynamic-head design
  - only if human review hears a real record-specific improvement should the project consider a stronger same-location design, for example joint `waveform_decoder + dynamic_basis` training or a higher-capacity conditional projection head
