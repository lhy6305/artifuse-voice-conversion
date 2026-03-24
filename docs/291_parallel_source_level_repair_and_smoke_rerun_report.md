# 2026-03-24 平行 source 电平修复、边界裁切与 smoke 复跑报告

## 结论
- 当前两条平行 source
  不是损坏静音文件。
- 真正问题是：
  - 有效语音电平极低
  - 前后带静段
  - 开头结尾可能混有瞬态
- 本轮已完成：
  - 原文件备份
  - 前后裁切
  - 峰值归一化
  - 简短淡入淡出
  - main-listening
    smoke 复跑
- 修复后，
  这两条默认平行 source
  可以继续保留为当前实验线的正式 main-listening 输入。

## 一、问题如何被更正
- 上一轮基于极低 RMS
  和主观近似静音，
  一度把：
  - `chapter3_17_firefly_107.wav`
  - `chapter3_17_firefly_132.wav`
  误判成：
  - “整段全静音”
- 用户随后用外部音频软件复核，
  确认它们并非坏文件，
  而是：
  - 音量过于微小
  - 且边界含有不干净的前后段

## 二、本轮修复策略

### 1. 备份
- 原文件备份到：
  - `tmp/parallel_source_repair_backup_20260324_104026/`

### 2. 边界检测
- 使用
  `10 ms`
  分帧 RMS
  找持续能量段
- 规则：
  - 阈值取
    `max_rms * 0.12`
  - 至少要求
    `80 ms`
    持续越阈
  - 前后各补
    `30 ms`
    padding

### 3. 电平修复
- 裁切后按峰值做归一化
  到约
  `0.89`
- 再加
  `5 ms`
  淡入淡出，
  防止新边界点击

## 三、修复前后统计

### `chapter3_17_firefly_107.wav`
- 修复前：
  - `duration = 3.881224s`
  - `rms = 0.00037839`
  - `peak = 0.002441`
- 修复动作：
  - `trim_start = 0.600000s`
  - `trim_end = 2.990000s`
  - `gain = 364.533`
- 修复后：
  - `duration = 2.390000s`
  - `rms = 0.17538661`
  - `peak = 0.889984`

### `chapter3_17_firefly_132.wav`
- 修复前：
  - `duration = 3.518730s`
  - `rms = 0.00030798`
  - `peak = 0.002136`
- 修复动作：
  - `trim_start = 0.750000s`
  - `trim_end = 3.150000s`
  - `gain = 416.609`
- 修复后：
  - `duration = 2.400000s`
  - `rms = 0.15504410`
  - `peak = 0.889984`

## 四、smoke 复跑

### 命令
```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -OutputDir tmp/teacher_first_audible_smoke_bundle_repaired_parallel_sources `
  -Device cuda `
  -SkipFullPassVerify
```

### 结果
- `case_count = 2`
- `pipeline_succeeded = 2 / 2`
- `positive_controls_ready = 2 / 2`
- `decoded_present = 2 / 2`
- 输出目录：
  - `tmp/teacher_first_audible_smoke_bundle_repaired_parallel_sources/`

### 关键观测
- `parallel107`
  - `decoded_audio_sec = 2.389116`
  - `decoded_waveform_rms = 0.122387`
  - `centroid = 5848.471`
  - `high_band = 0.343068`
- `parallel132`
  - `decoded_audio_sec = 2.400000`
  - `decoded_waveform_rms = 0.112753`
  - `centroid = 5842.337`
  - `high_band = 0.342594`

## 五、当前正确解释边界
- 这轮复跑后，
  平行 source
  已经不是：
  “极低到几乎听不见”
  的假输入
- 因此当前 smoke
  比之前更有信息量
- 但仍要保留一条解释边界：
  - 若某次
    near-silence
    或极低能量输入
    下 decoded
    仍有 buzz，
    这只能证明：
    系统在那类极端输入上
    可能不稳
  - 不能直接推出：
    正常语音输入
    也一定异常

## 六、下一步
1. 保留这两条修复后的
   平行 source
   作为当前默认
   main-listening
   smoke 输入
2. 继续基于：
   - `tmp/teacher_first_audible_smoke_bundle_repaired_parallel_sources/listening/`
   做主观核查
3. 若需要继续判断
   inference-only
   适配候选，
   再接上当前 compare bundle
   做并排试听

## 一句话结论
- 平行 source
  的问题已从
  “疑似静音坏文件”
  更正为
  “电平极低且边界不干净”；
  当前两条文件已完成裁切和归一化，
  并成功重跑 main-listening smoke。
