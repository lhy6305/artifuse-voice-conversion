# 2026-03-27 teacher-first branch-specific energy alignment 报告

## 结论
- 我把
  `E_log_rms_norm`
  从整家族拆成了：
  - `periodic_E_log_rms_norm`
  - `noise_E_log_rms_norm`
- 然后只做最小必要的
  `time_shuffle`
  对照，
  目的是确定下一步训练/结构候选
  应该落在哪一支
- 当前结论已经很硬：
  1. 真正该优先约束的
     不是 periodic 支能量，
     而是：
     - `noise_E_log_rms_norm`
  2. `periodic_E_log_rms_norm = time_shuffle`
     不但无益，
     反而把
     `activity_corr`
     从
     `0.519889`
     拉高到
     `0.556154`
  3. `noise_E_log_rms_norm = time_shuffle`
     则把
     `activity_corr`
     压到
     `0.310713`
  4. 更关键的是：
     - `aper + noise_E_log_rms_norm = time_shuffle`
       达到：
       - `decoded_template = 0.982003`
       - `activity_corr = 0.012374`
     - 这比
       `aper + E_log_rms_norm = time_shuffle`
       的
       `0.981053 / 0.101686`
       还更强
- 因而当前最小训练候选应明确收敛为：
  - 不是“整条 energy family 去耦”
  - 而是：
    - `noise energy`
      优先
    - 与
      `aper`
      联动去耦

## 一、probe 目录
- `periodic_E_log_rms_norm = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_per_e_shuf/`
- `noise_E_log_rms_norm = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_noise_e_shuf/`
- `aper + noise_E_log_rms_norm = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_noise_e_shuf/`

## 二、关键对照
- baseline：
  - `decoded_template = 0.984637`
  - `activity_corr = 0.519889`
- `periodic_E_log_rms_norm = time_shuffle`
  - `decoded_template = 0.983162`
  - `activity_corr = 0.556154`
- `noise_E_log_rms_norm = time_shuffle`
  - `decoded_template = 0.984628`
  - `activity_corr = 0.310713`
- `aper = time_shuffle`
  - `decoded_template = 0.983125`
  - `activity_corr = 0.259761`
- `aper + E_log_rms_norm = time_shuffle`
  - `decoded_template = 0.981053`
  - `activity_corr = 0.101686`
- `aper + noise_E_log_rms_norm = time_shuffle`
  - `decoded_template = 0.982003`
  - `activity_corr = 0.012374`

## 三、读法
- `periodic energy`
  单独打断会更坏，
  说明：
  - periodic 支能量
    不是当前 residual EF
    的主异常入口
  - 它更可能还在提供
    相对有用的周期侧动态
- `noise energy`
  单独打断能稳定见效，
  说明：
  - 当前上游危险对齐
    更准确地落在
    noise 支
- `aper + noise energy`
  联动时，
  `activity_corr`
  几乎被压平到
  `0.012374`
  而
  `template`
  仍维持在
  `0.982003`
  没有塌回
  `zero / reference_mean`
  那种模板区

## 四、当前主线如何更新
1. `energy`
   不能再被当成
   一个不分支的整体控制
2. 当前更准确的训练/结构入口应是：
   - `noise_E_log_rms_norm`
3. 当前最小候选应写成：
   - 限制
     `noise energy`
     对 envelope 的即时对齐
   - 并与
     `aper`
     联动去耦
4. 当前不应再把下一步误写成：
   - 改 periodic energy
   - 改整条 energy family

## 一句话结论
- 当前最小训练候选已经收敛为：
  - `noise_E_log_rms_norm`
    与
    `aper`
    的联动去耦；
  - periodic 支能量
    不是当前应优先动的方向。 
