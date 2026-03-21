# 2026-03-21 `teacher-first / single-target` 终端用户线设计文档

## 目标
- 当前终端用户线的目标不是：
  - many-to-many
  - 最终成品级质量
  - student 主路径
  - final adversarial vocoder
- 当前目标是：
  - 在现有仓库资产上，
    交付一条
    `source audio -> target audio`
    的最小可运行闭环
  - 让终端用户能够输入一段源音频，
    得到一段目标音频，
    并保留必要中间产物用于排障

## 为什么现在要单独拆出这条线
- 当前实验线已经推进到：
  - `step72__decode_gate_smooth3_postenv`
    待审主分支
  - 下一步是 focused human audit
- 但这条线主要回答的是：
  - 哪个 decode-side 分支更健康
  - 哪个 validation 听审主线更合理
- 它不直接回答：
  - 终端用户现在能不能输入一段源音频，
    让系统真正跑起来
- 所以终端用户线必须从当前实验线中独立出来，
  单独定义：
  - 输入输出契约
  - 可复用资产
  - validation-only 禁用项
  - 最小验收标准

## 当前可直接复用的资产

### 1. 源侧控制预测
- 已有正式 teacher runtime wrapper：
  - `src/v5vc/offline_teacher_runtime.py`
- 已有正式 CLI：
  - `run-offline-mvp-teacher-runtime`
- 当前能力：
  - 输入任意源音频
  - 输出 teacher 控制张量
  - 支持 chunked runtime

### 2. 下游控制合同
- 已有正式 contract exporter：
  - `src/v5vc/offline_teacher_downstream_contract.py`
- 已有正式 CLI：
  - `export-offline-mvp-teacher-downstream-contract`
- 当前能力：
  - 输出
    `teacher_downstream_control_contract.pt`
  - 同时带上目标 conditioning：
    - `s_spk_target`
    - `s_geom_target`
    - `alpha`

### 3. consumer-side 桥接
- 已有 consumer-side scaffold：
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
- 已有正式 CLI：
  - `build-offline-mvp-teacher-vocoder-input-scaffold`
- 当前能力：
  - 把 teacher contract
    转成 vocoder 双支路输入特征

