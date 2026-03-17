# 186. Stage5 seeded GPU baseline96 边际收益复核报告

## 背景
- `docs/185_stage5_gpu_seed_reproducibility_and_long_horizon_baseline_report.md`
  已把 Stage5 正式停点
  推到:
  - full-split
  - seeded GPU
  - `48-step`
  - proxy baseline
- 当时的核心问题是:
  - `48-step`
    之后是否还值得继续拉长
  - 还是已经基本摸到
    当前 proxy objective
    的平台区

## 本轮目标
1. 基于同一 full-split package 池
   跑通 seeded GPU
   `96-step`
   baseline
2. 对照:
   - `24-step = 0.469644`
   - `48-step = 0.441292`
3. 判断当前 Stage5
   是仍应继续拉长 horizon，
   还是应转向
   decoder / waveform-STFT
   目标

## 实验命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline96_round1_1 --device cuda:0 --num-steps 96 --packages-per-step 8 --validation-interval 24 --checkpoint-interval 24 --sampler-mode shuffle --seed 20260317
```

## 结果
- dataset:
  - `592 train`
  - `66 validation`
- 总耗时:
  - `11.698783 sec`
- validation `loss_total`:
  - step24 = `0.469644`
  - step48 = `0.441292`
  - step72 = `0.435399`
  - step96 = `0.432645`
- best checkpoint:
  - `step96`
  - `loss_total = 0.432645`

## 对照判断

### 1. `48 -> 96` 仍然有收益
- 对比 `48-step`:
  - `0.441292 -> 0.432645`
  - 继续下降
  - `delta = -0.008647`
- 所以现在还不能写成:
  - horizon 已经完全摸顶

### 2. 但收益已经明显进入边际收窄
- 对比早期区间:
  - `24 -> 48`
    改善:
    - `0.469644 -> 0.441292`
    - `delta = -0.028352`
- 对比后期区间:
  - `48 -> 96`
    改善:
    - `0.441292 -> 0.432645`
    - `delta = -0.008647`
- 这说明:
  - 继续拉长 horizon
    仍然有价值
  - 但当前改善速度
    已经不像
    `24 -> 48`
    那么陡

### 3. 训练主线仍不需要退回 loader 争论
- 即使跑到:
  - `96-step`
  - 全 validation pass
  - checkpoint 落盘
- 总耗时
  也只有:
  - `11.698783 sec`
- 这仍然不支持
  把主线切回:
  - packed loader
  - cache 重构

## 当前阶段判断
- 现在更合理的写法是:
  - Stage5 full-split seeded GPU proxy baseline
    已推进到 `96-step`
  - validation 仍在继续下降
  - 但已进入边际收窄区
- 所以当前主线
  不该误判成:
  - 已经彻底平台化
- 也不该误判成:
  - 只要继续加步数
    还会保持同等斜率改进

## 当前边界
- 这里仍然只是:
  - spectral/gate proxy target
- 不是:
  - decoder baseline
  - waveform-STFT objective
  - final vocoder training

## 当前产物
- `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline96_round1_1`

## 下一步建议
1. 若继续沿当前 proxy objective
   深挖，
   下一步优先做:
   - `96-step`
     checkpoint review
   - 而不是立刻再粗暴翻倍
     到更长 horizon
2. 若希望再探一次更远停点，
   可做:
   - `144-step`
     或 `192-step`
     的低频 validation probe
3. 若更看重阶段切换效率，
   当前也已经具备理由
   开始设计:
   - decoder / waveform-STFT
     目标接入

## 一句话结论
- Stage5 在
  `96-step` seeded GPU baseline
  下仍把 validation
  从 `0.441292`
  压到 `0.432645`，
  说明当前 proxy baseline
  还没完全摸顶；
  但收益已明显进入
  边际收窄区，
  下一步更适合做
  checkpoint review
  或低频长程 probe，
  而不是把“继续加步数”
  误写成无限高收益主线。
