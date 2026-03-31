# Stage5 Dynamicheadsmokea Manual Review And Oracle Probe Plan Report

## Summary
- Date: `2026-03-31`
- Review target: full5 paired bundle `templatepushb` vs `dynamicheadsmokea`
- Human result: both variants are still pure buzz, with no substantive audible change and effectively no perceivable difference

## Human Review Result
- Reviewed bundle:
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_reviewslice_full5_templatepushb_vs_dynamicheadsmokea_round1_1`
- Human conclusion:
  - `dynamicheadsmokea` is still pure buzz
  - no speech structure appears
  - no human-voice-like region appears
  - no meaningful improvement over `templatepushb` is audible
  - the difference is small enough that it is effectively not distinguishable by listening

## Re-Evaluation
- `templatepushb` already established the machine-side frontier:
  - better energy following
  - lower template-collapse scalars
  - still pure buzz by listening
- `dynamicheadsmokea` added a genuinely different local freedom at the same bottleneck:
  - dynamic residual basis mixture on `waveform_decoder_base_logits`
  - clean training from partial init
  - slight machine-side gains over `templatepushb`
  - still no human-audible gain
- Combined reading now becomes stricter:
  - repeated small local changes around `decoder_hidden -> waveform_decoder_base_logits` can move machine-side buzz metrics
  - but they do not generate speech structure
  - therefore the current problem should no longer be framed as "the head just needs a slightly better local projector"

## Updated Problem Statement
- The stable bottleneck localization at `decoder_hidden -> waveform_decoder_base_logits` is still useful, but it should now be read as an interface failure, not yet as proof that a better same-locality head is sufficient
- The real unresolved question is now:
  - does `decoder_hidden` already contain recoverable record-specific speech structure that the current head family cannot express
  - or has the representation already collapsed upstream so strongly that no small local head change can recover speech

## Decision
- Stop treating the current minimal dynamic-head family as the next main line
- Do not continue:
  - same-scope dynamic-head continuation
  - another small output-head freedom tweak
  - more template-push or logspec regularizer stacking

## Recommended Next Step
- Run an oracle-style representation sufficiency probe on the current best anchor checkpoints
- Purpose:
  - directly test whether `decoder_hidden` contains enough target-specific structure to reconstruct aligned target-side speech descriptors under an easier readout than the current production head

## Concrete Probe Plan
- Inputs:
  - current machine-side anchor `templatepushb`
  - optional side-by-side reference `dynamicheadsmokea`
  - full5 or hardpaircontrol4 slice
- Probe stages:
  - `periodic_hidden`
  - `noise_hidden`
  - `fused_hidden`
  - `decoder_hidden`
  - `waveform_decoder_base_logits`
- Oracle targets:
  - aligned target frame log-spectrum or low-dimensional log-mel proxy
  - aligned frame RMS contour
  - voiced/unvoiced side target
- Readout family:
  - frozen-feature ridge or tiny linear readout first
  - optionally one tiny MLP readout if linear probe is clearly underfitting
- Main question:
  - can a cheap oracle readout recover materially more target-specific structure from `decoder_hidden` than the production head currently expresses

## Decision Rule
- If oracle readout from `decoder_hidden` still fails badly:
  - root cause has effectively moved upstream
  - next work should target fusion / producer representation, not another local output head
- If oracle readout from `decoder_hidden` succeeds materially better than the production head:
  - the interface is still the right target
  - but the next mechanism must be a stronger conditional projector, not another tiny residual tweak

## Next Action
- Build and run the oracle representation sufficiency probe before any further training continuation
