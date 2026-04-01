# 557 Stage5 Source-Scaffold Control-Contract Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`556` upstream localization step and test whether the read-only `source_scaffold` control contract still contains materially stronger record-generalizable fine waveform geometry than the current Stage5-selected dynamic subset
- Result: the new `source_scaffold` oracle probe is now implemented, wired into `manage.py`, and run on the current `templatepushb.step8` anchor over the full active `5`-record review slice
- Main conclusion:
  - coarse target structure remains highly recoverable directly from the `source_scaffold` dynamic control contract
  - cross-record fine waveform geometry remains near zero even before the Stage5 branch-input package is rebuilt
  - the current Stage5-selected dynamic subset is not the main reason for the missing fine structure
  - the omitted `unselected_available_controls` subset is only slightly different and still remains deeply sub-threshold
  - therefore the main missing fine structure is already absent in the current `source_scaffold` dynamic control contract itself

## Implementation
- New formal probe:
  - `src/v5vc/stage5_source_scaffold_oracle_probe.py`
- New CLI entry:
  - `analyze-stage5-nores-source-scaffold-oracle-probe`
- The probe reads the package-linked `source_scaffold` payload directly and compares:
  - `selected_dynamic_controls`
  - `selected_joint_contract`
  - `all_available_controls`
  - `unselected_available_controls`
  - `all_controls_plus_conditioning`
  - plus narrower dynamic families such as `event_full_family`, `f0_family`, `voicing_aper_family`, `energy_family`, `proxy_family`, and `aux_stat_family`

## Runtime
- Checkpoint anchor:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Dataset index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Split:
  - `validation`
  - `5` records
- Output:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`

## Key Results
- The primary dynamic-control comparison remains low-signal throughout:
  - `selected_dynamic_controls = 0.009515 / 0.012218`
  - `all_available_controls = 0.005871 / 0.003945`
  - `unselected_available_controls = 0.011726 / 0.008911`
  - format above is `linear / mlp`
- Coarse structure remains strong in the same three views:
  - `selected_dynamic_controls` keeps `logspec = 0.933891`, `rms_corr = 0.99906`, `vuv_accuracy = 0.99937`
  - `all_available_controls` keeps `logspec = 0.930091`, `rms_corr = 0.999035`, `vuv_accuracy = 1.0`
  - `unselected_available_controls` keeps `logspec = 0.929562`, `rms_corr = 0.997616`, `vuv_accuracy = 0.99937`
- Adding more dynamic controls does not improve the main signal:
  - `selected_dynamic -> all_available` waveform gain is `-0.003644 / -0.008273`
  - `selected_dynamic -> unselected_available` waveform gain is only `+0.002211 / -0.003307`
  - format above is `linear / mlp`
- Narrow family reading:
  - best dynamic linear waveform score is only `voicing_aper_family = 0.023317`
  - best dynamic waveform MLP score is only `f0_family = 0.02111`
  - `energy_family = 0.016711 / 0.008211`
  - `event_full_family = 0.011207 / 0.012212`
- Conditioning caution:
  - `conditioning_family = 0.022368 / 0.022368`
  - but it also has `oracle_rms_corr = 0.0` and `oracle_vuv_accuracy = 0.471101`
  - because it is frame-constant conditioning, that tiny score should still be read only as record-level leakage rather than temporal fine waveform structure
- Formal probe diagnosis:
  - `fine_waveform_geometry_is_already_weak_in_source_scaffold_control_contract`

## Interpretation
- This probe closes the next ambiguity left by `556`.
- The earlier Stage5-local reading remains valid:
  - the Stage5 branch inputs were already low-signal
  - the periodic and noise input encoders were not the newly proven main collapse site
- `557` now shows that moving one step earlier into the read-only `source_scaffold` contract still does not reveal a strong recoverable temporal reservoir:
  - the current selected dynamic subset is weak
  - the full available dynamic control set is also weak
  - the omitted unselected subset is only trivially different and is still far below any convincing fine-structure regime
- So the next structural question must move earlier again:
  - either stronger target-specific fine geometry still exists in the upstream teacher hidden-state path before explicit control packaging
  - or the upstream representation and supervision route is already too coarse even before the current `source_scaffold` contract is formed

## Decision
- Keep:
  - the new `source_scaffold` oracle probe as the current earliest explicit-control localization reference after `556`
  - the interpretation guard that `selected_dynamic_controls`, `all_available_controls`, and `unselected_available_controls` are the main comparison, while conditioning-augmented variants stay secondary
- Stop treating as the default next move:
  - widening the current Stage5-selected control subset
  - blaming the omitted scaffold controls as a hidden strong temporal reservoir
  - overreading conditioning-augmented scores as proof that the dynamic contract is already sufficient

## Recommended Next Action
- Move one step earlier than the read-only `source_scaffold` control contract.
- The next valid structural probe is:
  - inspect whether upstream teacher-contract hidden states such as `hidden` and `fused_hidden` still contain materially stronger fine waveform geometry than the explicit control package that `source_scaffold` exports
- If those hidden states are also low-signal, the bottleneck must move even earlier into source acoustic-state formation or upstream supervision rather than any Stage5-local consumer redesign.
