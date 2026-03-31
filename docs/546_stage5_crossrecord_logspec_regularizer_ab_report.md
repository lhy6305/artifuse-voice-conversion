# 546 Stage5 Crossrecord Logspec Regularizer AB Report

## Summary
- This round executes the next bounded move implied by `545`.
- The new hypothesis was:
  - the route is trapped in a shared cross-record resonance template
  - so a batch-level regularizer should directly penalize cross-record template similarity at the active projection bottleneck
- A new batch-level cross-record log-spectral template excess loss is now implemented for:
  - `waveform_decoder_base_logits`
  - `waveform_frames`
- Two bounded AB runs were executed from the current `templatepush_b` checkpoint on the same `hardpaircontrol4` subset:
  - `crossrecordspeca`: base-logits cross-record regularizer only
  - `crossrecordspecb`: base-logits plus waveform-frames cross-record regularizer
- Result:
  - both runs do reduce shared decoded resonance structure materially on the full active `5`-record slice
  - but both also regress real no-gate rectangular export from `0/5 auto_reject` back to `1/5 auto_reject`
  - the regressed record is the near-open control `target::chapter3_30_firefly_132`
- Therefore:
  - the shared cross-record resonance template is movable
  - but the current global de-sharing regularizer does not move the route toward speech
  - it pushes the route into a different non-speech basin while leaving the hard blocker pair partially unresolved

## Code Changes
- New batch-level training loss plumbing is now implemented in:
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- The new objective family adds optional dataset-loop weights for:
  - `waveform_frames_cross_record_logspec_template`
  - `waveform_decoder_base_logits_cross_record_logspec_template`
- The loss is applied at the dataset-step level rather than the single-package loss path.
- For each selected package in the step:
  - active frames are chosen from aligned target frame RMS
  - active predicted and aligned frames are normalized
  - mean centered log-spectral templates are built per record
  - pairwise cosine similarity is compared across records
  - only predicted similarity excess above the aligned-target pairwise similarity is penalized

## Training Runs

### `crossrecordspeca`
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_crossrecordspeca_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 4 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj fusion_branch_mean_contrast_gate fusion_branch_mean_contrast_proj --disable-resume-optimizer-from-init-checkpoint --waveform-frames-active-template-weight 0.1 --waveform-decoder-base-logits-active-template-weight 0.25 --waveform-decoder-base-logits-frame-delta-weight 0.05 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.25 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05 --waveform-decoder-base-logits-cross-record-logspec-template-weight 0.1`
- Best checkpoint:
  - step `8`

### `crossrecordspecb`
- Command:
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_crossrecordspecb_round1_1 --init-checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --device cuda:0 --num-steps 8 --packages-per-step 4 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential --learning-rate 0.0005 --harmonic-weight 1.0 --noise-weight 1.0 --periodic-gate-weight 0.2 --noise-gate-weight 0.2 --activity-gate-weight 0.2 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --fusion-mode branch_mean_contrast_residual_v1 --waveform-decoder-mode fused_single --use-residual-shape-branch-condition-adapter --residual-shape-branch-condition-scale 0.5 --use-waveform-decoder-input-adapter --waveform-decoder-input-adapter-scale 1.0 --use-noise-hidden-residual-adapter --noise-hidden-residual-mode delta_direct_v1 --noise-hidden-residual-scale 1.0 --trainable-parameter-prefixes waveform_decoder waveform_decoder_input_adapter waveform_decoder_input_gate waveform_decoder_input_proj fusion_branch_mean_contrast_gate fusion_branch_mean_contrast_proj --disable-resume-optimizer-from-init-checkpoint --waveform-frames-active-template-weight 0.1 --waveform-decoder-base-logits-active-template-weight 0.25 --waveform-decoder-base-logits-frame-delta-weight 0.05 --waveform-decoder-base-logits-frame-adjacent-cosine-weight 0.25 --waveform-decoder-base-logits-voicing-negative-corr-weight 0.05 --waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-active-weight 0.05 --waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight 0.05 --waveform-decoder-base-logits-high-band-excess-weight 0.05 --waveform-decoder-base-logits-cross-record-logspec-template-weight 0.1 --waveform-frames-cross-record-logspec-template-weight 0.05`
- Best checkpoint:
  - step `8`

