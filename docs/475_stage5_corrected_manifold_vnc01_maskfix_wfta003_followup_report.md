# 2026-03-28 Stage5 corrected-manifold `vnc01_maskfix + waveform_frames_active_template=0.03` follow-up report

## Conclusion
- Followed the next step from the `474` counterfactual result:
  - keep `vnc`
  - reduce `waveform_frames_active_template_weight` from `0.05` to `0.03`
- Result:
  - heard-route performance matches the current `wfta005` winner
  - validation loss improves further
  - structure probe is effectively unchanged from `wfta005`
- Main decision:
  - promote `wfta003` over `wfta005` as the new corrected-manifold winner
  - it keeps the same `12/24` post-gate and `14/24` no-gate result with a smaller direct template penalty

## Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_wfta003_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- recipe:
  - same `fbmcrs + residualshape + vnc01_maskfix` setup
  - only change from the previous winner:
    `waveform_frames_active_template_weight: 0.05 -> 0.03`

## Validation Loss

| run | best step | best validation loss |
| --- | ---: | ---: |
| `anchor_step8_fbmcrs_residualshape` | `8` | `1.311899` |
| `wfta005_step8` | `8` | `1.218598` |
| `wfta003_step8` | `8` | `1.199898` |

- reading:
  - `wfta003` is the best validation objective seen so far in this corrected-manifold branch
  - `step8` still beats `step4`:
    `1.226273 -> 1.199898`

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | --- |
| `anchor_step8` | `14` | `0.973165` | `4679.957520` | `0.354575` | `needs_more_localization` |
| `wfta003_step4` | `13` | `0.974016` | `4436.952148` | `0.333545` | `needs_more_localization` |
| `wfta003_step8` | `12` | `0.973039` | `4490.020996` | `0.336890` | `needs_more_localization` |
| `wfta005_step8` | `12` | `0.972969` | `4491.603027` | `0.337051` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `16` | `0.974278` | `4677.519043` | `0.351795` |
| `wfta003_step4` | `18` | `0.975300` | `4487.920898` | `0.333637` |
| `wfta003_step8` | `14` | `0.974472` | `4552.213379` | `0.337778` |
| `wfta005_step8` | `14` | `0.974407` | `4553.846680` | `0.337946` |

- reading:
  - `wfta003` reproduces the same winner-level heard-route counts as `wfta005`
  - differences in template and spectral gaps are negligible
  - the important result is that the lower weight does not give back the breakthrough

## Structure Probe Reading
- probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_wfta003_step8_validation24_gateoff_round1_1/`

| run | decoder_to_base_logits_voicing_jump | decoder_to_base_logits_aper_jump | decoder_to_base_logits_product_jump | waveform_frames_rms_to_voicing_corr |
| --- | ---: | ---: | ---: | ---: |
| `vnc01_maskfix_step8` | `-1.428482` | `-0.015697` | `-0.074409` | `-0.268987` |
| `wfta003_step8` | `+0.151361` | `+0.252433` | `+0.282766` | `+0.862164` |
| `wfta005_step8` | `+0.151222` | `+0.252332` | `+0.282437` | `+0.862340` |

- collapse summary:
  - `wfta003 waveform_frames_template_cosine_mean = 0.985843`
  - `wfta005 waveform_frames_template_cosine_mean = 0.985800`
- reading:
  - the internal regime is effectively identical between `wfta003` and `wfta005`
  - reducing the direct template pressure does not restore the old `vnc01_maskfix` regime
  - but it also does not hurt the heard-route winner behavior

## Interpretation
- The current route does need both pieces:
  - `vnc` as a training-time basin shaper
  - direct `waveform_frames` template pressure as the heard-route unlock
- But the direct template pressure does not need to be as strong as `0.05`.
- `0.03` is currently the cleanest point on this branch:
  - same heard-route result
  - lower objective value
  - smaller direct penalty

## Next Step
- Keep `wfta003` as the active winner.
- Stop shrinking the same weight in tiny increments for now.
- The next productive move should be a different axis:
  - add a small constraint that targets localization directly while staying inside the current `wfta003` basin
  - or probe whether `wfta003` can be improved by a lighter decoded-frame or waveform-frame localization term instead of more template pressure
