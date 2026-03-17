# 188. Stage5 seeded GPU baseline192 低频长程 probe 报告

## 背景
- `docs/186_stage5_seeded_gpu_baseline96_marginal_gain_review_report.md`
  已确认:
  - `96-step`
    仍优于
    `48-step`
  - 但边际收益
    已明显收窄
- `docs/187_stage5_checkpoint_review_broad_based_gain_report.md`
  又进一步确认:
  - `96-step`
    的收益
    不是少数 package
    拉低均值
  - 而是 broad-based gain
- 这之后需要回答的
  新问题是:
  - 再往更远 horizon
    探一次，
    是否仍有非零收益
  - 以及这份收益
    是否还具有
    足够广的覆盖面

## 本轮目标
1. 在同一 full-split package 池上
   跑一次
   seeded GPU `192-step`
   低频长程 probe
2. 判断:
   - `96 -> 144`
   - `144 -> 192`
   的 marginal gain
3. 用 checkpoint review
   判断后段收益
   是否仍然广覆盖

## 实验命令

### A. baseline192

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline192_round1_1 --device cuda:0 --num-steps 192 --packages-per-step 8 --validation-interval 48 --checkpoint-interval 48 --sampler-mode shuffle --seed 20260317
```

### B. baseline192 checkpoint review

```powershell
.\python.exe manage.py review-offline-mvp-nores-vocoder-checkpoints --summary reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline192_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_baseline192_round1_1 --top-k 10
```

## 结果

### 1. checkpoint 级 validation 轨迹
- step48:
  - `0.441292`
- step96:
  - `0.432645`
  - 相对 step48:
    `delta = -0.008647`
- step144:
  - `0.428461`
  - 相对 step96:
    `delta = -0.004184`
- step192:
  - `0.425898`
  - 相对 step144:
    `delta = -0.002563`

### 2. runtime
- dataset:
  - `592 train`
  - `66 validation`
- 总耗时:
  - `8.366645 sec`
- best checkpoint:
  - `step192`
  - `loss_total = 0.425898`

## review 结果

### 1. `96 -> 144`
- improved:
  - `65 / 66`
- worsened:
  - `1 / 66`
- average delta:
  - `-0.004184`
- 说明:
  - 后段收益仍然明显以
    广覆盖改善为主，
    但已经不再是
    `66 / 66`
    的全量同步改善

### 2. `144 -> 192`
- improved:
  - `64 / 66`
- worsened:
  - `2 / 66`
- average delta:
  - `-0.002563`
- 轻微回退记录:
  - `target::chapter4_7_firefly_119`
    `0.424759 -> 0.425456`
  - `target::chapter3_22_firefly_114`
    `0.434350 -> 0.434752`
- 说明:
  - `192-step`
    仍然不是
    “只靠少数 package
     拖均值”
  - 但局部轻微回退
    已经开始出现，
    且边际收益继续缩小

### 3. `48 -> 192`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`
- average delta:
  - `-0.015395`
- 说明:
  - 从中程到当前长程，
    总体仍然是
    全 validation package
    广覆盖改善

## 当前判断

### 1. `192-step` 仍然有收益，但已经非常接近收敛边缘
- 继续对比:
  - `96 -> 144`
    `delta = -0.004184`
  - `144 -> 192`
    `delta = -0.002563`
- 这说明:
  - gain 还没归零
  - 但已经进入
    更窄的尾段收益区

### 2. 当前不该再把“继续翻倍步数”默认当主线
- 如果继续粗暴翻倍到
  更远 horizon，
  更可能得到的是:
  - 更小的 marginal gain
  - 更多需要解释的局部回退
- 而当前更值钱的动作
  已经变成:
  - checkpoint review
  - objective 切换准备

### 3. 当前最合理口径
- Stage5 full-split seeded GPU
  proxy baseline
  现在正式推进到:
  - `192-step`
- 其收益特征应写成:
  - still improving
  - still mostly broad-based
  - but already near diminishing-return tail

## 当前产物
- baseline192:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline192_round1_1`
- review192:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_baseline192_round1_1`

## 下一步建议
1. 默认不再继续把
   `384-step`
   之类更远 horizon
   直接升格为主线
2. 更合理的下一步是:
   - 基于当前 proxy scaffold
     开始准备
     decoder / waveform-STFT
     目标接入
3. 若必须再做一次
   训练向确认，
   也应优先做:
   - 更精细的 review
   - 或最小成本的对照实验
   而不是单纯继续翻倍

## 一句话结论
- Stage5 seeded GPU
  在 `192-step`
  仍把 validation
  从 `96-step` 的
  `0.432645`
  继续压到
  `0.425898`，
  且后段收益仍以
  `65 / 66`
  与 `64 / 66`
  的 package 级广覆盖改善为主；
  但局部轻微回退
  已经出现，
  边际收益也进一步收窄，
  因此当前更合理的主线
  是收束 brute-force horizon scaling，
  转向 objective 切换准备。
