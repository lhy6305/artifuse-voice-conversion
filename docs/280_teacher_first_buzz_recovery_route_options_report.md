# 2026-03-24 teacher-first / Stage5 buzz 修复路线选项报告

## 结论
- 重新补读
  `initial_design.md`
  与
  `initial_design_judg.md`
  后，
  当前最关键的判断是：
  - 现在不应再把
    buzzing
    当成
    decode-side
    小参数问题
  - 也不应直接押注
    “再训久一点”
    就会自然长出语音
- 当前更准确的阶段判断应写成：
  1. 现有 Stage5
     训练路线
     已被多份 probe
     证实稳定停在
     `template-buzz + envelope-following`
     假解
  2. 当前 user-line
     又额外偏离了设计态 contract：
     - 缺
       `f0_hz`
     - 缺
       `r_res`
     - `vuv/aper/E`
       也仍只是 proxy 化语义
  3. 因此如果要继续以
     “解决 decoded 只剩 buzz”
     为目标，
     最可能有效的路线
     已经不是
     inference 小修，
     而是：
     - 训练目标修正
     - 或更进一步的
       Stage5 contract 修正

## 当前事实基线

### 1. 设计稿对当前阶段的硬要求
- `initial_design.md`
  已明确：
  - 无残差主干
    应先靠
    `z_art + e_evt + F0/vuv/aper/E`
    站住
  - `r_res`
    不是当前第一优先
  - 若主干本身站不住，
    后续残差只会掩盖失败

### 2. 当前代码与设计态的关键偏离
- `src/v5vc/offline_teacher_downstream_contract.py`
  当前明确把下列设计键
  标成缺失：
  - `f0_hz`
  - `r_res`
  - `final_vocoder_waveform`