## Real Export Reading
- Full5 real no-gate rectangular exports were replayed at:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_crossrecordspeca_rectgateoff_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_crossrecordspecb_rectgateoff_round1_1`
- Relative to `templatepush_b`:
  - `templatepush_b`: `0/5 auto_reject + 5/5 review_required`
  - `crossrecordspeca`: `1/5 auto_reject + 4/5 review_required`
  - `crossrecordspecb`: `1/5 auto_reject + 4/5 review_required`
- The regressed record is the same in both runs:
  - `target::chapter3_30_firefly_132`
- Aggregate source-filter metrics move strongly but not in the direction needed for route opening:
  - `decoded_template_cosine_mean`:
    - `templatepush_b = 0.968295`
    - `crossrecordspeca = 0.802901`
    - `crossrecordspecb = 0.802644`
  - `decoded_vuv_high_band_ratio_mean`:
    - `templatepush_b = 0.111866`
    - `crossrecordspeca = 0.265358`
    - `crossrecordspecb = 0.265808`
  - `decoded_vuv_centroid_gap_hz_mean`:
    - `templatepush_b = 1206.279004`
    - `crossrecordspeca = 2668.964160`
    - `crossrecordspecb = 2676.437696`
- Reading:
  - the regularizer is not merely a no-op
  - it changes the decoded basin strongly
  - but the changed basin is still machine-negative on one reviewed record and still unverified by human listening

## Cross-Record Peak Sharing
- This family does materially reduce shared decoded resonance structure across the full active `5`-record slice.
- Mean pairwise decoded peak-set Jaccard:
  - `templatepush_b = 0.773`
  - `crossrecordspeca = 0.504`
  - `crossrecordspecb = 0.494`
- Mean aligned-target pairwise Jaccard remains:
  - `0.116`
- So the current cross-record regularizer does move the decoded route away from the old global shared-template basin.
- But one hard shared pair still remains at the maximum overlap:
  - `target::chapter3_26_firefly_114` vs `target::chapter4_7_firefly_105 = 1.0`
- This is important:
  - the regularizer breaks the broad full5 shared-template pattern
  - but it does not resolve the hard blocker pair that originally motivated the focused `templatepush` line

## Handoff And Structure Reading
- Full5 handoff replay was run for `crossrecordspeca`:
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_full5_crossrecordspeca_rectcontract_r1_1`
- Relative to `templatepush_b`, the internal route becomes much less template-collapsed:
  - `waveform_frame_logits_template_cosine_mean = 0.971137 -> 0.805198`
  - `waveform_frames_template_cosine_mean = 0.967072 -> 0.790112`
  - `decoded_no_gate decoded_frame_template_cosine_mean = 0.968295 -> 0.802902`
- But the no-gate route still regresses:
  - `decoded_no_gate auto_reject_count = 0 -> 1`
  - `decoded_no_gate decoded_frame_rms_to_aligned_frame_rms_corr = 0.542405 -> 0.493782`
- Full5 structure replay was also run for `crossrecordspeca`:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_full5_crossrecordspeca_r1_1`
- The main structural localization does not move:
  - coupling diagnosis remains `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - geometry diagnosis remains `decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - strongest transition remains `decoder_to_base_logits`
- The geometry reading becomes even more extreme:
  - `decoder_to_base_logits_template_distance_drop = -1.463558 -> -3.675515`
- Variant reading still says the heard path is dominated by the same projection family:
  - baseline decoded template cosine `0.786381`
  - `waveform_decoder_base_logits_only = 0.786567`
  - `fused_hidden_from_branch_mean = 0.803193`

## Updated Interpretation
- This AB proves something useful:
  - the shared cross-record resonance template is not fixed
  - a batch-level regularizer can materially break it
- But it also proves a limit:
  - simply penalizing global cross-record similarity is not enough
  - it can lower template-collapse and lower cross-record peak overlap
  - while still leaving the route non-speech and even hurting the current near-open control
- The current family is therefore best read as:
  - successful de-sharing of the old broad stripe basin
  - failure to convert that de-sharing into speech structure
  - continued domination by the same `decoder_hidden -> waveform_decoder_base_logits` bottleneck

## Decision
- Keep:
  - the new cross-record batch regularizer code path as a valid localization tool
  - the conclusion that the old shared-template basin is movable
- Retire:
  - the current simple global cross-record-logspec regularizer as the next direct route-opening candidate
  - any assumption that lower cross-record sharedness alone is enough to produce speech
- Keep `templatepush_b` as the stronger bounded machine-side frontier:
  - because it still keeps `0/5 auto_reject`
  - while the new family regresses to `1/5 auto_reject`

## Recommended Next Action
- Do not continue the current global cross-record regularizer family by inertia.
- The next bounded move should be narrower than "de-share everything":
  - preserve the near-open control `target::chapter3_30_firefly_132`
  - focus pressure on the remaining hard pair `114/105`
  - target record-specific differentiation at the active bottleneck without globally destroying the already-better frontier
- In practice, the next candidate should look more like:
  - hard-pair-targeted contrastive or pair-specific anti-collapse pressure
  - plus explicit control preservation for `132`
  - rather than another full-batch global similarity penalty on all reviewed records
