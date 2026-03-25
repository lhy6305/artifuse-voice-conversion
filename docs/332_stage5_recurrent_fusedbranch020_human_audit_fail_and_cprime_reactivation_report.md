# 332. Stage5 `recurrent_fusedbranch020` 听审失败与 `C-prime / v2-core` 主线重启报告

## 结论
- 用户已完成对
  `331`
  中
  `recurrent_fusedbranch020`
  对比包的人工试听，
  主观结论是：
  - **仍不存在人声结构**
  - **仍是单声调 buzz**
  - **唯一可感知变化是音调比 baseline overfit72 更高**
- 这条反馈非常关键，
  因为它把当前 Stage5
  的又一类“看起来不同”的候选
  也正式判成了：
  - **没有脱离 buzz 解**
  - 只是把 buzz 的参数化形态改了
- 到这一步，
  当前主线应正式停止：
  - 继续围绕
    Stage5
    `paired overfit`
    做同类
    `waveform head / objective / recurrent / fusion-side`
    小结构迭代
- 当前最有价值的下一步，
  应恢复到此前已经拍板、
  但被后续实验打断的正式路线：
  - **`C-prime / v2-core contract`**

## 一、为什么这次失败比前几次更有决定性
- 当前 paired overfit
  已经连续排掉三类路线：
  1. `baseline overfit72`
     - 包络更贴
     - 但仍是定调 buzz
  2. `acttmpl005_delta6`
     - template 指标更好
     - 但听感与 baseline
       无可感知差异
  3. `recurrent_fusedbranch020`
     - 结构已经显著不同
     - 但听感仍无人声，
       只是音调整体更高
- 这三轮一起说明：
  - 当前问题不再像：
    - “再换一组 Stage5 局部结构”
  - 更像：
    - **当前 contract 本身就没把主干拉到有资格长人声的状态**

## 二、当前应如何解释 `recurrent_fusedbranch020` 的失败
- 它不是：
  - 完全没变化
- 用户已经明确听到：
  - 音调比 baseline 更高
- 但这不是我们要的变化，
  因为阶段目标是：
  - **先出现人声结构**
- 所以正确解释应是：
  - 这条线确实能改变输出形态
  - 但改变的是
    buzz 的工作点，
    不是从 buzz 变成 speech

## 三、为什么现在不该再继续做 Stage5 同类微调
- 当前仓库里，
  关于下一主线的设计判断，
  其实早就写过，
  只是后面为了快速验证
  paired 路线，
  又多做了几轮 Stage5
  最小 smoke：
  - `docs/280_teacher_first_buzz_recovery_route_options_report.md`
  - `docs/281_teacher_first_v2_cprime_reconstruction_assessment_and_handoff.md`
  - `docs/282_teacher_first_v2_core_acoustic_state_and_c3_boundary_design.md`
- 这些文档的共同结论是：
  - 真正推荐的主线不是继续扫
    Stage5 局部补丁，
  - 而是：
    - 补齐
      `v2-core`
      设计态 contract
    - 再在该 contract 下
      重训 no-res baseline

## 四、当前最有价值的下一步是什么

### 正式答案
- **重启 `C-prime / v2-core contract` 实施**

### 具体含义
1. 定义并落地：
   - `teacher_downstream_control_contract_v2`
2. 补齐
   `v2-core`
   字段：
   - `z_art`
   - `e_evt`
   - `f0_hz`
   - `vuv`
   - `aper`
   - `E`
   - `s_spk_target`
   - `s_geom_target`
   - `alpha`
3. 先不打开：
   - `r_res`
   - GAN / adversarial
   - 更大一版 waveform objective 重构
4. 用新 contract
   重建 Stage5 package，
   再重训
   `no-res baseline`

### 为什么这是现在最值钱的一步
- 因为当前已经基本证明：
  - 现有 proxy contract
    下，
    你无论怎么调
    Stage5
    本地结构，
    都还在
    buzz manifold
    里打转
- 先把 contract
  拉回设计态，
  才能回答更高价值的问题：
  - **Stage5 主干究竟是被 contract 限死了，
    还是 waveform route 本身更深层有问题**

## 五、下一任务建议
1. 不再继续发新的听审包。
2. 下一任务直接进入：
   - `teacher_downstream_control_contract_v2`
     字段与代码实现拆解
3. 其中第一发最小可执行任务应是：
   - 明确
     `f0_hz / vuv / aper / E`
     的生成链、
     数值口径、
     时间轴对齐方式
   - 并把它们接进
     scaffold / package builder

## 一句话结论
- `recurrent_fusedbranch020`
  也已被人工确认失败；
  当前 Stage5
  不应再继续做同类微调。
- 下一步最有价值的动作是：
  - **恢复并实施
    `C-prime / v2-core contract`**
  - 先把
    `f0_hz / vuv / aper / E`
    正式接回 Stage5 主干。
