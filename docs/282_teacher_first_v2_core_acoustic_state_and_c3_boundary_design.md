# 2026-03-24 teacher-first v2-core 声学状态与 C3 边界设计

## 结论
- 本文只收口三个已拍板设计点：
  1. `aper-v1`
     如何定义
  2. 源侧第一版
     如何做成
     **可复现字段生成链**
     而不是新研究模型
  3. `C-prime Phase C3`
     重训时
     为什么必须继续保持
     `no-res baseline only`
- 本文不是：
  - code patch
  - 训练执行记录
- 它的作用是：
  - 在开始
    `contract_v2`
    实施前，
    先把最容易发散的设计口径钉死

## 一、`aper-v1` 设计

### 1. 目标
- `aper`
  在 `v2-core`
  中必须成为正式字段，
  但第一版必须：
  - 语义稳定
  - 计算可复现
  - 与 Stage5
    训练时间轴严格对齐
- 当前不追求：
  - 物理真值
  - 频带级高保真建模
  - 复杂说话人风格表达

### 2. 正式定义
- 字段名：
  - `aper`
- 版本口径：
  - `aper-v1`
- 数值范围：
  - `[0, 1]`
- 语义：
  - `0`
    更周期
  - `1`
    更非周期

### 3. 时间分辨率
- `aper-v1`
  必须与
  Stage5 当前
  `frame_length / hop_length`
  严格对齐
- 不允许：
  - 另起一套更粗时间轴
  - 或在 contract 中
    再做隐式重采样

### 4. 形态选择
- 第一版只采用：
  - **单标量 per-frame `aper`**
- 当前明确不做：
  - 频带化 `aper`
  - 多维 noise descriptor
  - 更细 source excitation
    参数化

### 5. 生成思路
- `aper-v1`
  当前建议采用：
  - 基于
    `f0_hz + vuv + 能量分布`
    的确定性工程定义
- 一个可接受的第一版思路是：
  1. 对 voiced 帧，
     依据 `f0_hz`
     在频域上划分 harmonic 区域
  2. 计算：
     - non-harmonic energy
       占比
  3. 对 unvoiced 帧，
     令：
     - `aper = 1.0`
  4. 对结果做：
     - 裁剪到 `[0, 1]`
     - 轻微时域平滑
- 关键点不是
  “算法多先进”，
  而是：
  - 语义稳定
  - 可复现
  - 不再退化成
    换名后的
    `zero_cross_rate` proxy

### 6. 训练中的角色
- `aper-v1`
  只进入：
  - noise / aperiodic branch
- 它的职责是：
  - 辅助
    `e_evt`
    与
    `vuv`
    建模：
    - breath
    - frication
    - non-periodic energy
- 当前明确不让它：
  - 替代 `e_evt`
  - 替代 `vuv`
  - 承担 speaker-style
    或 style token
    语义

### 7. 当前边界
- `aper-v1`
  是工程定义字段，
  不是物理真值
- 当前第一版目标是：
  - 补齐
    `v2-core`
    contract
- 不是：
  - 彻底解决所有
    noise-side
    表达问题

## 二、源侧第一版：`source acoustic state extraction chain`

### 1. 总原则
- 第一版不把源侧定义成：
  - 一个新的学习型研究模型
- 第一版正式定位为：
  - **source acoustic state extraction chain**
- 目标是：
  - 稳定、可复现地产出
    `v2-core`
    需要的基础声学状态字段

### 2. 第一版必须产出的字段
- `f0_hz`
- `vuv`
- `aper`
- `E`

### 3. 第一版实现原则
- 优先采用：
  - 成熟现成方案
    + 确定性工程计算
- 当前不优先采用：
  - 自研 source-side
    新模型
  - source-side
    文本结构监督
  - source-side
    phone/manner alignment

### 4. 建议拆层

#### A. extractor-backend
- 负责真实字段生成
- 可由：
  - 成熟 F0 提取器
  - voiced 判定逻辑
  - `aper-v1`
    计算链
  - 能量计算链
    组成

#### B. contract-core adapter
- 把上游产物统一写入
  `teacher_downstream_control_contract_v2`
