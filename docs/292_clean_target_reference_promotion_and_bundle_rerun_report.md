# 2026-03-24 clean target reference 默认提升与 bundle 复跑报告

## 结论
- 当前 audible smoke / compare
  的默认
  `target_reference`
  已不再来自
  calibration asset
  的隐式首条记录。
- 本轮已把默认 shared
  target reference
  显式切到：
  - `data_convert/dataset_firefly_raw/chapter3_3_firefly_135.wav`
- 这条 target
  位于
  clean-no-reverb split，
  且不在已知
  `chapter3_5 / chapter3_6`
  reverb_like
  章节内。
- 在这个 clean reference
  下重跑后，
  smoke / compare
  都正常落盘；
  但 decoded
  仍未摆脱 buzz。
- 因而当前更合理的下一阶段
  已转为：
  - decoder /
    waveform head /
    objective
    主线诊断

## 一、为什么要改默认 target reference
- 原默认逻辑是：
  - 若用户未显式传
    `--target-reference-audio`
  - 就从
    calibration asset
    的
    `selection_summary.selected_record_ids`
    里取第一条
- 当前实际取到的是：
  - `target::chapter3_20_firefly_112`
  - 对应音频：
    `data_convert/dataset_firefly_raw/chapter3_20_firefly_112.wav`
- 虽然它不在
  `chapter3_5 / chapter3_6`
  的正式
  `reverb_like`
  标注里，
  但用户主观听感已指出：
  - 它不适合作为当前听审参照物
- 因此本轮目标不是
  “证明它一定带混响”，
  而是：
  - 去掉这条听审混淆项

## 二、本轮默认 clean reference

### 选定条目
- `target::chapter3_3_firefly_135`
- 音频：
  - `data_convert/dataset_firefly_raw/chapter3_3_firefly_135.wav`
- 文本：
  - `这位小姐，也是你的熟人吗？`
- 时长：
  - `3.000998s`

### 选择理由
- 落在：
  - `data_prep/round1_1/splits/hybrid_stratified_blocked_target_clean_no_reverb/`
- 不属于：
  - `chapter3_5`
  - `chapter3_6`
  这两章
  已人工标注
  `reverb_like`
  的 target 集合
- 时长适中，
  适合作为：
  - shared target reference
  - 每个 case
    都复用的听审参照物

## 三、代码改动
- 更新：
  - `src/v5vc/teacher_first_vc_demo.py`
- 新增显式默认常量：
  - `DEFAULT_EXPLICIT_CLEAN_TARGET_REFERENCE_AUDIO_PATH`
- 当前逻辑：
  1. 若命令显式传
     `--target-reference-audio`
     则优先使用
  2. 否则优先使用
     `DEFAULT_EXPLICIT_CLEAN_TARGET_REFERENCE_AUDIO_PATH`
  3. 只有显式默认路径缺失时，
     才回退到
     calibration asset
     的旧逻辑

## 四、复跑

### compare bundle
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_compare_bundle.ps1 `
  -OutputDir tmp/teacher_first_audible_compare_bundle_cleanref_repaired_parallel `
  -Device cuda `
  -SkipFullPassVerify
```

### smoke bundle
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -OutputDir tmp/teacher_first_audible_smoke_bundle_cleanref_repaired_parallel `
  -Device cuda `
  -SkipFullPassVerify
```

## 五、复跑结果

### clean reference 已生效
- compare / smoke
  summary
  均显示：
  - `shared_target_reference.resolved_source_audio_path = data_convert/dataset_firefly_raw/chapter3_3_firefly_135.wav`

### compare bundle
- 输出：
  - `tmp/teacher_first_audible_compare_bundle_cleanref_repaired_parallel/`
- 结果：
  - `case_count = 2`
  - `variant_count = 2`
  - `variant_runs_succeeded = 4 / 4`
  - `variant_decoded_high_risk_count = 4`

### smoke bundle
- 输出：
  - `tmp/teacher_first_audible_smoke_bundle_cleanref_repaired_parallel/`
- 结果：
  - `case_count = 2`
  - `pipeline_succeeded = 2 / 2`
  - `decoded_high_risk_count = 2`

## 六、当前解释
- 这轮 clean-reference
  复跑的意义是：
  - 让听审不再被
    “参照物本身可能不够干净”
    这件事干扰
- 但它并没有反转核心现象：
  - 默认链路仍是 buzz
  - 当前 inference-only
    候选
    也没有在 repaired parallel
    输入上
    明确转正
- 所以在这一步之后，
  继续优先做：
  - source 输入修补
  - target reference
    再挑一条
  的收益会明显下降

## 七、下一步
1. 以后所有默认 audible
   smoke / compare
   都沿用当前 clean target reference
2. 不再把
   calibration asset
   的首条记录
   当作默认听审参照物
3. 当前实验线下一阶段
   更应进入：
   - decoder behavior
   - waveform head
   - objective permissiveness
     诊断

## 一句话结论
- clean target reference
  已正式提升为默认，
  听审参照物污染这个混淆项已基本去掉；
  若在这个前提下 decoded
  仍是 buzz，
  那下一步就不该再优先修前端输入，
  而应转入后端发声器主线诊断。
