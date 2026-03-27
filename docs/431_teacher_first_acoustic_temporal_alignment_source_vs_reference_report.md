# 2026-03-27 teacher-first acoustic temporal alignment source-vs-reference 报告

## 结论
- 我没有直接跳去改训练，
  而是先把一个更上游的问题量化清楚：
  - residual `envelope-following`
    到底是不是 teacher/scaffold
    端就已经把 source-side 包络
    带进来了
- 当前最关键的新结论是：
  1. user-line source scaffold
     不是“完全正常、只在 checkpoint 才出问题”
  2. 但也不是
     `aper / energy`
     所有时间对齐都已经
     全面离谱
  3. 更准确地说：
     - `energy -> frame_rms`
       的零延迟耦合
       已经明显高于
       Stage5 training packages
     - `aper * energy -> frame_rms`
       也明显从 reference 的
       更负相关 / 更长滞后
       区间，
       向更即时的 envelope 跟随
       偏移
     - `aper -> frame_rms`
       本身则只部分偏移，
       没有 energy 那么统一
- 因而当前更稳的主结论应写成：
  - user-line source-derived
    acoustic-state scaffold
    已经把一部分
    过强的即时包络耦合
    带进来了，
    尤其在 `energy`
    和 `aper*energy`
    上
  - checkpoint 后段
    更像是在放大这条已有耦合，
    不是凭空创造它

## 一、probe 入口
- 新命令：
  - `analyze-offline-mvp-teacher-first-vc-acoustic-temporal-alignment`
- 代码：
  - [teacher_first_vc_demo.py](F:\proj_dev\tmp\workdir4\src\v5vc\teacher_first_vc_demo.py)
  - [cli.py](F:\proj_dev\tmp\workdir4\src\v5vc\cli.py)
- 本轮输出目录：
  - `reports/runtime/offline_mvp_teacher_first_vc_demo_applicability_probe/rbt_atap/`

这个 probe 的读法是：
- user-line：
  - 从 input audio
    跑 teacher runtime
    到 scaffold，
    但不走 waveform decode
- reference：
  - 直接读取
    Stage5 train packages
- 比较对象：
  - `aper / E / aper*E`
    与真实 waveform frame RMS
    的 lag-correlation 曲线

所以它回答的是：
- source-derived controls
  自己的时间对齐形状
  是否已经 OOD

## 二、reference 基线
- 32 个 Stage5 train packages
  aggregate：
  - `aper -> frame_rms`
    - `zero_lag_mean = -0.759019`
    - `best_lag_mean = 12.0`
    - `zero_minus_best_nonzero_mean = -0.176260`
  - `energy -> frame_rms`
    - `zero_lag_mean = 0.787623`
    - `best_lag_mean = 0.0`
    - `zero_minus_best_nonzero_mean = 0.002550`
  - `aper*energy -> frame_rms`
    - `zero_lag_mean = -0.317557`
    - `best_lag_mean = 11.25`
    - `zero_minus_best_nonzero_mean = -0.236711`

reference 的基本形状是：
- `energy`
  本来就和 waveform envelope
  零延迟正相关
- 但 `aper`
  以及
  `aper*energy`
  并不是强零延迟跟随，
  更像带明显滞后结构

## 三、user-line 三样本 aggregate
- 三条 pure buzz
  user-line 平均：
  - `aper -> frame_rms`
    - `user_zero_lag_mean = -0.633824`
    - `user_best_lag_mean = 12.0`
    - `user_gap_mean = -0.267571`
  - `energy -> frame_rms`
    - `user_zero_lag_mean = 0.872423`
    - `user_best_lag_mean = 0.0`
    - `user_gap_mean = 0.007271`
  - `aper*energy -> frame_rms`
    - `user_zero_lag_mean = -0.030862`
    - `user_best_lag_mean = 8.333333`
    - `user_gap_mean = -0.241002`

最值得注意的是：
- `energy`
  的零延迟相关
  从
  `0.787623`
  抬到了
  `0.872423`
- `aper*energy`
  的零延迟相关
  从
  `-0.317557`
  被推到了
  `-0.030862`
  也就是明显更接近
  即时 envelope 跟随

## 四、逐项读法

### 1. `energy -> frame_rms`
- 三条 user case
  的 `zero_lag_z`：
  - `4.317569`
  - `7.181635`
  - `0.413092`

读法：
- `energy`
  在 user-line
  上已经表现出
  明显偏高的
  零延迟 envelope 耦合
- 其中两条样本
  已经是很强的
  reference 外偏移

### 2. `aper*energy -> frame_rms`
- 三条 user case：
  - case1:
    - `zero_lag_corr = -0.121010`
    - `best_lag_frames = 12`
  - case2:
    - `zero_lag_corr = 0.473948`
    - `best_lag_frames = 1`
  - case3:
    - `zero_lag_corr = -0.445523`
    - `best_lag_frames = 12`

读法：
- 这组最说明问题：
  - reference 上
    `aper*energy`
    更像带滞后的结构
  - user-line
    则至少有一条
    已经滑到
    近零延迟正相关
    的即时跟随区
- 所以当前 residual EF
  很可能不是单靠
  checkpoint 后段
  凭空造出来，
  而是 source scaffold
  已经把危险的
  `aper*energy`
  时间对齐
  带高了

### 3. `aper -> frame_rms`
- 三条 user case
  的偏移不如
  `energy`
  一致
- 说明：
  - `aper`
    仍然是重要承载项
  - 但更稳定的上游偏移
    主要落在：
    - `energy`
    - `aper*energy`

## 五、和前一轮 time-shuffle 的关系
- 前一轮已经证明：
  - `aper + energy = time_shuffle`
    能把
    `activity_corr`
    压到
    `0.101686`
    同时保住
    `decoded_template = 0.981053`
- 这一轮则进一步解释了
  为什么这招有效：
  - 不是因为
    acoustic-state
    整体不该存在
  - 而是因为
    user-line source scaffold
    已经把
    `energy`
    尤其
    `aper*energy`
    的即时 envelope 对齐
    带高了
  - `time_shuffle`
    实际上是在切断
    这条已被带高的
    时间耦合

## 六、当前主线如何更新
1. 当前 residual 主故障
   不应再写成：
   - 纯 checkpoint 消费问题
   - 或纯 scaffold 问题
2. 更准确的写法应是：
   - source-derived scaffold
     已经把
     `energy / aper*energy`
     的即时包络耦合
     带高
   - checkpoint downstream
     再把这条耦合
     放大成可听的
     residual envelope-following
3. 因而下一步应优先研究：
   - 训练/结构上
     如何限制
     `energy`
     尤其
     `aper*energy`
     的即时 envelope 对齐
   - 而不是继续泛泛地写成：
     - 删 acoustic-state
     - 或只改静态均值/方差

## 一句话结论
- 当前 user-line residual `envelope-following`
  的上游问题已经能更精确地定位为：
  - source scaffold
    在
    `energy`
    和
    `aper*energy`
    上已经出现了
    偏高的即时包络耦合，
  - checkpoint 后段
    再把这条耦合
    放大成了最终可听故障。 
