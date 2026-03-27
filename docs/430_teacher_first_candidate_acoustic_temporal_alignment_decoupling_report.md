# 2026-03-27 teacher-first 候选线 acoustic-state 时间对齐去耦 probe 报告

## 结论
- 我继续沿着
  acoustic-state
  时间动态这条主线推进，
  没有回到静态 replacement。
- 这轮新增了两类
  inference-only 时序 override：
  - `time_roll_half`
  - `time_shuffle`
- 当前最关键的新结论是：
  1. 只要打断
     `aper`
     与当前样本 activity
     的时间对齐，
     `activity_corr`
     就会显著下降，
     但 anti-template
     大部分还能保住
  2. 更强的是
     `aper + energy = time_shuffle`
     这组：
     - `decoded_template = 0.981053`
     - `activity_corr = 0.101686`
  3. 这组结果明显优于：
     - `aper + energy = zero`
       的
       `0.988933 / 0.141311`
     - `aper + energy = reference_mean`
       的
       `0.990502 / 0.050668`
  4. 因而当前 residual 问题
     可以更明确地写成：
     - 主故障不是
       acoustic-state
       “存在”本身
     - 而是它们与当前 activity
       的时间对齐耦合
- 所以下一步应优先研究：
  - 如何削弱
    acoustic-state
    对当前 activity envelope
    的对齐能力
  - 同时保留其
    anti-template 动态贡献

## 一、代码推进
- `analyze-offline-mvp-teacher-first-vc-waveform-handoff`
  现在新增支持：
  - `family=time_roll_half`
  - `family=time_shuffle`
- 实现仍复用：
  - `normalize_scaffold_payload_for_decoder_probe(...)`
- 同时顺手修了一个 probe 契约问题：
  - 参考分布统计现在按需加载，
    不再因为非 reference 模式
    误读 `per_dim_std`

## 二、probe 目录
- `aper = time_roll_half`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_rh/`
- `aper = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_shuf/`
- `aper + energy = time_roll_half`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_e_rh/`
- `aper + energy = time_shuffle`
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_whp_fbmc_rs_aper_e_shuf/`

## 三、关键对照
- baseline：
  - `decoded_template = 0.984637`
  - `activity_corr = 0.519889`
  - `centroid = 6510.052734`
  - `high_band = 0.449300`

### 1. `aper`
- `aper = zero`
  - `decoded_template = 0.988699`
  - `activity_corr = 0.217405`
- `aper = reference_mean`
  - `decoded_template = 0.988538`
  - `activity_corr = 0.297761`
- `aper = reference_affine_match`
  - `decoded_template = 0.983265`
  - `activity_corr = 0.535281`
- `aper = time_roll_half`
  - `decoded_template = 0.983379`
  - `activity_corr = 0.243811`
  - `centroid = 6571.307129`
  - `high_band = 0.453882`
- `aper = time_shuffle`
  - `decoded_template = 0.983125`
  - `activity_corr = 0.259761`
  - `centroid = 6551.867676`
  - `high_band = 0.452369`

读法：
- 对 `aper` 来说，
  只打断时间对齐，
  就能把
  `activity_corr`
  从
  `0.519889`
  压到
  `0.243811 / 0.259761`
- 更关键的是：
  - `template`
    仍维持在
    `0.983xxx`
  - 明显比
    `zero / reference_mean`
    更能保住 anti-template

### 2. `aper + energy`
- `aper + energy = zero`
  - `decoded_template = 0.988933`
  - `activity_corr = 0.141311`
- `aper + energy = reference_mean`
  - `decoded_template = 0.990502`
  - `activity_corr = 0.050668`
- `aper + energy = reference_affine_match`
  - `decoded_template = 0.979448`
  - `activity_corr = 0.604880`
- `aper + energy = time_roll_half`
  - `decoded_template = 0.980483`
  - `activity_corr = 0.348705`
- `aper + energy = time_shuffle`
  - `decoded_template = 0.981053`
  - `activity_corr = 0.101686`
  - `centroid = 6560.539062`
  - `high_band = 0.450547`

读法：
- `time_roll_half`
  说明：
  - 仅破坏长程对齐，
    就能压下一部分
    `activity_corr`
- `time_shuffle`
  则更直接说明：
  - 当
    `aper / energy`
    的时间对齐被彻底打散时，
    residual envelope-following
    基本被压下去
  - 但系统仍保留了
    明显优于
    `zero / reference_mean`
    的 anti-template 状态

## 四、当前最稳的解释
- 结合上一轮
  reference-backed 结果，
  现在可以更明确地区分两件事：
  1. 静态分布修正：
     - 不能解释主问题
  2. 时间对齐打断：
     - 能显著压低
       residual envelope-following
     - 且不必把系统拉回
       模板塌缩
- 因而当前 residual 主故障
  应写成：
  - acoustic-state
    尤其
    `aper / energy`
    与当前 activity
    的时间对齐耦合
- 这也解释了为什么：
  - `reference_affine_match`
    会失败；
    它保留了时间动态
  - `reference_mean`
    会表面有效；
    它只是把时间动态
    直接压扁了

## 五、下一步如何收敛
1. 不再继续做：
   - 静态 reference replacement
   - family-level 大扫表
2. 直接研究：
   - acoustic-state
     与 activity envelope
     的时间对齐约束
3. 更偏训练/结构上的方向应是：
   - 限制 `aper / energy`
     直接跟随 source-side activity
   - 保留它们的
     anti-template 动态

## 一句话结论
- 当前候选线 residual `envelope-following`
  的主故障已经可以更硬地写成：
  - `aper / energy`
    对当前 activity
    的时间对齐耦合；
  - 只要打断这种对齐，
    `activity_corr`
    就会明显下降，
    而 anti-template
    不必随之塌回去。 
