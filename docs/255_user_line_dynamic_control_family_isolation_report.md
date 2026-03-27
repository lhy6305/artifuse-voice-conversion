# 2026-03-21 用户线动态控制 family 隔离试验报告

## 结论
- 本轮把
  `analyze-offline-mvp-teacher-first-vc-decoder-behavior`
  正式补齐为可接收：
  - `--control-family-override family=mode`
- 在同一组用户线 triplet case
  上完成首轮 family-level
  替换后，
  当前更准确的判断是：
  - `z_art`
    与
    `event_probs`
    不是当前 buzzing
    的主杠杆
  - proxy family
    里真正最有信息量的，
    更接近：
    `noise_energy_proxy`
  - 但任何单一 family
    的替换，
    都没有把
    `decoded_spectral_high_band_energy_ratio`
    从
    `~0.48`
    拉回训练内参考
    `~0.0645`
- 所以当前不能把问题写成：
  - “已经找到唯一根因”
- 更合理的写法是：
  - 已定位到
    noise-side energy proxy semantics
    是当前最强局部杠杆
  - 但整体适用性失配
    仍未被单 family
    替换消掉

## 本轮代码变更
- `src/v5vc/cli.py`
  - 为
    `analyze-offline-mvp-teacher-first-vc-decoder-behavior`
    新增
    `--control-family-override`
- `src/v5vc/teacher_first_vc_demo.py`
  - 正式接通
    family-level
    override
  - 新增更细的
    `periodic_energy_proxy`
    与
    `noise_energy_proxy`
    probe alias

## 本轮 probe 范围

### 固定 triplet case
- `segment_0001_0000020110_0000021640.wav`
- `segment_0061_0000300400_0000300910.wav`
- `peak_011_0002370615_top_peak.wav`

### 基线
- `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/review_bundle_triplet_decoder_behavior_probe/`

### 第一轮 family 替换
- `z_art=reference_mean`
  - `.../review_bundle_triplet_decoder_behavior_zartref_probe/`
- `event_probs=reference_mean`
  - `.../rbt_db_evtref_probe/`
- `proxy_family=reference_mean`
  - `.../rbt_db_pfref_probe/`

### proxy family 细分
- `voiced_proxy=reference_mean`
  - `.../rbt_db_vpref_probe/`
- `energy_proxy=reference_mean`
  - `.../rbt_db_eproxyref_probe/`
- `aperiodicity_proxy=reference_mean`
  - `.../rbt_db_aperref_probe/`
- `event_presence_proxy=reference_mean`
  - `.../rbt_db_evtpresref_probe/`
- `energy_change_proxy=reference_mean`
  - `.../rbt_db_echgref_probe/`
- `periodic_energy_proxy=reference_mean`
  - `.../rbt_db_peref_probe/`
- `noise_energy_proxy=reference_mean`
  - `.../rbt_db_neref_probe/`

## 关键结果

### 1. `z_art` 与 `event_probs` 没有给出“主杠杆”信号
- 常规 segment
  上：
  - baseline:
    `HF=0.479510`
  - `z_art=reference_mean`:
    `HF=0.481074`
  - `event_probs=reference_mean`:
    `HF=0.479400`
- peak case
  上：
  - baseline:
    `HF=0.477874`
  - `z_art=reference_mean`:
    `HF=0.490003`
  - `event_probs=reference_mean`:
    `HF=0.476529`
- 更准确的解释是：
  - `z_art`
    甚至会把一部分 case
    推得更差
  - `event_probs`
    只有轻微扰动，
    不是当前最值钱的方向

### 2. proxy family 里真正有信息量的是 energy proxy，而不是其他单 proxy
- 常规 segment：
  - baseline:
    `HF=0.479510`
    `centroid=3303.06`
  - `energy_proxy=reference_mean`:
    `HF=0.476588`
    `centroid=3262.89`
  - `voiced_proxy=reference_mean`:
    `HF=0.479576`
    `centroid=3303.71`
  - `aperiodicity_proxy=reference_mean`:
    `HF=0.479548`
    `centroid=3303.38`
