# 2026-03-24 Stage5 `contractv2_normfix` periodic-path high-band restraint 代码接线与 smoke 报告

## 结论
- 已完成一条新的更窄 periodic-path 频谱约束代码接线：
  - `periodic_waveform_high_band_excess_weight`
- 当前语义不是整段 STFT 对齐，
  而是：
  - 对 `periodic_waveform_frames`
    经 `periodic_gate`
    重建后的 periodic-only waveform，
    只惩罚
    `high_band_energy_ratio`
    高于 aligned target 的部分
- 已完成：
  - CLI 参数接线
  - train step / train loop / dataset loop / validation 透传
  - summary 指标落盘
  - `compileall`
  - 单步 `cpu` smoke
- 当前还**没有**新的量化优劣结论；
  这次只证明：
  - 代码通了
  - 参数通了
  - 指标通了

## 一、为什么这次改成 high-band restraint
- 最近两轮已经确认：
  - 全局 `stft_weight`
    会把当前
    `periodic_gate rms_floor=0.65`
    主线往回拉
  - local periodic `stft`
    也会出现同类 tradeoff
- 所以下一发不再做：
  - 整段频谱对齐
- 改做：
  - 更局部的
    periodic-path 高频能量 restraint

## 二、本轮代码改动
- `src/v5vc/offline_vocoder_training.py`
  - 新增：
    - `DEFAULT_PERIODIC_WAVEFORM_HIGH_BAND_HZ = 4000.0`
    - `compute_waveform_high_band_energy_ratio(...)`
    - `compute_waveform_high_band_energy_excess_loss(...)`
  - 新增 loss：
    - `loss_periodic_waveform_high_band_excess`
  - 新增 summary 指标：
    - `periodic_waveform_high_band_energy_ratio`
    - `aligned_waveform_high_band_energy_ratio`
- `src/v5vc/cli.py`
  - 新增：
    - `--periodic-waveform-high-band-excess-weight`
  - 已接入：
    - `run-offline-mvp-nores-vocoder-train-step`
    - `run-offline-mvp-nores-vocoder-training-loop`
    - `run-offline-mvp-nores-vocoder-dataset-training-loop`

## 三、当前 loss 语义
- 当前不是惩罚：
  - 全频段误差
- 也不是要求：
  - periodic-only waveform
    逐点复刻 target 频谱
- 当前只做：
  - `high_band_energy_ratio(predicted_periodic_only)`
    若高于
    `high_band_energy_ratio(aligned_target)`
    才产生损失
- 这更接近：
  - 高频能量 restraint
  而不是：
  - 新一轮局部 STFT 对齐

## 四、smoke 验证

### 1. 编译检查
- 已通过：
  - `.\python.exe -m compileall src/v5vc/cli.py src/v5vc/offline_vocoder_training.py`

### 2. 单步 smoke
- 命令入口：
  - `.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step`
- 使用 train package：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/packages/train/target__archive_firefly_1/train_targets/offline_mvp_nores_vocoder_train_targets.pt`
- 输出目录：
  - `tmp/nores_periodic_highband_smoke/`
- 本轮只开：
  - `--periodic-waveform-high-band-excess-weight 0.1`
  - `--use-predicted-activity-gate`
  - `--device cpu`
  - `--deterministic`

### 3. smoke 结果
- 命令已成功完成：
  - `loss_total = 0.914944`
  - `duration_sec = 5.379710`
- summary 已落出新字段：
  - `loss_weights.periodic_waveform_high_band_excess = 0.1`
  - `loss_metrics.loss_periodic_waveform_high_band_excess`
  - `loss_metrics.periodic_waveform_high_band_energy_ratio`
  - `loss_metrics.aligned_waveform_high_band_energy_ratio`
- 本次单步 smoke 上，
  新 loss 数值为：
  - `loss_periodic_waveform_high_band_excess = 0.0`
  - `periodic_waveform_high_band_energy_ratio = 0.0`
  - `aligned_waveform_high_band_energy_ratio = 0.0`

## 五、如何解读这次 smoke
1. 这次 smoke 的目标不是证明：
   - 新 loss 已经有效改善指标
2. 它证明的是：
   - CLI 参数已透传
   - loss 已进入训练图
   - summary 已能稳定记录新字段
3. 本次数值为 `0.0`
   不应直接解读成：
   - 参数没接上
4. 更准确的解释是：
   - 这个单包单步样本上，
     periodic-only waveform 的高频占比并没有高于 aligned target，
     所以 restraint 没有被触发

## 六、当前阶段判断
1. 当前最好主线仍然不变：
   - `periodic_gate rms_floor = 0.65`
2. 新增的只是：
   - 下一发更窄 periodic-path 频谱约束的代码入口
3. 因此当前还不能写成：
   - high-band restraint 已优于 baseline
4. 现在可以写成：
   - 下一轮实验不再受限于“代码没接上”

## 七、下一步建议
1. 直接在当前最好主线
   `periodic_gate rms_floor=0.65`
   上做一个最小 dataset-loop smoke：
   - `periodic_waveform_high_band_excess_weight = 0.02`
   - `0.05`
   - `0.1`
2. 首先观察：
   - `loss_periodic_waveform_high_band_excess`
     是否稳定非零
   - `periodic_waveform_high_band_energy_ratio`
     是否被压回
   - 同时
     `adjacent cosine / active_template / rms_ratio`
     是否比 local periodic STFT 更稳
3. 若这条线仍然表现成：
   - `waveform / stft`
     变好
   - 但
     `adjacent cosine / active_template / rms_ratio`
     回吐
   那就可以更有把握地封口：
   - “even narrower periodic spectral restraint”
     也不够

## 一句话结论
- periodic-path 的 high-band restraint 代码已经落地并通过 smoke；
  当前下一步不是再补接线，
  而是围绕
  `periodic_gate rms_floor=0.65`
  真正做一轮最小 dataset-level 量化验证。
