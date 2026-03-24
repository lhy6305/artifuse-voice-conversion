# 2026-03-24 teacher-first audible compare bundle inference-only variant 扩展与当前听审入口固化报告

## 结论
- 当前实验线已经不该继续沿用
  旧 compare bundle
  的默认
  `baseline / candidate`
  口径。
- 本轮已把
  teacher-first
  audible compare bundle
  扩到：
  - 不只支持换 checkpoint
  - 也支持每个 variant
    自带 inference-only
    适配参数
- 当前默认 compare
  已正式切到：
  - `contractv2_normfix`
    默认链路
  - `affine_events_refmean_gateoff`
    候选链路
- 这意味着：
  - 下次继续这条实验线时，
    默认可以直接从正式听审入口开始，
    不必再手工拼参数或重建 bundle

## 一、为什么这轮要先改 compare bundle

### 1. 当前实验线真正的下一问已经变了
- 到
  `docs/289`
  为止，
  当前最高价值问题已经不是：
  - 再解释
    `contractv2_normfix`
    loss
    为什么略好
- 而是：
  - 当前最小 user-line
    候选
    `affine + event_probs refmean + gate_off`
    是否第一次真正脱离 buzz

### 2. 旧 compare bundle 已不再对题
- 旧默认 compare bundle
  有两个问题：
  1. variant
     只能换 checkpoint，
     不能表达：
     - normalization
     - control-family override
     - gate on/off
  2. 默认 variant
     仍指向更早期
     smoke baseline / candidate
- 所以如果不先修入口，
  后续人工听审就会继续听错对象

## 二、本轮代码改动

### 1. variant 级新字段
- 更新：
  - `src/v5vc/teacher_first_vc_demo.py`
  - `src/v5vc/cli.py`
- 当前 audible compare
  的 vocoder spec
  已支持：
  - `checkpoint_selection_path`
  - `selection_target`
  - `use_predicted_activity_gate`
  - `predicted_activity_gate_apply_mode`
  - `normalization_strategy`
  - `control_family_overrides`

### 2. compare bundle 已真正消费这些字段
- 当前每个 variant
  在运行
  `run-offline-mvp-teacher-first-vc-demo`
  时，
  都会把上述 inference-only
  参数真实传进去，
  不再只是落在 spec
  里当备注

### 3. compare summary / markdown 已同步扩展
- compare bundle
  的：
  - `teacher_first_vc_audible_compare_bundle.json`
  - `teacher_first_vc_audible_compare_bundle.md`
- 现在会同时记录：
  - variant 使用的
    selection source
  - gate on/off
  - apply mode
  - normalization strategy
  - control-family overrides

## 三、当前默认 compare 已切到什么

### variant 1
- `normfix_default`
- checkpoint 解析自：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json`
- selection：
  - `best_validation`
- decode 参数：
  - predicted gate `on`
  - apply mode `post_ola_envelope`
  - normalization `none`

### variant 2
- `affine_events_refmean_gateoff`
- 使用同一
  `contractv2_normfix`
  `best_validation`
  checkpoint
- decode 参数：
  - predicted gate `off`
  - normalization
    `reference_affine_match`
  - control override
    `event_probs=reference_mean`

## 四、本轮 smoke

### 执行命令
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -OutputDir tmp/teacher_first_audible_compare_bundle_normfix_adaptation_smoke `
  -Device cuda `
  -SkipFullPassVerify
```

### 结果
- `case_count = 2`
- `variant_count = 2`
- `variant_runs_succeeded = 4 / 4`
- `positive_controls_ready = 2 / 2`
- listening 目录：
  - `tmp/teacher_first_audible_compare_bundle_normfix_adaptation_smoke/listening/`

### 当前已落盘的试听文件
- `parallel_firefly_107`
  - `source_input.wav`
  - `smoke_baseline_passthrough.wav`
  - `target_reference.wav`
  - `decoded_normfix_default.wav`
  - `decoded_affine_events_refmean_gateoff.wav`
- `parallel_firefly_132`
  - `source_input.wav`
  - `smoke_baseline_passthrough.wav`
  - `target_reference.wav`
  - `decoded_normfix_default.wav`
  - `decoded_affine_events_refmean_gateoff.wav`

## 五、本轮 smoke 观察

### `parallel107`
- `normfix_default`
  - `centroid = 6002.995`
  - `high_band = 0.352024`
  - `decoded_rms = 0.020747`
- `affine_events_refmean_gateoff`
  - `centroid = 5906.304`
  - `high_band = 0.346510`
  - `decoded_rms = 0.171846`

### `parallel132`
- `normfix_default`
  - `centroid = 6010.095`
  - `high_band = 0.352541`
  - `decoded_rms = 0.018922`
- `affine_events_refmean_gateoff`
  - `centroid = 5915.599`
  - `high_band = 0.346928`
  - `decoded_rms = 0.171957`

### 当前解释
- 这进一步说明：
  - 适配候选不仅在
    `parallel107`
    上成立，
    在默认第二条平行样例
    `parallel132`
    上也继续保持
    同方向改善
- 但当前还不能写成：
  - 已完成主观转正
- 因为：
  - 这轮只是 compare bundle
    smoke
  - 还没有正式人工听审结论

## 六、关于当前 `high_risk`

### 当前事实
- 这轮 bundle
  两个 variant
  仍全部被旧
  `teacher_first_runtime_risk_v1`
  判为：
  - `high_risk`

### 当前正确解释
- 这不等于：
  - compare bundle
    没价值
  - 或候选一定仍然是 buzz
- 更准确的写法是：
  - bundle
    已经把当前最需要人工听的对比
    正式固化出来
  - 但 risk heuristic
    仍沿用旧阈值，
    不能直接代替听感结论

## 七、下一步
1. 直接基于：
   - `tmp/teacher_first_audible_compare_bundle_normfix_adaptation_smoke/listening/`
   做人工对比听审
2. 核心比较对象：
   - `decoded_normfix_default.wav`
   - `decoded_affine_events_refmean_gateoff.wav`
3. 若听感确认候选首次脱离 buzz，
   就把它固化成：
   - 当前实验线最小 user-line
     适配口径
4. 同时重做
   user-line risk
   制度，
   使其从旧固定阈值
   转为 reference-aware
   判断

## 一句话结论
- 当前实验线的默认 compare 入口
  已正式升级为：
  - `contractv2_normfix`
    默认链路
  - 对比
    `affine_events_refmean_gateoff`
    候选
- bundle
  已能真实导出两条平行 source
  的并排试听资产；
  下一步不该再回到旧 compare 默认值，
  而应直接基于这份 bundle
  做人工听审。
