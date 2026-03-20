# 220. Stage5 low-activity smoothness sidecar 补充报告

## 背景
- `docs/219_stage5_low_activity_validation12_recheck_report.md`
  已确认:
  - `36/48/60`
    在当前 low-activity
    四个核心指标上
    发生塌缩
  - 当前主要差异
    不在:
    - `fragmentation`
    - `active_fraction`
    - `alignment`
    - `activity_excess`
- 这意味着:
  - 若还想在
    `36/48/60`
    之间提取一点
    治理信息，
    需要找
    secondary metric

## 本轮目标
1. 检查
   `mean_sample_delta_peak`
   是否能稳定区分
   `36/48/60`
2. 如果它足够稳定，
   就把它降级接入为:
   - low-activity smoothness sidecar
3. 保持策略克制:
   - 不改主 selector
   - 不改当前 soft rerank 主权重

## 当前观察

### 1. branch aggregate 上的顺序
- 在
  `validation12`
  decoded probe
  上:
  - `step36 mean_sample_delta_peak = 0.34293`
  - `step48 mean_sample_delta_peak = 0.221658`
  - `step60 mean_sample_delta_peak = 0.196337`
- 当前解释:
  - 数值越低，
    代表低活动段内
    波形相邻采样跳变峰值越小，
    可以作为
    “泄漏簇内部更平滑”
    的次级代理

### 2. record 级稳定性
- `12 / 12`
  条记录上，
  都满足:
  - `step36 > step48`
- `12 / 12`
  条记录上，
  都满足:
  - `step36 > step60`
- `10 / 12`
  条记录上，
  满足:
  - `step48 > step60`
- 平均差值:
  - `mean(step36 - step48) = 0.121271`
  - `mean(step48 - step60) = 0.025321`
  - `mean(step36 - step60) = 0.146593`

### 3. 两条未满足 `48 > 60` 的记录
- `target::chapter3_3_firefly_245`
- `target::chapter3_4_firefly_106`
- 这说明:
  - `48`
    对
    `60`
    的优势不是绝对单边
  - 但 aggregate
    与大多数 record
    仍然支持:
    - `60`
      更平滑

## 本轮代码补充

### 1. selection sidecar 新增平滑度表达
- 修改:
  - `src/v5vc/nores_vocoder_checkpoint_selection.py`
- 当前新增:
  - `best_low_activity_smoothness_branch`
  - `best_low_activity_smoothness_branches`
  - `worst_floor_leakage_smoothness_ranking`

### 2. markdown / payload 行为
- 当
  `worst_floor_leakage`
  存在多路并列时，
  现在会额外输出:
  - `Worst-Floor-Leakage Tie-Break`
- 当前在
  `validation12`
  上写出的顺序为:
  - `step60 < step48 < step36`

## 当前策略层级

### 1. 这不是新的主目标
- `mean_sample_delta_peak`
  当前只作为:
  - secondary smoothness sidecar
- 不直接进入:
  - 主 selector
  - 当前 soft rerank 主权重

### 2. 当前最合理的使用方式
- 当
  `36/48/60`
  这类 checkpoint
  在核心 low-activity
  指标上塌缩时，
  再用
  `mean_sample_delta_peak`
  做:
  - 泄漏簇内部的次级排序

### 3. 当前工程口径
- 如果未来因
  `fragmentation`
  风险
  不想选
  `step72`
  ，
  而又只能在当前
  泄漏簇里选 fallback，
  当前优先级更像:
  - `step60`
  - 再看
    `step48`
  - 最后才是
    `step36`

## 当前风险边界

### 1. `mean_sample_delta_peak` 不能被误写成“更安静”或“更尊重 target”
- 它当前表达的是:
  - 低活动段波形边缘跳变粗糙度
- 它不直接等价于:
  - floor leakage 更少
  - alignment 更好
  - fragmentation 更少

### 2. 所以它必须是次级指标
- 当前默认只在:
  - 核心 low-activity
    指标已经塌缩
  时使用
- 不直接拿它覆盖:
  - fragmentation
  - alignment
  - excess
  - active_fraction

## 一句话结论
- 当前 low-activity
  四个核心指标
  仍然无法区分
  `36/48/60`
  ，
  但
  `mean_sample_delta_peak`
  已经足够稳定地给出
  一个次级平滑度顺序:
  - `step60 < step48 < step36`
- 因此它适合作为:
  - 泄漏簇内部的
    smoothness sidecar，
  但还不应升格为
  主 selector
  或
  soft rerank
  的主规则。