- peak case：
  - baseline:
    `HF=0.477874`
    `centroid=3283.61`
    `abs_z_median=2.875917`
  - `energy_proxy=reference_mean`:
    `HF=0.475601`
    `centroid=3244.11`
    `abs_z_median=2.212766`
  - 其余单 proxy
    只带来很小变化，
    或没有同等级改善
- 说明：
  - proxy family
    的主要信号
    不是均匀分布在所有 proxy 子项上，
    而更集中在
    energy proxy

### 3. `energy_proxy` 再细分后，主杠杆更接近 noise-side，而不是 periodic-side
- 常规 segment：
  - baseline:
    `HF=0.479510`
    `centroid=3303.06`
  - `periodic_energy_proxy=reference_mean`:
    `HF=0.480834`
    `centroid=3328.91`
  - `noise_energy_proxy=reference_mean`:
    `HF=0.477369`
    `centroid=3290.61`
- peak case：
  - baseline:
    `HF=0.477874`
    `centroid=3283.61`
    `abs_z_median=2.875917`
  - `periodic_energy_proxy=reference_mean`:
    `HF=0.479411`
    `centroid=3316.41`
    `abs_z_median=5.351823`
  - `noise_energy_proxy=reference_mean`:
    `HF=0.476625`
    `centroid=3276.44`
    `abs_z_median=2.344595`
- 当前更合理的工程判断是：
  - periodic-side
    energy proxy
    不是缓解方向，
    甚至会恶化
  - 当前最强局部杠杆
    更像是
    noise-side
    energy proxy semantics

### 4. 高静音 case 仍没有被任何单 family 替换救回
- 高静音 case baseline：
  - `HF=0.477566`
  - `centroid=3297.70`
- `energy_proxy=reference_mean`:
  - `HF=0.478850`
  - `centroid=3336.30`
- `noise_energy_proxy=reference_mean`:
  - `HF=0.480506`
  - `centroid=3370.89`
- `periodic_energy_proxy=reference_mean`:
  - `HF=0.477749`
  - `centroid=3307.24`
- 说明：
  - 当前 silence-heavy
    case
    的适用性失配
    没有被单 family
    替换反转
  - 不能把 audible case
    上看到的一点改善
    误写成：
    “根因已定位并修复”

## 当前解释
- 当前用户线 buzzing
  不是：
  - 单纯的
    `z_art`
    错位
  - 单纯的
    `event_probs`
    错位
- 现有证据更支持：
  - Stage5 checkpoint
    对用户线
    noise-side energy proxy
    的语义最敏感
- 但它仍不是：
  - 单一替换后就能回到健康分布
    的那种问题
- 所以当前更像是：
  - 某些动态控制 family
    会加重或缓解失配
  - 但整体 user-line
    control semantics
    仍没有真正落在
    Stage5 checkpoint
    的健康适用范围里

## 当前建议的下一步
1. 若继续用户线定位题，
   优先围绕：
   - noise-side energy proxy
     做更结构化的语义核对
   - 例如对比：
     user-line
     与 train-package
     的时间轨迹、
     静音窗口分布、
     与其它噪声侧控制的耦合
2. 当前不建议回去继续扩：
   - `z_art`
   - `event_probs`
   - 通用归一化策略
   这类新增信息量较低的小题
3. 高静音 case
   应继续保留为单独 applicability boundary；
   不要用常规/peak case
   上的一点改善
   去替代它

## 一句话结论
- 当前 family-level 隔离试验已经把用户线 buzzing 的最强局部杠杆收敛到
  `noise_energy_proxy`
  附近，
  但它还远不是“单一替换即可修复”的问题；
  当前更接近
  Stage5 checkpoint
  对整组 user-line 控制语义
  的适用性失配，
  只是其中 noise-side energy
  最值得优先继续深挖。
