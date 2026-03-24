# 2026-03-24 Stage5 `contract_v2` consumer-side 分布错位诊断与最小热修报告

## 结论
- 当前已经可以把
  `contract_v2`
  首轮正式训练
  落后旧 baseline
  的主要问题，
  从“泛化怀疑”
  收敛成两个
  consumer-side
  实现问题：
  1. `f0_hz`
     以原始 `Hz`
     直接进入
     Stage5 periodic branch，
     输入尺度严重偏离旧 recipe
  2. `noise_gate_target = max(aper, event_presence_proxy)`
     与
     `unvoiced -> aper = 1`
     叠加后，
     把 noise gate
     推成近似常开
- 本轮已完成最小热修，
  且用真实样例重建
  scaffold / package
  后确认：
  分布已明显回到
  旧 `v1`
  附近。

## 一、问题如何被收敛出来

### 1. 现有正式状态
- 上一轮正式状态已是：
  - `contract_v2`
    full-split package
    导出完成
  - no-res baseline
    `72 step`
    正式训练完成
  - checkpoint review /
    selection /
    validation export /
    teacher-first smoke
    都已跑通
- 但数值结果仍落后于旧主线：
  - 旧
    `gate72 deterministic`
    `best_validation = 0.564671`
  - 原始
    `contract_v2`
    `best_validation = 0.658881`

### 2. 当前问题不再是 plumbing
- 因为以下项都已成立：
  - full export
  - full training
  - selection
  - source-to-target smoke
- 所以当前更值得问的不是：
  - “v2 有没有真正执行”
- 而是：
  - “为什么执行了以后，
     输入/目标分布反而把训练推偏”

## 二、数据级证据

### 1. 全 validation 聚合观察
- 直接读取已导出的
  validation package
  后，观察到：
  - `old_v1`
    `periodic_mean_abs ≈ 0.416032`
  - 原始
    `v2`
    `periodic_mean_abs ≈ 6.122333`
- 同时：
  - `old_v1`
    `noise_gate_mean ≈ 0.598460`
  - 原始
    `v2`
    `noise_gate_mean ≈ 0.813996`
  - `old_v1`
    `energy_target_mean ≈ 0.623226`
  - 原始
    `v2`
    `energy_target_mean ≈ 0.874094`

### 2. 直接原因
- 原始
  `v2`
  periodic branch
  直接消费：
  - `f0_hz`
  - `vuv`
  - `E`
- 其中
  `f0_hz`
  是原始 `Hz`
  量纲，
  当前 validation
  聚合里：
  - `f0_nonzero_mean ≈ 272.646747`
  - `f0_nonzero_p90_mean ≈ 410.430386`
- 这会把 periodic branch
  的输入尺度，
  从旧 `v1`
  近似 `0~1`
  的 proxy 区间，
  突然抬到
  几百 `Hz`
  级别。

### 3. `noise_gate_target` 被系统性抬高
- 原始实现里：
  - `source_acoustic_state_extraction`
    对 unvoiced
    直接写：
    `aper = 1`
  - `training_package`
    再写：
    `noise_gate_target = max(aper, event_presence_proxy)`
- 这意味着：
  - 只要一帧是 unvoiced，
    就几乎天然要求
    noise branch
    打到很高
- 结果就是：
  noise gate target
  相比旧 `v1`
  被整体抬高，
  很容易把
  predicted activity /
  reconstruction gate
  一起往“噪声始终活跃”
  的方向推。

## 三、本轮热修

### 1. 修正原则
- 不改：
  - `contract_v2`
    原始落盘字段
- 只改：
  - Stage5
    consumer-side
    的消费方式
- 这样可以保留：
  - `f0_hz / vuv / aper / E`
    作为正式字段
- 同时避免：
  - 训练支路
    直接吃到不合适量纲

### 2. scaffold 侧修正
- 文件：
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
- 当前改为：
  - `f0_hz`
    先做
    `log-norm`
    后再进入
    periodic branch
  - `E`
    先做
    bounded
    `log-RMS norm`
    后再进入
    periodic /
    noise branch
- 同时保留原始：
  - `f0_hz`
  - `E`
  在
  `available_controls`
  中继续可读，
  仅新增：
  - `f0_hz_log_norm`
  - `E_log_rms_norm`
  作为 consumer-side
  适配字段

### 3. training package 侧修正
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
- 当前改为：
  - `energy_proxy_target`
    直接使用
    `E_log_rms_norm`
  - `noise_gate_target`
    改成：
    `max(aper * E_log_rms_norm, event_presence_proxy)`
- 这样做的直接作用是：
  - 保留
    `aper`
    对噪声支路的指导意义
  - 但不再让
    低能量 unvoiced
    把 noise gate
    强行顶满

## 四、验证

### 1. 编译检查
- 已执行：
```powershell
.\python.exe -m compileall src/v5vc/offline_teacher_vocoder_input_scaffold.py src/v5vc/offline_vocoder_training.py
```
- 通过。

### 2. 8 条真实 validation 样例重建对比
- 使用现有
  `contract_v2`
  合同，
  重新按新代码生成：
  - scaffold
  - training package
- 对比结果如下：

#### 旧 `v1`
- `periodic_mean_abs = 0.426505`
- `noise_mean_abs = 0.408067`
- `periodic_gate_mean = 0.582659`
- `noise_gate_mean = 0.629192`
- `energy_target_mean = 0.684512`

#### 原始 `v2`
- `periodic_mean_abs = 5.987897`
- `noise_mean_abs = 0.430275`
- `periodic_gate_mean = 0.553365`
- `noise_gate_mean = 0.797156`
- `energy_target_mean = 0.889977`

#### 热修后 `v2`
- `periodic_mean_abs = 0.427962`
- `noise_mean_abs = 0.401214`
- `periodic_gate_mean = 0.553365`
- `noise_gate_mean = 0.633375`
- `energy_target_mean = 0.688073`

### 3. 当前解释
- 这组结果说明：
  - periodic branch
    的主尺度
    已从原始 `v2`
    的明显失衡，
    回到和旧 `v1`
    接近的区间
  - noise gate
    也已从原始 `v2`
    的高位常开趋势，
    回到和旧 `v1`
    接近的区间
- 因此这轮热修的意义是：
  - 把 `contract_v2`
    从
    “字段已补齐但消费错位”
    拉回到
    “字段已补齐且可被公平训练”
    的状态

## 五、当前边界
- 当前尚未重新跑：
  - full-split export
  - 正式 `72-step`
    no-res baseline
    重训
- 所以现在还不能写成：
  - 热修后
    `v2`
    已经胜过旧主线
- 当前能写清的只有：
  - 主要消费层分布错位
    已被明确定位
  - 对应最小修正
    已完成
  - 抽样重建结果
    已证明方向正确

## 六、下一步
1. 用新代码重导：
   - full-split
     `contract_v2`
     package
2. 沿用旧
   `72-step`
   recipe
   重训一轮，
   先判断数值是否回到
   旧 baseline
   附近
3. 若仍明显落后，
   再继续追：
   - `source acoustic state`
     字段质量
   - `aper-v1`
     口径
   - waveform objective
     耦合问题

## 一句话结论
- 当前
  `contract_v2`
  首轮落后旧 baseline
  的主要问题，
  已从“泛化怀疑”
  收敛成：
  - `f0/E`
    消费尺度失衡
  - `noise_gate_target`
    过度常开
- 对应的
  consumer-side
  最小热修
  已完成，
  且抽样重建已确认
  分布被拉回到
  接近旧 `v1`
  的区间。
