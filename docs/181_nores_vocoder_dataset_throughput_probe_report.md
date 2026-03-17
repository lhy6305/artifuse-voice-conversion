# 181. no-residual vocoder dataset throughput probe 报告

## 背景
- `docs/180_nores_vocoder_dataset_path_smoke_report.md`
  已确认:
  - Stage5 dataset path
    已成立
- 但当时还缺:
  - package 导出耗时统计
  - package 体积统计
  - 更大 subset
    的吞吐边界观察

## 本轮目标
1. 给 Stage5 dataset index
   补:
   - `timing`
   - `package_build_sec`
   - `package_size_bytes`
   - split summary
2. 跑两组 probe，
   分别看:
   - 短句 lower-bound
   - 较长样本 file-order 对照
3. 再用更大的 subset
   跑一次 dataset loop，
   确认训练侧在多 package 池上仍稳定

## 本轮代码落地

### 1. `offline_vocoder_training.py` 已补 dataset throughput 统计
- 现在 dataset index
  会正式记录:
  - `timing.started_at / ended_at / duration_sec`
  - 每条 package 的
    - `package_build_sec`
    - `package_size_bytes`
    - `package_status`
  - split 级 summary:
    - `total_audio_duration_sec`
    - `total_frame_count`
    - `total_package_size_bytes`
    - `avg_package_build_sec`
    - `avg_package_size_bytes`

### 2. markdown 也已同步显示这些字段
- 这样后续接班时
  不需要再单独扫文件系统
  或重新手算体积

## probe A: shortest-duration lower-bound

### 命令

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_round1_1 --max-train-records 8 --max-validation-records 2 --selection-mode shortest_duration --device cpu
```

### 结果
- index build:
  - `duration_sec = 0.852473`
- train summary:
  - `package_count = 8`
  - `total_audio_duration_sec = 4.567936`
  - `total_frame_count = 1242`
  - `total_package_size_bytes = 2927726`
  - `avg_package_build_sec = 0.077927`
  - `avg_package_size_bytes = 365965.75`
- validation summary:
  - `package_count = 2`
  - `total_audio_duration_sec = 1.588979`
  - `total_frame_count = 434`
  - `total_package_size_bytes = 998599`
  - `avg_package_build_sec = 0.091079`
- 总包体积:
  - `3926325 bytes`

### 当前解释
- 这组 probe
  说明:
  - 对极短目标样本，
    当前导出链已经足够轻
- 但它只能作为:
  - lower-bound throughput
- 不能直接当作:
  - full split 导出速度估计

## probe B: file-order 较长样本对照

### 命令

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1 --max-train-records 3 --max-validation-records 1 --selection-mode file_order --device cpu
```

### 结果
- index build:
  - `duration_sec = 1.977267`
- train summary:
  - `package_count = 3`
  - `total_audio_duration_sec = 44.111951`
  - `total_frame_count = 12153`
  - `total_package_size_bytes = 26342076`
  - `avg_package_build_sec = 0.628782`
  - `avg_package_size_bytes = 8780692.0`
- validation summary:
  - `package_count = 1`
  - `total_audio_duration_sec = 0.612993`
  - `total_frame_count = 167`
  - `total_package_size_bytes = 391145`
  - `avg_package_build_sec = 0.069947`
- 总包体积:
  - `26733221 bytes`

### 当前解释
- 一旦切到较长样本，
  package 体积和导出耗时
  都会明显抬升
- 这更像当前路径的:
  - 中等现实负载对照
- 但它仍不是:
  - full split 全量 probe

## dataset loop probe

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1 --num-steps 4 --packages-per-step 4 --validation-interval 1 --checkpoint-interval 2 --sampler-mode shuffle --seed 20260317
```

### 结果
- loop 总耗时:
  - `duration_sec = 1.417011`
- train `loss_total`:
  - `1.050081 -> 0.888035 -> 0.773256 -> 0.751396`
- validation `loss_total`:
  - `0.902686 -> 0.803836 -> 0.737672 -> 0.694789`
- best checkpoint:
  - `step4`
  - `loss_total = 0.694789`

## 当前判断

### 1. Stage5 dataset path 已有第一版 throughput 仪表盘
- 现在不仅知道:
  - 能不能导出
- 还知道:
  - 每包大概多大
  - 每包大概多久
  - 不同子集长度下
    开销差多少

### 2. 当前最关键的分界已经变清楚
- 短句 subset:
  - 很快
  - 更像 lower-bound
- 较长 file-order:
  - 体积和耗时立刻放大
- 所以当前真正的下一个工程问题
  不再是
  “dataset path 有没有”
- 而是:
  - 是否需要 package cache / packed loader
  - 以及 full split 导出前
    要不要先分桶

### 3. dataset loop 在更大 package 池上仍稳定
- `8 train + 2 validation`
  的 loop probe
  已显示:
  - train / validation
    都能继续下降
- 这说明:
  - Stage5 训练侧
    没有因为多 package 采样
    重新掉回单包假设

## 当前边界
- 当前 throughput probe
  仍是 capped subset，
  不是 full split
- 当前 loop
  仍是:
  - Python 级逐包加载
  - 不是 packed dataloader
- 当前 package 内容
  仍是:
  - proxy spectral/gate target
  - 不是最终 waveform decoder 目标

## 当前产物
- shortest-duration probe:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- file-order probe:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- dataset loop probe:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_probe_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`

## 下一步
1. 先做更像 full split
   的 package export 预算，
   决定:
   - 一次性全量导出
   - 还是分桶 / 分批导出
2. 若 package 体积继续放大，
   优先补:
   - package cache
   - packed loader
   - 或 frame bucket
3. throughput 边界清楚后，
   再决定 Stage5
   是继续沿 proxy target
   做 dataset-level 稳定化，
   还是切到 decoder / waveform-STFT 目标

## 一句话结论
- 本轮已经把 Stage5
  从“dataset path 能跑”
  推进到“dataset path 的耗时/体积边界也开始可量化”；
  当前最合理的下一步
  是继续做 full-split 预算与 package-loader 取舍，
  而不是直接跳到大规模正式训练口径。
