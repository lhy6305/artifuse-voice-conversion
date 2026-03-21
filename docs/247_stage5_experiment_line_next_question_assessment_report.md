# 2026-03-21 Stage5 实验线下一问题评估报告

## 结论
- 当前实验线已经把最近这一轮最容易继续缠绕的小题基本收完了：
  - decode-side
    `postenv`
    已正式默认化
  - training-side
    apply mode
    已接成正式参数
  - 最小 A/B
    已确认
    training-side
    `pre_overlap_add`
    vs
    `post_ola_envelope`
    在短程上几乎打平
  - clean-only /
    reverb-like
    路线
    已有负结论
- 因此当前最推荐的下一步不是继续开新的小型 probe，
  而是：
  - 暂停这条局部微调线，
  - 不再追加低信息量实验，
  - 等待新的明确症状、
    新 family，
    或更高价值的问题出现

先说人话：
- 最近这几条支线不是没做完，
  而是已经做到“再往前推，信息增量很低”。
- 这时候继续跑，
  更像是在消耗实验预算，
  不是在提高决策质量。

## 当前已确认的事实

### 1. decode-side `postenv` 已经收口
- `docs/241_stage5_step72_postenv_default_promotion_after_human_audit_report.md`
  已确认：
  - `post_ola_envelope`
    量化不反转
  - focused human audit
    不反转
  - 当前默认已提升
- 这条题当前已经不再是：
  - 待审分支
  - 或待定默认

### 2. training-side apply mode 已有正式实验入口
- `docs/245_stage5_training_reconstruction_apply_mode_plumbing_report.md`
  已确认：
  - 训练 CLI
    已支持
    `--reconstruction-frame-gain-apply-mode`
  - train-step /
    loop /
    dataset-loop
    都已接通

### 3. training-side apply mode 的短程信号很弱
- `docs/246_stage5_training_applymode_minimal_ab_probe_report.md`
  已确认：
  - 单步 A/B
    差异约
    `1e-6 ~ 1e-5`
  - 同包 `3 step`
    loop
    差异约
    `1e-5`
  - 小型 dataset loop
    差异约
    `1e-5 ~ 1e-4`
- 当前没有足够信号支持：
  - 立即把 training-side
    `postenv`
    升级成更大训练主实验

### 4. clean-only / reverb-like 路线当前也没有升格理由
- `docs/231_stage5_reverb_sample_retention_evaluation.md`
  已确认：
  - 不建议因为少量混响样本删数据重训
- `docs/234_stage5_clean_only_vs_baseline_training_run_report.md`
  已确认：
  - clean-only
    没有赢 baseline
  - 同验证面交叉评估
    也仍小幅落后
- 所以这条线当前也不值得重开

## 当前可选下一步

### 方案 A. 继续放大 training-side apply mode A/B
- 具体做法：
  - 直接上更长 fullsplit dataset-loop，
    比较
    `pre_overlap_add`
    vs
    `post_ola_envelope`
- 优点：
  - 已经有正式参数入口，
    工程上开跑门槛低
  - 能直接回答：
    training-side
    是否也值得切到
    `postenv`
- 缺点：
  - 当前最小 A/B
    几乎完全打平，
    预期信息密度不高
  - 训练代价明显高于当前已知信号
  - 很容易把
    “参数已可实验”
    误推进成
    “必须继续放大”

### 方案 B. 重开 clean-only / reverb-like 数据治理实验
- 具体做法：
  - 继续扩 clean-only
    对照训练
  - 或继续围绕
    `reverb_like`
    样本做删样本重训
- 优点：
  - 路线清晰，
    资产已存在
- 缺点：
  - 已有正式负结论
  - 当前更像重复劳动，
    而不是新的高价值问题
  - 极易再次把
    validation-only
    的轻度混响观察，
    误读成训练污染

### 方案 C. 重新回到 decode-side 局部修正
- 具体做法：
  - 在
    `smooth3 + postenv`
    之后，
    再找更窄的局部 decode-side 修补
- 优点：
  - 仍在实验线核心范围内
  - 可继续复用现有 low-activity
    probe / GUI / governance
    工具链
- 缺点：
  - 当前并没有一个新的明确痛点
    证明必须继续修
  - 容易退化成：
    为了继续调而继续调
  - 若缺少新的主观或量化异常，
    这条线的收益预期也偏低

### 方案 D. 当前不再开新实验，先冻结并等待新高价值问题
- 具体做法：
  - 认可当前实验线已阶段性收口
  - 停止追加低信息量专项
  - 仅在出现以下条件之一时再重开：
    - 新的主观异常
    - 新的治理冲突
    - 新 family
      候选需要进入 Stage5 主线
    - 或用户明确要求把
      training-side
      apply mode
      升级到正式长程对照
- 优点：
  - 最符合当前证据密度
  - 能避免“因为线还活着所以必须继续跑”的惯性
  - 给后续真正高价值问题留预算
- 缺点：
  - 短期内不会新增实验结果
  - 从节奏上看更像阶段暂停，
    而不是继续扩写新分支

## 推荐排序
1. 方案 D：
   当前不再开新实验，
   先冻结并等待新高价值问题
2. 方案 C：
   仅当出现新的明确 decode-side 症状时，
   再重开局部修正题
3. 方案 A：
   只有当用户明确要追
   training-side
   apply mode
   时，
   才升级到正式长程 A/B
4. 方案 B：
   当前最不推荐

## 为什么推荐先冻结
- 当前最像“下一步”的几条题，
  其实都已经被事实压缩了：
  - training-side
    apply mode
    没有强信号
  - clean-only
    已有负结论
  - decode-side
    也没有新症状要修
- 这时最稳妥的动作不是再找一个勉强能跑的实验，
  而是承认：
  - 当前线在现阶段已经收够了

## 当前建议执行动作
1. 把当前实验线口径正式写成：
   - `postenv`
     默认提升已完成
   - training-side
     apply mode
     有正式实验能力，
     但短程无强信号
   - clean-only /
     reverb-like
     当前不升格
2. 后续若没有新症状，
   不再为这三条子线新增实验会话
3. 若用户后续仍希望继续“做点什么”，
   优先先做新的候选题评估，
   而不是直接起实验

## 一句话结论
- 当前实验线最合理的下一步，
  不是再开一个新 probe，
  而是正式承认：
  最近几条局部题都已阶段性收口；
  在新的高价值问题出现前，
  先不要继续消耗实验预算。
