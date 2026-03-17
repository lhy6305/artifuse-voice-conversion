# round1 target special eval 评估

- overall_ok: True

## 检查项
- special_eval_manifest_nonempty: True
- special_eval_record_ids_unique: True
- special_eval_disjoint_from_main_validation: True
- special_eval_all_from_no_text_voice: True
- special_eval_all_target_role: True

## 摘要
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- split_option_name: hybrid_stratified_blocked
- target_validation_record_count: 62
- target_special_eval_record_count: 8
- target_special_eval_group_counts: {"no_text_voice": 8}
- target_special_eval_punctuation_only_count: 8

## 备注
- target_special_eval is a challenge-only set and should not be merged back into regular validation.
- current round1 special_eval records are expected to come from no_text_voice only.
- current special_eval clean text is punctuation-only, so this set should be interpreted as a stress slice rather than normal content validation.
