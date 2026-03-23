# 2026-03-23 Stage5 waveform-objective collapse probe 报告

## 结论
- 当前实验线已经把
  “固定模板也能拿到低 waveform objective”
  这件事，
  从口头判断推进成：
  - 独立 probe 模块
  - 正式 CLI
  - 可重复运行结果
- 当前结果明确支持：
  - 现有
    `waveform=0.5 + stft=0.5 + rms_guard=0.2`
    这套 Stage5 waveform objective，
    不能强力拒绝
    fixed-template 假解
- 更强一点说：
  - 不只是某个
    “取自目标的一帧模板”
    能拿到低 objective
  - 连
    `纯正弦固定模板 + 目标帧 RMS 包络`
    都能在 aggregate 上
    打到比当前 baseline decode route
    更低的
    weighted waveform objective

先说人话：
- 现在可以正式说，
  当前 waveform loss
  不是在稳定奖励
  “更像语音的短时结构”。
- 它更像是在奖励：
  - 包络跟得像
  - 粗频谱别太离谱
  - 全局 RMS 别差太多
- 所以固定模板
  也有机会拿到不错分数。

## 本轮工程动作

### 1. 补齐独立 probe 模块
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 作用：
  - 对同一批 Stage5 package，
    比较：
    - 当前 baseline decode route
    - `oracle_active_frame_target_rms`
    - `oracle_sine_target_rms`
  - 并按当前 waveform objective
    重新计算：
    - `loss_waveform`
    - `loss_stft`
    - `loss_rms_guard`
    - `weighted_wave_objective`

### 2. 补齐正式 CLI
- 新命令：
  - `analyze-stage5-nores-waveform-objective-collapse`
- 文件：
  - `src/v5vc/cli.py`
- 当前默认 objective 权重：
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
- 这样做的目的不是：
  - 发明一个新评分
- 而是：
  - 直接复用当前实验线正在追的
    waveform objective 口径

## 本轮运行口径

### 1. 对齐对象
- checkpoint:
  - `best_validation = step72`
- split:
  - `validation`
- sample_count:
  - `12`
- decode baseline:
  - predicted gate on
  - `smooth3`
  - `post_ola_envelope`

### 2. 当前正式命令
```powershell
$env:PYTHONPATH = "src"
.\python.exe manage.py analyze-stage5-nores-waveform-objective-collapse `
  --output-dir reports/runtime/stage5_waveform_objective_collapse_probe_round1_1 `
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
  --predicted-activity-gate-apply-mode post_ola_envelope `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2
```

## 关键结果

### 1. 两个固定模板 counterexample 都比 baseline 更低分
- baseline:
  - `weighted_wave_objective = 0.150852`
- `oracle_active_frame_target_rms`:
  - `0.141467`
  - 相对 baseline
    `-0.009384`
- `oracle_sine_target_rms`:
  - `0.147455`
  - 相对 baseline
    `-0.003397`
- 这说明：
  - 当前 objective
    至少在这批正式样本上，
    没有把 fixed-template route
    压到 baseline 之上

### 2. 低分不是靠“更像语音结构”，
  而是靠 waveform/STFT 子项更低
- baseline:
  - `loss_waveform = 0.105494`
  - `loss_stft = 0.161646`
  - `loss_rms_guard = 0.086407`
- `oracle_active_frame_target_rms`:
  - `loss_waveform = 0.088810`
  - `loss_stft = 0.110583`
  - `loss_rms_guard = 0.208855`
- `oracle_sine_target_rms`:
  - `loss_waveform = 0.090315`
  - `loss_stft = 0.138861`
  - `loss_rms_guard = 0.164335`
- 这说明：
  - 两个 fixed-template 变体
    虽然 RMS guard
    都比 baseline 更差，
  - 但它们在
    waveform / STFT
    两项上的收益，
    足以把总 objective
    拉到更低

### 3. fixed-template 变体仍然明显停留在结构塌缩区间
- baseline:
  - `decoded_frame_template_cosine_mean = 0.994838`
- `oracle_active_frame_target_rms`:
  - `0.923083`
- `oracle_sine_target_rms`:
  - `0.925485`
- 对照：
  - aligned target
    仍约为
    `0.022486`
- 同时：
  - `oracle_active_frame_target_rms`
    的
    `decoded_frame_rms_to_aligned_frame_rms_corr = 0.998475`
  - `oracle_sine_target_rms`
    的
    `0.998668`
- 这说明：
  - 这两个 counterexample
    依然远远不是
    “真实语音短时结构”
  - 它们更接近：
    - 固定模板
    - 再跟随目标能量包络

### 4. 当前更准确的 objective-level 解释
- 结合
  `docs/257`
  与
  `docs/258`
  的 temporal-structure 结论，
  本轮可以把判断再收紧一层：
  - 当前 Stage5 waveform objective
    会奖励
    `template + envelope`
    这类假解
  - 它没有提供足够强的约束，
    去逼模型学出
    真实语音所需的
    短时结构多样性

## 当前判断
- 当前实验线已经不只是：
  - “waveform route
    看起来像 template-buzz”
- 而是：
  - 已经有 constructive counterexample
    直接证明：
    当前 objective
    对这类假解是宽容的
- 所以当前下一题更应写成：
  - 为什么
    `L1 + single-resolution log-STFT + RMS guard`
    仍允许
    fixed-template
    低分路线存在
- 当前不应回退去继续优先做：
  - checkpoint 排名
  - decode-side 小 tweak
  - control-family 小扫尾

## 产物
- probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 主结果：
  - `stage5_waveform_objective_collapse_probe.json`
  - `stage5_waveform_objective_collapse_probe.md`

## 一句话结论
- 当前 Stage5 实验线已经把
  “template-buzz 假解存在”
  推进到
  “当前 waveform objective
  连固定模板 counterexample
  都可能给出比 baseline 更低的分数”；
  因此下一题应优先转向
  objective / loss
  为什么没有惩罚掉
  这类假解。
