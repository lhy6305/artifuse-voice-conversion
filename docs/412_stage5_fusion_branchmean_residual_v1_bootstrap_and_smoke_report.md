# 2026-03-26 Stage5 `fusion_mode = branch_mean_residual_v1` bootstrap 与 smoke 报告

## 结论
- 我已把下一条更强的 fusion-path 结构候选落进代码并做通了最小真链路：
  - `fusion_mode = branch_mean_residual_v1`
- 这条候选的核心改动不是再叠一层 `fused_hidden` penalty，
  而是直接改写 fusion handoff：
  - `branch_mean_hidden`
    变成显式主通路
  - fusion 只学习
    `periodic_hidden / noise_hidden / (periodic_hidden - noise_hidden)`
    到 `fused_hidden`
    的残差项
- 当前已确认：
  - CLI 入口已接通
  - training summary 已写出
    `fusion_mode = branch_mean_residual_v1`
  - checkpoint state_dict
    可被导出 / probe 端自动反推回正确 fusion mode
  - export manifest
    也已写出
    `fusion_mode = branch_mean_residual_v1`
- 这一步的性质是：
  - 结构候选实现完成
  - plumbing smoke 通过
  - 还不是质量结论

## 一、动机
- 到 `docs/411`
  为止，
  当前 corrected native-teacher 主线上，
  现有 fusion-side `loss`
  家族已经可以视作封口：
  - `fused_hidden_template + fused_hidden_delta`
  - `fused_hidden_branch_mean_weight = 0.25`
- 同时 gate-off decoder-structure probe
  继续明确指出：
  - 主坍缩仍在
    `fusion -> fused_hidden`
  - 不是 export gate 开关，
    也不是 waveform decoder 单点
- 因而下一步不能再是同层 penalty sweep，
  而必须升级为更强的
  `fusion-path structural`
  改路

## 二、实现内容
- 文件：
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/stage5_waveform_decoder_structure_probe.py`
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 新增结构：
  - `fusion_mode = plain`
  - `fusion_mode = branch_mean_residual_v1`
- `branch_mean_residual_v1`
  的 forward 语义：
  - `branch_mean_hidden = 0.5 * (periodic_hidden + noise_hidden)`
  - `branch_difference_hidden = periodic_hidden - noise_hidden`
  - `fusion_residual_hidden`
    由
    `cat(periodic_hidden, noise_hidden, branch_difference_hidden)`
    经过小 MLP 得到
  - `fused_hidden = branch_mean_hidden + fusion_residual_hidden`
- 这样做的目的不是“把 branch_mean 硬喂给 decoder”，
  而是：
  - 把 branch-side dynamics
    提升为 fusion 的默认主底座
  - 同时保留残差自由度，
    避免退回纯固定 `mix_alpha`
    或纯 penalty 方案

## 三、最小 smoke

### 1. 训练
- 命令口径：
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`
  - dataset index：
    `tmp/stage5_dataset_parallel_smoke/offline_mvp_nores_vocoder_dataset_index.json`
  - `num_steps = 1`
  - `packages_per_step = 1`
  - `device = cpu`
  - `fusion_mode = branch_mean_residual_v1`
- 训练目录：
  - `tmp/stage5_fusion_branchmean_residual_smoke_round1_1/`

### 2. selector
- 目录：
  - `tmp/stage5_fusion_branchmean_residual_smoke_selection_round1_1/nores_vocoder_checkpoint_selection.json`
- 结果：
  - `best_validation_checkpoint.step = 1`
  - `loss_total = 1.761581`

### 3. 导出
- 目录：
  - `tmp/stage5_fusion_branchmean_residual_smoke_export_round1_1/nores_vocoder_audio_export.json`
- 当前 tiny validation 只有 1 条，
  `buzz gate`
  给出：
  - `record_count = 1`
  - `auto_reject_count = 1`
- 这一步不用于判断结构好坏，
  只用于确认：
  - checkpoint 反推模型结构
  - export 端重建 waveform
  - manifest 写回 fusion mode
  三件事都已成立

## 四、链路核验
- training summary：
  - `forward_path.fusion_mode = branch_mean_residual_v1`
  - `model.fusion_mode = branch_mean_residual_v1`
- export summary：
  - `waveform_decode.fusion_mode = branch_mean_residual_v1`
- 因而当前不是
  “只在训练入口有参数、实际导出端还不知道结构变了”

## 五、当前阶段判断
1. 当前更强的 fusion-path 候选已经具备：
   - 代码实现
   - CLI 入口
   - summary / export 反推
   - 最小真 smoke
2. 这意味着下一步可以直接进入：
   - corrected native-teacher fullsplit24 fail-fast
   - 不再需要先做额外 plumbing 接线
3. 当前最合理的下一步不是：
   - 再补一个 `fused_hidden` 小 penalty
   - 再扫一个 `branch_mean_weight`
   - 再回到 decoder-only patch
4. 而是：
   - 直接拿
     `fusion_mode = branch_mean_residual_v1`
     跑真实 `24-step -> checkpoint selection -> validation3 decoded.wav`
     的 fail-fast

## 一句话结论
- `fusion_mode = branch_mean_residual_v1`
  这条更强的 fusion-path 结构候选已经实现完成并通过最小真链路，
  下一步可以直接上 corrected native-teacher fullsplit24 fail-fast。
