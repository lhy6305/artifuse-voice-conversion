# 2026-03-28 Stage5 corrected-manifold `vnc01_maskfix + waveform_frames_active_template=0.05` report

## Conclusion
- Added a direct heard-route regularizer on `waveform_frames`:
  - `waveform_frames_active_template_weight = 0.05`
- Ran it on top of the current corrected-manifold `vnc01_maskfix` anchor.
- This is the first follow-up in this family that materially improves both training-side validation and heard-route rejection counts at the same time.
- Best checkpoint:
  - `step8`
- Best heard-route result so far inside corrected-manifold:
  - `decoded_post_ola_gate auto_reject: 14 -> 12`
  - `decoded_no_gate auto_reject: 16 -> 14`
  - diagnosis stays
    `needs_more_localization`
  - but the route is now clearly less stuck than the previous anchor

## Code Change
- Added a direct `waveform_frames` active-template penalty path to Stage5 no-res training:
  - new loss weight:
    `waveform_frames_active_template_weight`
- Threaded it through:
  - core `compute_nores_vocoder_losses(...)`
  - validation helpers
  - Stage5 no-res CLI entrypoints
- Metric name:
  - `loss_waveform_frames_active_template_excess_relu_0p02`

## Smoke Read
- smoke output:
  - `reports/runtime/tmp_offline_mvp_nores_vocoder_dataset_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_smoke_round1_1/`
- key read:
  - the new loss is active immediately
  - validation `loss_total` improves:
    `1.382643 -> 1.264157`
- smoke handoff:
  - `decoded_post_ola_gate auto_reject = 14/24`
  - `decoded_no_gate auto_reject = 18/24`
- meaning:
  - early signal was good enough to justify a full 8-step run
  - heard-route was not yet a clean win at smoke scale

## Full Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_wfta005_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- setup:
  - same `fbmcrs + residualshape` corrected-manifold recipe
  - keep `waveform_decoder_base_logits_voicing_negative_corr = 0.1`
  - add `waveform_frames_active_template = 0.05`

## Validation Loss

| run | best step | best validation loss |
| --- | ---: | ---: |
| `anchor_step8_fbmcrs_residualshape` | `8` | `1.311899` |
| `vnc01_maskfix_step8` | `8` | `1.242400` |
| `wfta005_step8` | `8` | `1.218598` |

- reading:
  - `wfta005` is the best objective value seen so far in this corrected-manifold branch
  - `step8` also beats `step4`:
    `1.244973 -> 1.218598`

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `anchor_step8` | `14` | `0.973165` | `0.907448` | `4679.957520` | `0.354575` | `needs_more_localization` |
| `vnc01_maskfix_step8` | `15` | `0.974073` | `0.906457` | `4451.310547` | `0.334622` | `needs_more_localization` |
| `wfta005_step4` | `13` | `0.973993` | `0.905378` | `4437.242188` | `0.333571` | `needs_more_localization` |
| `wfta005_step8` | `12` | `0.972969` | `0.903931` | `4491.603027` | `0.337051` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `anchor_step8` | `16` | `0.974278` | `0.755193` | `4677.519043` | `0.351795` |
| `vnc01_maskfix_step8` | `19` | `0.975258` | `0.759468` | `4504.020020` | `0.334638` |
| `wfta005_step4` | `18` | `0.975278` | `0.786683` | `4488.258301` | `0.333665` |
| `wfta005_step8` | `14` | `0.974407` | `0.797691` | `4553.846680` | `0.337946` |

### Handoff Stage Aggregates

| run | logits_template | frames_template | logits_abs_ge_1 | frames_abs_ge_095 |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `0.987227` | `0.985322` | `0.067440` | `0.007914` |
| `vnc01_maskfix_step8` | `0.988032` | `0.986222` | `0.070867` | `0.007819` |
| `wfta005_step4` | `0.987981` | `0.986183` | `0.072446` | `0.007300` |
| `wfta005_step8` | `0.987669` | `0.985800` | `0.072547` | `0.006869` |

- reading:
  - `step4` already improves post-gate rejection to `13/24`
  - `step8` is the first one in this branch to reach `12/24`
  - `decoded_no_gate` is the more important confirmation:
    `16/24 -> 14/24`
  - so this is not just gate-side masking

## Structure Probe Reading
- probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_step8_validation24_gateoff_round1_1/`

| run | decoder_to_base_logits_voicing_jump | decoder_to_base_logits_aper_jump | decoder_to_base_logits_product_jump | waveform_frames_rms_to_voicing_corr |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `-1.751059` | `+0.134542` | `+0.112305` | `-0.813209` |
| `vnc01_maskfix_step8` | `-1.428482` | `-0.015697` | `-0.074409` | `-0.268987` |
| `wfta005_step8` | `+0.151222` | `+0.252332` | `+0.282437` | `+0.862340` |

- reading:
  - `wfta005` does not preserve the old `vnc01_maskfix` internal solution
  - by `step8`, the explicit `vnc` loss is effectively dormant again on validation
  - the route has moved into a different internal coupling regime
  - but that new regime is also the first one that gives a real heard-route breakthrough

## Interpretation
- Direct `waveform_frames` template pressure is stronger than the earlier `base_logits`-side micro-penalties.
- In this recipe, it becomes the dominant mechanism:
  - training objective improves
  - `waveform_frames_template` comes down
  - heard-route rejection counts improve
- The tradeoff is that the original `vnc01_maskfix` internal coupling gains are not preserved as-is.
- So the new winner should be interpreted as:
  - a better heard-route operating point
  - reached by a different internal solution than the previous probe-aligned `vnc` line

## Decision
- Promote `wfta005 step8` to the active corrected-manifold anchor.
- Keep `vnc01_maskfix` as a useful mechanism reference, not as the final winner.
- Do not keep optimizing for `vnc` activation by itself.
- Next iteration should start from `wfta005 step8` and ask one of two questions:
  - whether the same heard-route gain survives if `vnc` is reduced or removed
  - whether a smaller direct `waveform_frames` template penalty can keep the `12/24` gain while recovering some internal coupling cleanliness

## Artifacts
- smoke summary:
  - `reports/runtime/tmp_offline_mvp_nores_vocoder_dataset_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_smoke_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- smoke handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_smoke_step1_validation24_round1_1/stage5_waveform_handoff_probe.json`
- smoke structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_smoke_step1_validation24_gateoff_round1_1/stage5_waveform_decoder_structure_probe.json`
- full training summary:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_wfta005_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- step4 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_step4_validation24_round1_1/stage5_waveform_handoff_probe.json`
- step8 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_step8_validation24_round1_1/stage5_waveform_handoff_probe.json`
- step8 structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta005_step8_validation24_gateoff_round1_1/stage5_waveform_decoder_structure_probe.json`
