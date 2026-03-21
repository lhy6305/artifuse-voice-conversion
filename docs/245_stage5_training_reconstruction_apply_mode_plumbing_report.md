# 2026-03-21 Stage5 training reconstruction apply-mode 参数接线报告

## 结论
- 当前 Stage5 训练侧已经拥有正式参数：
  - `--reconstruction-frame-gain-apply-mode`
- 该参数已接到：
  - 单步 train-step
  - 最小 training loop
  - dataset training loop
- 当前默认仍保持：
  - `pre_overlap_add`
- 也就是说，
  这次补的是：
  - “训练 apply mode
    可正式立题”
- 不是：
  - “训练默认已经切到
    postenv”

## 背景
- `docs/244_stage5_decode_apply_mode_semantics_hardening_report.md`
  已把训练侧的隐式旧默认，
  收口成显式事实：
  - training reconstruction loss
    当前显式保持
    `pre_overlap_add`
- 但如果后续要真正比较：
  - 训练侧
    `pre_overlap_add`
    vs
    `post_ola_envelope`
- 只靠改源码常量不够，
  因为那会把：
  - 工程默认
  - 实验变量
  混在一起

## 本轮代码动作

### 1. 新增训练侧 normalize 入口
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
- 新增：
  - `normalize_training_reconstruction_frame_gain_apply_mode(...)`
- 当前支持：
  - `pre_overlap_add`
  - `post_ola_envelope`

### 2. 三条训练 CLI 已接入正式参数
- 文件：
  - `src/v5vc/cli.py`
- 当前新增参数的命令：
  - `run-offline-mvp-nores-vocoder-train-step`
  - `run-offline-mvp-nores-vocoder-training-loop`
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`

### 3. 参数已穿透到训练核心路径
- `run_offline_mvp_nores_vocoder_training_step(...)`
- `run_offline_mvp_nores_vocoder_training_loop(...)`
- `run_offline_mvp_nores_vocoder_dataset_training_loop(...)`
- `run_nores_vocoder_validation_pass(...)`
- `run_nores_vocoder_dataset_validation_pass(...)`
- `compute_nores_vocoder_losses(...)`

当前都能显式接收并传递：
- `reconstruction_frame_gain_apply_mode`

### 4. 训练 summary / loss metrics 已继续保持可见
- 单步 summary
- loop summary
- dataset loop summary
- loss metrics

当前都会显式写出：
- `reconstruction_frame_gain_apply_mode`

## 本轮验证

### 1. 语法与 CLI
- 已执行：
```powershell
.\python.exe -m py_compile src\v5vc\offline_vocoder_training.py src\v5vc\cli.py
```
- 结果：
  - exit code `0`

- 已执行：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step --help
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --help
```
- 结果：
  - 新参数均已出现在帮助文本中

### 2. 单步真实 smoke
- 命令：
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step `
  --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt `
  --output-dir tmp/stage5_training_applymode_postenv_smoke `
  --device cpu `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode post_ola_envelope
```

- 结果：
  - exit code `0`
  - `loss_total = 1.745658`
  - 输出：
    - `tmp/stage5_training_applymode_postenv_smoke/offline_mvp_nores_vocoder_train_step.pt`
    - `tmp/stage5_training_applymode_postenv_smoke/offline_mvp_nores_vocoder_train_step.json`
    - `tmp/stage5_training_applymode_postenv_smoke/offline_mvp_nores_vocoder_train_step.md`

- summary 核对：
  - `loss_weights.reconstruction_frame_gain_apply_mode = post_ola_envelope`
  - `train_step.loss_metrics.reconstruction_frame_gain_apply_mode = post_ola_envelope`

## 当前意义

### 1. 训练 apply mode 现在可以被独立实验化
- 后续若真要比较：
  - 训练沿
    `pre_overlap_add`
  - 还是训练也切到
    `postenv`
- 现在已经不需要再改源码默认，
  而可以直接作为命令参数做正式对照

### 2. 默认边界保持稳定
- 当前没有改：
  - export / user runtime
    默认 `postenv`
  - training
    默认 `pre_overlap_add`
- 所以当前主线结论没有被这次接线扰动

## 下一步建议
1. 如果后续实验线继续深入，
   可以正式设计：
   - 训练侧
     `pre_overlap_add`
     vs
     `post_ola_envelope`
     的最小对照实验
2. 在该实验真正开始前，
   继续把
   `pre_overlap_add`
   视为当前训练正式默认，
   不要把“参数已存在”
   误写成“默认已变更”

## 一句话结论
- 当前 Stage5 训练侧已经具备
  apply-mode
  的正式实验入口，
  但默认语义没有变；
  这轮完成的是
  “把未来实验变量接成正式参数”，
  不是直接改主线结论。
