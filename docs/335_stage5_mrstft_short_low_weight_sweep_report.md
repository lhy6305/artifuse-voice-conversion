# 335. Stage5 short-window MRSTFT 低权重 sweep 报告

## 结论
- 已按同一口径补跑
  short-window MRSTFT
  的低权重 sweep：
  - `0.05`
  - `0.1`
- 在这组严格可比的
  paired overfit24
  对照里，
  **`0.05` 是当前最合理的折中点**：
  - 相比 baseline，
    单分辨率
    `loss_stft`
    变好
  - `loss_waveform`
    也没有变坏，
    反而略好
  - 但
    `loss_rms_guard`
    和
    `decoded_to_target_rms_ratio`
    略退
- `0.1`
  与
  `0.2`
  虽然继续压低
  `loss_stft`，
  但对
  `loss_waveform`
  与稳定性轴
  的代价更明显，
  不适合作为当前默认候选。
- 因此当前更准确的阶段结论是：
  - short-window MRSTFT
    **不是应该直接废弃**
  - 但也**不应保留 `0.2`**
  - 若这条线还要继续，
    当前应只保留
    **`0.05`**
    作为最小候选，
    后续再决定是否值得做听感验证

## 说明：本轮不再用 `loss_total` 做跨实验主排序
- 因为
  baseline
  与
  MRSTFT
  的 objective 组成不同，
  `loss_total`
  已不再是可直接横比的共享指标。
- 所以本报告主要比较：
  - `loss_stft`
  - `loss_waveform`
  - `loss_rms_guard`
  - `decoded_to_target_rms_ratio`
  - 以及
    `loss_mrstft_short_256_512_1024`
    是否被真实压低

## 对照对象
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_activitygate000_baseline_round1_1/`
- MRSTFT 0.05：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort005_round1_1/`
- MRSTFT 0.1：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort010_round1_1/`
- MRSTFT 0.2：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort020_smoke_round1_2/`

## step24 validation 共享指标对照

### baseline `0.0`
- `loss_stft = 0.364725`
- `loss_waveform = 0.159988`
- `loss_rms_guard = 0.021712`
- `decoded_to_target_rms_ratio = 0.978607`
- `loss_mrstft_short_256_512_1024 = 0.0`

### MRSTFT `0.05`
- `loss_stft = 0.350943`
- `loss_waveform = 0.159745`
- `loss_rms_guard = 0.026847`
- `decoded_to_target_rms_ratio = 0.97361`
- `loss_mrstft_short_256_512_1024 = 0.34921`

### MRSTFT `0.1`
- `loss_stft = 0.349081`
- `loss_waveform = 0.162687`
- `loss_rms_guard = 0.013706`
- `decoded_to_target_rms_ratio = 1.001947`
- `loss_mrstft_short_256_512_1024 = 0.349835`

### MRSTFT `0.2`
- `loss_stft = 0.337852`
- `loss_waveform = 0.161479`
- `loss_rms_guard = 0.019621`
- `decoded_to_target_rms_ratio = 0.980703`
- `loss_mrstft_short_256_512_1024 = 0.336557`

## 如何解释
1. 三个权重都能把
   `loss_mrstft_short_256_512_1024`
   压到非零且较低，
   说明 short-window MRSTFT
   已稳定接通并参与优化。
2. 三个权重都能改善共享
   `loss_stft`，
   且权重越大，
   这条轴通常越低。
3. 但继续加权并没有带来一致更好的共享平衡：
   - `0.1`
     的
     `loss_waveform`
     明显差于 baseline
   - `0.2`
     也没有守住
     `loss_waveform`
   - `0.05`
     是唯一一个同时做到：
     - `loss_stft`
       变好
     - `loss_waveform`
       不变坏
4. 代价是：
   - `0.05`
     的
     `loss_rms_guard`
     和
     `decoded_to_target_rms_ratio`
     略退，
     但幅度相对温和

## 当前判断
- 若目标是：
  - “找一个暂时最值得保留的
     short-window MRSTFT
     权重”
- 当前答案是：
  - **`0.05`**
- 若目标是：
  - “今天是否已经足够证明
     short-window MRSTFT
     应该升为默认”
- 当前答案是：
  - **还不够。**

## 下一步建议
1. 不再继续扩做
   `0.1`
   和
   `0.2`
   这类更高权重。
2. 若要继续这条线，
   只保留
   `0.05`
   做下一步：
   - 最小 training-sync audio
     对照导出
   - 或 tiny human audit
3. 若当前主线优先级更高，
   则可以把 short-window MRSTFT
   暂时收口为：
   - plumbing 已补齐
   - 高权重不优
   - 仅
     `0.05`
     保留为候选备忘
