# 355. 多轮 pure buzz 后的主方案重评估与 `v2-core` 缺口审计报告

## 结论
- 到 `2026-03-25` 为止，当前已经有足够证据正式停止以下方向：
  - Stage5 loss 微调线
  - Stage5 target-only semantic / timing consumer 变体
  - Stage3 timing semantic weighting / routing 微调
  - paired Stage3 直接训练设想
  - teacher-first inference-only 末端小修
- 这些线的问题不是“还差一点参数”，而是：
  - 多次量化改善并没有带来第一次真实人声 emergence
  - 多次人工听审结论仍是 pure buzz / pure fuzz
- 当前唯一仍然自洽、且与设计稿对齐的主线，应正式收束回：
  - `C-prime / v2-core`
  - `no-res baseline only`
  - 重点修正真正的 design-state contract，尤其是：
    - `e_evt`
    - teacher / Stage3 / Stage5 对该语义的真实消费链

## 一、为什么现在必须停掉同层微调

### 1. 已有失败证据已经足够
- `MRSTFT short-window`：
  - 权重链路已接通
  - 量化并非完全无效
  - 但人工听审仍是 pure buzz
- `target-side semantic weighting`
  - 权重已真实生效
  - 仍是 pure fuzz
- `target semantic forward consumer`
  - 已真正进 forward path
  - 机器门禁不再直接 auto reject
  - 人工仍判 pure fuzz
- `target timing consumer`
  - 真接通
  - export gate 仍 `all_records_auto_reject = true`
- `source parity consumer`
  - 量化略好
  - export gate 仍 `all_records_auto_reject = true`
- `teacher-first inference-only`
  - `risk_v2` 与 `reference_shift` 的治理升级是有效的
  - 但人工听审仍确认：
    - `default_postenv_decoded`
    - `affine_refmean_gateoff_decoded`
    均为 pure buzz

### 2. 当前不能再把什么误判成“进展”
- 不能再把：
  - `loss_stft` 下降
  - `reference_shift` 下降
  - risk 状态从 `high_risk` 变 `elevated_risk`
  直接等同于：
  - 人声已经开始出现
- 现在更准确的结构判断是：
  - 末端 decoder / loss / weighting 层已经被反复试过
  - 真正没立起来的是更上游的控制合同语义

## 二、当前代码里，`v2-core` 到底已经有什么

### 1. 已经接通的部分
- `src/v5vc/source_acoustic_state_extraction.py`
  已有确定性的
  `source_acoustic_state_extraction_v1`
  ，能导出：
  - `f0_hz`
  - `vuv`
  - `aper`
  - `E`
- `src/v5vc/offline_teacher_downstream_contract.py`
  已把这些字段正式写入
  `offline_teacher_downstream_control_v2`
  contract
- `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  已把这些字段正式接成
  Stage5 periodic / noise branch features
- 所以从代码事实看：
  - `f0_hz / vuv / aper / E`
    这条 source acoustic state extraction chain
    已经不是“还没做”
  - 它已经在链上

### 2. 仍然没有真正接通的部分
- 当前 contract 里虽然叫 `v2`
  ，但 `event` 侧仍是：
  - `event_probs`
  - heuristic metadata
- `src/v5vc/offline_teacher_downstream_contract.py`
  已明确写了：
  - 当前 `event_probs`
    仍是
    `offline_mvp_heuristic_event_target_v1`
  - 不应误读成设计稿里的
    `e_evt`
- `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  也同样写明：
  - 当前 `event_probs`
    不等于最终 named
    `e_evt`

### 3. Stage3 当前吃的仍是旧 `teacher_event_probs`
- `src/v5vc/streaming_student/teacher_labels.py`
  仍导出：
  - `event_logits`
  - `event_probs`
- `src/v5vc/streaming_student/data.py`
  仍把监督载入为：
  - `teacher_event_probs`
- `src/v5vc/streaming_student/losses.py`
  仍直接用：
  - `teacher_event_probs`
    做
    `event`
    与
    `event_prior`
    损失
  - `vuv_proxy`
    与
    `aper_proxy`
    也仍从这套 target 中切片派生
- 所以现在最关键的代码事实是：
  - `z_art + source acoustic state`
    基本已经在链上
  - `e_evt`
    还没有
  - Stage3 / Stage5
    现在仍主要围绕旧 heuristic
    `event_probs`
    工作

## 三、paired 这条线现在应如何定性
- 当前 paired 路线的价值只剩：
  - 数据合同审计
  - source-aware 诊断
- 它不是：
  - 当前训练主线
  - 平行语料监督学习立项
- 这轮 dry-run 已经证明：
  - source parity sidecar
    可以修到 source 轴
  - 但 source waveform
    和 target teacher frames
    不天然对齐
- 所以在没有明确
  `source-target frame bridge`
  之前：
  - paired Stage3
    不能开训练
  - 更不能拿它替代主线

## 四、当前最有价值的调整是什么
- 当前最有价值的调整，不是再改：
  - MRSTFT
  - semantic weight
  - timing boost
  - gate on/off
  - normalization strategy
- 而是正式开始：
  - `design-state e_evt` 升级
  - 并让它真正贯穿
    teacher contract ->
    teacher labels ->
    Stage3 supervision ->
    Stage5 no-res baseline

### 这件事的本质
- 不是再做一个 target-only sidecar 小实验
- 也不是继续抠 user-line demo
- 而是把系统从：
  - “source acoustic state 已补，event 语义仍停在 heuristic”
  拉回到：
  - “真正开始接 design-state control contract”

## 五、下一步的正式建议

### 1. 先写死 `e_evt_v1` 合同，而不是先开训练
- 先明确：
  - 字段名
  - 每维语义
  - target 监督来源
  - 哪些维度是概率
  - 哪些维度是类别或 proxy
  - 与旧 `event_probs(8D)` 的映射关系
- 同时明确：
  - 旧 `event_probs`
    后续降级为
    diagnostic / legacy compatibility
    资产
  - 不再继续冒充最终 event contract

### 2. 把 `teacher_labels` 从 `event_probs-only` 升级到 `e_evt + legacy_event_probs`
- 保持兼容：
  - 旧字段可以保留
- 但新的监督主键应开始显式变成：
  - `teacher_e_evt`
- 这样 Stage3
  才能真正从“旧 heuristic 事件目标”
  过渡到“设计态事件合同”

### 3. Stage3 先做 contract-level smoke，不急着大训练
- 先验证：
  - config
  - label export
  - data batch
  - loss
  - short loop
  是否真实沿链路生效
- 仍然保持：
  - `no-res`
  - 不碰 paired training
  - 不引入 GAN / waveform 大改

### 4. 只有 `e_evt` 真接通后，才值得重训 Stage5 `C3`
- 到那一步再重训的，应该是：
  - `C-prime Phase C3`
  - `v2-core`
  - `no-res baseline only`
- 如果那时仍是主要 buzz，
  才有资格进入：
  - waveform objective / waveform head
    层面的 `C4`

## 六、当前一句话决策
- 现在不再继续做任何同层 buzz 微调；
  当前唯一值得投入的主线，是把
  `event_probs`
  彻底升级为真正的
  `design-state e_evt`
  合同，并据此重建
  Stage3 -> Stage5
  的 `C-prime / v2-core / no-res`
  验证链。
