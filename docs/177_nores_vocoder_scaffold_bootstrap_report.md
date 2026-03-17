# 177. no-residual vocoder scaffold bootstrap 报告

## 背景
- `docs/176_teacher_downstream_control_contract_report.md`
  已把 teacher-first
  下游输入合同
  固定下来
- 下一步若还停留在
  “只有 contract，
   没有消费者”，
  就会再次卡在
  纸面边界
- 所以本轮目标是:
  - 先把 Stage5
    无残差声码器的
    最小代码锚点
    落到仓库里

## 本轮目标
1. 新增一个
   consumer-side
   vocoder input scaffold
2. 在其上再新增一个
   no-residual source-filter
   vocoder scaffold
3. 用真实 contract
   做 dry-run，
   确认双分支前向 shape
   已成立

## 本轮代码落地
### 1. 新增 consumer-side vocoder input scaffold
- 新增:
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
- CLI:
  - `build-offline-mvp-teacher-vocoder-input-scaffold`

作用:
- 从
  `teacher_downstream_control_contract.pt`
  读取 teacher-first 输入
- 生成:
  - `periodic_branch_features`
  - `noise_branch_features`
- 同时显式保留:
  - 周期支路缺失 `f0_hz`
  - 噪声支路缺失 `r_res`

### 2. 新增 no-residual source-filter vocoder scaffold
- 新增:
  - `src/v5vc/offline_vocoder_scaffold.py`
- CLI:
  - `prepare-offline-mvp-nores-vocoder-scaffold`

当前 forward 输出:
- `periodic_hidden`
- `noise_hidden`
- `fused_hidden`
- `periodic_gate`
- `noise_gate`
- `harmonic_envelope`
- `noise_envelope`

说明:
- 这不是已训练声码器
- 也不是最终 waveform 合成器
- 它的意义是:
  - 把 Stage5
    无残差双分支代码入口
    先钉住

## smoke test
### 步骤 1. 先构建 consumer-side scaffold

```powershell
.\python.exe manage.py build-offline-mvp-teacher-vocoder-input-scaffold --contract reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/teacher_downstream_control_contract.pt --output-dir reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_smoke_chapter3_3_firefly_162
```

结果:
- `frame_count = 167`
- `periodic_branch_feature_dim = 35`
- `noise_branch_feature_dim = 29`

### 步骤 2. 再构建 no-residual vocoder scaffold

```powershell
.\python.exe manage.py prepare-offline-mvp-nores-vocoder-scaffold --input-scaffold reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_smoke_chapter3_3_firefly_162/teacher_vocoder_input_scaffold.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_scaffold_smoke_chapter3_3_firefly_162
```

结果:
- `periodic_hidden = [167, 64]`
- `noise_hidden = [167, 64]`
- `fused_hidden = [167, 64]`
- `periodic_gate = [167, 1]`
- `noise_gate = [167, 1]`
- `harmonic_envelope = [167, 32]`
- `noise_envelope = [167, 32]`

## 当前判断
- 现在 Stage5
  已不再是
  “完全没有代码入口”
- 当前仓库已经有:
  - teacher-first contract
  - consumer-side scaffold
  - no-residual vocoder scaffold

- 这意味着下一步
  可以真正开始补:
  - 声码器目标定义
  - 上采样 / 时域或频域解码
  - 训练入口

而不是继续停留在:
- 只有设计稿
- 没有代码落点

## 当前边界
- 当前仍没有:
  - waveform decoder
  - STFT / adversarial / feature-matching 训练
  - 最终音频导出
- 所以现在只能说:
  - Stage5 scaffold 已成立
- 不能说:
  - 无残差声码器已实现

## 下一步
1. 基于当前
   `offline_vocoder_scaffold.py`
   补最小训练合同
2. 明确:
   - 训练目标是频域重建
     还是直接时域重建
3. 在仍缺 `f0_hz / r_res`
   的前提下，
   先只推进:
   - no-residual baseline 路线
