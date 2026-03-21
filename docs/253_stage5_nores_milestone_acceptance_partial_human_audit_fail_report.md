# 2026-03-21 Stage5 no-res 门槛验收部分人工听审失败报告

## 结论
- 当前
  `step72 + decode_gate_smooth3 + post_ola_envelope`
  这条
  Stage5 no-res
  best route，
  已被本轮人工听审直接判定为：
  - `未通过`
    milestone acceptance
- 失败不是：
  - “边界还有点差”
  - 或“自然度不够好但勉强可懂”
- 而是更基础的失败：
  - 完全不存在可辨识人声或音节
  - 也几乎不存在音调变化
  - 听到的是纯粹由能量包络驱动音量起伏的
    buzzing

先说人话：
- 这不是
  “还能不能再调一调更自然”
  的问题。
- 这是
  “当前导出的东西连语音都还不是”
  的问题。

## 当前听审覆盖范围

### 1. 已完整听审
- 第一条记录：
  - `target::chapter3_17_firefly_133`

### 2. 已抽样试听
- 后续若干条记录
  已做抽样试听，
  用户反馈结论一致：
  - 仍然没有人声、
    没有音节、
    没有音调变化，
    只有 buzzing

### 3. 当前覆盖边界
- 本轮不是
  `12 / 12`
  逐条完成式 GUI
  打分
- 但现有主观证据已经足够回答：
  - 当前 route
    没有达到
    Stage5 no-res
    门槛

## 当前已落盘的 session 证据
- `reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/audio_audit_progress.json`
  当前已写出：
  - `review_mode = milestone_acceptance`
  - 第一条记录：
    - `intelligibility = 不可懂`
    - `stability = 不稳定`
    - `basic_naturalness = 明显不自然`
    - `milestone_verdict = 未通过`
  - `session_notes`：
    - 本包全部音频完全不存在任何可辨识音节，
      甚至不像人声，
      只存在由能量包络驱动的单调 buzzing

## 为什么这轮可以直接判失败

### 1. 失败维度已经越过“局部缺陷”
- 如果只是：
  - 句尾差
  - 边界差
  - 有些毛刺
- 那还需要继续做更完整的
  per-record
  验收
- 但当前不是这个级别

### 2. 当前问题落在“语音是否存在”这一层
- 用户给出的不是：
  - 语音可懂但不自然
- 而是：
  - 根本不存在可辨识语音
- 所以这轮题已经不需要再继续问：
  - “是不是基本自然”
- 因为更早的门槛：
  - “是不是语音”
  都没有过

## 对当前实验线状态的更新

### 1. 当前实验线不再处于“等待 milestone acceptance 结果”
- 当前更准确的状态是：
  - milestone acceptance
    已得到负结论

### 2. 当前不建议继续完成这轮逐条 GUI 穷举
- 原因不是流程不重要，
  而是：
  - 当前失败已经非常明确
  - 继续把剩余记录逐条打完，
    信息增量很低

### 3. 当前下一题应改成 root-cause
  问题
- 更合理的新题应是：
  - 为什么当前 best route
    导出的
    `decoded`
    不是语音，
    而是 envelope-modulated buzzing
- 在这个 root cause
  被明确前，
  不应再把当前 route
  当作
  “待继续验收”
  的正常候选

## 与前序实验线文档的关系
- `docs/249_stage5_nores_milestone_acceptance_audit_kickoff_report.md`
  记录的是：
  - 这轮验收如何启动
- 本文记录的是：
  - 启动后得到的第一手人工负结论
- `docs/248_stage5_original_design_milestone_review_report.md`
  提出的问题是：
  - no-res 主干
    是否已达到
    可懂、稳定、基本自然
- 本文给出的当前答案是：
  - `否`
  - 而且失败发生在比
    “基本自然”
    更早的层级

## 下一步建议
1. 当前先把实验线真实状态写成：
   - milestone acceptance
     failed
2. 下一题改成：
   - 当前 decoded route
     的 root-cause isolation
3. 在新题被定义前，
   不再继续：
   - 旧 decode tweak
   - training apply-mode
   - 当前 milestone session
     的穷举式补打分

## 一句话结论
- 当前 Stage5 no-res
  best route
  已被人工试听直接判定为：
  - 不是“还不够自然的语音”
  - 而是“根本没有形成可辨识语音，只剩 buzzing”
- 因此这条 route
  当前明确
  `未通过`
  milestone acceptance。
