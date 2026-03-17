# 175. teacher runtime wrapper 与 streaming smoke test 报告

## 背景
- 在 `docs/174_stage3_teacher_runtime_feasibility_probe_report.md`
  里，
  已确认:
  - 当前正式 teacher
    在本机上
    速度明显快于实时
  - 因而当前主线
    应从 `student training`
    切到 `teacher-first`
- 所以下一步不再是
  继续训 student，
  而是把 teacher
  变成一个
  真正可调用的
  runtime wrapper

## 本轮目标
1. 正式新增
   teacher runtime 代码入口
2. 支持分块输入、
   尾样本缓存、
   连续输出新增控制帧
3. 用真实音频验证:
   - 分块 runtime 输出
   - 是否与整句 full pass
     对齐

## 本轮代码落地
### 1. 新增 teacher runtime 模块
- 新增:
  - `src/v5vc/offline_teacher_runtime.py`
- 当前能力:
  - 从 formal route handoff
    或显式 checkpoint
    加载 teacher
  - 对单条 wav
    做 chunked runtime
  - 输出:
    - `hidden`
    - `fused_hidden`
    - `z_art`
    - `event_logits`
    - `event_probs`
    - `acoustic`
  - 同时落盘:
    - `teacher_runtime_streaming_outputs.pt`
    - `teacher_runtime_summary.json`
    - `teacher_runtime_summary.md`

### 2. 新增 CLI 入口
- 新增命令:

```powershell
.\python.exe manage.py run-offline-mvp-teacher-runtime --input-audio <wav>
```

- 当前关键参数:
  - `--route-handoff`
  - `--checkpoint`
  - `--chunk-samples`
  - `--chunk-ms`
  - `--device`
  - `--max-audio-sec`
  - `--skip-full-pass-verify`

## 关键实现点
### 1. runtime 只输出下游真正需要的控制量
- 没有把 `text_aux`
  当成 streaming 必需输出
- 理由是:
  - 当前 d87 配置
    `uses_text_in_runtime = false`
  - `text_aux`
    还带 pooled whole-utterance 语义，
    不适合作为当前最小 streaming 合同

### 2. 尾帧 flush 逻辑已对齐 teacher 原始 full pass
- 初版 wrapper
  在 stream 结束时
  会把尾部不足一帧的残留样本
  也补成最后一帧
- 这会导致:
  - `streaming frame_count`
    比 full pass
    多 `1`
- 已修正为:
  - 只有当整条音频
    从头到尾都不足一帧时，
    才允许 pad 出
    唯一一帧
  - 只要已经产生过
    正常帧，
    尾部残留就直接丢弃，
    与原 teacher 行为保持一致

## smoke test
### 样本 1: 短样本
- 输入:
  - `data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav`
- 命令:

```powershell
.\python.exe manage.py run-offline-mvp-teacher-runtime --input-audio data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav --output-dir reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_3_firefly_162 --chunk-samples 2048 --device cpu
```

- 结果:
  - `streaming_frame_count = 167`
  - `frame_count_equal = true`
  - `frame_alignment_equal = true`
  - 各控制张量
    `max_abs_diff`
    在 `1e-6` 量级，
    且全部满足
    `allclose_atol_5e-6 = true`

### 样本 2: 2 秒长样本
- 输入:
  - `data_convert/dataset_firefly_raw/chapter3_2_firefly_178.wav`
- 命令:

```powershell
.\python.exe manage.py run-offline-mvp-teacher-runtime --input-audio data_convert/dataset_firefly_raw/chapter3_2_firefly_178.wav --output-dir reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_2_firefly_178 --chunk-samples 1024 --device cpu --max-audio-sec 2.0
```

- 结果:
  - `streaming_frame_count = 549`
  - `frame_count_equal = true`
  - `frame_alignment_equal = true`
  - 各控制张量
    `max_abs_diff`
    仍在 `3e-6`
    以内，
    全部满足
    `allclose_atol_5e-6 = true`

## 当前判断
- 现在不只是
  “teacher 足够快”
- 而是:
  - teacher 已有正式 runtime wrapper
  - chunked 输出与 full pass
    在控制层面严格对齐到
    工程可接受的浮点误差范围

- 因此当前主线可以正式写成:
  - 暂停 `streaming_student`
    训练推进
  - 直接用 teacher
    做下一环节接线

## 当前产物
- 代码:
  - `src/v5vc/offline_teacher_runtime.py`
  - `src/v5vc/cli.py`
- smoke test 产物:
  - `reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_3_firefly_162/`
  - `reports/runtime/offline_mvp_teacher_runtime_smoke_chapter3_2_firefly_178/`

## 下一步
1. 以当前 runtime wrapper
   输出的控制张量
   作为下游模块的输入合同
2. 若需要更接近在线调用，
   再补:
   - session 级状态对象
   - 更明确的 chunk API
   - 批量 / socket / service 包装
3. 在出现真实部署约束前，
   不再优先恢复
   `student` 训练线
