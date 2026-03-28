# 2026-03-28 Stage5 corrected-manifold `fbmcrs + residualshape` finetune report

## Conclusion
- Promoted the next stronger mechanism level from probe-only discussion into a real corrected-manifold finetune:
  - init checkpoint:
    `fusion_mode = branch_mean_contrast_residual_v1`
  - decoder route:
    `use_residual_shape_branch_condition_adapter = true`
  - dataset:
    `corr24 train/val`
  - budget:
    `8 steps`
- This run produces the first material corrected-manifold jump beyond the plain `corr24 step8` route:
  - `decoded_post_ola_gate auto_reject: 24 -> 14`
  - diagnosis:
    `buzz_present_by_waveform_frames_before_gate -> needs_more_localization`
  - `decoded_no_gate auto_reject: 24 -> 16`
- Meaning:
  - this is not just a gate-side cosmetic gain
  - the early waveform-frame attractor is being weakened
- But it is still not a solved route:
  - `14/24 auto_reject` remains too high
  - `waveform_frames_template_cosine_mean` rebounds upward
  - the system appears to trade away high-band pure-buzz failure for a more localized but still template-heavy regime

## Training Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_fusionbranchmeancontrast_residualshape_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- setup:
  - `num_steps = 8`
  - `packages_per_step = 6`
  - `validation_interval = 4`
  - `checkpoint_interval = 4`
  - `learning_rate = 1e-4`
  - same loss family as `corr24 step8 plain`

## Validation Loss

| run | best step | best validation loss |
| --- | ---: | ---: |
| `corr24_step8_plain` | `8` | `1.182152` |
| `corr24_step8_fbmcrs_residualshape` | `8` | `1.311899` |

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `corr24_step8_plain` | `24` | `0.920997` | `0.892176` | `8774.619141` | `0.660415` | `buzz_present_by_waveform_frames_before_gate` |
| `corr24_step8_fbmcrs_residualshape` | `14` | `0.973165` | `0.907448` | `4679.957520` | `0.354575` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `corr24_step8_plain` | `24` | `0.924694` | `-0.783244` | `9254.138672` | `0.700916` |
| `corr24_step8_fbmcrs_residualshape` | `16` | `0.974278` | `0.755193` | `4677.519043` | `0.351795` |

## Stage Reading
- plain corrected-manifold `step8`:
  - `fused_hidden_template = 0.948296`
  - `waveform_frames_template = 0.949051`
  - failure is already present before gate
- `fbmcrs + residualshape` corrected-manifold `step8`:
  - `fused_hidden_template = 0.956970`
  - `waveform_frame_logits_template = 0.987227`
  - `waveform_frames_template = 0.985322`
  - `decoder_to_logits_template_gap = 0.030257`
- Interpretation:
  - the new route dramatically lowers brightness / centroid failure
  - but the heard path is now more template-heavy than the plain corrected route
  - remaining work is no longer “escape obvious high-band buzz”
  - remaining work becomes “reduce residual template / envelope operating-point collapse without reintroducing brightness”

## Same-Family Checkpoint Choice
- Also probed `step4` from the same finetune run.

| run | `decoded_no_gate` reject | `decoded_post_ola_gate` reject | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | --- |
| `fbmcrs_residualshape_step4` | `20` | `21` | `4861.294922` | `0.369993` | `needs_more_localization` |
| `fbmcrs_residualshape_step8` | `16` | `14` | `4679.957520` | `0.354575` | `needs_more_localization` |

- Decision:
  - `step8` is the better corrected-manifold anchor within this family
  - no reason to early-stop at `step4`

## Artifacts
- training summary:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- step8 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8_round1_1/stage5_waveform_handoff_probe.json`
- step4 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step4_round1_1/stage5_waveform_handoff_probe.json`

## Decision
- Keep `corr24 step8 plain` as the low-template reference.
- Keep `corr24 step8 fbmcrs + residualshape` as the first corrected-manifold route that materially breaks the early pure-buzz basin.
- Do not go back to `branch_mean` linear-mix micro-sweeps.
- The next mechanism work should target the new residual failure mode:
  - preserve the current low brightness / centroid gains
  - reduce `waveform_frame_logits -> waveform_frames` template-heavy operating region
  - stay on `fbmcrs + residualshape step8` as the active mechanism anchor
