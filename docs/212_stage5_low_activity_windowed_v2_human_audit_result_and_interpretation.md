# 212. Stage5 低活动段 windowed_v2 听审结果与解释

## 背景
- `docs/211_stage5_low_activity_decoded_audit_window_rebuild_and_partial_human_feedback.md`
  已把
  low-activity
  定点听审窗
  重建为:
  - 前后至少
    `200ms`
    上下文
  - 总长优先约
    `2.4s`
- 当前用户已完成:
  - `windowed_v2`
    session
    的全部 4 条 decoded 主听样本

## 听审结果来源
- `reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session_windowed_v2/audio_audit_review.json`
- `reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session_windowed_v2/audio_audit_review.md`
- 对照 probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/stage5_low_activity_fragmentation_probe.md`

## 本轮人耳结论

### 1. 不能把“step72 更容易毛刺”写成稳定结论
- 当前共 4 条样本
  听审完成
- 其中:
  - `1` 条偏向
    `step72`
    整体更好
  - `1` 条偏向
    `step60`
    整体更好
  - `1` 条打平
  - `1` 条不建议比较
- 这说明:
  - `step72`
    的毛刺现象
    不是稳定必现
  - 当前不足以支持
    “`step72` 在低活动段系统性更差”

### 2. 用户关于“原音频本身可能就有 breath / sigh 类能量毛刺”的猜测是成立的，而且与本轮记录一致
- `target::chapter3_3_firefly_213`
  被明确标记为:
  - 原音频存在频繁辅音 / 爆破音，
    不适合细粒度比较毛刺
- `target::chapter3_4_firefly_109`
  被明确记录为:
  - 两个模型在清音段
    都出现毛刺
  - 用户怀疑
    这是原音频对应段
    本来就有的能量毛刺，
    不是模型单方新增
- 因此当前更合理的解释是:
  - 低活动段里的可疑现象
    至少有一部分
    是 target-correlated
    的
    breath / sigh / 清辅音能量变化
  - 不能把这部分
    直接全部记到
    `step72`
    头上

### 3. `step72` 仍然有局部、偶发的模型侧毛刺风险
- `target::chapter3_4_firefly_106`
  的备注明确指出:
  - 结尾出现
    `step72`
    的典型毛刺
- 但同条里
  `step60`
  也不是完全干净，
  只是毛刺间隔更短，
  主观上更平滑
- 所以当前更准确的说法应是:
  - `step72`
    仍有局部瞬态毛刺风险
  - 但不是此前短窗 probe
    暗示的那种
    “多数样本稳定更差”

### 4. `step60` 的静音段底音泄漏是当前更稳定、更可重复的问题
- 用户本轮明确补充:
  - `step60`
    的静音段底音仍然存在
- 这与 probe 的
  decoded aggregate
  一致:
  - `step60 mean_active_fraction = 1.0`
  - `step72 mean_active_fraction = 0.521389`
- 含义是:
  - 在 target 已被标为低活动段的窗口里，
    `step60`
    仍持续输出较高比例的活动能量
  - `step72`
    更愿意跟随原音量起伏收下去
- 这也解释了为什么:
  - `step60`
    可能主观上
    没那么“炸”
  - 但代价是
    静音/气声区间
    更容易带着底音拖尾

## 当前解释框架

### 1. 现在至少要把两类现象分开
- 现象 A:
  - target-correlated
    的 breath / sigh / 清辅音瞬态
- 现象 B:
  - model-added
    的局部毛刺 / 跳变

### 2. 当前 checkpoint 听感差异更像 tradeoff，而不是单边胜负
- `step72`
  的优势:
  - 更尊重原音频音量变化
  - 低活动段更容易真的收下去
- `step72`
  的风险:
  - 在少数窗口
    仍会出现更突出的局部毛刺
- `step60`
  的优势:
  - 某些毛刺会因为持续底音/更高频细碎扰动
    被主观上“抹平”
- `step60`
  的问题:
  - 静音段底音泄漏
    仍然明显存在

## 当前对主结论的影响
1. 不应再把
   low-activity probe
   的
   fragmentation
   结果
   直接解释为:
   - `step72`
     人耳已确认系统性更差
2. 当前更可信的结论应改成:
   - `step72`
     在低活动段更尊重原音量变化，
     但仍存在局部偶发毛刺风险
   - `step60`
     没有彻底解决静音段底音泄漏
3. 因此下一步治理目标
   更像是:
   - 保留
     `step72`
     的量感/静音控制优势
   - 同时压掉其局部 breath-like
     瞬态毛刺

## 建议的下一步
1. 在 probe / checkpoint governance
   中把
   `mean_active_fraction`
   明确提升为:
   - 低活动段底音泄漏指标
2. 新增一条
   target-correlated
   判别口径:
   - 若 target 自身在窗口里
     已有明显 breath / 爆破 / 清辅音突变，
     该窗口不直接用于给模型判“毛刺罪名”
3. 后续若还要做人工复核，
   优先再补:
   - 更长窗的 breath-like 样本
   - 明确纯静音或近静音样本
   用来专门验证
   `step60`
   的底音泄漏

## 一句话结论
- 本轮听审把问题从
  “`step72` 是否更差”
  收敛成了更准确的两条:
  - `step72`
    更尊重原音量变化，
    但有局部偶发毛刺风险
  - `step60`
    的静音段底音泄漏
    仍是更稳定的残留问题
