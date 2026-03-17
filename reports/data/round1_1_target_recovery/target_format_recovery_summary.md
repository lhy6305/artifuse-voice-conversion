# round1.1 target format recovery 摘要

- base_round1_train_count: 624
- recovered_count: 42
- remaining_excluded_count: 5
- failed_recovery_count: 0
- target_sample_rate: 44100
- target_channels: 1
- base_duration_sec: 3826.049737
- recovered_duration_sec: 235.470887
- remaining_excluded_duration_sec: 7.854

## notes
- round1.1 target recovery keeps current no_text_voice exclusions isolated by default.
- recovered records are normalized to 44100 Hz mono and written under output_dir/audio.
- combined manifest_round1_train.jsonl now contains original round1 target records plus recovered lexical records.
