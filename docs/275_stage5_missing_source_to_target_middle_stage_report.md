# 2026-03-24 Stage5 当前 smoke 缺少真正 source-to-target 中间变换段报告

## 结论
- 当前我已经确认：
  之前这轮 Stage5
  `dataset_training_loop + audio_export`
  smoke
  并不是真正的
  source-to-target
  闭环
- 更准确地说：
  - 当前 bundle
    走的是
    target-derived teacher controls
    -> Stage5 no-res vocoder
    -> decoded
  - 不是：
    source audio
    -> teacher runtime
    -> target conditioning
    -> Stage5 no-res vocoder
    -> decoded
- 所以你刚才听的那些
  `offline_mvp_nores_vocoder_audio_export_*`
  bundle，
  无法回答
  “真实 source-to-target
  中间变换后
  还会不会 buzz”
  这个问题

先说人话：
- 这轮最大的发现不是
  export 丢了一两个参数
- 而是：
  我之前拿来做最小 smoke
  的那条 Stage5 训练/导出线，
  从数据包构建开始
  就没有把
  源说话人音频
  接进去

## 直接证据

### 1. dataset package builder 只读 target split
- 当前默认 split：
  - `target_train.jsonl`
  - `target_validation.jsonl`
- 可见于：
  - [cli.py](F:/proj_dev/tmp/workdir4/src/v5vc/cli.py)
  - [offline_mvp_nores_vocoder_dataset_index.json](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json)

### 2. package builder 把同一条 target audio 同时当作 teacher 输入和训练 target
- 代码位置：
  - [offline_vocoder_training.py](F:/proj_dev/tmp/workdir4/src/v5vc/offline_vocoder_training.py)
- 当前逻辑是：
  - `export_offline_mvp_teacher_downstream_contract(input_audio_path=audio_path, ...)`
  - `build_offline_mvp_nores_vocoder_training_package(target_audio_path=audio_path, ...)`
- 也就是：
  - teacher contract
    的输入音频
    就是 target 音频
  - 最终训练 target
    也还是同一条 target 音频

### 3. 实际 package 产物已坐实 source/target 是同一路径
- 实例：
  [teacher_vocoder_input_scaffold.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_2_firefly_212/scaffold/teacher_vocoder_input_scaffold.md)
  显示：
  - `source_audio_path = ...chapter3_2_firefly_212.wav`
- 同一实例：
  [offline_mvp_nores_vocoder_train_targets.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_2_firefly_212/train_targets/offline_mvp_nores_vocoder_train_targets.md)
  显示：
  - `target_audio_path = ...chapter3_2_firefly_212.wav`
  - `source_audio_path = ...chapter3_2_firefly_212.wav`
- 所以当前 Stage5 package
  本质上是：
  - target self-reconstruction
    package

### 4. teacher contract 也明确缺少关键中间语义
- 实例：
  [teacher_downstream_control_contract.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_2_firefly_212/contract/teacher_downstream_control_contract.md)
- 当前明确缺失：
  - `f0_hz`
  - `r_res`
  - `final_vocoder_waveform`
- 当前 scaffold
  只是在用：
  - `z_art`
  - `event_probs`
  - `energy_proxy`
  - `voiced_proxy`
  - `aperiodicity_proxy`
  等 proxy
  做 consumer-side adapter

## 我补做的运行级确认

### 1. 真正的 source-driven path 是存在的
- 当前仓库里
  已有单独命令：
  - `run-offline-mvp-teacher-first-vc-demo`
- 这条线
  才会走：
  - source input audio
  - teacher runtime
  - teacher contract
  - vocoder scaffold
  - Stage5 checkpoint
  - decoded wav

### 2. 我已用 smoke checkpoint 实际跑通两条 source-driven demo
- baseline smoke checkpoint：
  - [offline_mvp_teacher_first_vc_demo_baseline_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_baseline_smoke_round1_2)
- candidate smoke checkpoint：
  - [offline_mvp_teacher_first_vc_demo_active_template_delta_smoke_round1_2](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_active_template_delta_smoke_round1_2)
- 输入都是：
  - `data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav`

### 3. 真 source-driven path 也仍然是高风险 buzz
- 两条 summary
  都给出同一方向判断：
  - `Applicability Risk = high_risk`
  - `Decoded spectral behavior crosses the current high-risk buzzing heuristics`
- candidate 示例：
  [teacher_first_vc_demo.md](F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_first_vc_demo_active_template_delta_smoke_round1_2/teacher_first_vc_demo.md)
- 当前关键谱统计：
  - `centroid_hz = 8689.365707`
  - `high_band_energy_ratio = 0.633386`

## 当前更准确的判断
1. 是的，之前那批
   `offline_mvp_nores_vocoder_audio_export_*`
   试听包
   对“真实 source-to-target 是否还是 buzz”
   这个问题来说，
   确实缺了一整段
   中间变换链路
2. 但我补跑后的结果也说明：
   - 就算换成真正的
     source-driven path
   - 当前 smoke checkpoint
     仍然是
     高风险 buzz
3. 所以现在不能把问题
   简化成：
   - “只是导出包拿错了”
4. 更准确的写法是：
   - 之前的 bundle
     测错了路径
   - 而真正的路径
     现在也还没有通过

## 对下一步的直接含义
1. 后续如果要评估
   user-line / source-driven
   结果，
   不应再用：
   - `export-offline-mvp-nores-vocoder-audio`
   的 target package bundle
   代替
2. 应该改用：
   - `run-offline-mvp-teacher-first-vc-demo`
   或基于它的
   多输入 review bundle
3. 当前实验线若继续推进，
   更合理的下一棒是：
   - 给 source-driven demo
     做一个 baseline / candidate
     并排 review bundle
   - 而不是继续扩 target self-reconstruction bundle

## 一句话结论
- 当前确实存在“缺少真正 source-to-target 中间变换段”的测试口径问题；
  但我已经补跑了真正的 source-driven 路径，
  结果仍然是高风险 buzz，
  所以问题不只是试听包拿错，
  而是当前 Stage5 vocoder checkpoint
  本身还没有通过真实 user-line 输入。