### 4. 目标侧 decoder / vocoder checkpoint
- 已有 Stage5 no-res vocoder 训练与 checkpoint
- 已有 waveform 重建与导出逻辑：
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/offline_vocoder_training.py`
- 当前能力说明：
  - 已能从训练包特征
    前向得到
    `waveform_frames`
  - 已能通过 overlap-add
    重建
    `decoded.wav`

## 当前不能直接复用到用户线的能力

### 1. `aligned_target.wav`
- 用户线没有 paired target reference，
  所以不能假设存在：
  - `aligned_target.wav`
  - `decoded_to_target_rms_ratio`
  - target-relative validation 指标

### 2. `decoded_pitch_matched.wav`
- 当前 pitch-match
  的参考是：
  - `aligned_target`
- 用户线没有这个参考，
  所以当前实现不能直接复用

### 3. `audit_proxy.wav`
- 当前 audit proxy
  依赖：
  - `aligned_target`
    提供静音 gate
- 用户线没有目标参考音频，
  所以当前版本默认不应承诺 audit proxy

### 4. low-activity probe / governance / GUI compare
- 这些都建立在：
  - 多 bundle
  - paired validation
  - suspicious windows 排序
  之上
- 它们属于实验线，
  不是终端用户线的第一阶段目标

## 当前更准确的工程判断
- 仓库当前已经具备：
  - 目标侧训练与导出链
  - validation 样本级可听 wav
  - 人工听审与治理工具
- 但还没有一条正式命令完成：
  - 任意 `input_audio`
  - 经 teacher-first 控制预测
  - 进入下游 no-res vocoder
  - 导出最终 `decoded.wav`

## 终端用户线的建议范围

### 1. 第一阶段只做 single-target
- 默认只支持单目标预设
- conditioning 直接来自现有 calibration asset
- 不在这一阶段承诺：
  - 多目标切换
  - many-to-many
  - 用户自定义 target embedding

### 2. 第一阶段只做 teacher-first
- 不等待 student
- 不把 student 训练作为当前 blocker
- teacher 直接作为源侧控制预测器

### 3. 第一阶段只做最小可运行闭环
- 先保证：
  - 跑得通
  - 能稳定落盘
  - 有基础 summary
- 不要求：
  - 成品级自然度
  - 完整 pitch fidelity
  - 多种诊断 sidecar 一次到位

## 建议新增的正式入口

### 命令名建议
- `run-offline-mvp-teacher-first-vc-demo`

### 最小输入
- `--input-audio <wav>`
- `--output-dir <dir>`

### 可选输入
- `--teacher-route-handoff`
- `--teacher-checkpoint`
- `--calibration-asset`
- `--vocoder-checkpoint`
- `--vocoder-checkpoint-selection`
- `--selection-target stable_late_stop`
- `--chunk-samples` / `--chunk-ms`
- `--device`
- `--max-audio-sec`
- `--predicted-activity-gate-smoothing-frames`
- `--predicted-activity-gate-floor`
- `--predicted-activity-gate-apply-mode`
- `--save-intermediates`

### 第一阶段不建议暴露的参数
- `--pitch-match-reference aligned_target`
- 任何依赖
  `aligned_target`
  的 audit-only 参数
- 多目标 speaker 切换参数

## 建议输出

### 1. 用户主输出
- `decoded.wav`

### 2. 调试资产
- `teacher_downstream_control_contract.pt`
- `teacher_vocoder_input_scaffold.pt`
- `run_summary.json`
- `run_summary.md`

### 3. 当前不承诺的输出
- `aligned_target.wav`
- `decoded_pitch_matched.wav`
- `audit_proxy.wav`
- validation-style
  `loss_metrics`

## 建议实现路径

### 方案 A：新增一条一站式 orchestration 命令
- 步骤：
  1. 读入源音频
  2. 运行 teacher runtime / contract exporter
  3. 构建 vocoder input scaffold
  4. 加载指定 Stage5 checkpoint
  5. 前向得到 `waveform_frames`
  6. 直接做 OLA 重建
  7. 输出 `decoded.wav`
- 优点：
  - 最符合终端用户心智
  - 一条命令即可判断“能不能跑”
- 缺点：
  - 需要新写一层 orchestration
  - 需要补新的 summary 契约

### 方案 B：先做脚本级串联，不急着上新 CLI
- 步骤：
  - 用现有三个命令和一段内部 glue code 串起来
- 优点：
  - 开发快
  - 有利于先验证技术可行性
- 缺点：
  - 对终端用户不友好
  - 很容易变成临时脚本长期存活

### 当前建议
- 建议采用：
  - 方案 A
- 理由：
  - 终端用户线的核心价值
    就是交付一个真正的一站式入口
  - 如果继续停在脚本拼接，
    很容易再次滑回
    “研究线资产很多，
    用户入口仍不存在”

## 与实验线的接口边界

### 1. 当前用户线不要阻塞在 `postenv` 听审结果上
- 终端用户线可以先把：
  - `predicted_activity_gate_apply_mode`
    设计成显式可选参数
- 当前默认值
  暂时仍沿正式主线
  `smooth3`
  所在设置

### 2. 实验线结论落锤后再决定是否改默认
- 若 focused human audit
  支持
  `postenv`
  不反转，
  再把用户线默认 apply mode
  升过去
- 在那之前，
  终端用户线只需要做到：
  - 能跑
  - 可显式切换

## 第一阶段验收标准
1. 一条正式命令可运行
2. 输入一段源音频后，
   能稳定导出：
   - `decoded.wav`
   - 运行摘要
   - 中间 contract/scaffold
3. 运行过程中不依赖：
   - `aligned_target`
   - validation package
   - paired target 音频
4. 默认目标为单目标预设，
   不承诺 many-to-many
5. 若运行失败，
   summary 中能明确指出失败发生在：
   - teacher runtime
   - contract
   - scaffold
   - vocoder checkpoint
   - waveform reconstruction

## 非目标
- 本阶段不是：
  - final product quality review
  - many-to-many demo
  - student promotion
  - 最终成品 pitch 修复
  - 完整 GUI 用户产品

## 当前推荐的下一步
1. 新增一条
   `teacher-first / single-target`
   的 orchestration 命令
2. 先让它输出：
   - `decoded.wav`
   - `run_summary.json`
   - 中间 contract/scaffold
3. 第一轮只支持：
   - 单目标 calibration
   - 指定 Stage5 checkpoint
4. 代码结构上显式避免依赖：
   - `aligned_target`
   - pitch-match
   - audit proxy

## 一句话结论
- 终端用户线当前最合理的定义不是
  “继续证明 Stage5 validation 导出能听”，
  而是：
  用现有 teacher-first 与 Stage5 资产，
  真正补出一条
  `source audio -> target audio`
  的 single-target 最小闭环入口。
