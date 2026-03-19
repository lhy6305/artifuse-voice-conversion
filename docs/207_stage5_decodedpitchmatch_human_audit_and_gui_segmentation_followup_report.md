# 207. Stage5 decoded-pitchmatch human audit 与 GUI 分段试听跟进报告

## 背景
- `docs/206_stage5_decoded_pitchmatch_listening_contract_report.md`
  已把当前
  Stage5
  人工听评主入口
  切到:
  - `decoded_pitch_matched.wav`
- 对应正式 session
  目录为:
  - `reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_decodedpitchmatch_session/`
- 本轮用户已完成
  `activitygate60`
  对
  `activitygate72`
  的听审，
  同时提出两个
  GUI 级阻碍:
  1. 方向键会误切换条目，
     干扰备注输入
  2. 长音频整段试听时，
     容易记不住另一条候选
     或参考音频的状态

## 本轮目标
1. 把本轮人工听审结果
   以正式口径落盘
2. 修正听审 GUI
   的两个可用性问题
3. 明确当前
   `60 vs 72`
   的真实结论
   与下一步推进方向

## 本轮人工听审结果

### 1. 本轮解释口径
- 本轮用户明确要求:
  - 对于
    `completed = true`
    且
    `valid_for_comparison = yes`
    的记录，
    若某一评分字段留空，
    应解释为:
    - `打平`
  - 不能再解释为:
    - “未填写”

### 2. 当前 6 条记录汇总
- `节奏最好`
  - `打平: 6`
- `边界最好`
  - `step72: 3`
  - `打平: 3`
- `最稳定`
  - `step60: 1`
  - `打平: 5`
- `综合首选`
  - `step72: 2`
  - `step60: 1`
  - `打平: 3`

### 3. 用户主观结论
- `step60`
  的静音段底噪
  比
  `step72`
  更明显
- 因而在:
  - 边界收束
  - 静音段干净程度
  上，
  当前更偏向:
  - `step72`
- 但并不是
  `step72`
  全面胜出
- 在部分
  非音节段 /
  叹气样式片段里，
  `step72`
  存在更明显的:
  - 毛刺
  - 断续
  - 跳变感
- 典型记录是:
  - `target::chapter3_3_firefly_213`

### 4. 本轮额外操作性结论
- `target::chapter3_4_firefly_106`
  这类较长记录，
  若整段听，
  容易出现:
  - 候选记忆漂移
  - 参考记忆不稳
- 因此后续同类听审，
  不应继续默认整段播放

先说人话:
- 这轮听下来，
  `72`
  在
  “安静的时候能不能真安静”
  这件事上
  更像主线候选。
- 但它在某些
  非正常发声、
  非音节段里
  又冒出了
  `60`
  没那么明显的
  毛刺问题，
  所以现在还不能写成
  “72 已经综合稳赢”。

## 本轮 GUI 修复

### 1. 禁止方向键切换条目
- 修改文件:
  - `src/v5vc/audio_audit_gui.py`
- 当前已去掉:
  - 根窗口
    `Left / Right`
    切条目快捷键
- 同时阻止:
  - 记录列表上的
    `Up / Down / Left / Right`
    键盘切换

这次修的不是
“快捷键不好用”，
而是:
- 备注输入时
  光标键
  不该再偷偷把
  当前记录切走

### 2. 为长音频加入自动分段试听
- 当前 GUI
  对较长 wav
  会自动生成:
  - 多个短片段
  - 以及一个
    `整段`
    回退选项
- 当前策略:
  - 长于 `8s`
    自动分段
  - 每段约 `4s`
  - 相邻片段约
    `0.5s`
    overlap
- GUI 中新增:
  - `试听片段`
    下拉框
  - `上一段`
  - `下一段`

### 3. 听审导出补齐 tie 语义
- `audio_audit_review.json`
  新增:
  - `tie_policy`
  - `interpreted_review`
- `audio_audit_review.md`
  也会把
  已完成且可比较的空项
  显示成:
  - `打平`

## 验证

### 1. 代码级验证
- 已通过:

```powershell
.\python.exe -m py_compile src\v5vc\audio_audit_gui.py
```

### 2. GUI smoke
- 已通过:

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 --output-dir tmp/stage5_audio_audit_gui_segmented_smoke --auto-close-ms 1000
```

### 3. 本轮听审导出已按新口径重写
- 当前 session:
  - `reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_decodedpitchmatch_session/`
- 其中:
  - `audio_audit_review.json`
  - `audio_audit_review.md`
  已按
  `空项 = 打平`
  口径更新

## 当前判断

### 1. 这轮结果不支持把默认点从 `72` 改成 `60`
- 原因:
  - `72`
    在:
    - 静音段底噪
    - 边界收束
  上更稳
- 这两个维度
  当前不是局部小偏好，
  而是主线质量问题

### 2. 这轮结果也不支持把 `72` 写成综合明确胜出
- 原因:
  - `72`
    在部分
    非音节段 /
    叹气样式片段
    暴露了更明显的
    毛刺跳变
- 所以当前更准确的口径是:
  - `72`
    仍是默认主点
  - `60`
    保留为
    非音节段稳定性
    对照点

### 3. 当前最值钱的下一步
- 不是继续
  大范围反复盲听
  同一批
  `60 vs 72`
- 而是补一条
  更针对性的治理线:
  - 非音节段 /
    低活动段 /
    叹气起始段
    的毛刺与断续监控

## 下一阶段任务
1. 以
   `target::chapter3_3_firefly_213`
   这类样本为起点，
   补做
   非音节段 /
   breath-like
   片段的专项复核
2. 为后续 checkpoint
   治理补一类
   transient / fragmentation
   侧口径，
   避免:
   - 静音更干净了
   但
   - 低活动段更容易断续
3. 后续人工听审
   默认使用
   新版 GUI
   的分段试听，
   不再把长条记录
   整段硬听

## 一句话结论
- 本轮 pitch-matched
  人工听审说明:
  - `step72`
    仍应保留为
    当前默认主点，
    因为它在
    静音段与边界上更干净
  - 但它在部分
    非音节段里
    暴露出比
    `step60`
    更明显的毛刺跳变，
    因此当前最合理的后续推进
    不是简单宣布赢家，
    而是补
    “低活动段瞬态稳定性”
    这条专项治理口径。
