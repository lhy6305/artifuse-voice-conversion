# 182. no-residual vocoder full-split export budget 报告

## 背景
- `docs/181_nores_vocoder_dataset_throughput_probe_report.md`
  已经拿到两组 Stage5 dataset probe:
  - shortest-duration lower-bound
  - file-order 较长样本对照
- 当前还缺:
  - 面向正式 split
    的粗预算

## 本轮目标
1. 统计 `round1_1`
   正式 target split
   的总记录数与总时长
2. 基于已有 probe
   给出:
   - 全量 package 导出时长
   - 全量 package 体积
     的粗预算
3. 用这个预算回答:
   - 当前是否必须先做 cache / packed loader

## 正式 split 统计
- `target_train.jsonl`
  - `592` 条
  - `3645.610714 sec`
- `target_validation.jsonl`
  - `66` 条
  - `407.451586 sec`
- 合计:
  - `658` 条
  - `4053.0623 sec`

说明:
- 本页预算只覆盖:
  - `target_train + target_validation`
- 不把
  `target_special_eval`
  混进正式训练导出预算

## probe 回顾

### shortest-duration lower-bound
- package 数:
  - `10`
- 总音频时长:
  - `6.156915 sec`
- 总导出耗时:
  - `0.805575 sec`
- 总体积:
  - `3926325 bytes`

### file-order 较长样本对照
- package 数:
  - `4`
- 总音频时长:
  - `44.724944 sec`
- 总导出耗时:
  - `1.956294 sec`
- 总体积:
  - `26733221 bytes`

## 线性粗拟合

为了不直接拿 shortest probe
硬外推，
本页用两组 probe
做一个最小线性拟合:

- `export_time ~= package_overhead + audio_duration_term`
- `export_size ~= package_overhead + audio_duration_term`

拟合结果:
- 时间模型:
  - `time_overhead_per_package_sec = 0.056752`
  - `time_per_audio_sec = 0.038665`
- 体积模型:
  - `bytes_overhead_per_package = 26052.84`
  - `bytes_per_audio_sec = 595395.04`

## full-split 粗预算
- package 数:
  - `658`
- 总音频时长:
  - `4053.0623 sec`
- 估计导出耗时:
  - `194.054 sec`
  - `3.234 min`
- 估计总包体积:
  - `2430315959 bytes`
  - `2.263 GiB`

## 当前判断

### 1. 当前 full-split 导出不算夸张
- 按这组粗预算，
  Stage5 package export
  量级大约是:
  - 数分钟
  - 数 GiB
- 这说明:
  - 当前还没有立刻逼到
    “必须先做大规模基础设施重构”

### 2. 但也已经足够大到值得提前管控
- `~2.26 GiB`
  不是可以完全无视的量级
- 如果后面继续叠:
  - 多版本 package
  - 不同 target objective
  - 多轮 rerun
- 体积很快就会继续放大

### 3. 当前更像“可以先继续，但要留后手”
- 现在最合理的理解不是:
  - 立刻停下先重写 loader
- 而是:
  - 可以先继续做一版 full-split package export
    或更大 subset 验证
  - 同时把
    cache / packed loader
    保持为下一优先级准备项

## 当前边界
- 这仍是:
  - probe-based budget
  - 不是 full export 实测
- 线性拟合只用了:
  - 两组 probe
- 所以它更适合解释为:
  - first-pass engineering estimate
- 不适合写成:
  - final throughput commitment

## 下一步
1. 先跑一版更接近 full split
   的 package export 实测，
   验证:
   - `~3.2 min / ~2.26 GiB`
     这一估计是否站得住
2. 若实测明显高于预算，
   立即转向:
   - package cache
   - packed loader
   - bucket 化
3. 若实测接近预算，
   则可以先继续:
   - Stage5 dataset-level proxy training
   再决定什么时候切 decoder 目标

## 一句话结论
- 依据当前 probe 的粗预算，
  Stage5 `target_train + target_validation`
  全量 package 导出大约在
  `3.2 分钟 / 2.26 GiB`
  量级；
  这还没到必须先重写 loader 的程度，
  但已经足够提示后续要把
  cache / packed loader
  当作明确候选项。
