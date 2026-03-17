# 166. Stage3 proxy 音调对齐与适用边界复核报告

## 背景
- 在修完 Stage3 proxy bundle 的
  响度不一致问题后，
  用户继续人工试听时又提出一个合理担心:
  - teacher 与 student
    会不会还存在
    载频 / 音调不一致，
    从而继续干扰主观判断
- 同时用户实际听感反馈为:
  - 当前 proxy audio
    几乎都是单调频率
  - 基本听不出音节级结构

## 本轮目标
1. 确认当前 Stage3 proxy
   是否存在 teacher/student
   之间的 pitch 不对齐
2. 确认“几乎单调频率”
   是异常回归，
   还是当前 proxy 设计本身的结果
3. 把这条边界重新写实，
   避免后续误判

## 代码检查结论

### 1. 当前 proxy 合成使用固定载频
- 文件:
  - `src/v5vc/proxy_audio_export.py`
- 当前 `synthesize_proxy_waveform`
  内部写死:
  - `carrier_frequency = 185.0`

这意味着:
- teacher_proxy
- student_proxy
  在合成时都会共用同一根基础载频
- 当前 proxy 不是
  - F0 重建
  - 也不是带真实音高轮廓的代理重建

## 当前 bundle 的频率复核

### 1. dominant frequency 检查
- 对当前正式 bundle:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
  的 teacher/student wav
  做了简单 dominant frequency 统计

结果:
- validation bundle:
  - teacher / student
    主峰频率都在:
    - `186.476 ~ 187.000 Hz`
  - 同记录下
    `delta = 0.000 Hz`
- special bundle:
  - teacher / student
    主峰频率都在:
    - `187.076 ~ 187.403 Hz`
  - 同记录下
    `delta = 0.000 Hz`

结论:
- 当前 teacher 与 student
  在 pitch / carrier 上
  没有额外错位
- 不会出现:
  - teacher 更高
  - student 更低
    这种会误导听感的额外偏差

### 2. 频带集中度检查
- 对 student proxy
  追加检查了频带能量占比

结果:
- `150-230 Hz`
  频带能量占比大约为:
  - `0.9120 ~ 0.9367`
- `230-400 Hz`
  频带能量占比大约为:
  - `0.0366 ~ 0.0669`

这说明:
- 当前 proxy 的主体能量
  高度集中在固定低频载波附近
- “听起来像单调嗡声”
  不是偶发问题，
  而是当前合成策略的直接结果

## 当前应如何解释这次听感

### 1. “音调没对齐”不是当前主要问题
- 当前 teacher/student
  的 carrier 已经天然对齐
- 所以不会再因为
  pitch 错位
  额外污染比较

### 2. “几乎没有音节结构”是当前 proxy 的真实边界
- 当前 proxy
  只有:
  - energy
  - abs_mean
  - zero_cross / brightness
  - delta_energy
    这一类极简低维结构映射
- 再加上:
  - 固定载频
  - 强平滑
  - 低频结构优先
- 最终结果就是:
  - 更像包络/稳定性监听信号
  - 而不像带真实音节感的可懂度代理

## 当前适用边界更新

### 现在还能听什么
- 明显停顿有没有出来
- 整段能量包络是否接近
- 有没有忽大忽小
- 有没有突然塌陷、发飘、失稳

### 现在不要拿它判断什么
- 真实音节结构是否成立
- 清晰度 / 可懂度
- 真实音高轮廓
- speaker identity
- 最终用户听感

## 已做的补充
- 已把这条边界补进:
  - `src/v5vc/audio_audit_gui.py`
    的 GUI 帮助文本

## 当前结论
1. 当前 Stage3 proxy
   的 pitch / carrier
   没有 teacher/student 之间的错位
2. 用户听到“几乎单调频率”
   是真实现象，
   但这是当前 proxy 设计本身的结果
3. 因此当前 proxy
   仍可用于:
   - 粗粒度停顿/包络/稳定性审核
   但不应再拿来判断:
   - 音节级结构
   - 可懂度

## 一句话结论
- 当前 Stage3 proxy 的问题
  不在于 teacher/student
  音调没对齐；
  它们本来就被固定到同一载频上。
- 真正的边界是:
  这版 proxy 更像单调低频结构监听信号，
  不足以承载音节级人工判断。
