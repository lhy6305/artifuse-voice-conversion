# 2026-03-24 Stage5 `contract_v2` Phase C1 代码落地启动报告

## 结论
- `C-prime`
  的第一批实验线代码已开始落地，
  不再是纯方案状态。
- 当前已完成的范围是：
  - `teacher_downstream_control_contract_v2`
    的首版导出
  - `v2-core`
    的 source acoustic state
    提取链接入
  - scaffold / training package
    对 `v2-core`
    的首版消费
- 当前仍未做的范围是：
  - 真实 teacher checkpoint
    上的正式整链导出
  - dataset 级
    package smoke
  - Stage5 no-res baseline
    重训

## 本轮代码改动

### 1. 新增 source acoustic state extraction
- 新增：
  - `src/v5vc/source_acoustic_state_extraction.py`
- 当前首版口径：
  - `f0_hz`
    使用确定性自相关峰值估计
  - `vuv`
    由周期性峰值
    与能量共同构成
    `[0, 1]`
    概率
  - `aper`
    采用
    `aper-v1`
    单标量 per-frame
    谐波能量占比反推口径
  - `E`
    使用与 Stage5
    frame/hop 对齐的
    `log-RMS`

### 2. `teacher_downstream_control_contract_v2` 已接入
- 更新：
  - `src/v5vc/offline_teacher_downstream_contract.py`
- 当前行为：
  - contract tensor / json / md
    默认导出
    `offline_teacher_downstream_control_v2`
  - 新增正式字段：
    - `f0_hz`
    - `vuv`
    - `aper`
    - `E`
  - 同时保留：
    - `energy_proxy`
    - `voiced_proxy`
    - `aperiodicity_proxy`
    等旧 proxy
    作为诊断兼容层
- 当前仍明确缺失：
  - `r_res`
  - `final_vocoder_waveform`

### 3. scaffold 已开始真正消费 `v2-core`
- 更新：
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
- 当前首版分支输入：
  - periodic:
    `z_art + f0_hz + vuv + E + alpha + s_spk_target + s_geom_target`
  - noise:
    `event_probs + aper + vuv + E + alpha + s_spk_target + s_geom_target`
- 当前仍保持：
  - 对旧
    `contract_v1`
    的兼容读取

### 4. Stage5 training package 已开始支持 `v2`
- 更新：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/offline_vocoder_scaffold.py`
- 当前行为：
  - `scaffold_v2`
    可生成
    `training_package_v2`
  - `periodic_gate_target`
    由
    `vuv`
    提供
  - `noise_gate_target`
    使用
    `max(aper, event_presence_proxy)`
  - 旧
    `v1`
    scaffold / package
    仍可继续读取

## 本轮最小验证
- 已完成：
  - `compileall`
    编译检查
  - 人工构造
    `contract_v2`
    最小 payload
    的
    `contract -> scaffold -> training package`
    链路 smoke
- smoke 结果：
  - `scaffold_version`
    成功落为：
    `offline_teacher_vocoder_input_scaffold_v2`
  - `training_package_version`
    成功落为：
    `offline_mvp_nores_vocoder_train_targets_v2`
  - 分支输入张量形状正常生成
- 另已完成：
  - 真实短音频
    `segment_0001_0000020110_0000021640.wav`
    上的直接函数链路 smoke
  - 已确认真实
    `contract_v2 -> scaffold_v2 -> training_package_v2`
    能连续生成

## 当前真实 smoke 观察
- 当前真实 smoke
  导出的统计显示：
  - `voiced_ratio ≈ 0.319`
  - `f0_mean ≈ 385.6 Hz`
  - `f0_max ≈ 551.7 Hz`
- 这说明：
  - 第一版
    source acoustic state extraction
    已经可跑
  - 但
    `vuv / f0`
    的校准仍偏粗，
    还不能直接当作
    “声学口径已完全站稳”

## 当前边界与风险
- 当前 source acoustic state
  是第一版工程实现，
  目标是先把
  `v2-core`
  contract
  立起来，
  不是最终声学真值方案。
- 当前尚未证明：
  - 真实 teacher checkpoint
    导出的
    `f0_hz / vuv / aper / E`
    在更多样例上的统计是否稳定
  - dataset 级 package
    批量导出速度与一致性
  - 重训后
    no-res baseline
    是否脱离 buzz

## 下一步
1. 用真实 teacher checkpoint
   扩大到多条短样例，
   继续检查
   `f0_hz / vuv / aper / E`
   的统计与边界案例，
   先把
   `vuv / f0`
   校准到更可信区间。
2. 跑最小 dataset package smoke，
   确认
   `build_offline_mvp_nores_vocoder_dataset_packages`
   在真实数据上
   可稳定生成
   `v2` 包。
3. 在不改 waveform objective
   主项的前提下，
   启动第一轮
   `C3`
   no-res baseline
   重训。

## 一句话结论
- `contract_v2`
  的 Phase C1
  已从文档方案
  进入代码状态；
  当前可以把下一轮默认起点
  改成：
  - 真实导出验证
  - dataset smoke
  - no-res baseline
    重训准备
