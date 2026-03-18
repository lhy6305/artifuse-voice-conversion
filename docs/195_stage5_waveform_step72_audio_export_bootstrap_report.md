# 195. Stage5 waveform `step72` 音频导出 bootstrap 报告

## 背景
- `docs/194_stage5_waveform_checkpoint_selection_and_late_stop_policy_report.md`
  已把当前
  waveform route
  的默认工程晚停点
  固定为:
  - `stable late-stop = step72`
- 下一步需要把
  这个结论
  从“选点”
  推进到
  “可听验证”

## 本轮目标
1. 给 Stage5
   no-res waveform route
   补最小音频导出入口
2. 支持直接从
   checkpoint-selection
   payload 里
   取:
   - `stable_late_stop`
   - `best_validation`
   - `best_rms`
3. 用当前
   `step72`
   先导出一组
   validation 样本，
   作为后续人工听审入口

## 本轮代码落地

### 1. `src/v5vc/nores_vocoder_audio_export.py`
- 新增
  Stage5 no-res vocoder
  音频导出器
- 关键能力:
  - 从
    `checkpoint_selection.json`
    解析 checkpoint
  - 默认支持:
    - `stable_late_stop`
    - `best_validation`
    - `best_rms`
  - 对选中 package
    导出:
    - `aligned_target.wav`
    - `decoded.wav`
  - 同时记录
    每条样本的:
    - `loss_total`
    - `loss_stft`
    - `loss_rms_guard`
    - `decoded_to_target_rms_ratio`

### 2. `src/v5vc/cli.py`
- 新增命令:
  - `export-offline-mvp-nores-vocoder-audio`

## 导出命令

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_baseline96_deterministic_round1_1/nores_vocoder_checkpoint_selection.json --selection-target stable_late_stop --split-name validation --sample-count 6 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1
```

## 结果

### 1. 导出 checkpoint
- 解析得到:
  - `step72`
  - `loss_total = 0.625926`
  - `decoded_to_target_rms_ratio = 0.979730`

### 2. 导出样本
- 本轮导出:
  - `6`
    条 validation package
- 产物目录:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`

### 3. 导出记录
- `target::chapter3_3_firefly_162`
- `target::chapter3_22_firefly_114`
- `target::chapter3_3_firefly_213`
- `target::chapter3_3_firefly_122`
- `target::chapter3_4_firefly_109`
- `target::chapter3_4_firefly_106`

### 4. 样本级指标观察
- 当前导出样本里，
  `loss_total`
  约在:
  - `0.597543`
    到
    `0.659719`
- 但样本级
  `decoded_to_target_rms_ratio`
  分布更宽，
  本轮 6 条样本里约为:
  - `0.782090`
    到
    `1.283669`

## 当前判断

### 1. `step72` 现在已经不只是“纸面默认晚停点”，而是可直接进入听审的可用 checkpoint
- 这一步的价值在于:
  - 把 selector
    的输出
    真正接到
    WAV 导出
- 所以后面如果要做
  听审，
  已经不需要再
  手工拼装 checkpoint
  和 package

### 2. 平均 RMS 比例接近 1，不代表单条样本都已经贴近 1
- 虽然
  `step72`
  的全量 validation
  平均:
  - `decoded_to_target_rms_ratio = 0.979730`
- 但本轮导出的
  6 条样本里，
  仍能看到:
  - 明显偏低的
    `0.782090`
  - 明显偏高的
    `1.283669`
- 这说明:
  - 当前 guard
    的整体均值
    已经比较平衡
  - 但单样本层面
    幅度波动
    仍然值得人工确认

### 3. 当前更合理的下一步是“听审收束”，不是继续拉长 horizon
- 现在已经具备:
  - 默认晚停点
  - 选择器
  - 导出样本
- 所以下一步
  最值钱的是:
  - 听
  - 对比
  - 判断问题
    更偏:
    - 幅度
    - 频谱细节
    - 还是整体自然度

先说人话:
- 这一步就是把
  `step72`
  真的变成
  “可以拿来听”的东西。
- 现在你不用再从一堆
  checkpoint 里猜，
  也不用手工导出，
  直接去听
  `aligned_target.wav`
  和
  `decoded.wav`
  就行。

## 当前产物
- selector:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_baseline96_deterministic_round1_1`
- audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`

## 下一步建议
1. 直接对
   `step72`
   导出的
   `6`
   条 validation 样本
   做人工听审
2. 若听审发现
   主要问题集中在:
   - 幅度波动，
   优先继续做
   per-record RMS /
   loudness 侧分析
3. 若听审发现
   主要问题集中在:
   - 高频细节
   - 自然度
   - 瞬态
   则主线更应转向:
   - multi-resolution STFT
   - adversarial / feature-matching

## 一句话结论
- 当前 Stage5
  waveform route
  已经从
  “选出 `step72`”
  推进到
  “`step72` 可直接导出并进入听审”，
  且导出的样本已显示:
  - 全局平均 RMS
    虽然接近 1
  - 但单样本
    仍存在明显幅度波动；
  因此下一步最合理的是
  用这批导出样本做人工听审，
  而不是继续 brute-force
  拉长训练。
