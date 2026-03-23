# 2026-03-23 Stage5 waveform-objective sidecar diagnostic 报告

## 结论
- 在
  `docs/259`
  已确认
  fixed-template counterexample
  可以拿到不高于 baseline 的
  waveform objective
  之后，
  本轮继续补看两个
  structure-sidecar：
  - `loss_mrstft_short_256_512_1024`
  - `loss_frame_unit_rms_l1`
- 当前结果显示：
  - 这两个 sidecar
    也都没有把
    `baseline_decode_route`
    排到
    fixed-template
    counterexample
    前面
- 更准确的人话是：
  - 当前问题已经不只是
    “single-resolution STFT
    太弱”
  - 而是：
    - 当前 `step72` baseline
      本身就比这两个
      fixed-template oracle
      更接近结构塌缩端

## 背景
- `docs/259_stage5_waveform_objective_collapse_probe_report.md`
  已确认：
  - `oracle_active_frame_target_rms`
    和
    `oracle_sine_target_rms`
    的
    `weighted_wave_objective`
    都低于
    baseline decode route
- 但当时仍有一个可能误判：
  - 会不会只是
    当前 objective
    太依赖：
    - 单一 STFT 尺度
    - 包络主导的 raw waveform L1
  - 所以只要换成：
    - 更短窗的 MRSTFT
    - 去包络后的 frame-shape loss
    就能自然把排序扳回来

## 本轮补充

### 1. 新增 sidecar 指标
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增：
  - `loss_mrstft_short_256_512_1024`
    - 以
      `256 / 512 / 1024`
      三个窗长、
      `hop = frame_length / 4`
      的 log-STFT 平均值
      作为短窗 MRSTFT 诊断
  - `loss_frame_unit_rms_l1`
    - 先对每帧：
      - 去均值
      - 归一到 unit RMS
    - 再做 frame-level L1
    - 目的不是替代正式 loss，
      而是看
      “不让包络主导以后，
      短时 shape mismatch
      会不会更清楚”

### 2. 运行方式
- 沿用
  `docs/259`
  的同一条命令、
  同一批
  `validation12`
  记录、
  同一
  `step72 + smooth3 + post_ola_envelope`
  口径，
  不改样本，
  只补 sidecar 输出

## 关键结果

### 1. 短窗 MRSTFT 没有把 baseline 拉回更优
- `loss_mrstft_short_256_512_1024`
  aggregate:
  - `oracle_active_frame_target_rms = 0.109326`
  - `oracle_sine_target_rms = 0.135768`
  - `baseline_decode_route = 0.162566`
- 这说明：
  - 即便把 STFT
    从单窗补到
    `256 / 512 / 1024`
    三个尺度，
  - 当前 baseline
    仍然比两个 fixed-template oracle
    更差

### 2. 去包络后的 frame-shape L1 也没有把 baseline 拉回更优
- `loss_frame_unit_rms_l1`
  aggregate:
  - `oracle_active_frame_target_rms = 1.071623`
  - `oracle_sine_target_rms = 1.073684`
  - `baseline_decode_route = 1.119374`
- 这说明：
  - 就算把每帧：
    - 去均值
    - 去 RMS 振幅
  - baseline
    仍然没有比 fixed-template oracle
    更接近 aligned target

### 3. 这不是“oracle 更像语音”，
  而是 baseline 自己更塌
- baseline:
  - `decoded_frame_template_cosine_mean = 0.994838`
- `oracle_active_frame_target_rms`:
  - `0.923083`
- `oracle_sine_target_rms`:
  - `0.925485`
- 对照：
  - aligned target
    约为
    `0.022486`
- 这说明：
  - 两个 oracle
    当然仍然远离真实语音结构
  - 但 baseline
    其实比它们还更接近
    “固定模板极限”

## 当前判断
- 当前最值得避免的误判是：
  - “把 single-resolution STFT
    换成短窗 MRSTFT，
    问题大概就会自己消失”
- 本轮结果更支持：
  - 当前 baseline
    的结构塌缩程度
    本身就非常重
  - 所以简单把
    current STFT
    换成短窗 MRSTFT，
    或简单补一个
    去包络 frame L1，
    不足以单独解释成
    最小修复路径
- 当前更合理的下一题是：
  1. 明确需要的
     不是“稍微更灵敏一点的
     waveform loss”
  2. 而是：
     - 更直接针对
       speech-structure emergence
       的约束
     - 或更接近目标 frame structure
       的 supervision / target 设计

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `loss_mrstft_short_256_512_1024`
  - `loss_frame_unit_rms_l1`

## 一句话结论
- 当前实验线已经进一步确认：
  - 问题不是
    “single-resolution STFT
    稍微太弱”
  - 而是当前
    `step72` baseline
    本身就比两个
    fixed-template oracle
    更接近结构塌缩端；
    因此下一步不应把希望押在
    “简单换成短窗 MRSTFT”
    这种轻量 objective 替换上。
