# 337. Stage5 MRSTFT `0.05` 听审失败与最有价值调整评估

## 结论
- 用户已完成
  `docs/336`
  对照包的人工听审，
  当前明确反馈是：
  - `mrstft005`
    仍是单声调纯 buzz
  - 没有人声结构
- 因此这次判断不再是：
  - “`0.05`
    还可再微调”
- 而是：
  - short-window MRSTFT
    这条线应正式收口
  - 更广义的
    Stage5
    局部 waveform / objective
    微调线，
    也不应继续投入
- 当前最有价值的调整，
  不是再试一个 loss、
  再推一个 decoder 小改、
  再扫一个更细权重，
  而是回到已经拍板的主线：
  - 以
    `contractv2_normfix`
    为底座
  - 正式把仍缺失的设计态
    `e_evt`
    语义接回
    Stage5
    no-res baseline

## 一、为什么 MRSTFT 线现在应停止

### 1. 这次失败不是“参数还没打通”
- `docs/333`
  已确认：
  - `multires_stft_short_weight`
    已沿
    CLI -> dataset loop -> loss
    调用链真正生效
- `docs/334`
  与
  `docs/335`
  已完成：
  - 可比 baseline
  - `0.05 / 0.1 / 0.2`
    低权重 sweep
- `docs/336`
  已把
  baseline `0.00`
  与
  `mrstft005`
  的最小听审包准备完成

### 2. 这次失败也不是“还没找到更细点的 sweet spot”
- 量化上，
  `0.05`
  已经是这条线里最温和的候选
- 但人工听审仍给出：
  - 单声调 pure buzz
  - 无有效人声 emergence
- 这意味着：
  - 当前瓶颈
    不在
    short-window spectral detail
    是否再细一点
  - 而在更上游的
    representation / contract / semantics
    主干是否把对的人声状态送到了
    vocoder

## 二、为什么下一步应转回 contract / semantic 主线

### 1. acoustic-state 侧其实已经补过，而且确实有过正向信号
- `docs/281`
  与
  `docs/288`
  已明确：
  - 当前主线早已不是继续扫
    B 方案
    或局部 inference 小修
  - 而是
    `C-prime / v2-core`
    工程化落地
- `contractv2_normfix`
  已把：
  - `f0_hz`
  - `vuv`
  - `aper`
  - `E`
  接回
  Stage5
  no-res baseline
- 且
  `docs/288`
  的正式重训结果已到：
  - `best_validation = 0.554104`
  - 优于旧主线
    `0.564671`

### 2. 当前仍最大的结构缺口在 semantic 侧，而不是 waveform loss 侧
- `docs/322`
  已明确写清：
  - 当前 runtime
    的
    `event_probs(8D)`
    仍是旧 heuristic frame target
  - 它不是设计态
    `e_evt`
- 也就是说，
  现在 Stage5
  并不是已经拿到了完整设计态 contract，
  然后只差一个更好的
  waveform loss。
- 更准确的现状是：
  - acoustic-state
    侧补了一大半
  - semantic
    主干仍未真正升级到
    design-state
    `e_evt`

## 三、当前最有价值的调整

### 正式建议
1. 停止：
   - short-window MRSTFT
   - 更广义的
     STFT / waveform / decoder-family
     局部微调线
2. 回到
   `contractv2_normfix`
   底座，
   继续做：
   - target-side semantic
     contract
     升级
3. 具体优先级应是：
   - 把
     `target_event_semantic_sidecar`
     正式并入
     Stage5
     package / contract / no-res baseline
   - 把当前旧 heuristic
     `event_probs`
     与设计态
     `e_evt`
     明确区分，
     并让训练真正消费新的
     target-side semantic
   - 以
     `contractv2_normfix + target-side semantic`
     作为下一条干净主线重训

### 边界约束
- 继续坚持：
  - no-res baseline
  - 不打开
    `r_res`
  - 不引入 GAN
  - 不再往 waveform objective
    里叠更多 sidecar

## 四、当前判断的工程含义
- 如果
  `contractv2_normfix + target-side semantic`
  之后，
  audible 结果仍然只是 pure buzz，
  那时才能更有把握地说：
  - 当前更深层瓶颈
    可能确实在
    waveform generator / consumer route
    本体
- 在此之前，
  继续追加局部 loss
  或小结构 tweak，
  只会持续把时间消耗在错误层级上