- `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  当前 periodic branch
  只吃：
  - `z_art`
  - `voiced_proxy`
  - `energy_proxy`
  - `alpha`
  - `s_spk_target`
  - `s_geom_target`
- noise branch
  只吃：
  - `event_probs`
  - `aperiodicity_proxy`
  - `event_presence_proxy`
  - `energy_change_proxy`
  - `energy_proxy`
  - `alpha`
  - `s_spk_target`

### 3. 当前训练路线已被正式 probe 判定为假解稳定区
- `docs/257`
  已确认：
  - waveform head
    几乎输出固定模板
  - controls
    主要只在调
    包络和强弱
- `docs/258`
  已确认：
  - 这种 template collapse
    不是后期 checkpoint
    局部退化
  - 而是
    `step24 -> step72`
    整条路线都在
    同类假解里
- `docs/259`
  已确认：
  - 当前
    `waveform + single-resolution STFT + rms_guard`
    objective
    对 fixed-template 假解
    宽容
  - 甚至固定模板 counterexample
    aggregate 上
    还能拿到
    不高于 baseline
    的分数

### 4. 当前 user-line 不是单纯训练外微扰
- `docs/250/251/252/275/276`
  已共同确认：
  - buzzing
    不是主要由：
    - apply mode
    - predicted gate
    - 常量 conditioning
    - q01/q99 clip
    - 一阶 affine match
      造成
  - 当前 user-line
    更像是：
    - 设计态 contract
      缺关键语义
    - 且喂给
      一个本来就容易塌到
      template-buzz
      的 checkpoint

## 选项

### 方案 A：继续做 inference-side 热修，不改训练

#### 具体做法
- 继续在 user-line
  上扫：
  - normalization
  - gate
  - decode apply mode
  - family override
  - control clip / affine

#### 优点
- 改动小
- 不用重训
- 风险低

#### 缺点
- 现有事实已经基本否证
- 即便能略降
  高频占比，
  也没有证据说明
  能把
  template-buzz
  变成真实语音

#### 判断
- 不推荐作为主线

## 方案 B：保留当前 proxy contract，优先改 Stage5 objective / waveform head，再重训

#### 具体做法
- 不先补
  `f0_hz`
- 先承认当前 contract
  仍是 proxy baseline
- 在这条 baseline 上：
  - 强化 anti-template
    结构约束
  - 继续收紧
    waveform objective
  - 必要时限制
    waveform head
    直接输出自由度
- 然后重跑最小
  dataset smoke
  和 source-driven
  compare bundle

#### 优点
- 代码变动集中在
  Stage5
  训练侧
- 不改 teacher contract
  主语义
- 更快得到
  “当前 proxy 路线
  到底还有没有救”
  的答案

#### 缺点
- 仍然回避了
  设计稿里最核心的
  `F0/vuv/aper/E`
  直接条件
- 当前已有
  `active_template + delta`
  训练 smoke，
  只能证明：
  - anti-template 指标
    会变
  - 但尚未证明
    可听结果
    开始转正
- 即便 objective 变强，
  也可能仍受限于
  contract 语义缺口

#### 判断
- 可作为
  最小成本验证路线
- 但更像
  “先证明当前 proxy baseline
  是否彻底无救”
  的路线，
  不是最设计对齐的路线

## 方案 C：按设计稿升级 Stage5 contract 到 `F0/vuv/aper/E` 主线，再重训 no-res 基线

#### 具体做法
- 在 teacher-first /
  Stage5 contract
  中补一版
  `v2`
  语义：
  - `f0_hz`
  - `vuv`
  - `aper`
  - `E`
  - 保留
    `z_art`
    与
    `event_probs`
- scaffold
  也切到设计对齐输入，
  不再只靠
  `voiced_proxy / energy_proxy / aperiodicity_proxy`
  近似
- 基于新 contract
  重建 Stage5 package
  并重训
  no-res baseline
- 仍先不引
  `r_res`

#### 优点
- 最符合
  `initial_design.md`
  当前阶段要求
- 更有机会让
  periodic branch
  真学到
  周期结构，
  不再只靠
  gate + 能量
  去调模板
- 即便后续仍失败，
  也能更明确判断：
  - 是 contract 语义不够
  - 还是 waveform route
    本身有更深层问题

#### 缺点
- 这是明确的大改：
  - contract
  - scaffold
  - 训练包
  - 模型输入维度
  - checkpoint
    全要重来
- 当前 teacher
  没有现成
  `f0_hz`
  输出，
  需要补取值来源
  与稳定性口径
- 实施成本明显高于
  方案 B

#### 判断
- 这是当前
  最推荐的主线
- 因为它不只是
  “继续围着假解补丁”，
  而是在把 Stage5
  拉回设计稿要求的
  最低主干语义

## 方案 D：同时改 contract 与训练目标，直接做“大一版 Stage5 重构”

#### 具体做法
- 方案 C
  加上
  方案 B
  同时做
- 也就是：
  - 先补
    `F0/vuv/aper/E`
  - 再同时收紧
    anti-template /
    frame-structure
    objective
  - 必要时再改
    waveform head

#### 优点
- 一次性覆盖
  当前两类最强嫌疑：
  - contract 语义缺口
  - waveform objective 假解

#### 缺点
- 变量太多
- 一旦结果仍差，
  很难判断：
  - 是哪个改动起效
  - 是哪个改动失效
- 对接班和回归
  都不友好

#### 判断
- 当前不推荐直接作为第一步
- 更适合在
  方案 C
  或
  方案 B
  单独验证后
  再进入

## 推荐顺序

### 推荐主线
1. 首选：
   - 方案 C
2. 若你希望先用更小代价
   验证“当前 proxy 路线
   还有没有救”，
   可先：
   - 方案 B
3. 当前不建议：
   - 方案 A
   作为主线
4. 当前不建议一上来就：
   - 方案 D

## 我建议的具体执行口径

### 若选方案 C
- 先做：
  - `teacher_downstream_control_contract_v2`
    设计与代码落地
- 然后：
  - scaffold 升级
  - 最小 dataset smoke
  - 最小 source-driven
    compare bundle
- 当前阶段先不做：
  - `r_res`
  - GAN
  - 大规模联合重构

### 若选方案 B
- 先保持当前 contract
  不动
- 直接把训练目标
  收紧到：
  - 明确惩罚
    template collapse
  - 明确惩罚
    仅包络跟随
- 然后只做：
  - baseline / candidate
    最小重训 smoke
  - user-line
    compare bundle

## 我的建议
- 当前建议你拍板：
  - **方案 C**
- 理由：
  1. 这是唯一一条
     明确把 Stage5
     拉回设计稿主线的路线
  2. 当前证据已经足够说明：
     - 只做 inference
       小修不够
     - 只围绕当前 proxy contract
       补丁式修 objective，
       有可能继续在错误语义上内卷
  3. 即便最终仍需再改
     objective，
     先把
     `F0/vuv/aper/E`
     接回来
     也不会是浪费动作

## 一句话结论
- 当前若真要继续解决
  `decoded` 只剩 buzz，
  最合理的主线
  已经不是继续扫推理参数，
  而是：
  - 要么先验证
    “当前 proxy contract
    在更强 objective 下
    还有没有救”
  - 要么直接按设计稿，
    把 Stage5
    拉回
    `z_art + e_evt + F0/vuv/aper/E`
    的无残差主干路线；
  我更推荐后者。
