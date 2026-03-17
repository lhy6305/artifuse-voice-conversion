# 167. Stage3 proxy audio 首轮人工听审报告

## 背景
- 当前 Stage3 已完成:
  - proxy audio 导出
  - audio audit GUI
  - 响度对齐修正
  - pitch 对齐与适用边界复核
- 本轮进入的是:
  - 当前默认 checkpoint
    `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
  的首轮正式人工听审

## 听审范围
- 会话目录:
  - `reports/audio/audio_audit_gui_stage3_baseline48_session/`
- bundle:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
- 总记录数:
  - `6`
- 已完成数:
  - `6`

## 当前已导出的正式听审结果
- `reports/audio/audio_audit_gui_stage3_baseline48_session/audio_audit_review.json`
- `reports/audio/audio_audit_gui_stage3_baseline48_session/audio_audit_review.md`

## 用户主观结论
- 总体判断:
  - `student` 除了存在一定“毛刺感”外，
    与 `teacher` 基本差不多
- 解释约定:
  - 未填写的条目
    视为:
    - 平手 / 无明显差异

## 听审汇总

### 1. 可比较性
- `6 / 6`
  记录均被标记为:
  - `可比较`

### 2. 节奏
- `teacher_proxy`
  获得:
  - `2`
    条明确胜出
- 其余:
  - `4`
    条未填写，
    按当前约定解释为:
    - 平手

### 3. 边界
- `6`
  条全部未填写
- 按当前约定解释为:
  - teacher / student
    在当前 proxy 口径下
    没有稳定可分辨的边界优势

### 4. 稳定性
- `teacher_proxy`
  在:
  - `6 / 6`
    条记录中
    都被选为:
    - 最稳定

### 5. 综合首选
- `teacher_proxy`
  在:
  - `6 / 6`
    条记录中
    都被选为:
    - 综合首选

### 6. 会话备注
- 当前正式会话备注为:
  - `每条都是：student模型听起来有“毛刺”，瞬态变化较teacher模型居多。`

## 当前最重要的结论

### 1. student 与 teacher 的 gap 已经不在“完全不像”这个级别
- 从用户主观反馈看，
  当前 student
  并不是大幅跑偏
- 更准确地说:
  - 大体结构已经比较接近
  - 差别主要收敛到:
    - 毛刺
    - 稳定性
    - 瞬态更容易发飘

### 2. 当前 teacher 的主要优势是稳定性，不是全面碾压
- `best_rhythm`
  只有:
  - `2`
    条 teacher 明确胜出
- `best_boundary`
  没有形成明确分胜负的记录
- 但 `most_stable / overall_pick`
  都是:
  - `6 / 6`
    teacher 胜出

这说明:
- 当前 gap
  更像:
  - 稳定性 / 毛刺控制问题
- 而不是:
  - 大范围节奏失配
  - 或显著的整体结构崩坏

### 3. 这轮听审不能证明“音节结构已经成立”
- 当前 proxy
  仍然是固定低频载波的结构监听信号
- 所以这轮结论只应解释为:
  - student 已较接近 teacher 的粗粒度结构代理
  - 但仍存在稳定性与毛刺差距
- 不能解释成:
  - 真正可懂度已经成立
  - 或最终成品听感已经成立

## 当前阶段判断
- 若只问:
  - student 有没有完全跟丢 teacher
- 当前答案倾向于:
  - 没有

- 若问:
  - 当前默认 checkpoint
    的 student
    是否已经足够平滑稳定
- 当前答案倾向于:
  - 还不够
  - teacher 仍然稳定得多

## 对后续主线的启发
1. 当前更值得优先处理的，
   不是“teacher/student 是否同一大结构”
   这个问题
2. 更值得优先处理的是:
   - student 的毛刺感
   - 瞬态稳定性
   - 微观平滑性
3. 若后续继续做 Stage3 近邻推进，
   更合理的目标应是:
   - 降低 student 的局部失稳
   而不是先假定
   - 需要推翻当前整体主线

## 一句话结论
- 首轮正式人工听审显示:
  当前 Stage3 student proxy
  已与 teacher proxy 大体接近，
  主要剩余问题集中在
  `毛刺 / 瞬态不稳 / 整体稳定性偏弱`，
  而不是明显的大结构脱轨。
