# Stage5 混响样本保留评估

## 结论

当前**不建议**因为本次听审里发现的少量原生混响样本而删除数据并重训。

原因有两条，而且都足够硬：

1. 当前被明确标注为“存在混响”的关键记录
   `target::chapter3_6_firefly_106`
   在当前推荐拆分
   `hybrid_stratified_blocked`
   中位于 **target validation**，
   不在 train。
   因此它不是当前训练污染源，
   “删除并重训”不会解决任何已训练参数里的问题。
2. 这条记录并没有在主观或量化上表现成异常离群点。
   相反，
   它和其他 glitch 样本一样，
   仍然稳定支持
   `step72__decode_gate_smooth3`
   优于 baseline `step72`。

## 证据

### 1. 数据拆分层面

- `reports/data/round1_1_split_analysis/options/hybrid_stratified_blocked.json`
  中，
  `target::chapter3_6_firefly_106`
  明确位于
  `validation_record_ids`
  列表，
  不在 train。
- 这意味着：
  - 它当前承担的是验证/听审观察位，
    不是训练监督样本。
  - 即使你现在把它从数据目录里移除，
    也不会改变当前模型已经学到的东西。

### 2. validation12 听审导出

- `reports/audio/audio_audit_gui_stage5_step72_glitch_smooth3_validation12_session/audio_audit_review.json`
  里，
  一共有
  `2`
  条记录被显式备注为
  “样本存在混响”。
- 其中：
  - `1`
    条已完成；
  - 另 `1`
    条是重复窗口，
    备注为
    “本条与上一条完全一致。为避免统计出错，本条不再写入评估。”，
    因而未纳入完成统计。
- 已完成的混响窗口并没有导致判断摇摆，
  `best_boundary / most_stable / overall_pick`
  仍然全部指向
  `decoded:offline_mvp_nores_vocoder_dataset_loop.step72__decode_gate_smooth3`。

### 3. focused validation3 听审导出

- `reports/audio/audio_audit_gui_stage5_step72_glitch_smoothing_session/audio_audit_review.json`
  中，
  同一记录的
  `3`
  个混响窗口都被单独标出。
- 其中：
  - `2`
    条
    `valid_for_comparison=yes`；
  - `1`
    条标记为
    `valid_for_comparison=no`，
    原因是样本条件不够理想，
    不是因为出现了和总体结论相反的偏好。
- 即便如此，
  这些窗口的
  `overall_pick`
  依然都落在
  `step72__decode_gate_smooth3`，
  没有出现
  “混响把模型优劣关系颠倒”
  的情况。

### 4. 量化 probe 没显示这条记录是反常点

- 在
  `reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/stage5_low_activity_fragmentation_probe.json`
  里，
  `target::chapter3_6_firefly_106`
  的聚合指标为：
  - baseline `step72`
    `mean_fragmentation_score = 3.358236`
    `mean_sample_delta_peak = 0.090525`
  - `step72__decode_gate_smooth3`
    `mean_fragmentation_score = 1.355229`
    `mean_sample_delta_peak = 0.064535`
- 同一文件的 top window 里，
  该记录的代表性窗口
  `segment_index=1`
  上：
  - baseline
    `fragmentation_score = 6.013935`
    `sample_delta_peak = 0.156067`
  - smooth3
    `fragmentation_score = 2.007351`
    `sample_delta_peak = 0.077332`
- `segment_index=2`
  上同样成立：
  - baseline
    `fragmentation_score = 3.006222`
  - smooth3
    `fragmentation_score = 1.00356`

这些读数说明：
这条混响记录并没有把量化指标推向奇怪方向，
它只是和其他 glitch 样本一样，
在 baseline 下暴露更重的边界毛刺，
在 smooth3 下得到明显缓解。

## 解释

这次发现的“样本原生有混响，但似乎不影响模型效果”，
更接近下面这个情形：

- 它是一个 **validation robustness sample**，
  不是 train 污染源。
- 它带来了一点声场差异，
  但没有掩盖我们真正关注的失真轴：
  低活动段边界毛刺 / burst 跳变。
- 因此它当前更像是
  “额外证明当前修复在轻度非纯净条件下仍成立”，
  而不是
  “说明训练集有脏样本必须回炉”。

## 当前建议

1. 不删除这批混响样本，不为此重训。
2. 保留它们在 validation / audit 中的观察价值，
   因为它们能顺手检验修复是否只在“纯净样本”上成立。
3. 如果后续要做更严格的数据治理，
   正确动作不是立刻删库重训，
   而是先给这类样本打 tag：
   - `reverb_light`
   - `reverb_heavy`
   - `off_domain_room_response`
4. 只有在后续出现以下证据时，
   才值得考虑单独剔除并重训：
   - 这类样本实际进入了 train；
   - 在 train 中占比不再是极少数；
   - 它们持续导致 clean-only 目标域上的指标劣化；
   - 或它们系统性地掩盖/反转模型分支排序。

## 一句话结论

这次不需要因为混响样本删数据重训。
当前证据支持把它们视为
“validation-only 的轻度非纯净鲁棒性样本”，
而不是
“已经污染训练的脏数据”。
