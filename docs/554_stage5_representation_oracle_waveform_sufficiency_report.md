# 554 Stage5 Representation Oracle Waveform Sufficiency Report

## Summary
- Extended the Stage5 representation oracle probe to add two finer targets on top of the existing RMS / VUV / compressed log-spectrum readouts:
  - aligned target unit-RMS waveform frames
  - a small `2-layer` waveform-frame MLP oracle readout in addition to the existing ridge readout
- Formalized the new oracle path in:
  - `src/v5vc/stage5_representation_oracle_probe.py`
  - `src/v5vc/cli.py`
- Ran the updated probe on the current bounded anchor:
  - checkpoint: `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
  - full5 runtime with linear waveform oracle: `reports/runtime/stage5_representation_oracle_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1`
  - full5 runtime with waveform MLP oracle: `reports/runtime/stage5_representation_oracle_probe_reviewslice_full5_templatepushb_hireslogspec_waveformmlp_r1_1`

## What Changed
- The previous oracle probe already showed that coarse target-side structure is still recoverable from multiple stages:
  - cross-record compressed log-spectrum remains strong
  - RMS and VUV are almost perfectly recoverable everywhere
- The missing question was whether any stage still contains recoverable fine frame geometry that could plausibly support speech-like waveform structure.
- To answer that, the probe now fits frozen readouts to aligned target waveform frames directly.

## Key Results
- Coarse structure remains recoverable:
  - cross-record best log-spectrum stage is still `periodic_hidden` at `0.938546`
  - cross-record RMS correlation stays around `0.992` to `0.999`
  - cross-record VUV accuracy remains `1.0` for all probed stages
- Fine waveform-frame structure does not become meaningfully recoverable:
  - cross-record best linear waveform-frame cosine is only `0.012454` at `noise_hidden`
  - cross-record `decoder_hidden` waveform-frame cosine is `0.006279`
  - cross-record `waveform_decoder_base_logits` waveform-frame cosine collapses to `0.000339`
- A small nonlinear readout does not materially change that conclusion:
  - cross-record best waveform MLP cosine is only `0.013228` at `noise_hidden`
  - cross-record `decoder_hidden` waveform MLP cosine is `0.006768`
  - cross-record `waveform_decoder_base_logits` waveform MLP cosine is `0.005996`
  - `decoder_hidden` only beats `base_logits` by `0.000772` on the MLP waveform metric

## Interpretation
- The current Stage5 chain is not representation-empty in the coarse sense:
  - envelope / activity information is present
  - voicing information is present
  - compressed spectral shape is present
- But the current bounded anchor does not expose shared record-generalizable fine waveform structure at a meaningful level anywhere in the probed chain.
- That sharply narrows the diagnosis:
  - the problem is no longer well described as "just one more local output-head tweak"
  - the current `decoder_hidden -> waveform_decoder_base_logits` interface is still a visible failure point
  - but upstream representations also fail to show strong recoverable fine waveform geometry under either a linear oracle or a small nonlinear oracle

## Decision
- Stop treating local output-head redesign as the default next move.
- The next structural probe should move upstream into the fusion / producer path and ask where target-specific fine structure is already lost before the current waveform head sees it.
- Future oracle work, if any, should only be justified when it materially changes this conclusion, not when it merely nudges near-zero waveform cosine by a few thousandths.
