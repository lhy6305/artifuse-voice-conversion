# 2026-03-21 Stage5 no-res 下一题收缩为 root-cause 问题报告

## 结论
- 当前实验线下一题不应再写成：
  - “当前这个 checkpoint
    为什么门槛验收失败”
- 更准确的写法应是：
  - “为什么到目前为止，
    整条 Stage5 no-res
    训练路线在所有人工听审里
    都从未产出过可辨识语音，
    而是始终停留在
    buzzing /
    非语音输出”

先说人话：
- 这已经不是
  “这次导出坏了”
  的问题。
- 也不是
  “这几个 checkpoint
    里选错了一个”
  的问题。
- 现在更像：
  - 整条 no-res route
    还没有真正学会
    把控制量变成语音

## 为什么要把题目收紧到这里

### 1. 当前新增的历史边界
- 用户本轮补充确认：
  - 从头到尾的人工听审里，
    没有任何一次训练结果
    出现过可辨识的人声
- 这意味着：
  - `docs/253`
    记录的
    当前 milestone failure
    不是一次局部翻车
  - 而是
    历史一致负结论

### 2. 这会改变问题层级
- 如果只是：
  - 当前 best route
    第一次失败
- 那下一题还可以是：
  - 哪个 checkpoint 更好
  - 哪个 decode 参数有问题
- 但如果历史上：
  - 所有人工听审
    都没有出现可辨识语音
- 那下一题就必须上升到：
  - 路线级 root cause

## 当前不再值得继续追的问题
- 不再优先：
  - `step72 vs step96`
  - `smooth3 vs postenv`
  - training apply-mode
  - milestone session
    剩余记录逐条补打分

## 当前真正值得追的问题

### 1. 语音为什么从未出现
- 更准确的问题是：
  - 当前 Stage5 no-res
    是否根本没有学到
    speech-like waveform mapping

### 2. 当前需要优先区分的几类根因
- 条件控制没有真正被 decoder 使用
- 条件控制被使用了，
  但只足以驱动能量起伏，
  不足以形成语音结构
- waveform decoder /
  loss recipe
  学到的是某种
  envelope-following
  假解
- 当前训练与导出看到的
  “改善”
  只是在噪声 / 幅度 /
  局部治理维度改善，
  从来没有跨过
  speech emergence
  这条线

## 对后续实验线组织方式的影响

### 1. 当前不应再以“听审收口”为主轴
- 因为：
  - 听审已经反复给出同一负结论

### 2. 当前应改成“root-cause isolation”为主轴
- 新任务应围绕：
  - speech emergence
    为什么没有发生
- 而不是围绕：
  - 当前 buzz
    有没有比上一版更平滑

## 推荐的新题标题
- `Stage5 no-res speech-emergence root-cause isolation`

## 一句话结论
- 当前实验线下一题应正式升级为：
  - 为什么整个
    Stage5 no-res
    路线到现在都没有产出过可辨识语音；
    当前最需要的不是继续听审或继续微调，
    而是把
    speech emergence
    缺失
    这个 root cause
    单独立题。
