# 2026-03-23 Stage5 no-res speech-emergence root-cause probe 首轮报告

## 结论
- 当前实验线的 `speech-emergence root cause` 已从“只有题目，没有正式入口”，推进到：
  - 有正式 CLI
  - 有首轮 probe 结果
  - 有可重复的固定输出目录
- 当前首轮 probe 不支持
  “模型完全没在用 `z_art`” 这一说法。
- 当前更接近的判断是：
  - 全局 conditioning
    是最强外层杠杆
  - `z_art`
    是最强内容侧杠杆
  - `event_probs`
    与 noise-side proxies
    也会改输出，
    但更像次级杠杆
  - 多数组控制在
    `frame_mean`
    下影响明显弱于
    `zero`
    下的影响，
    说明当前 route
    更像在吃
    “控制存在/总量”
    而不是稳定利用
    逐帧动态去形成语音结构
- 但这轮 probe
  还没有单独解释掉：
  - 为什么人耳听到的仍是
    buzzing / 非语音

先说人话：
- 现在已经能正式回答
  “哪些控制一动就变、哪些动了也几乎不变”。
- 但还不能直接说
  “根因已经锁死在某一个 family”。

## 本轮工程动作

### 1. 补齐正式 CLI
- 新命令：
  - `analyze-stage5-nores-speech-emergence`
- 文件：
  - `src/v5vc/cli.py`
- 作用：
  - 把已存在的
    `src/v5vc/stage5_speech_emergence_probe.py`
    正式接入 `manage.py`

### 2. 修复 probe 自身的 delta 计算 bug
- 文件：
  - `src/v5vc/stage5_speech_emergence_probe.py`
- 问题：
  - 首次接通后发现
    `waveform_mean_abs_delta_vs_baseline`
    对所有非 baseline 变体都错误地写成了 `0`
- 根因：
  - 计算 delta 时，
    非 baseline 变体没有传入自己的 decoded waveform，
    实际拿了 baseline waveform
- 修复后：
  - 每个变体都使用自己的 decoded waveform
    参与 `delta_vs_baseline`

## 本轮运行口径

### 1. 当前 probe 对齐的不是任意 checkpoint
- 对齐对象是：
  - 当前 milestone acceptance
    听审失败的正式 route
- 具体口径：
  - checkpoint:
    `best_validation = step72`
  - split:
    `validation`
  - sample_count:
    `12`
  - decode:
    predicted gate on
    + smooth3
    + `post_ola_envelope`

### 2. 本轮正式命令
```powershell
$env:PYTHONPATH = "src"
.\python.exe manage.py analyze-stage5-nores-speech-emergence `
  --output-dir reports/runtime/stage5_speech_emergence_root_cause_probe_round1_1 `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --split-name validation `
  --target-record-ids `
    target::chapter3_3_firefly_162 `
    target::chapter3_2_firefly_212 `
    target::chapter3_29_firefly_113 `
    target::chapter3_3_firefly_174 `
    target::chapter3_20_firefly_133 `
    target::chapter3_2_firefly_163 `
    target::chapter3_6_firefly_106 `
    target::chapter3_2_firefly_155 `
    target::chapter3_3_firefly_245 `
    target::chapter3_26_firefly_107 `
    target::chapter3_17_firefly_133 `
    target::chapter3_4_firefly_106 `
  --device cpu `
  --use-predicted-activity-gate `
  --predicted-activity-gate-floor 0.0 `
  --predicted-activity-gate-smoothing-frames 3 `
  --predicted-activity-gate-apply-mode post_ola_envelope
```

## 结果

### 1. baseline 本身并不表现成“高频塌穿”
- baseline aggregate:
  - `decoded_spectral_high_band_energy_ratio = 0.064479`
  - `decoded_spectral_centroid_hz = 3009.312256`
  - `decoded_to_aligned_rms_ratio = 0.937478`
- 这说明：
  - 当前整包的粗粒度频谱统计，
    不能直接复刻
    “人耳听到的是 buzzing”
    这件事

### 2. 最强杠杆是 global conditioning
- `conditioning_zero`
  aggregate:
  - `waveform_mean_abs_delta_vs_baseline = 0.080387`
  - `decoded_spectral_centroid_delta_hz_vs_baseline = +1774.204468`
  - `decoded_spectral_high_band_ratio_delta_vs_baseline = +0.212547`
  - `predicted_activity_mean_delta_vs_baseline = +0.264720`
