# 367. Stage3 `teacher_fused_hidden` projection A/B fail-fast 报告

## 结论
- 我把 Stage3 显式 `teacher_fused_hidden` projection distillation 接进了 model/loss/config。
- 这次不是再扫 `teacher_e_evt` 小几何，而是第一次让当前 Stage3 scaffold 直接拟合 teacher 内部态：
  - `shared_hidden -> teacher_hidden_projection`
  - `student_hidden -> teacher_fused_hidden_projection`
- 但第一轮最小候选
  - `teacher_fused_hidden_projection = 0.002`
  在严格可比 12-step A/B 里更差：
  - baseline
    - `validation step12 loss_total = 1.848593`
    - `loss_total_semantic_disabled_reference = 1.738708`
  - candidate
    - `validation step12 loss_total = 1.955228`
    - `loss_total_semantic_disabled_reference = 1.845649`
- 更关键的是：
  - `loss_teacher_fused_hidden_projection`
    自己虽然下降了
    - `84.372002 -> 56.47525`
  - 但 `loss_teacher_event / event_prior`
    基本没有形成净改善
- 所以当前结论应写死为：
  - 简单的 Stage3 `teacher_fused_hidden` projection route
    不值得继续扫第二个小权重
  - 当前更合理的判断仍是：
    - teacher-label generation-side
      比 state-space imitation
      更有价值

## 一、本轮做了什么

### 1. 新增显式 hidden projection heads
- 代码：
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/losses.py`
- 新输出：
  - `teacher_hidden_projection`
  - `teacher_fused_hidden_projection`
- 当前映射约定：
  - `shared_hidden`
    对齐 teacher `hidden`
  - `student_hidden`
    对齐 teacher `fused_hidden`

### 2. 当前只开 fused-hidden 路线
- 新增配置：
  - `configs/streaming_student_loss_weights_eevt_timingaux_fusedhiddenproj002_v1.json`
- 当前 candidate
  只比 baseline 多：
  - `teacher_fused_hidden_projection = 0.002`
- 没有继续同时打开：
  - `teacher_hidden_projection`
- 这样可以避免把
  `hidden/fused_hidden`
  两条变量混在一起

## 二、smoke 与 raw loss 量级

### 1. scaffold smoke
- 输出：
  - `reports/plans/streaming_student_stage_hiddenproj_smoke_round1_1/`
- 关键确认：
  - `teacher_hidden_projection.shape = [B, T, 64]`
  - `teacher_fused_hidden_projection.shape = [B, T, 64]`

### 2. 1-step smoke
- 输出：
  - `reports/training/streaming_student_eevt_fusedhiddenproj_step_smoke_round1_1/`
- raw loss 量级：
  - train
    - `loss_teacher_hidden_projection = 41.042278`
    - `loss_teacher_fused_hidden_projection = 77.62674`
  - validation
    - `loss_teacher_hidden_projection = 50.282715`
    - `loss_teacher_fused_hidden_projection = 41.701206`

解释：
- 这说明：
  - hidden projection
    不是挂空
  - 但量级明显大于
    现有主监督项
- 所以本轮没有照搬
  旧 offline 路线里的
  `0.05`
  级权重，
  而是只试：
  - `0.002`

## 三、严格可比 12-step A/B

### 1. baseline
- 输出：
  - `reports/training/streaming_student_loop_eevt_acousticbridge_hiddenproj_baseline12_round1_1/`
- step12 validation：
  - `loss_total = 1.848593`
  - `loss_total_semantic_disabled_reference = 1.738708`
  - `loss_teacher_event = 0.541441`
  - `loss_teacher_event_prior = 0.701748`
  - `loss_teacher_fused_hidden_projection = 84.372002`

### 2. candidate
- 输出：
  - `reports/training/streaming_student_loop_eevt_acousticbridge_fusedhiddenproj002_12_round1_1/`
- step12 validation：
  - `loss_total = 1.955228`
  - `loss_total_semantic_disabled_reference = 1.845649`
  - `loss_teacher_event = 0.540836`
  - `loss_teacher_event_prior = 0.700734`
  - `loss_teacher_fused_hidden_projection = 56.47525`

### 3. 关键对照
- 当前 candidate
  确实压低了：
  - `loss_teacher_fused_hidden_projection`
- 但同时：
  - `loss_total`
    变差：
    - `1.848593 -> 1.955228`
  - `loss_total_semantic_disabled_reference`
    变差：
    - `1.738708 -> 1.845649`
- `loss_teacher_event / event_prior`
  只有极弱变化，
  不足以支撑继续扩实验

## 四、当前解释
1. 这说明：
   - 当前 Stage3
     的问题
     不是
     “只差一条显式 fused-hidden imitation”
2. 更精确地说：
   - student
     可以被拉去更像 teacher `fused_hidden`
   - 但这并没有同步转成
     更好的主监督收敛
3. 所以不能把：
   - `loss_teacher_fused_hidden_projection`
     自身下降
   解释成：
   - 当前主线已经更接近
     听感突破

## 五、结论与下一步
1. 正式停止：
   - current
     `teacher_fused_hidden_projection`
     Stage3 route
2. 不再继续做：
   - `0.001 / 0.003 / 0.005`
     这类同层小权重 sweep
   - 再补一个
     `teacher_hidden_projection only`
     的平移变体
3. 当前更合理的下一步仍应是：
   - 回到
     teacher-label / target-state
     生成资产层
   - 或重新评估
     哪个下游层
     真正能承接
     上游正向改动
