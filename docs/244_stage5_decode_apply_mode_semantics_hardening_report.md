# 2026-03-21 Stage5 decode apply-mode 语义硬化报告

## 结论
- 当前
  `postenv`
  的正式提升范围，
  继续保持为：
  - Stage5 decode / export
    默认口径
  - 终端用户线 decode
    默认口径
- 本轮没有改写训练语义，
  而是把训练路径里原本隐式吃到的旧口径，
  显式钉成：
  - `pre_overlap_add`
- 这样做的目的不是“让训练回退”，
  而是避免以后出现两种误读：
  - 误以为
    `postenv`
    默认提升已经自动扩散到所有低层重建调用
  - 或者反过来，
    因为低层还保留旧字面量默认，
    让训练/工具调用静默吃回旧行为却没人看出来

## 背景
- `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`
  已确认：
  - `step72__decode_gate_smooth3_postenv`
    focused human audit
    已完成
  - 当前 Stage5 decode-side 默认 apply mode
    已提升为
    `post_ola_envelope`
- 但本轮恢复实验线时又确认：
  - `src/v5vc/offline_vocoder_training.py`
    的低层函数
    `reconstruct_waveform_from_frames(...)`
    仍保留旧默认
    `pre_overlap_add`
  - 且训练损失路径此前没有显式传
    `frame_gain_apply_mode`

## 本轮代码动作

### 1. 新增训练侧显式常量
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
- 新增：
  - `DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE = "pre_overlap_add"`

### 2. 训练损失路径改为显式传参
- `compute_nores_vocoder_losses(...)`
  中，
  调用
  `reconstruct_waveform_from_frames(...)`
  时，
  当前会显式传：
  - `frame_gain_apply_mode = DEFAULT_TRAINING_RECONSTRUCTION_FRAME_GAIN_APPLY_MODE`

### 3. 训练 summary / metrics 现在会把该语义写出来
- 单步训练 summary
- 最小 loop summary
- dataset loop summary
- loss metrics

当前都会显式写出：
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 当前意义

### 1. 现在“训练仍沿旧重建口径”变成了显式事实
- 以前这件事存在于：
  - 低层函数默认值
  - 未显式传参的调用路径
- 现在它已经变成：
  - 训练常量
  - summary 可见字段

### 2. `postenv` 默认提升与训练语义现在边界更清楚
- 当前可以明确区分：
  - export / user runtime
    默认：
    `post_ola_envelope`
  - training reconstruction loss
    当前显式保持：
    `pre_overlap_add`

### 3. 这次改动不等于重新打开新实验
- 本轮没有：
  - 新 probe
  - 新听审
  - 新分支排名变更
- 只是把一处容易在多轮接班中被误读的默认语义，
  从“隐式”改成“显式”

## 验证
- 已执行：

```powershell
.\python.exe -m py_compile src\v5vc\offline_vocoder_training.py
```

- 结果：
  - exit code `0`

## 下一步建议
1. 若未来真的要讨论：
   - 训练路径是否也要切到
     `postenv`
   那应把它当成独立实验问题，
   不要借导出默认提升顺手带过去
2. 未来若新增直接调用
   `reconstruct_waveform_from_frames(...)`
   的工具链，
   也应显式传
   `frame_gain_apply_mode`，
   不要继续依赖隐式默认

## 一句话结论
- 当前 Stage5 已正式默认
  `postenv`，
  但训练路径并没有被偷偷一起改掉；
  本轮做的是把这个边界显式写进代码和 summary，
  让后续接班者不会再靠猜。
