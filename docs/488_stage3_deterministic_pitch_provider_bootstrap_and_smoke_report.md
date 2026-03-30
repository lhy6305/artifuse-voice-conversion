# 488 Stage3 deterministic pitch provider bootstrap and smoke report

## Goal
- Complete Step A of the approved `A -> B` recovery route for Stage3 F0.
- Formalize the in-repo deterministic acoustic-state extractor as the first official Stage3 pitch provider.
- Verify that the explicit provider path really reaches the main Stage3 training and export routes.

## Implementation summary

### 1. A formal Stage3 pitch-provider module now exists
- Added `src/v5vc/streaming_student/pitch_provider.py`.
- It now owns:
  - provider mode normalization
  - deterministic extractor tensor building
  - audio-length to frame-length alignment
  - model-input packaging for explicit `pitch_provider_log2_f0` and `pitch_provider_vuv`

### 2. Stage3 batch contract now carries explicit provider tensors
- `src/v5vc/streaming_student/data.py` now materializes:
  - `pitch_provider_f0_hz`
  - `pitch_provider_log2_f0`
  - `pitch_provider_vuv`
- These are derived from the existing target acoustic-state tensors when available.

### 3. The Stage3 frontend can now consume explicit pitch-provider inputs
- `src/v5vc/streaming_student/model.py` now accepts:
  - `pitch_provider_log2_f0`
  - `pitch_provider_vuv`
- Under `pitch_provider_mode != none`, frontend `coarse_log_f0` and `vuv_logits` can be supplied directly by the provider path instead of relying on waveform-only discovery.

### 4. Main Stage3 routes were updated
- The explicit provider path is now wired into:
  - supervision dry-run
  - one-step training
  - multi-step training loop
  - checkpoint evaluation
  - proxy audio export
  - downstream control packet export
- `prepare-streaming-student-training-data` now supports provider-mode target dry-runs.
- `prepare-streaming-student-paired-training-data` and `build-streaming-student-eval-bridge` now fail fast under explicit provider mode instead of silently falling back to the old waveform-only route.

### 5. A dedicated Step A config was added
- Added `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_v1.json`.
- This keeps the controlfamily baseline architecture but enables:
  - `pitch_provider_mode = deterministic_extractor_v1`

## Smoke verification

### Commands executed
- `.\python.exe manage.py prepare-streaming-student-supervision --config configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_v1.json --output-dir reports/plans/streaming_student_supervision_detpitch_smoke --batch-size 1 --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py run-streaming-student-training-step --config configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_v1.json --output-dir reports/training/streaming_student_detpitch_smoke --batch-size 1 --experiment-id streaming_student_detpitch_smoke_step1 --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py export-streaming-student-proxy-audio --checkpoint reports/training/streaming_student_detpitch_smoke/checkpoints/streaming_student_detpitch_smoke_step1.step1.pt --output-dir reports/runtime/streaming_student_proxy_audio_detpitch_smoke --sample-count 1 --split-name target_validation --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py export-streaming-student-downstream-control-packet --checkpoint reports/training/streaming_student_detpitch_smoke/checkpoints/streaming_student_detpitch_smoke_step1.step1.pt --output-dir reports/runtime/streaming_student_downstream_control_packet_detpitch_smoke --sample-count 1 --split-name target_validation --allow-student-line-while-teacher-unsatisfied`

### Result
- All four commands completed successfully.
- This confirms that explicit deterministic pitch-provider tensors now pass through:
  - data loading
  - batch collation
  - frontend forward
  - teacher-supervised loss
  - checkpoint save/load
  - proxy audio export
  - downstream packet export

### Important observed numbers
- In the downstream packet smoke artifact for `target::chapter3_3_firefly_162`:
  - `f0_proxy_reference_corr = 0.999885`
  - `f0_calibrated_log2_mae = 0.003998`
  - `vuv_reference_mae = 0.028987`
- The packet still remained `auto_reject_named_control_incomplete` because:
  - `aper_status = auto_reject_not_ready`
  - `energy_status = auto_reject_not_ready`

## Interpretation

### What this proves
- Step A is no longer just a design note.
- The repository now has a real explicit Stage3 pitch-provider contract.
- The contract is sufficiently wired to support real Stage3 experiments and packet exports.

### What this does not prove
- This smoke does not prove that Stage3 F0 is solved in a deployment sense.
- The deterministic provider is derived from the same in-repo acoustic-state extraction family already used for target-reference analysis.
- Therefore very strong F0 agreement in this smoke is expected and should be interpreted as a plumbing-validity result, not as proof that an external runtime sidecar has already been validated.

## Next action
- Step B is now the correct next experiment:
  - add RMVPE behind the same `pitch_provider_mode` contract
  - keep all downstream metrics identical
  - compare deterministic extractor vs RMVPE on the same Stage3 supervision, packet, and proxy-audio screens

## Artifacts
- `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_v1.json`
- `reports/plans/streaming_student_supervision_detpitch_smoke/streaming_student_supervision_plan.json`
- `reports/training/streaming_student_detpitch_smoke/logs/streaming_student_detpitch_smoke_step1.step1.json`
- `reports/training/streaming_student_detpitch_smoke/checkpoints/streaming_student_detpitch_smoke_step1.step1.pt`
- `reports/runtime/streaming_student_proxy_audio_detpitch_smoke/proxy_audio_export.json`
- `reports/runtime/streaming_student_downstream_control_packet_detpitch_smoke/streaming_student_downstream_control_packet.json`
