# 567 Stage3 Fine-Structure Reference Oracle Gate Report

## Summary
- Date: `2026-04-01`
- Goal: start the upstream representation-redesign line from `566` by adding an analysis-only dense fine-structure reference family to the Stage3 packet / Stage5 source scaffold, then replay the existing source-scaffold oracle on the active full5 review slice
- Code changes:
  - `src/v5vc/streaming_student/downstream_control_packet.py`
  - `src/v5vc/streaming_student/stage5_handoff.py`
  - `src/v5vc/stage5_source_scaffold_oracle_probe.py`
- Runtime outputs reused in place:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/`
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_tv8_r1_1/`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_richercontract_se8_r1_1/`
  - oracle report:
    - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructref_r1_1/`
- Main conclusion:
  - the first compact dense candidate, `unit_rms_logspec_48 + delta`, still does not pass the upstream oracle gate and remains in the old `~0.02` waveform regime
  - a direct `unit_rms_waveform_frame` reference does pass immediately, with cross-record linear waveform cosine `0.999958`
  - therefore the next valid upstream redesign should target a compact local waveform-geometry code, not another magnitude-only compact log-spectrum family

## A. What Was Added
- The Stage3 downstream packet now exports an analysis-only `fine_structure_reference` family:
  - `unit_rms_waveform_frame`
  - `unit_rms_logspec`
  - `unit_rms_logspec_delta`
- The Stage5 source scaffold now carries these as extra `available_controls`:
  - `packet_unit_rms_waveform_frame`
  - `packet_unit_rms_logspec`
  - `packet_unit_rms_logspec_delta`
- These controls are explicitly analysis-only:
  - they are exported from target waveform frames
  - they are not current student predictions
  - current Stage5 branch layouts do not consume them

## B. Why This Experiment Was Needed
- `566` said the next move must be an oracle-gated upstream redesign rather than more Stage5-local tuning.
- But that still left one concrete design question open:
  - what kind of dense local representation actually escapes the current weak `~0.02` waveform-oracle regime?
- This experiment answered that by testing two classes:
  - compact magnitude-like local representation:
    - `unit_rms_logspec_48 + delta`
  - direct local waveform-geometry representation:
    - `unit_rms_waveform_frame`

## C. Replay Setup
- Stage3 packet anchor:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Review slice:
  - same active full5 richer-contract review slice used by the current upstream route
  - records:
    - `target::chapter3_26_firefly_114`
    - `target::chapter3_30_firefly_132`
    - `target::chapter4_7_firefly_105`
    - `target::no_text_voice/chapter3_18_firefly_101`
    - `target::no_text_voice/chapter3_21_firefly_108`
- Oracle command:
  - `analyze-stage5-nores-source-scaffold-oracle-probe`
  - `logspec_bins = 201`
  - leave-one-record-out cross-record aggregates used as the decision surface

## D. Key Result
- Old current route remains weak:
  - `selected_dynamic_controls = 0.009515 / 0.012218`
- Compact dense log-spectrum family remains weak:
  - `fine_structure_reference_family = 0.017661 / 0.019218`
- Adding that compact family to the current selected controls still remains weak:
  - `selected_dynamic_plus_fine_structure_reference = 0.013366 / 0.021660`
- But direct waveform-frame geometry opens the gate immediately:
  - `fine_structure_waveform_reference_family = 0.999958 / 0.845117`
  - `selected_dynamic_plus_fine_structure_waveform_reference = 0.999957 / 0.854163`
- Format above is:
  - `linear waveform cosine / waveform-MLP cosine`

## E. Correct Reading
- The important contrast is not between `selected_dynamic_controls` and `all_available_controls` anymore.
- Once the analysis-only waveform reference is present, `all_available_controls` and `unselected_available_controls` inherit that upper-bound family and jump to near-identity too.
- Therefore:
  - treat `all_available_controls` and `unselected_available_controls` in this run only as sanity-check upper bounds
  - do not misread them as proof that the current deployable student control contract is already solved
- The real design answer comes from the isolated families:
  - compact magnitude-only local representation:
    - still too weak
  - direct local waveform geometry:
    - more than sufficient

## F. What This Rules Out
- It rules out the comforting but wrong idea that “any compact dense log-spectrum-like sidecar” is enough.
- Even though `unit_rms_logspec_48 + delta` is clearly denser than the old scalar packet family, it still fails the actual waveform oracle gate.
- So the next upstream redesign should not default to:
  - another scalar bundle
  - another compressed magnitude-only log-spectrum family
  - another Stage5-local regularizer loop around the same weak signal class

## G. What The Next Step Should Be
- The next correct implementation target is a compact code that preserves local waveform geometry more directly.
- Concretely:
  - design a learned short-horizon fine-structure code whose supervision target is local waveform-frame geometry, not only magnitude log-spectrum
  - keep the oracle gate in front of Stage5 integration
  - require the learned compact code to materially escape the current `~0.02` regime before it is allowed into the richer-contract consumer line
- A reasonable next candidate is:
  - a compact learned projection or autoencoding target derived from `unit_rms_waveform_frame`
  - not a hand-designed `48`-bin magnitude-only contract

## Decision
- The upstream redesign route is confirmed.
- The first compact magnitude-style dense family is rejected.
- The next frontier is a compact local waveform-geometry representation with direct supervision and the same oracle gate.
