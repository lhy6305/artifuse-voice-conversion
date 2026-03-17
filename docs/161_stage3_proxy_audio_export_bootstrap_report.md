# 161. Stage3 proxy audio export bootstrap 报告

## 背景
- `docs/160_stage3_baseline48_vs_eventprior025_full_validation_report.md`
  已把当前默认 Stage3 主线
  固定到:
  - `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
- 但到这一步为止，
  Stage3 仍然主要只有:
  - teacher-supervised proxy loss
  - fuller checkpoint eval
- 还没有一条正式的
  `可试听代理导出链路`

## 本轮目标
1. 不等最终 vocoder。
2. 先把当前默认 Stage3 checkpoint
   接到一条可重复执行的
   `proxy audio` 导出命令。
3. 让用户至少可以试听:
   - `input.wav`
   - `teacher_proxy.wav`
   - `student_proxy.wav`
4. 明确这条链路的能力边界，
   防止被误读成最终音质试听。

## 本轮实际完成

### 1. 新增正式命令
- 新增:
  - `export-streaming-student-proxy-audio`

### 2. 新增实现
- 新增:
  - `src/v5vc/streaming_student/proxy_audio_export.py`

### 3. 当前导出内容
- 对每条选中记录，
  同时导出:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`

说明:
- `teacher_proxy`
  直接用该记录对应的
  `teacher_acoustic`
  重建
- `student_proxy`
  则用 Stage3 当前预测的:
  - `energy`
  - `vuv_logits`
  - `aperiodicity`
  - `event_probs`
  通过保守映射
  组装成结构型代理 `acoustic`
  后再重建

### 4. 已完成 validation bundle 导出
- 执行:
  - `.\python.exe manage.py export-streaming-student-proxy-audio --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt --split-name target_validation --sample-count 3 --max-audio-sec 4.0 --output-dir reports/audio/streaming_student_proxy_audit_baseline48_step48_v1`

### 5. 已完成 special bundle 导出
- 执行:
  - `.\python.exe manage.py export-streaming-student-proxy-audio --checkpoint reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt --split-name target_special_eval --sample-count 3 --max-audio-sec 4.0 --output-dir reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1`

## 已生成正式产物

### validation bundle
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`

其中包含:
- `proxy_audio_export.json`
- `proxy_audio_export.md`
- `3` 条记录的:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`

### special bundle
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`

其中包含:
- `proxy_audio_export.json`
- `proxy_audio_export.md`
- `3` 条 `target_special_eval`
  记录的:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`

## 当前结果

### validation bundle
- 记录数:
  - `3`
- split:
  - `target_validation`
- 当前导出样本:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

### special bundle
- 记录数:
  - `3`
- split:
  - `target_special_eval`
- 当前导出样本:
  - `target::no_text_voice/chapter3_17_firefly_106`
  - `target::no_text_voice/chapter3_29_firefly_139`
  - `target::no_text_voice/chapter3_3_firefly_110`

### 工程验证
- 新命令 `--help`
  已通过
- validation bundle
  已成功生成完整 wav 与元数据
- special bundle
  已成功生成完整 wav 与元数据
- 每条导出记录
  的 `teacher_frame_count`
  与 `student_frame_count`
  当前均已对齐

## 当前最重要的结论

### 1. Stage3 现在已经首次具备
   正式可试听代理导出链路
- 这不是最终成品链路
- 但它已经让 Stage3
  从纯 loss / eval 比较
  进入:
  - 可做人工 gate 的试听阶段

### 2. 当前最有价值的听法
   不是只听 `student_proxy`
- 当前更推荐的相对试听顺序是:
  - `input.wav`
  - `teacher_proxy.wav`
  - `student_proxy.wav`
- 因为这样能先听出:
  - 原始结构
  - teacher 结构代理
  - student 是否在停顿、能量、稳定性上跟上 teacher

### 3. 这仍然不是最终用户试听
- 当前 `student_proxy`
  仍是启发式重建
- 它只能支持:
  - 粗结构审核
  - student/teacher gap 排查
  - 稳定性异常检查
- 不能支持:
  - 最终音质判断
  - speaker identity 判断
  - 细粒度 branch ranking

## 当前边界

### 1. `student_proxy`
   不是从最终声码器来的
- 它只是把当前 Stage3 预测头
  映射回一个低频、去音调化、
  结构优先的 audible proxy

### 2. `teacher_proxy`
   也不是真正 ground-truth audio
- 它只是用 teacher 的
  `acoustic`
  标签重建出的结构代理
- 适合拿来做
  `student vs teacher`
  的相对比较
- 不等于最终真实目标波形

### 3. 当前 bundle
   还不能直接证明
   最终链路已成立
- 它证明的是:
  - Stage3 已有正式试听入口
- 不是:
  - 最终用户可用音质
  - 最终 runtime conversion

## 下一步建议
1. 先对这两组 bundle
   做一轮用户试听，
   重点听:
   - `student_proxy`
     与
   - `teacher_proxy`
     的结构差距
2. 若当前 student/teacher
   在 proxy 结构上
   已比较接近，
   再决定是否继续推更长 horizon
   或开始接更接近成品的后续链路
3. 若当前 proxy 里
   已能明显暴露结构异常，
   则优先把问题回写到:
   - loss
   - 监督定义
   - 或 checkpoint 选择

## 一句话结论
- Stage3 现已首次拥有
  正式的 `input + teacher_proxy + student_proxy`
  试听导出链路；
  这让项目从纯 proxy loss 比较
  前进到了可做人耳结构 gate 的阶段，
  但它仍然不是最终 vocoder 试听。
