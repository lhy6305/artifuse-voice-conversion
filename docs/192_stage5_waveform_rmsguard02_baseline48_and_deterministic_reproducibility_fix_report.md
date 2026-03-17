# 192. Stage5 waveform `rms_guard=0.2` baseline48 与确定性复现修正报告

## 背景
- `docs/190_stage5_waveform_rms_guard_tradeoff_report.md`
  已确认:
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
    是当前更平衡的
    Stage5 waveform bootstrap
    配方
- 当时正式停点
  仍只到:
  - `24-step`
- 所以下一步需要回答:
  - 这条配方继续拉到
    `48-step`
    是否仍有广覆盖收益
  - 以及
    “同 seed”
    是否已经足够代表
    严格可复现

## 本轮目标
1. 在现有
   waveform/STFT + RMS guard
   配方上
   跑通
   `48-step`
   baseline
2. 用 checkpoint review
   判断:
   - `12 -> 24`
   - `24 -> 36`
   - `36 -> 48`
   是否仍然是
   broad-based gain
3. 修正 Stage5
   当前只设 seed、
   但未显式提供
   strict deterministic mode
   的复现缺口

## 本轮代码落地

### 1. `src/v5vc/offline_vocoder_training.py`
- `set_training_seed`
  现在支持:
  - `deterministic`
- 当 CUDA 且
  `deterministic = true`
  时，新增:
  - `CUBLAS_WORKSPACE_CONFIG=:4096:8`
  - `torch.use_deterministic_algorithms(True, warn_only=True)`
  - `torch.backends.cudnn.deterministic = True`
  - `torch.backends.cudnn.benchmark = False`
- Stage5 三个训练入口
  summary 现在会记录:
  - `deterministic_algorithms`
  - `cudnn_deterministic`
  - `cudnn_benchmark`
  - `training.deterministic`

### 2. `src/v5vc/cli.py`
- 为以下入口新增:
  - `--deterministic`
- 覆盖:
  - `run-offline-mvp-nores-vocoder-train-step`
  - `run-offline-mvp-nores-vocoder-training-loop`
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`

## baseline48 实验

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1 --device cuda:0 --num-steps 48 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2
```

### 结果
- dataset:
  - `592 train`
  - `66 validation`
- 总耗时:
  - `70.135011 sec`
- best checkpoint:
  - `step48`
  - `loss_total = 0.655545`

### validation 轨迹
- step12:
  - `loss_total = 0.907863`
  - `loss_waveform = 0.124450`
  - `loss_stft = 0.547908`
  - `decoded_to_target_rms_ratio = 0.903182`
- step24:
  - `loss_total = 0.750610`
  - `loss_waveform = 0.126556`
  - `loss_stft = 0.355624`
  - `decoded_to_target_rms_ratio = 0.940165`
- step36:
  - `loss_total = 0.698990`
  - `loss_waveform = 0.125767`
  - `loss_stft = 0.295132`
  - `decoded_to_target_rms_ratio = 0.912635`
- step48:
  - `loss_total = 0.655545`
  - `loss_waveform = 0.131214`
  - `loss_stft = 0.238908`
  - `loss_rms_guard = 0.116006`
  - `decoded_waveform_rms = 0.119697`
  - `target_waveform_rms = 0.123402`
  - `decoded_to_target_rms_ratio = 0.994095`

## checkpoint review

### 命令

```powershell
.\python.exe manage.py review-offline-mvp-nores-vocoder-checkpoints --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_rmsguard02_baseline48_round1_1 --top-k 10
```

### 结果

#### 1. `12 -> 24`
- average delta:
  - `-0.157253`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

#### 2. `24 -> 36`
- average delta:
  - `-0.051620`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

#### 3. `36 -> 48`
- average delta:
  - `-0.043445`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

#### 4. `12 -> 48`
- average delta:
  - `-0.252318`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

## 确定性复现修正验证

### 触发原因
- 新跑的
  `baseline48`
  在 `step24`
  给出:
  - `loss_total = 0.750610`
