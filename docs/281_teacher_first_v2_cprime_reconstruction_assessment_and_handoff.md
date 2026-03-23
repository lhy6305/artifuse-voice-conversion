# 2026-03-24 teacher-first / Stage5 v2 C-prime 重构评估与交接文档

## 结论
- 本轮方案探讨已收口，
  当前正式拍板路线为：
  - `方案 C-prime`
- 这不是：
  - “最全版 C 一次做完”
- 而是：
  - **设计对齐**
  - **分阶段推进**
  - **避免变量爆炸**
    的工程约束版 C
- 当前下一轮默认不再重复讨论：
  - 要不要选 B
  - 要不要继续扫 inference 小修
  - 要不要一步打开 `r_res`
- 下次对话开始后，
  默认直接进入：
  - `teacher_downstream_control_contract_v2`
    与
    `v2-core`
    实施拆解

## 本轮评估输入
- 临时文档：
  - `1.md`
  - `2.md`
- 约束：
  - 只读，不修改
  - 由用户后续手动删除
- 联读基线：
  - `initial_design.md`
  - `initial_design_judg.md`
  - `docs/250-259`
  - `docs/275-280`

## 当前最终判断

### 1. 源侧基础发声状态必须补
- 当前正式采纳的判断是：
  - 源侧应补：
    - `f0_hz`
    - `vuv`
    - `aper`
    - `E`
- 但定位必须收紧为：
  - **contract 补齐工程**
  - 不是新研究线
- 当前明确不做：
  - 源侧文本结构监督镜像化
  - 源侧 phone/manner 对齐大工程
  - 源侧与目标侧完全对称的双边全监督体系

### 2. v2 字段必须分层
- 当前正式采纳：
  - `v2-core`
  - `v2-optional`
  - `v2-diagnostic`
    三层结构
- 当前本轮训练主线只强制吃：
  - `v2-core`
- 其中：
  - `r_res`
    明确保留在
    `v2-optional`
    不作为本轮 no-res baseline
    的训练通过条件

### 3. F0 第一版先用成熟方案
- 当前正式采纳：
  - `F0` 采用“两阶段策略”
- 第一阶段：
  - 优先成熟现成方案，
    先把 contract 补齐
- 第二阶段：
  - 等 `v2-core`
    主干已跨过
    speech emergence，
    再考虑专用化
- 当前推荐口径：
  - 离线 package / teacher
    链路优先采用成熟提取器
    作为第一版 baseline

### 4. `aper` 必须单独写死口径
- 本轮评估后，
  这条被提升为正式硬约束
- 当前正式判断：
  - `aper`
    是最容易
    “名义补齐、语义发虚”
    的字段
- 因此在开始代码重构前，
  必须先写清：
  - 数值范围
  - 时间分辨率
  - 第一版是否单标量
  - 训练里进入哪条 branch
  - 不承担哪些语义

### 5. `C-prime` 的价值不是“保证成功”
- 当前正式判断：
  - `C-prime`
    的价值是把 Stage5
    拉回
    **有资格被检验**
    的设计对齐状态
- 不能写成：
  - 补齐 `v2-core`
    后 buzz
    就一定消失
- 更准确的写法是：
  - 补齐 `v2-core`
    后，
    若仍有 buzz，
    才更有资格继续判断：
    - 是 waveform objective
      问题
    - 还是 waveform head
      问题

## 当前正式采纳的 C-prime 路线

### Phase C1
- 设计并定义：
  - `teacher_downstream_control_contract_v2`
- 明确：
  - `v2-core`
  - `v2-optional`
  - `v2-diagnostic`
    边界
- 单独写清：
  - `aper`
    口径

### Phase C2
- 接入稳定、可复现的
  `v2-core`
  字段生成链
- 当前重点不是：
  - 新模型创新
- 而是：
  - 让这些字段可稳定落盘、
    可进入 scaffold /
    package /
    Stage5 训练

### Phase C3
- 只在
  `v2-core`
  contract 下
  重训 Stage5 no-res baseline
- 当前明确不同时打开：
  - `r_res`
  - GAN / adversarial
  - 大规模 waveform objective
    联合重构

### Phase C4
- 只有在：
  - `v2-core`
    已补齐
  - no-res baseline
    已重训
  - source-driven demo
    仍主要是 buzz
  这三个条件同时成立后，
  才进入：
  - waveform objective /
    waveform head
    假解修正

## 当前采纳的 v2 分层

### v2-core
- `z_art`
- `e_evt`
- `f0_hz`
- `vuv`
- `aper`
- `E`
- `s_spk_target`
- `s_geom_target`
- `alpha`

### v2-optional
- `r_res`
- 更细 source-style /
  noise-side controls
- 未来 unified front-end
  高阶输出

### v2-diagnostic
- hidden / fused_hidden
- confidence
- debug stats
- probe sidecars

## 当前采纳的实施边界

### 本轮后续不做的
- 不继续扩
  inference-side
  小 tweak
- 不把 source-side
  声学状态建模
  升级成新研究线
- 不同时推进
  contract 重构
  和
  waveform objective
  大改
- 不在 no-res baseline
  重新站稳前
  打开 `r_res`

### 下次对话默认要做的
1. `teacher_downstream_control_contract_v2`
   字段草案
2. `aper`
   口径定义
3. `f0_hz / vuv / aper / E`
   生成链落点梳理
4. scaffold /
   package /
   Stage5 no-res baseline
   的 v2-core
   改造拆解

## 对下一轮的默认交接语句
- 下次开始时，
  默认假设：
  - 方案评估已经完成
  - `C-prime`
    已拍板
  - `1.md / 2.md`
    只是已读临时参考
    而非正式依赖文档
- 下一轮不再从：
  - “选 B 还是 C”
    开始
- 直接从：
  - `v2-core`
    contract 设计
    开始

## 一句话结论
- 当前方案探讨已经结束，
  正式路线确定为
  `C-prime`：
  先补齐
  `v2-core`
  的设计对齐主干，
  再用 no-res baseline
  重训去验证
  speech emergence；
  下次对话默认直接进入实施拆解，
  不再回到路线争论。
