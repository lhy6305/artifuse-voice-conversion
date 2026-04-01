# 555 Stage5 Producer Fine-Structure Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`554` upstream localization step and test whether record-generalizable fine waveform structure is materially stronger inside the Stage5 producer and fusion path than it looked at the old `decoder_hidden -> waveform_decoder_base_logits` boundary alone
- Result: the new producer/fusion oracle probe is now implemented, wired into `manage.py`, and run on the current `templatepush_b.step8` anchor over the full active `5`-record review slice
- Main conclusion:
  - coarse target structure still remains strongly recoverable across the producer path
  - cross-record fine waveform structure remains near zero at every probed producer/fusion stage
  - `waveform_decoder_base_logits` is still the sharpest visible linear collapse site
  - but the producer path itself also does not preserve strong shared fine waveform geometry
  - therefore the project should not reopen another local output-head family and should not blame branch-contrast fusion alone

## Implementation
- New formal probe:
  - `src/v5vc/stage5_producer_fine_structure_probe.py`
- New CLI entry:
  - `analyze-stage5-nores-producer-fine-structure-probe`
- The probe fits the same cheap frozen-feature readouts used by `554`, but over a narrower producer/fusion stage set:
  - `periodic_hidden`
  - `noise_hidden`
  - `branch_mean_hidden`
  - `branch_difference_hidden`
  - `fusion_residual_hidden`
  - `fused_hidden`
  - `decoder_hidden`
  - `waveform_decoder_input_hidden`
  - `waveform_decoder_base_logits`

## Runtime
- Checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Dataset index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Split:
  - `validation`
  - `5` records
- Output:
  - `reports/runtime/stage5_producer_fine_structure_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`

## Key Results
- Coarse structure is still strong across the producer path:
  - best cross-record compressed log-spectrum stage remains `periodic_hidden = 0.938546`
  - cross-record RMS correlation remains around `0.986` to `0.999`
  - cross-record VUV accuracy remains `1.0` except a tiny `fusion_residual_hidden = 0.999055`
- Fine waveform recoverability remains weak everywhere:
  - best cross-record linear waveform cosine is only `fusion_residual_hidden = 0.015881`
  - best cross-record waveform MLP cosine is only `noise_hidden = 0.013228`
  - `fused_hidden = 0.006278 / 0.006768`
  - `decoder_hidden = 0.006278 / 0.006768`
  - `waveform_decoder_input_hidden = 0.006793 / 0.007796`
  - `waveform_decoder_base_logits = 0.000344 / 0.006028`
  - format above is `linear / mlp`
- Transition reading:
  - `branch_mean_hidden -> fused_hidden` waveform MLP drop is only `-0.000080`
  - `decoder_hidden -> waveform_decoder_input_hidden` waveform MLP drop is only `-0.001028`
  - `waveform_decoder_input_hidden -> waveform_decoder_base_logits` linear waveform drop is `0.006449`
- Formal probe diagnosis:
  - `fine_waveform_geometry_is_weak_across_the_full_producer_path_and_base_logits_remains_the_sharpest_visible_collapse_site`

## Interpretation
- This probe refines `554` instead of reversing it.
- The old output-head collapse story is still partially true:
  - the last `waveform_decoder_input_hidden -> waveform_decoder_base_logits` projection remains the clearest visible place where already-weak waveform structure becomes even weaker
- But the new probe also shows why another local head family is still the wrong default:
  - there is no strong shared fine waveform geometry anywhere earlier in the current producer path
  - fusion does not look like a new catastrophic collapse site by itself
  - the branch-contrast residual path is not hiding a large recoverable waveform signal that the current head simply fails to read out
- So the next structural question moves one step earlier again:
  - how to create or preserve stronger target-specific fine structure before the current producer path reaches its present low-signal regime

## Decision
- Keep:
  - the new producer/fusion fine-structure probe as the current upstream localization reference after `554`
  - the conclusion that `waveform_decoder_base_logits` is still the sharpest visible collapse boundary inside the current downstream stack
- Stop treating as the default next move:
  - another small local output-head redesign
  - another dynamic-head replay
  - a story that fusion alone is the newly proven main collapse source

## Recommended Next Action
- The next structural work should move earlier than the current producer-path endpoint.
- Valid next directions now are:
  - localize where target-specific structure is already weak before the current producer/fusion path
  - or change upstream supervision and representation formation so that later producer stages receive stronger fine target structure than the current near-zero waveform oracle signal
