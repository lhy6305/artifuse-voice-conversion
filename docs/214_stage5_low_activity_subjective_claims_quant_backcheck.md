# 214. Stage5 low-activity 主观结论量化回查报告

## 背景
- `docs/213_subjective_conclusion_quant_validation_protocol.md`
  已要求:
  - 所有主观结论
    都要尽量回到
    可复查量化证据
- 当前最需要回查的主观判断有三条:
  1. `step72`
     更尊重原音量变化
  2. `step60`
     静音段底音仍然存在
  3. `step72`
     是否在 low-activity
     区间系统性更毛刺

## 本轮代码补充
- 修改:
  - `src/v5vc/stage5_low_activity_probe.py`
- 当前 probe
  新增并正式输出:
  - `activity_alignment_mae`
    - candidate activity
      与 target activity
      在低活动段内的平均偏差
    - 越低表示越贴近 target
      的能量轨迹
  - `activity_excess_mean`
    - candidate activity
      相对 target activity
      的正向超出量
    - 越低表示低活动段残留能量更少
  - `target_context_toggle_mean`
  - `target_boundary_jump_max`
    - 用于提示该窗口
      可能混有
      target 自身的瞬态变化

## 回查数据来源
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/stage5_low_activity_fragmentation_probe.json`
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/stage5_low_activity_fragmentation_probe.md`
- `reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session_windowed_v2/audio_audit_review.json`

## 量化回查结果

### 1. “`step72` 更尊重原音量变化”得到量化支持
- decoded aggregate:
  - `step60 mean_activity_alignment_mae = 0.975229`
  - `step72 mean_activity_alignment_mae = 0.546807`
- 解释:
  - 在 target 已进入低活动段时，
    `step72`
    的活动曲线
    明显更接近
    target
  - `step60`
    基本还维持
    接近满活动状态

### 2. “`step60` 的静音段底音泄漏仍存在”得到量化支持
- decoded aggregate:
  - `step60 mean_active_fraction = 1.0`
  - `step72 mean_active_fraction = 0.521389`
  - `step60 mean_activity_excess_mean = 0.975229`
  - `step72 mean_activity_excess_mean = 0.546807`
- 解释:
  - 在 target 低活动段里，
    `step60`
    持续保留了更多
    本不该存在的活动能量
  - 这与人耳听到的
    静音底音泄漏
    是同向的

### 3. “`step72` 系统性更毛刺”没有被量化和听审共同确认
- decoded aggregate
  仍显示:
  - `step60 mean_fragmentation_score = 0.0`
  - `step72 mean_fragmentation_score = 1.222465`
- 但对应的人耳长窗听审结果是:
  - `1` 条偏向
    `step72`
  - `1` 条偏向
    `step60`
  - `1` 条打平
  - `1` 条不建议比较
- 解释:
  - `fragmentation`
    确实能提示
    `step72`
    的局部风险窗口
  - 但它不足以单独推出
    “`step72` 人耳上系统性更差”
  - 当前更适合把它解释为:
    - 局部偶发毛刺风险提示器
    - 不是单独裁决器

## target-correlated 混淆回查

### 1. 当前新增的 target 上下文指标确实能提示“这不是纯净静音窗”
- 例如 decoded top windows 里:
  - `target::chapter3_22_firefly_114`
    `target_boundary_jump_max = 0.970427`
  - `target::chapter3_4_firefly_106`
    `target_boundary_jump_max = 1.0`
  - `target::chapter3_4_firefly_109`
    `target_context_toggle_mean = 0.045455`
- 说明:
  - 这些窗口周围
    的 target
    自身存在明显边界/瞬态变化

### 2. 但当前这组指标还只能当“混淆提示”，不能直接自动判案
- 原因:
  - 有些高边界跳变窗口
    人耳仍听到了
    更偏模型侧的毛刺风险
  - 有些用户判为
    target-correlated
    的窗口，
    当前数值也没有形成
    足够稳定的单一阈值
- 结论:
  - `target_context_toggle_mean`
    和
    `target_boundary_jump_max`
    当前适合作为:
    - 风险提示字段
  - 还不适合作为:
    - 自动排除规则

## 当前结论分级

### 1. 已升级为“量化支持的结论”
- `step72`
  更尊重原音量变化
- `step60`
  的静音段底音泄漏仍然存在

### 2. 仍停留在“听感观察 / 局部风险”
- `step72`
  在 low-activity
  区间系统性更毛刺

## 对后续流程的影响
1. 后续 low-activity
   结论默认至少同时看:
   - `fragmentation_score`
   - `mean_active_fraction`
   - `mean_activity_alignment_mae`
   - `mean_activity_excess_mean`
2. `fragmentation`
   默认解释为:
   - 局部毛刺风险提示
   不再单独当作
   最终优劣裁决
3. 若后续要继续做
   target-correlated
   排除，
   应优先围绕:
   - 更纯净静音样本
   - 更长 breath-like 过渡样本
   再校准阈值

## 一句话结论
- 这轮量化回查已经把两条主观判断正式坐实:
  - `step72`
    更贴近 target
    的低活动能量轨迹
  - `step60`
    的低活动底音泄漏
    更重
- 但它也同时说明:
  - `fragmentation`
    只能证明
    `step72`
    有局部风险窗口，
    还不能单独证明
    `step72`
    人耳上系统性更差。
