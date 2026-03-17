# Offline MVP Teacher Runtime Summary

- generated_at: 2026-03-17T21:53:38
- input_audio_path: F:/proj_dev/tmp/workdir4/data_convert/dataset_firefly_raw/chapter3_2_firefly_178.wav
- teacher_experiment_id: EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration
- teacher_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260316-043.step200.pt
- device: cpu
- sample_rate: 44100
- audio_sec: 2.0
- frame_length: 400
- hop_length: 160
- frame_ms: 9.070295
- hop_ms: 3.628118
- chunk_samples: 1024
- chunk_ms: 23.219955
- streaming_frame_count: 549
- runtime_outputs_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_2_firefly_178/teacher_runtime_streaming_outputs.pt
- full_pass_outputs_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_2_firefly_178/teacher_runtime_full_pass.pt

## Verification
- frame_count_equal: True
- frame_alignment_equal: True
- hidden: shape_equal=True max_abs_diff=1.192e-06 mean_abs_diff=5e-09 allclose_atol_5e-6=True
- fused_hidden: shape_equal=True max_abs_diff=2.861e-06 mean_abs_diff=8e-09 allclose_atol_5e-6=True
- z_art: shape_equal=True max_abs_diff=4.17e-07 mean_abs_diff=6e-09 allclose_atol_5e-6=True
- event_logits: shape_equal=True max_abs_diff=4.77e-07 mean_abs_diff=7e-09 allclose_atol_5e-6=True
- event_probs: shape_equal=True max_abs_diff=1.19e-07 mean_abs_diff=1e-09 allclose_atol_5e-6=True
- acoustic: shape_equal=True max_abs_diff=1.907e-06 mean_abs_diff=1.1e-08 allclose_atol_5e-6=True
