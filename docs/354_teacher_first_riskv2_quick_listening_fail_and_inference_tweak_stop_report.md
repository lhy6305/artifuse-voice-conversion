# 354. teacher-first riskv2 最小试听失败与 inference-only 小修停线报告

## 结论
- 当前两条
  teacher-first
  user-line
  候选：
  - `default_postenv_decoded`
  - `affine_refmean_gateoff_decoded`
  经人工听审后，
  结论一致：
  - 仍为纯 buzz
  - 没有任何稳定人声结构
- 所以这条
  inference-only
  小修线应正式判停。
- 现在不能再把：
  - `reference_shift`
    变小
  - `risk_v2`
    从 `high_risk`
    降到 `elevated_risk`
  当成：
  - 声音已经开始转正

## 一、本轮听审对象
- 试听包：
  - `reports/audio/teacher_first_riskv2_quick_compare_20260325/`
- 关键对比：
  - `default_postenv_decoded.wav`
  - `affine_refmean_gateoff_decoded.wav`

## 二、人工结论
- 当前结论明确且一致：
  1. `default_postenv_decoded`
     仍是纯 buzz
  2. `affine_refmean_gateoff_decoded`
     也仍是纯 buzz
  3. 两者都没有出现
     可接受的
     人声轮廓
     或稳定发声结构

## 三、当前应如何解释这轮结果
- 本轮
  `risk_v2`
  升级
  的价值仍然成立：
  - 它修正了旧
    `risk_v1`
    的误报问题
  - 让我们知道：
    某些候选只是更接近
    reference decoder
    分布，
    而不是所有都属于同一种
    obvious-buzz
    失败
- 但这不改变主结论：
  - 只靠当前这类
    inference-only
    normalization /
    gate /
    control override
    小修，
    不能把
    teacher-first
    user-line
    从纯 buzz
    拉成人声

## 四、当前判断
- 现在应正式写死：
  1. teacher-first
     当前这条
     inference-only
     小修路线，
     到此为止
  2. 后续不再继续做：
     - 再换一组
       normalization
     - 再换一组
       gate on/off
     - 再加一组
       `control_family_override`
  3. 若继续投入，
     必须回到：
     - 更上游的结构问题
     - 或更换主方案
     而不是继续修
     demo 末端参数

## 五、下一步
1. teacher-first
   inference-only
   小修线
   正式停止
2. 回到更高层级，
   重新评估：
   - 当前项目里
     还剩哪条主线
     最可能产生
     第一次真实人声
3. 后续若再继续 user-line，
   也不再默认以
   “再调 demo 参数”
   作为主推进方向