- 对下游保证：
  - 字段名稳定
  - 量纲稳定
  - 时间轴稳定

### 5. 字段建议

#### `f0_hz`
- 第一版来自：
  - 成熟提取器
- 当前目标：
  - contract 内有正式字段
  - 不是继续靠
    `voiced_proxy`
    间接近似

#### `vuv`
- 第一版建议：
  - 与 `f0_hz`
    同链路稳定导出
- 当前建议输出口径：
  - 连续概率
    优先于
    生硬 0/1
    判决
- contract 名称直接叫：
  - `vuv`

#### `E`
- 第一版统一成：
  - 与 Stage5
    frame/hop
    对齐的正式能量字段
- 当前建议：
  - 采用稳定的
    `log-energy`
    或
    `log-RMS`
    口径
- contract 中
  不再继续沿用：
  - `energy_proxy`

#### `aper`
- 采用：
  - `aper-v1`

### 6. 源侧第一版明确不做
- 不做：
  - source-side
    clause / punctuation
    监督
  - source-side
    文本对齐事件监督
  - source-side
    与 target-side
    对称镜像化
    的大工程

### 7. 当前成功标准
- 第一版源侧链路的成功标准不是：
  - 某个新模型指标多高
- 而是：
  1. `f0_hz / vuv / aper / E`
     能稳定落盘
  2. 字段定义明确
  3. 下游 scaffold /
     package /
     Stage5
     可直接消费

## 三、`C-prime Phase C3`：为什么必须继续保持 `no-res baseline only`

### 1. 目标
- `C3`
  的唯一核心问题应是：
  - 在
    `v2-core`
    contract
    下，
    `no-res`
    主干是否开始出现
    speech emergence

### 2. 当前必须保持不变的项
- 当前明确不打开：
  - `r_res`
  - GAN / adversarial
  - 更大规模 waveform objective
    重构
- 当前也不建议：
  - 同时重做
    user-line
    复杂运行逻辑

### 3. 原因
- 当前 Stage5
  已知同时存在两类大问题：
  1. contract
     偏离设计稿
  2. waveform objective
     容许
     `template-buzz + envelope-following`
     假解
- 如果在 `C3`
  同时改：
  - contract
  - `r_res`
  - adversarial
  - waveform objective
- 那后续无论结果变好还是变坏，
  都很难判断：
  - 到底是哪一层起了作用

### 4. 当前推荐的 C3 策略
- 只改：
  - `v2-core`
    contract /
    scaffold /
    package
- 尽量不改：
  - baseline
    训练 recipe
  - 主训练 loop
  - 验收方式
- 可以新增：
  - 更强诊断指标
  - 更清晰 summary
- 但不在 C3
  第一轮就引入
  新 loss 主项

### 5. C3 的成功/失败解释

#### 若结果明显变好
- 说明：
  - contract 语义修正
    很可能是主因

#### 若仍然主要是 buzz
- 说明：
  - contract 修正
    还不够
  - 下一步再进入
    `C4`
    去动：
    - waveform objective
    - waveform head

### 6. 当前边界
- `C3`
  的价值不是：
  - 直接承诺完全通过
- 更准确的写法是：
  - 它把系统拉回：
    **有资格被检验**
    的状态

## 四、对下一步实施的直接含义

### 下次开始时优先顺序
1. 定义
   `teacher_downstream_control_contract_v2`
2. 单独写清
   `aper-v1`
3. 设计
   `source acoustic state extraction chain`
   的字段与接口
4. 再进入：
   - scaffold
   - package
   - Stage5 no-res baseline
     的 C3 级改造

### 当前不建议跳步
- 不建议先做：
  - `r_res`
  - GAN
  - 大规模 loss 改造
- 不建议把第一版
  source-side
  路线，
  写成一个需要单独训练、
  单独评估的新模型项目

## 一句话结论
- `aper-v1`
  必须先窄化、定死、对齐时间轴；
  源侧第一版应被实现成
  可复现字段生成链，
  而不是新研究模型；
  `C-prime Phase C3`
  则必须继续保持
  `no-res baseline only`，
  以便把 contract 修正
  的作用单独隔离出来。
