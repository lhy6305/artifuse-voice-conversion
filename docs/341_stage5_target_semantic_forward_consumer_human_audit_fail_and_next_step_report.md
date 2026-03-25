# 341. Stage5 target-side semantic forward consumer 听审失败与下一步评估

## 结论
- 用户已完成
  `docs/340`
  对照包的人工听审，
  当前明确结论是：
  - `semanticconsumer_decoded`
    仍是 pure fuzz
  - 虽然没有之前那么响，
    但仍然没有任何人声成分
- 因此：
  - `target_sidecar_broadcast_v1`
    这条 Stage5 target-side semantic
    forward consumer
    不能继续沿
    “再调一点 broadcast 特征 /
    再调一点拼接位置 /
    再调一点小权重”
    方向推进
- 当前最有价值的下一步应改写为：
  - 停止继续做
    Stage5 侧
    target-only static semantic
    consumer 微变体
  - 转向构建
    **真正具有时序/事件结构的 design-state `e_evt` consumer 前置资产**

## 一、为什么这条线现在应停止

### 1. 它已经不是“没接通”
- `docs/340`
  已经确认：
  - semantic 真的进入了
    Stage5 forward path
  - 输入维度从
    `36 / 36`
    变成
    `45 / 45`
- 所以这次失败
  不是 plumbing 问题

### 2. 它也不是“还没过机器门禁”
- 这条线相对旧 baseline
  的确有两点正向信号：
  - shared metrics
    有改善
  - 已从
    `auto_reject_obvious_buzz`
    进入
    `review_required`
- 但人工听审已经说明：
  - 这仍然不是 speech emergence
  - 最多只是把 fuzz
    调得没那么刺

### 3. 这意味着问题不在这版 consumer 的小细节
- 当前这版 consumer
  的根本形态是：
  - target-only
  - utterance-level static semantic
  - frame broadcast
- 它缺的不是：
  - 再多 2 个特征
  - 或拼到 periodic/noise
    的哪个侧支
- 更深的缺口是：
  - 没有真正的
    frame/event-level
    时序语义
  - 也没有 source-side parity
  - 更没有 design-state
    `e_evt`
    本体

## 二、当前最有价值的调整

### 正式建议
1. 停止继续做：
   - `target_sidecar_broadcast_v1`
     的小改版
   - Stage5 target-only
     static semantic
     同层微调
2. 下一步上收到：
   - 构建更接近 design-state
     `e_evt`
     的时序语义资产
3. 然后再回到 Stage5，
   接：
   - 真正的
     time-aware semantic consumer

## 三、为什么下一步不是继续调 Stage5
- 当前
  `target_event_semantic_sidecar`
  本质上只有：
  - lexical / punctuation /
    clause structure
    的 utterance-level hints
- 它没有：
  - frame 对齐
  - phone / manner / place
  - source-side semantic parity
- 所以即便把它直接拼进
  Stage5 input，
  也更像：
  - 一个静态句级条件
- 而不是：
  - 能驱动 waveform route
    产生细粒度人声结构的
    `e_evt`

## 四、下一步应具体做什么

### 推荐主动作
1. 回到 semantic 资产层，
   先做：
   - source/target 可对齐的
     时序 semantic 设计
2. 当前最合理的最小方向是：
   - 在现有
     `target_event_semantic_sidecar`
     之上，
     继续补
     frame/event-level
     语义桥
3. 如果只能二选一，
   当前更推荐优先：
   - source-side / time-aligned semantic
     资产
   而不是继续在
   Stage5 package
   层做新 broadcast 变体

### 对 Stage5 consumer 的直接含义
- 下一版若继续做 consumer，
  应优先是：
  - explicit event/time-aware consumer
- 不应再优先是：
  - static target-side summary
    broadcast

## 五、当前工程判断
- 这次 forward consumer
  的真正价值已经拿到了：
  - 它证明了
    “target-side semantic 进入 forward path”
    本身并不会自动长出 speech
- 这使下一步可以更干净地写成：
  - 不是再试另一个 static semantic
    变体
  - 而是补真正缺失的
    temporal semantic /
    design-state `e_evt`
    资产

## 一句话结论
- `target_sidecar_broadcast_v1`
  已正式失败；
  下一步最有价值的工作，
  不是继续调这条 Stage5 static semantic 线，
  而是转向构建真正可支撑
  `e_evt`
  consumer 的时序语义资产。