- 这说明：
  - 当前输出非常依赖
    alpha / speaker / geom
    这层全局 conditioning

### 3. `z_art` 不是“没被用”
- `z_art_zero`
  aggregate:
  - `waveform_mean_abs_delta_vs_baseline = 0.032225`
  - `decoded_spectral_centroid_delta_hz_vs_baseline = +1665.743286`
  - `decoded_spectral_high_band_ratio_delta_vs_baseline = +0.139707`
  - `predicted_activity_mean_delta_vs_baseline = -0.000129`
- 这说明：
  - 去掉
    `z_art`
    会显著改变输出
  - 但这种变化不主要通过
    predicted activity
    均值反转来体现，
    更像是内容骨架和频谱形状本身被改写

### 4. `event_probs` 与 noise-side proxies 是次级但真实的杠杆
- `event_probs_zero`
  aggregate:
  - `waveform_mean_abs_delta_vs_baseline = 0.025215`
  - `decoded_spectral_centroid_delta_hz_vs_baseline = +519.153198`
  - `decoded_spectral_high_band_ratio_delta_vs_baseline = +0.050178`
  - `predicted_activity_mean_delta_vs_baseline = -0.127181`
- `noise_proxies_zero`
  aggregate:
  - `waveform_mean_abs_delta_vs_baseline = 0.024683`
  - `decoded_spectral_centroid_delta_hz_vs_baseline = +691.718445`
  - `decoded_spectral_high_band_ratio_delta_vs_baseline = +0.063224`
  - `predicted_activity_mean_delta_vs_baseline = -0.126877`
- 这说明：
  - noise-side
    控制也在被用
  - 但当前影响强度
    仍低于
    global conditioning
    与
    `z_art`

### 5. 大多数 family 的 “逐帧动态” 使用证据偏弱
- 代表性对照：
  - `event_probs_zero`
    `waveform delta = 0.025215`
  - `event_probs_frame_mean`
    `0.010583`
  - `noise_proxies_zero`
    `0.024683`
  - `noise_proxies_frame_mean`
    `0.023766`
  - `periodic_proxies_zero`
    `0.013467`
  - `periodic_proxies_frame_mean`
    `0.005885`
  - `z_art_zero`
    `0.032225`
  - `z_art_frame_mean`
    `0.014515`
- 当前更接近的解释是：
  - 多数控制 family
    在“完全去掉”时会明显改输出
  - 但在“只抹掉逐帧动态、保留均值”时，
    很多项变化明显缩小
  - 这更像：
    当前 route
    对控制的使用还偏 coarse / presence-level
  - 而不是稳定把这些动态控制
    用成可辨识语音结构

## 当前判断
- 当前首轮 probe
  支持：
  1. `conditioning`
     与
     `z_art`
     都是真杠杆
  2. `event_probs`
     与 noise-side proxies
     不是完全无效，
     但更像次级控制
  3. 当前 route
     对多数组控制的使用，
     还没有呈现出很强的
     “逐帧动态决定语音结构”
     证据
- 当前首轮 probe
  还不支持：
  - 直接把根因写死成某一个 family
  - 或直接宣布
    “已经解释完 buzzing”

## 下一步建议
1. 当前不回退去做：
   - checkpoint 排名
   - decode-side 小 tweak
   - milestone session
     穷举补打分
2. 下一轮若继续实验线，
   优先题应转向：
   - `conditioning / z_art / event_probs / proxy`
     的时间轨迹对照
   - 更细粒度的
     speech-structure
     指标，
     而不是只看整段频谱均值
3. 当前最需要核对的是：
   - 为什么粗粒度频谱统计看起来不坏，
     人耳却仍然稳定听成
     buzzing / 非语音

## 产物
- probe 输出目录：
  - `reports/runtime/stage5_speech_emergence_root_cause_probe_round1_1/`
- 主结果：
  - `stage5_speech_emergence_probe.json`
  - `stage5_speech_emergence_probe.md`

## 一句话结论
- 当前 Stage5 no-res
  的首轮 speech-emergence probe
  已经把问题从
  “没有正式入口”
  推进到
  “conditioning 最强、`z_art` 次强、event/proxy 次级，且多数 family 的动态使用证据偏弱”；
  但 buzzing 的最终根因
  还没有被这轮 coarse probe
  单独解释掉。
