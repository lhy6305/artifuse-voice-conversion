# 2026-03-24 Stage5 `contract_v2` 校准与重训前准备 smoke 报告

## 结论
- 本轮未启动重训，
  先完成了：
  - `v2-core`
    source acoustic state
    校准 smoke
  - Stage5 dataset package
    的最小预检
- 当前结论是：
  - `contract_v2`
    的接口层与分包层
    已经进入
    “可作为重训前准备继续推进”
    的状态
  - 当前主要阻塞
    不再是
    “代码还没接起来”
  - 而是：
    - 继续扩大
      `vuv / f0`
      的真实样例校准覆盖

## 一、source acoustic state 校准 smoke

### 审计入口
- 已新增：
  - `src/v5vc/source_acoustic_state_audit.py`
- 已接入 CLI：
  - `audit-source-acoustic-state`
- 当前默认审计样例：
  1. `segment_0001_0000020110_0000021640.wav`
  2. `segment_0061_0000300400_0000300910.wav`
  3. `peak_011_0002370615_top_peak.wav`

### 本轮关键实现修正
- 当前不再直接用
  Stage5
  单帧长度
  `frame_length = 400`
  去做
  `f0 / vuv / aper`
  估计
- 当前改为：
  - 时间轴仍对齐
    teacher runtime
    的 frame/hop
  - 但分析窗扩到：
    `analysis_frame_length = 2880`
- 这次修正后，
  `f0`
  不再稳定落在
  明显偏高区间

### 本轮审计结果
- `segment_0001_0000020110_0000021640.wav`
  - `voiced_ratio = 0.739606`
  - `f0_p90_hz_nonzero = 154.340836`
  - `f0_max_hz = 162.16217`
- `segment_0061_0000300400_0000300910.wav`
  - `voiced_ratio = 0.298013`
  - `f0_p90_hz_nonzero = 205.656448`
  - `f0_max_hz = 208.695648`
- `peak_011_0002370615_top_peak.wav`
  - `voiced_ratio = 0.940191`
  - `f0_p90_hz_nonzero = 372.093018`
  - `high_f0_ratio_ge_400hz = 0.07177`

### 当前判断
- 这三条固定短样例上，
  当前
  `vuv / f0`
  已明显好于上一版：
  - 不再大面积
    `f0_hz = 0`
  - 也不再普遍落到
    `500Hz+`
    偏高区
- 但还不能写成：
  - “校准已彻底完成”
- 仍需继续扩大到：
  - 更多 source 短样例
  - 更多 target 短句
  - 更安静 / 更强峰值
    的边界案例

## 二、重训前 package 预检

### 本轮执行
- 已直接调用：
  - `build_offline_mvp_nores_vocoder_dataset_packages(...)`
- 预检输入：
  - train:
    `target_train.jsonl`
    中最短样本 1 条
  - validation:
    `target_validation.jsonl`
    中最短样本 1 条
- 运行方式：
  - `cpu`
  - `selection_mode = shortest_duration`
  - `max_audio_sec = 2.0`
  - `verify_against_full_pass = false`

### 结果
- dataset index
  成功生成：
  - `offline_mvp_nores_vocoder_dataset_index_v1`
- train package
  成功生成为：
  - `offline_mvp_nores_vocoder_train_targets_v2`
- scaffold
  成功生成为：
  - `offline_teacher_vocoder_input_scaffold_v2`
- 本轮最短 train 样本：
  - `target::chapter3_22_firefly_105`
  - `duration_sec = 0.229002`
  - `frame_count = 61`
- 本轮最短 validation 样本：
  - `target::chapter3_3_firefly_162`
  - `duration_sec = 0.612993`
  - `frame_count = 167`

### 当前判断
- 这说明：
  - `contract_v2`
    已经不是孤立接口改动
  - 它可以真实穿过：
    - contract
    - scaffold
    - train package
    - dataset index
      这条重训前必经链路

## 三、当前剩余阻塞项

### 1. 校准仍需扩样例
- 当前审计样例仍偏少，
  只能证明：
  - 第一版口径
    不再明显失真
- 还不能证明：
  - 在更多 source / target
    短句上
    统计都稳定

### 2. CLI 入口的指定输出目录行为还需单独复核
- 本轮观察到：
  - 通过
    `python -m v5vc.cli ...`
    调命令时，
    指定 `tmp` 输出目录
    有一次未稳定落盘
- 当前直接函数调用
  已可稳定产出，
  因此不构成
  `contract_v2`
  的主阻塞
- 但在真正交付批量命令前，
  仍建议单独复核
  CLI 入口行为

## 四、下一步
1. 用
   `audit-source-acoustic-state`
   扩到更多真实短样例，
   继续校准：
   - `voiced_ratio`
   - `f0_p90`
   - `high_f0_ratio`
2. 用更接近正式训练规模的
   目标样例子集，
   再跑一轮 dataset package smoke，
   观察：
   - 速度
   - 版本一致性
   - 样本统计分布
3. 等上述两项都通过后，
   再进入：
   - `C3`
     no-res baseline
     重训

## 一句话结论
- 当前
  `contract_v2`
  的校准和重训前准备
  已经跨过
  “接口未打通”
  阶段；
  下一轮重点应转为：
  - 扩样例校准
  - 扩分包 smoke
  而不是继续回头补
  `contract_v2`
  基础接口。
