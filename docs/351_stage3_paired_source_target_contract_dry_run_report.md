# 351. Stage3 paired source-target contract dry-run 报告

## 结论
- 第一版
  paired Stage3
  training-data dry-run
  已正式接通，
  并且已经把
  source input /
  target teacher
  的真实合同问题量化出来。
- 修完 source parity
  的 duration drift
  之后，
  现在剩下的 mismatch
  是真实的：
  - source 实际时长
    只有 target 的
    `0.909098 / 0.95239`
  - source waveform
    进 Student
    后得到的 frame 数：
    `657 / 660`
  - target teacher
    的 frame 数：
    `723 / 693`
  - 逐样本 delta：
    `-66 / -33`
- 这说明：
  - 现在不能直接把
    source waveform
    和
    target teacher frame labels
    当成天然逐帧对齐的训练对
  - 如果要继续 paired Stage3，
    必须先补
    source-target frame bridge
    或显式对齐层

## 一、本轮代码改动
- 更新：
  - `src/v5vc/streaming_student/training_data_entry.py`
  - `src/v5vc/streaming_student/__init__.py`
  - `src/v5vc/cli.py`
- 新增命令：
  - `prepare-streaming-student-paired-training-data`
- 当前行为：
  1. 读取：
     - source waveform
     - target teacher label
     - target timing sidecar
     - source semantic parity sidecar
  2. 组装 paired batch
  3. 跑一遍
     Stage3 scaffold
     dry-run
  4. 输出：
     - source/target 实际时长
     - pair spec 时长
     - 时长 drift
     - source parity 对 source 帧轴是否一致
     - source model frames
       对 target teacher frames
       的 delta

## 二、执行命令
- 已执行：
```powershell
.\python.exe manage.py prepare-streaming-student-paired-training-data `
  --output-dir reports/plans/streaming_student_paired_training_data_overfit_smoke_round1_1 `
  --batch-size 2
```

## 三、产物位置
- summary json：
  - `reports/plans/streaming_student_paired_training_data_overfit_smoke_round1_1/streaming_student_paired_training_data_plan.json`
- summary markdown：
  - `reports/plans/streaming_student_paired_training_data_overfit_smoke_round1_1/streaming_student_paired_training_data_plan.md`

## 四、关键结果

### 1. source parity 现在已经和真实 source 帧轴对齐
- `source_semantic_parity_sidecar_path`
  已正确 attach
- `source_parity_frame_delta_per_sample = [0, 0]`
- `source_parity_duration_metadata_drift_sec = [0.0, 0.0]`
- 说明：
  - source parity sidecar
    这条线
    现在不再是假对齐

### 2. 但 source input 和 target teacher 仍存在真实帧长差
- 当前实际时长：
  - source:
    `2.39 / 2.4`
  - target:
    `2.62898 / 2.519977`
- `source_to_target_duration_ratio = [0.909098, 0.95239]`
- 模型输出帧：
  - `model_frame_lengths = [657, 660]`
- target teacher 帧：
  - `teacher_frame_lengths = [723, 693]`
- `delta_per_sample = [-66, -33]`
- `model_to_teacher_frame_ratio = [0.908714, 0.952381]`

### 3. pair spec 的 source duration metadata 仍然是漂移状态
- `source_audio_duration_sec_pair_spec = [3.881224, 3.51873]`
- `source_audio_duration_sec_actual = [2.39, 2.4]`
- `source_duration_metadata_drift_sec = [1.491224, 1.11873]`
- 说明：
  - 现在 dry-run
    已把这个 drift
    直接写进 summary，
    后续不会再误把旧 spec
    当真

## 五、当前判断
- 当前 paired Stage3
  可以正式写死的事实有两条：
  1. source parity sidecar
     已修正并可用
  2. source waveform
     与
     target teacher
     仍不具备天然逐帧对齐关系
- 所以：
  - 下一步不应直接开
    paired Stage3
    training loop
  - 也不应把
    target teacher frames
    直接硬监督到
    source frame 轴上

## 六、下一步
1. 设计第一版
   `source-target frame bridge`
   或
   paired alignment contract
2. 在 bridge
   成立前，
   只把这条 paired dry-run
   当成：
   - 合同核查
   - 风险量化
   不当成可训练闭环
3. 后续若继续扩展 paired spec，
   必须同步校验：
   - 实际 wav 时长
   - pair spec duration metadata
   - parity sidecar
   的 source frame count