- 而旧 `docs/190`
  记录的
  standalone `baseline24`
  为:
  - `0.749254`
- 差异很小，
  但说明:
  - 仅设置 seed
    还不能直接写成
    strict deterministic

### smoke 验证命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/tmp_nores_vocoder_waveform_deterministic_smoke_b --device cuda:0 --num-steps 2 --packages-per-step 2 --validation-interval 1 --checkpoint-interval 1 --sampler-mode shuffle --seed 20260318 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2
```

同命令再跑一次到:
- `tmp_nores_vocoder_waveform_deterministic_smoke_c`

### 验证结果
- 两次 run 的:
  - `training`
  - `validation_history`
    完全一致
- `step_history`
  不完全一致，
  仅因为:
  - `started_at`
  - `ended_at`
  - `duration_sec`
    这类时间字段不同
- best validation
  都是:
  - `1.604924`

## 当前判断

### 1. `rms_guard = 0.2` 的 waveform baseline 到 `48-step` 仍然明显受益
- 相比 `12-step`:
  - `0.907863 -> 0.655545`
- 相比 `24-step`:
  - `0.750610 -> 0.655545`
- 所以当前不能写成:
  - waveform baseline
    已在 `24-step`
    基本摸顶

### 2. 当前收益仍然是 broad-based gain
- 本轮最关键的
  review 结论是:
  - `12 -> 24`
    `66 / 66`
  - `24 -> 36`
    `66 / 66`
  - `36 -> 48`
    `66 / 66`
    全量改善
- 所以当前 gain
  不是少数 validation package
  拖低均值

### 3. RMS 已基本回到目标附近
- `step48`
  时:
  - `decoded_to_target_rms_ratio = 0.994095`
- 这比早期
  `12-step`
  的:
  - `0.903182`
  更接近目标
- 说明:
  - 当前 guard 配方
    不只是“没继续塌缩”，
  - 而是已经把
    平均振幅
    拉回到接近 target

### 4. 以后不能把“同 seed”直接等同于“严格可复现”
- 本轮新增的
  deterministic 修正
  主要意义是:
  - 给 Stage5
    一个明确可选的
    strict reproducibility mode
- 后续若需要:
  - 严格 checkpoint 对照
  - 精确复盘
  - 正式回归验证
  应优先开启:
  - `--deterministic`

先说人话:
- 这轮不是只把
  训练继续拉长了，
  还顺手把
  “seed 看起来有了，
   其实还不够严”
  这个工程坑补掉了。
- 现在更像样的口径是:
  - `rms_guard=0.2`
    到 `48-step`
    还在稳步变好，
  - 而且这份变好
    是全 validation
    一起在变好，
  - 同时以后如果要
    严格复盘，
    已经有了
    `--deterministic`
    入口。

## 当前产物
- baseline48:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline48_round1_1`
- review48:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_rmsguard02_baseline48_round1_1`

## 下一步建议
1. 若要继续沿
   当前 waveform 配方
   深挖，
   默认改用:
   - `--deterministic`
   再做:
   - `72-step`
     或 `96-step`
     long-horizon baseline
2. 若更看重
   阶段收束效率，
   当前也已具备理由
   开始规划:
   - 更强的
     multi-resolution STFT
   - 或后续
     adversarial / feature-matching
     objective
3. 暂时不建议
   把时间再花在:
   - 更重的
     RMS guard
   - 或没有 deterministic
     保护的
     严格对照实验

## 一句话结论
- Stage5 当前以
  `waveform=0.5 + stft=0.5 + rms_guard=0.2`
  跑到 `48-step`
  后，
  validation `loss_total`
  进一步降到
  `0.655545`，
  `decoded_to_target_rms_ratio`
  回到
  `0.994095`，
  且 `12/24/36/48`
  各 checkpoint 间都表现为
  `66 / 66`
  validation package
  全量改善；
  同时本轮补上了
  Stage5 的
  `--deterministic`
  与 CUDA 确定性配置，
  以后不再把
  “同 seed”
  误当成
  “严格可复现”。
