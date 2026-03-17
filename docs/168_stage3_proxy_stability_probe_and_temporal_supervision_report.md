# 168. Stage3 proxy 稳定性 probe 与 temporal supervision 对照报告

## 背景
- 首轮人工听审已确认:
  - `student` 与 `teacher`
    的粗结构大体接近
  - 但 `student`
    仍有:
    - 毛刺感
    - 瞬态更不稳
- 因此本轮目标不是继续问
  “有没有跟上 teacher”，
  而是更具体地问:
  - 能否用轻量 supervision
    压 student 的 proxy-level 毛刺

## 本轮思路
1. 先量化当前 checkpoint
   在 proxy 层的动态差距
2. 基于量化结果，
   分别尝试两类附加监督:
   - `teacher_proxy_acoustic`
   - `teacher_proxy_temporal`
3. 用统一的
   `12-step full-validation`
   短程对照，
   看哪条线更有价值

## 先验量化结论

### baseline48 step48 的 proxy-level probe
- 对当前正式主线
  `streaming_student_stage_loop_baseline48_fullval_v1.step48.pt`
  追加了 frame-to-frame probe

观察:
- `energy_delta_pred`
  比 teacher 略高
- 映射到 proxy acoustic 后，
  `delta_energy`
  这一维的时序 gap
  比其他维更突出

解释:
- 当前人耳听到的“毛刺”
  至少有一部分
  很可能与:
  - proxy 的动态变化
  尤其是
  - `delta_energy`
    相关

## 本轮新增实现

### 1. 新增共享 helper
- 文件:
  - `src/v5vc/streaming_student/proxy_acoustic.py`
- 用途:
  - 统一构造
    Stage3 `proxy_acoustic`
    四维结构表示

### 2. 新增可开关 loss
- 文件:
  - `src/v5vc/streaming_student/losses.py`

当前新增两项可选权重:
- `teacher_proxy_acoustic`
  - 直接拟合 student 映射后的
    `proxy_acoustic`
    与 `teacher_acoustic`
- `teacher_proxy_temporal`
  - 直接拟合
    `proxy_acoustic`
    的相邻帧变化量
    与 teacher 的相邻帧变化量

说明:
- 两项默认权重都保持:
  - `0.0`
- 只在 override 配置里显式开启

### 3. 新增 override 配置
- `configs/streaming_student_loss_weights_proxyacoustic020_v1.json`
- `configs/streaming_student_loss_weights_proxytemporal020_v1.json`
- `configs/streaming_student_loss_weights_proxytemporal50_v1.json`

## 12-step full-validation 对照结果

比较基线:
- baseline:
  - `streaming_student_stage_loop_baseline12_fullval_v1.step12`
  - validation:
    - `8.134648`
  - special:
    - `8.11794`

### A. `teacher_proxy_acoustic = 0.2`
- experiment:
  - `streaming_student_stage_loop_proxyacoustic020_fullval12_v1`
- `step12` external eval:
  - validation:
    - `8.101629`
  - special:
    - `8.109353`
- 相比 baseline:
  - validation 改善:
    - `-0.033019`
  - special 改善:
    - `-0.008587`

附加观察:
- `loss_teacher_proxy_acoustic`
  下降明显
  - validation:
    - `2.718466 -> 2.546075`
  - special:
    - `1.374896 -> 1.267219`
- 但我们用于粗看毛刺的
  `proxy_total_abs_gap / proxy_delta_energy_gap`
  没有同步改善，
  反而略变差

结论:
- 它更像是:
  - 把 proxy 值拟合得更近
- 但暂时还不能证明:
  - 毛刺变少了

### B. `teacher_proxy_temporal = 0.2`
- experiment:
  - `streaming_student_stage_loop_proxytemporal020_fullval12_v1`
- `step12` external eval:
  - validation:
    - `8.134487`
  - special:
    - `8.117873`

结论:
- 与 baseline
  基本重合
- 原因不是方向一定错误，
  而是:
  - raw temporal loss
    量级只有约 `0.005`
  - 配 `0.2`
    权重几乎不够影响优化

### C. `teacher_proxy_temporal = 50.0`
- experiment:
  - `streaming_student_stage_loop_proxytemporal50_fullval12_v1`
- `step12` external eval:
  - validation:
    - `8.105292`
  - special:
    - `8.107188`
- 相比 baseline:
  - validation 改善:
    - `-0.029356`
  - special 改善:
    - `-0.010752`

附加观察:
- 这是第一条
  “量级足够让优化器感知到”
  的 temporal probe
- 但当前简单 jitter probe
  仍未显示明确改善:
  - validation
    `proxy_delta_energy_gap`
    约:
    - `0.055983 -> 0.057530`
  - special
    约:
    - `0.048112 -> 0.051986`

结论:
- 它在统一参考 loss 上
  是有价值的候选
- 但对“毛刺是否真的更少”
  仍缺少直接证据

## 当前判断

### 1. `proxy_acoustic` 路线
- 优点:
  - 最直接拉近 proxy feature 本身
  - validation 改善幅度最大
- 缺点:
  - 目前没有证据表明
    人耳关注的毛刺感
    已同步改善

### 2. `proxy_temporal` 路线
- 优点:
  - 方向更对症
  - `50.0` 强权重下，
    validation / special
    都出现了小幅改善
- 缺点:
  - 当前自动 jitter probe
    还没看到明确收益
  - 说明这条线
    还需要人耳复核，
    不能只凭数值直接定案

## 当前最合理的推进结论
1. 当前不把
   `proxyacoustic020`
   或
   `proxytemporal50`
   直接升级为默认 Stage3 基线
2. 其中更值得继续做人耳复核的，
   优先是:
   - `proxytemporal50`
3. 原因:
   - 它比 baseline
     在 validation / special
     都略好
   - 同时方向上更贴近
     “毛刺 / 瞬态稳定性”
     这个真实问题

## 已导出的下一轮试听包
- validation:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
- special:
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`

## 一句话结论
- 本轮自动 probe 证明:
  轻量附加监督可以继续挖，
  但“数值更好”不等于“毛刺已更少”。
- 当前最合理的下一步
  不是直接换默认，
  而是拿
  `proxytemporal50`
  做一轮定向复听，
  确认它是否真的更稳。
