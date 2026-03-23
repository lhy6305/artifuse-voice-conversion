# 2026-03-23 Stage5 frame-structure candidate-loss probe 报告

## 结论
- 本轮继续沿
  `docs/259`
  与
  `docs/260`
  的
  waveform-objective
  主轴推进，
  目标不是直接换训练 loss，
  而是先回答：
  - 哪类 structure-sidecar
    至少会把
    baseline decode route
    排到 fixed-template oracle
    前面
- 当前结果是混合的，
  但已经出现一个值得跟进的新信号：
  - 静态 frame-shape / frame-logspec
    类指标，
    仍然更偏向 oracle
  - 但
    `loss_frame_delta_unit_rms_l1`
    已第一次把
    baseline
    排到两个 oracle 前面
- 更贴近人话的解释是：
  - 当前 baseline
    虽然短时模板仍极度塌缩，
  - 但它在
    “相邻帧怎么变化”
    这件事上，
    至少比完全固定模板
    更接近目标一点点

## 背景
- `docs/259`
  已确认：
  - 当前正式 waveform objective
    会放过
    fixed-template 假解
- `docs/260`
  已确认：
  - short-window MRSTFT
    和
    去包络 frame-shape L1
    也没有把 baseline
    拉回 oracle 之前
- 所以本轮继续补问：
  - 如果不再盯
    静态帧形状，
    而改看
    frame-to-frame transition，
    排序会不会开始变对

## 本轮补充的 candidate sidecar
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增：
  - `loss_frame_unit_rms_logspec_l1`
    - 每帧去均值、
      归一到 unit RMS 后，
      比较 frame log-spectrum
  - `loss_frame_delta_unit_rms_l1`
    - 先做 unit-RMS frame normalization，
      再比较相邻帧差分
  - `loss_frame_spectral_flux_l1`
    - 比较相邻帧 log-spectrum 差分
- 同时：
  - probe 输出里新增了
    `structure_sidecar_rankings`
    用来直接看每个 sidecar
    的排序方向

## 关键结果

### 1. 静态 frame-shape 还是更偏向 oracle
- `loss_frame_unit_rms_l1`
  aggregate:
  - `oracle_active_frame_target_rms = 1.071623`
  - `oracle_sine_target_rms = 1.073684`
  - `baseline_decode_route = 1.119374`
- `loss_frame_unit_rms_logspec_l1`
  aggregate:
  - `oracle_sine_target_rms = 0.588792`
  - `oracle_active_frame_target_rms = 0.629777`
  - `baseline_decode_route = 0.765419`
- 这说明：
  - 如果继续围绕：
    - 静态帧波形 shape
    - 静态帧频谱 shape
    去补 loss，
  - 很可能仍然会继续奖励
    某些 fixed-template oracle

### 2. 相邻帧变化 loss 第一次把 baseline 排到前面
- `loss_frame_delta_unit_rms_l1`
  aggregate:
  - `baseline_decode_route = 0.960329`
  - `oracle_sine_target_rms = 0.973493`
  - `oracle_active_frame_target_rms = 0.974862`
- 这说明：
  - baseline
    虽然在静态 frame-shape
    上依然很塌，
  - 但在
    frame-to-frame transition
    这件事上，
    已经比完全固定模板
    更接近 aligned target

### 3. 若把 `frame delta` 当 sidecar penalty，
  排序翻转门槛已经可量化
- 记：
  - 当前 baseline
    `weighted_wave_objective = 0.150852`
  - `oracle_sine_target_rms = 0.147455`
  - `oracle_active_frame_target_rms = 0.141467`
- 若定义新的 sidecar 评分：
  - `score = weighted_wave_objective + λ * loss_frame_delta_unit_rms_l1`
- 则当前按 aggregate 估算：
  - baseline
    压过
    `oracle_sine_target_rms`
    所需：
    - `λ >= 0.258052`
  - baseline
    压过
    `oracle_active_frame_target_rms`
    所需：
    - `λ >= 0.645772`
- 这说明：
  - `frame delta`
    不只是“方向可能对”
  - 而是已经能量化出：
    - 多大权重
      才能开始把
      fixed-template oracle
      压回去

### 4. spectral-flux 只有弱信号，
  还不能当主突破口
- `loss_frame_spectral_flux_l1`
  aggregate:
  - `oracle_sine_target_rms = 0.381680`
  - `baseline_decode_route = 0.381835`
  - `oracle_active_frame_target_rms = 0.385551`
- 这说明：
  - 频谱流方向
    并不是完全没信息
  - 但当前差距太小，
    还不足以单独支撑：
    - “先上 spectral-flux
      就行”

## 当前判断
- 当前最值得记住的新边界是：
  - 静态 frame-shape 类约束，
    仍容易和
    fixed-template oracle
    站到一边
  - 但 transition / delta
    类约束，
    开始出现
    对 baseline 更有利的排序
- 同时：
  - 这种排序优势
    已经不是纯定性描述，
  - 而是可以继续拿
    `λ ≈ 0.26 / 0.65`
    这类量级
    去做下一轮候选 objective
    设计参考
- 所以下一题更合理的方向应是：
  1. 继续优先围绕
     adjacent-frame transition
     构造候选 supervision / loss
  2. 而不是先押注：
     - 更静态的 frame shape
     - 更静态的 frame spectrum

## 对后续实验线的含义
- 当前并不等于：
  - `frame_delta_unit_rms_l1`
    已经可以直接进训练
- 当前更准确的含义是：
  - 如果继续做
    objective-level root cause
    诊断，
    优先级应开始从：
    - static frame resemblance
    转向：
    - transition / change pattern

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `loss_frame_unit_rms_logspec_l1`
  - `loss_frame_delta_unit_rms_l1`
  - `loss_frame_spectral_flux_l1`
  - `structure_sidecar_rankings`

## 一句话结论
- 当前实验线已经进一步把问题收紧成：
  - 静态 frame-shape 类 loss
    仍然容易偏向 fixed-template oracle；
    第一类真正开始把 baseline
    排到 oracle 前面的信号，
    来自
    adjacent-frame delta
    而不是静态帧相似度。
