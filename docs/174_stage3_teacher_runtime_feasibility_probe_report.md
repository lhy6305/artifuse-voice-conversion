# 174. Stage3 teacher runtime feasibility probe 报告

## 背景
- 用户已完成一轮非正式试听，
  并提出新的路线判断问题:
  - 如果当前 `offline_mvp teacher`
    在本机上已经足够快，
    是否可以直接跳过
    `streaming_student`
    训练，
    先把 teacher
    投入下一环节
- 这次问题不能只靠印象回答，
  需要同时确认:
  - 本机吞吐 / 延迟
  - teacher 结构上
    是否真的接近流式

## 本次检查范围
### 1. 结构边界检查
- 当前正式 teacher
  仍是 route handoff 默认锚点:
  - `EXP-20260316-043-offline-mvp-d87-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-lateretention-200step-calibration`
- 关键配置:
  - `uses_text_in_runtime = false`
  - `frame_length = 400`
  - `hop_length = 160`
- 在模型实现里，
  `z_art / event / acoustic`
  的主路径是:
  - 先把 waveform 切成局部帧
  - 再做逐帧 MLP 编码与控制融合
  - 没有 RNN / attention /
    整句级跨帧状态
- 唯一带全句聚合的是
  `text_aux`
  的 `pooled_hidden`
  头，
  但 d87 配置已经写明:
  - runtime 不使用 text
  - 所以这部分
    不是当前 runtime 的阻塞项

### 2. 本机速度基准
- 基准对象:
  - 当前正式 teacher checkpoint
    `EXP-20260316-043.step200.pt`
- 基准数据:
  - `target_validation + target_special_eval`
  - 共 `74` 条记录
  - 音频长度截到
    当前正式配置上限
    `2.0 sec`
- 计时口径:
  - 单条 utterance
    `waveform -> teacher control outputs`
  - 包含 host/device tensor movement
  - 不包含:
    - 磁盘 I/O
    - vocoder
    - 未来 runtime wrapper
- 产物:
  - `reports/eval/offline_mvp_teacher_runtime_probe_current_machine_d87/teacher_runtime_probe.json`
  - `reports/eval/offline_mvp_teacher_runtime_probe_current_machine_d87/teacher_runtime_probe.md`

## 量化结果
### 当前机器
- `torch = 2.5.0+cu124`
- `cuda_available = true`
- `GPU = NVIDIA GeForce RTX 3060 Laptop GPU`

### 数据集长度分布
- record_count = `74`
- min_audio_sec = `0.470998`
- median_audio_sec = `2.0`
- max_audio_sec = `2.0`

### CPU 单条推理
- avg_latency_ms = `6.952321`
- p95_latency_ms = `11.633498`
- max_latency_ms = `14.175917`
- avg_rtf = `0.003812657`
- p95_rtf = `0.005816748`
- max_rtf = `0.007087958`
- avg_per_frame_ms = `0.013900021`
- p95_per_frame_ms = `0.021190341`
- max_per_frame_ms = `0.025821342`

### GPU 单条推理
- avg_latency_ms = `1.481529`
- p95_latency_ms = `2.46726`
- max_latency_ms = `2.580416`
- avg_rtf = `0.000949361`
- p95_rtf = `0.002383867`
- max_rtf = `0.004366807`
- avg_per_frame_ms = `0.003465475`
- p95_per_frame_ms = `0.008720882`
- max_per_frame_ms = `0.016068406`

## 解释
### 1. 单看速度，teacher 远快于实时
- 当前帧设置下:
  - `sample_rate = 44100`
  - `frame_length = 400`
  - `hop_length = 160`
  - 对应:
    - `frame_ms = 9.070295`
    - `hop_ms = 3.628118`
- 即使按更严格的
  per-frame 成本看，
  CPU `p95_per_frame_ms`
  也只有:
  - `0.021190341 ms`
- 这比当前 hop 间隔
  `3.628118 ms`
  小两个数量级以上

### 2. 结构上也没有强离线依赖
- 这次不是“teacher 很快，
  但结构上仍是整句模型”
- 更准确地说:
  - 主控制路径只依赖局部帧窗口
  - runtime 不依赖 text
  - 没有显式 future-context stack
- 所以从控制预测角度，
  它已经足够接近
  直接流式部署

### 3. 当前还不能误写成“完整端到端实时语音系统已完成”
- 仓库当前仍然没有:
  - 正式 teacher runtime CLI
  - 端到端 waveform synthesis / vocoder
  - 面向在线调用的包装接口
- 所以本次结论只成立到:
  - “teacher 作为控制预测器，
     已足以直接投入下一环节”
- 还不能写成:
  - “当前仓库已经具备
     完整最终语音的实时推理产品链路”

## 结论
- 这次本机实测的结论是:
  - 可以
- 不是“勉强可以”，
  而是:
  - teacher 在当前机器上
    已明显快于实时预算
  - 且结构上没有
    必须依赖整句未来信息的
    主路径阻塞

- 因此当前更合理的路线是:
  - 暂停继续推进
    `streaming_student`
    训练线
  - 直接把当前正式 teacher
    作为下一环节的
    控制预测器基线

## 对下一步的影响
1. Stage3 student 训练
   不再是当前最高优先级
2. 下一步应转向:
   - teacher runtime wrapper
   - teacher 控制输出到下一模块的接线
   - 必要时补最小在线缓存 / 滑窗接口
3. 若后续还要保留 student 线，
   其理由应改成:
   - 模块统一
   - 未来共享前端 / `r_res`
   - 部署形态约束
   而不再是:
   - “teacher 太慢所以必须 student”
