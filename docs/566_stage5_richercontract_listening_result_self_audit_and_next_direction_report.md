# 566 Stage5 Richer-Contract Listening Result Self-Audit And Next Direction Report

## Summary
- Date: `2026-04-01`
- Goal: close the richer-contract paired listening audit, review the recent experiment direction at a higher level, and decide whether the project has been optimizing details past the point of diminishing return
- Human listening result:
  - `combo20` is less piercing than `baseline39`
  - `combo20` becomes more broken-up and intermittent, closer to a Morse-code-like burst pattern
  - neither variant contains any speech structure
  - both still show the same abnormal fixed-spacing thin-line spectrogram pattern
- Main conclusion:
  - yes, the project has now stayed too long inside Stage5-local waveform regularizer/detail tuning relative to the strength of the earlier upstream evidence
  - the recent regularizer work was still useful to close one ambiguity, but it did not change the route class
  - the next correct move is not another Stage5-local loss sweep
  - the next correct move is upstream representation/supervision redesign with a hard oracle gate before reintegrating into Stage5

## A. What The Listening Result Actually Resolves
- Compared bundle:
  - `baseline39`
  - `combo20`
- Human result:
  - `combo20` reduces harshness
  - `combo20` also becomes more discontinuous and bursty
  - neither route produces even local speech-like structure
  - spectrograms still remain dominated by evenly spaced thin stripes
- Meaning:
  - the combined regularizer route changes buzz texture
  - it does not open a speech-emergence route
  - machine-side improvements on loudness/brightness/template suppression were not the missing final step

## B. Self-Audit: Did We Drift Into Detail Optimization?
- Short answer:
  - partially yes
- Why that answer is fair rather than self-negating:
  - the recent `563-565` work did answer a real unresolved question:
    - whether the richer-contract route was failing mainly because of waveform-side RMS/high-band shaping
    - whether human listening would prefer the regularized branch once a more balanced checkpoint was chosen
  - that question is now closed
- But the larger evidence was already available earlier:
  - `554` showed frozen Stage5 representations do not expose meaningful fine waveform geometry anywhere in the bounded anchor
  - `558` showed the upstream student packet contract is also low-signal for that missing geometry
  - `560` showed even the earlier raw frontend/source-acoustic families are only weakly informative for the missing fine structure
- Therefore:
  - once the new paired listening round still reports "less harsh buzz, but no speech structure and the same fixed stripe pattern",
    it is no longer defensible to keep treating Stage5-local tuning as the main frontier

## C. What The Recent Regularizer Work Still Gave Us
- The regularizer branch was not wasted work.
- It established three useful boundaries:
  - `rms_guard` alone is not the right route
  - `bhb01` alone over-darkens and does not solve the real problem
  - the best available Stage5-local regularized branch can improve perceived harshness and some machine metrics without creating speech structure
- That is valuable because it removes a false hope:
  - the project no longer needs to wonder whether "one more local loudness/high-band tweak" is the likely unlock

## D. What The Big-Direction Evidence Now Says
- Current repeated pattern across multiple frontiers:
  - machine metrics improve
  - harshness can reduce
  - energy following can improve
  - buzz can become more intermittent
  - but spectrograms remain in the same fixed-spacing stripe basin
  - human listening still finds no speech structure
- Combined with `554/558/560`, the most coherent reading is:
  - the decoder is being driven by controls rich enough for coarse envelope and voicing organization
  - but not by a representation that carries record-specific fine temporal/spectral geometry
  - Stage5 then keeps reshaping the same low-information attractor instead of synthesizing speech structure

## E. What The Next Step Should Actually Be
- Stop as default:
  - another Stage5-local regularizer sweep
  - another checkpoint-ranking pass based on current richer-contract variants
  - more control-subset reshuffling inside the existing packet family
- Start instead:
  - a new upstream fine-structure-bearing representation line
- Concretely, the next experiment family should have this shape:
  - define a new upstream representation contract that is not another scalar-control bundle
  - make it a dense per-frame or short-horizon representation explicitly supervised to carry local spectral/fine-structure detail
  - only after that representation passes an oracle gate should it be wired into Stage5

## F. Recommended Concrete Plan
- Step 1:
  - design a new upstream contract family, for example `streaming_student_fine_structure_contract_v1`
  - it should carry a compact dense frame representation rather than only low-order scalar controls/diagnostics
- Step 2:
  - train or derive that representation under direct fine-structure supervision
  - the supervision target should be something like short-horizon spectral/frame geometry, not only RMS/VUV/control reconstruction
- Step 3:
  - probe the new representation first with the existing oracle workflow
  - require a clear jump over the current `~0.02` fine-waveform regime before touching Stage5 again
- Step 4:
  - only if the oracle gate is passed, integrate the new representation into the richer-contract Stage5 consumer path

## G. Decision
- The current richer-contract Stage5 branch is stopped as a local-tuning frontier.
- The project should now escalate back upstream.
- The most important next task is:
  - build a new fine-structure-bearing upstream representation and verify it with oracle probes before any further Stage5-local optimization.
