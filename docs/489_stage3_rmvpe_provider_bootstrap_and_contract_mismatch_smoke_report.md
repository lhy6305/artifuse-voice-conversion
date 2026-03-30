# 489 Stage3 RMVPE provider bootstrap and contract mismatch smoke report

## Goal
- Complete Step B of the approved `A -> B` route at the wiring level.
- Add `rmvpe_v1` behind the same Stage3 pitch-provider contract used by Step A.
- Verify whether naive direct RMVPE injection is already contract-compatible with the current Stage3 controlfamily route.

## Implementation summary

### 1. RMVPE provider mode was added to the Stage3 pitch-provider contract
- `src/v5vc/streaming_student/pitch_provider.py` now supports:
  - `none`
  - `deterministic_extractor_v1`
  - `rmvpe_v1`
- `rmvpe_v1` resolves:
  - `pitch_provider_model_path`
  - `pitch_provider_cache_dir`
  - `pitch_provider_voicing_threshold`

### 2. A minimal internal RMVPE ONNX inference path now exists
- Added `src/v5vc/streaming_student/rmvpe_inference.py`.
- Current implementation scope is intentionally narrow:
  - ONNX inference only
  - local mel frontend
  - local-average-cents decode
  - CPUExecutionProvider
  - per-record tensor cache on disk
- This is enough for Stage3 provider-side experiments without reintroducing the full external RVC codebase.

### 3. Stage3 data loading now materializes provider tensors per mode
- `src/v5vc/streaming_student/data.py` now attaches provider tensors to each target example.
- For `rmvpe_v1`, provider tensors are computed from waveform and aligned onto the Stage3 teacher-frame grid.
- The provider tensors are then collated into the shared batch contract and consumed by the same frontend input path as Step A.

### 4. A dedicated RMVPE config was added
- Added `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_v1.json`.
- Current local smoke asset path:
  - `tmp/reference_assets/rmvpe/rmvpe.onnx`
- Current local cache path:
  - `tmp/streaming_student_pitch_provider_cache/rmvpe_v1`

## Smoke verification

### Commands executed
- `.\python.exe manage.py prepare-streaming-student-supervision --config configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_v1.json --output-dir reports/plans/streaming_student_supervision_rmvpe_smoke --batch-size 1 --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py run-streaming-student-training-step --config configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_v1.json --output-dir reports/training/streaming_student_rmvpe_smoke --batch-size 1 --experiment-id streaming_student_rmvpe_smoke_step1 --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py export-streaming-student-proxy-audio --checkpoint reports/training/streaming_student_rmvpe_smoke/checkpoints/streaming_student_rmvpe_smoke_step1.step1.pt --output-dir reports/runtime/streaming_student_proxy_audio_rmvpe_smoke --sample-count 1 --split-name target_validation --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py export-streaming-student-downstream-control-packet --checkpoint reports/training/streaming_student_rmvpe_smoke/checkpoints/streaming_student_rmvpe_smoke_step1.step1.pt --output-dir reports/runtime/streaming_student_downstream_control_packet_rmvpe_smoke --sample-count 1 --split-name target_validation --allow-student-line-while-teacher-unsatisfied`
- `.\python.exe manage.py export-streaming-student-downstream-control-packet --checkpoint reports/training/streaming_student_rmvpe_smoke/checkpoints/streaming_student_rmvpe_smoke_step1.step1.pt --output-dir reports/runtime/streaming_student_downstream_control_packet_rmvpe_smoke_sample3 --sample-count 3 --split-name target_validation --allow-student-line-while-teacher-unsatisfied`

### Wiring result
- All smoke commands completed successfully.
- This confirms that `rmvpe_v1` is now a real Stage3 provider path, not just a planned mode string.

## Main findings

### 1. RMVPE is integrated, but naive direct injection is not yet contract-compatible
- In the 3-sample packet smoke:
  - `f0_ready_count = 0 / 3`
  - `all_core_controls_ready_count = 0 / 3`
  - `auto_reject_count = 3 / 3`
- Example packet metrics:
  - `target::chapter3_3_firefly_162`
    - `f0_proxy_reference_corr = -0.545358`
    - `f0_calibrated_log2_mae = 0.477778`
  - `target::chapter3_3_firefly_138`
    - `f0_proxy_reference_corr = 0.116822`
    - `f0_calibrated_log2_mae = 0.774553`
  - `target::chapter3_4_firefly_106`
    - `f0_proxy_reference_corr = -0.490576`
    - `f0_calibrated_log2_mae = 1.624407`

### 2. This is materially worse than Step A
- Step A deterministic provider was expected to be a plumbing-validity upper bound because it reused the same target-state extraction family.
- Step B was supposed to test whether an external expert signal could still remain useful under the same contract.
- Current answer is:
  - yes, RMVPE can be wired into the same contract
  - no, current naive direct RMVPE injection does not match the Stage3 teacher target contract well enough

### 3. The problem is not wiring failure
- A minimal one-record inspection confirmed that the raw provider tensors are being produced and cached successfully.
- Therefore the current negative result should be interpreted as a provider-to-contract mismatch, not as a code-plumbing failure.

## Interpretation

### What Step B proves
- The repository now supports both sides of the intended `A -> B` provider comparison:
  - deterministic in-repo provider
  - RMVPE external expert provider
- Future Stage3 provider experiments no longer need architectural rewiring first.

### What Step B currently disproves
- It is not safe to assume that "using RMVPE" automatically fixes the Stage3 F0 route.
- Under the current direct-injection contract, RMVPE does not preserve enough target-compatible F0 structure to pass even a small packet screen.

## Recommended next action
- Do not promote naive `rmvpe_v1` direct injection as the new default Stage3 route.
- The next valid follow-up is a provider-contract diagnosis step, for example:
  - inspect whether the mismatch is mostly octave bias, time alignment mismatch, or voiced-mask disagreement
  - add explicit provider-side calibration or normalization only if it remains runtime-plausible
  - keep Step A deterministic provider as the current contract-valid reference

## Artifacts
- `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_v1.json`
- `reports/plans/streaming_student_supervision_rmvpe_smoke/streaming_student_supervision_plan.json`
- `reports/training/streaming_student_rmvpe_smoke/logs/streaming_student_rmvpe_smoke_step1.step1.json`
- `reports/training/streaming_student_rmvpe_smoke/checkpoints/streaming_student_rmvpe_smoke_step1.step1.pt`
- `reports/runtime/streaming_student_proxy_audio_rmvpe_smoke/proxy_audio_export.json`
- `reports/runtime/streaming_student_downstream_control_packet_rmvpe_smoke/streaming_student_downstream_control_packet.json`
- `reports/runtime/streaming_student_downstream_control_packet_rmvpe_smoke_sample3/streaming_student_downstream_control_packet.json`
