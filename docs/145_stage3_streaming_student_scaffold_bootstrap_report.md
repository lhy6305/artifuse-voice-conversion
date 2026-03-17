# 145. Stage3 `streaming_student` scaffold bootstrap 报告

## 背景
- `docs/144_next_phase_development_handoff.md`
  已把项目主线从 offline MVP 收口，
  切到:
  - 下一阶段开发准备
- 该阶段的默认首个落点是:
  - 统一流式前端
  - Student 控制头
  - 与现有 `offline_mvp` 评估链兼容的接口骨架

## 本轮目标
- 不直接开新训练。
- 先把 Stage3 `streaming_student` 从“未接线草稿”
  推进到:
  - CLI 可调用
  - 配置模板固定
  - 能输出正式计划产物

## 本轮实际完成

### 1. 新增 Stage3 代码骨架
- 新增目录:
  - `src/v5vc/streaming_student/`
- 当前已落地文件:
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/__init__.py`

### 2. Stage3 scaffold 已正式接入 CLI
- 新增命令:
  - `.\python.exe manage.py prepare-streaming-student-stage`
- 当前默认参数:
  - `--config configs/streaming_student_stage_template.json`
  - `--output-dir reports/plans/streaming_student_stage`
  - `--experiment-id streaming_student_stage_scaffold`

### 3. 新增配置模板
- 新增:
  - `configs/streaming_student_stage_template.json`
- 当前模板固定:
  - `training.mode = streaming_student_stage`
  - `training.run_stage = scaffold_bootstrap`
  - `model.r_res_enabled = false`
  - `frame_length = 400`
  - `hop_length = 160`

### 4. 已跑通首个 scaffold bootstrap
- 执行命令:
  - `.\python.exe manage.py prepare-streaming-student-stage --config configs/streaming_student_stage_template.json --output-dir reports/plans/streaming_student_stage --experiment-id streaming_student_stage_scaffold`
- 运行结果:
  - 成功生成:
    - `reports/plans/streaming_student_stage/streaming_student_stage_scaffold.plan.json`
    - `reports/plans/streaming_student_stage/streaming_student_stage_scaffold.plan.md`

## 当前骨架的真实内容

### 1. 统一流式前端当前输出
- `shared_hidden`
- `coarse_log_f0`
- `vuv_logits`
- `aperiodicity`
- `energy`
- `event_prior_logits`

### 2. Student 当前输出
- `z_art`
- `event_logits`
- `event_probs`
- `log_f0_correction`
- `aper_correction`
- `r_res`

说明:
- 当前 `r_res` 仍被强制关闭，
  所以实际输出维度是:
  - `r_res = [B, T, 0]`

### 3. 当前条件输入
- `speaker_embedding`
- `geom_embedding`
- 二者先投影到:
  - `conditioning_hidden`
- 再与:
  - `shared_hidden`
  - 前端粗控制量
  一起送入 Student 控制头

## 本轮 bootstrap 已确认的事实

### 1. 数据侧接线已可复用
- scaffold 已确认能读取:
  - `data_prep/round1_1/manifests`
  - `data_prep/round1_1/splits/hybrid_stratified_blocked`
- 本轮读出的正式计数为:
  - `target_train = 592`
  - `target_validation = 66`
  - `target_special_eval = 8`
  - `source_train = 483`
  - `source_validation = 54`

### 2. sidecar 路径已接入 bootstrap 校验
- 当前会检查:
  - `target_weak_event_hints_path`
  - `target_special_supervision_path`
- 若路径不存在，bootstrap 会直接报错，
  不会默默跳过

### 3. 与 `offline_mvp` 的帧级合同已暂时对齐
- 当前固定:
  - `frame_length = 400`
  - `hop_length = 160`
- 目的不是复用旧训练循环，
  而是先保留帧级可比性，
  便于后续建立 eval bridge

### 4. 当前只是 scaffold，不是 Stage3 真实训练
- 本轮 bootstrap 只做:
  - 配置校验
  - split/sidecar 校验
  - synthetic waveform dry-run
  - contract 与 shape 落盘
- 当前还没做:
  - Teacher 监督标签装载
  - 真实 Student loss
  - Stage3 checkpoint 训练

## dry-run 结果摘要
- synthetic batch:
  - `batch_size = 2`
  - `waveform_length = 6400`
- 当前关键输出 shape:
  - `shared_hidden = [2, 38, 96]`
  - `z_art = [2, 38, 8]`
  - `event_logits = [2, 38, 8]`
  - `coarse_log_f0 = [2, 38, 1]`
  - `vuv_logits = [2, 38, 1]`
  - `aperiodicity = [2, 38, 1]`
  - `energy = [2, 38, 1]`
  - `log_f0_correction = [2, 38, 1]`
  - `aper_correction = [2, 38, 1]`
  - `r_res = [2, 38, 0]`

## 当前边界

### 1. 还不能把当前 scaffold 当成可训练 Student 系统
- 当前只是把:
  - 前端
  - Student 头
  - 条件输入
  - contract
  先焊成正式工程入口

### 2. 还没有校准资产格式
- 设计稿里的:
  - `s_spk_target`
  - `s_geom_target`
  - `alpha`
  还没有正式数据格式 / 生成入口 / 落盘位置

### 3. 还没有 eval bridge
- 当前 `streaming_student` 虽然输出了与 `offline_mvp` 接近的控制量，
  但还没有正式模块把这些输出汇总为:
  - 可直接复用的 `offline_mvp` 风格评估输入

## 当前建议的下一步
1. 先补 Teacher-label 数据接线，
   但不要把 Stage3 直接塞进 `offline_mvp` 训练循环。
2. 定义校准资产格式:
   - `s_spk_target`
   - `s_geom_target`
   - `alpha`
3. 建一个最小 Stage3 eval bridge，
   先复用现有控制汇总口径，
   再决定真实训练入口长什么样。
4. 在前端 / Student contract 稳定前，
   继续保持:
   - `r_res` 关闭
   - `frame_length / hop_length` 对齐 `offline_mvp`

## 一句话结论
- Stage3 `streaming_student` 现在已经不是想法，
  而是仓库里可执行、可出计划、可落盘的正式 scaffold；
  但它仍处于“接口骨架确认”阶段，
  还没有进入真实 Student 训练。
