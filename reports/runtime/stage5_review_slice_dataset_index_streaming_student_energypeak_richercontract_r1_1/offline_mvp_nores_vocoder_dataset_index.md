# Streaming Student Stage5 Dataset Index

- dataset_index_version: streaming_student_stage5_dataset_index_v1
- packet_export_path: ['F:/proj_dev/tmp/workdir4/reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/streaming_student_downstream_control_packet.json', 'F:/proj_dev/tmp/workdir4/reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/streaming_student_downstream_control_packet.json']
- split_name: validation
- semantic_consumer_mode: streaming_student_richer_source_contract_v1
- target_contract_mode: legacy_proxy
- noise_event_family: e_evt
- active_split_key: validation
- validation_package_count: 5
- periodic_input_dims: [84]
- noise_input_dims: [84]

## Notes
- This merged review-slice index combines tv8 and se8 packet exports for the same full5 richer-contract Stage5 validation slice.
- Packages append the streaming-student richer source-contract semantic consumer features into both Stage5 branches.
- This artifact is for Stage5 richer-contract training and smoke verification, not for reuse with old 36/36 checkpoints.
