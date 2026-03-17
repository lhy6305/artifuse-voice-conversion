# `round1.1` lexical-only target recovery 启动报告

## 目的
- 在不动 source 数据的前提下，把 `round1` 隔离区中可回收的 lexical target 样本正式拉回数据主线。
- 同时为后续是否切到 `round1.1` 训练准备：
  - recovery 结果
  - manifest 结果
  - split facts

先说人话：
- 这一步不是直接开练。
- 是先把能救回来的 target 样本救回来，再把新数据盘一遍，看它值不值得升成新训练底座。

## 已完成内容
### 1. target 格式回收命令已落地
- 新增命令：
  - `recover-round1-target-formats`
- 当前实现：
  - 对 lexical target 隔离样本做 mono 化和 `44100 Hz` 规范化
  - 把恢复后的音频写到：
    - `data_prep/round1_1/firefly_mainstream/audio/`

### 2. `round1.1` target recovery 已实际完成
- 原始 round1 target train：
  - `624`
- 当前恢复成功：
  - `42`
- 当前仍保持隔离：
  - `5`
  - 全部是 `no_text_voice`
- 恢复失败：
  - `0`

### 3. `round1.1` manifests 已生成
- 目标记录数：
  - `666`
- 源记录数：
  - `537`
- 当前 target 时长均值：
  - `6.098379s`

### 4. `round1.1` split analysis 已完成
- 当前推荐方案仍是：
  - `hybrid_stratified_blocked`
- 当前推荐理由没有变：
  - `no_text_voice` 仍应保持独立 challenge eval
  - source 仍不适合做随机拆分

## 当前关键事实
### 1. `round1.1` 不是“全重来”，而是有控制的 target-only 升级
- source 侧完全沿用：
  - `data_prep/round1/source_segments`
- 当前变化只发生在 target 侧：
  - 额外回收 `42` 条 lexical 样本
  - `5` 条 `no_text_voice` 继续隔离

### 2. recovery 的收益是实打实的，但仍然是“新数据版本”
- 当前新增 target 时长：
  - `235.470887s`
- 相比旧 round1 target：
  - 有明显增量
- 但它依然意味着：
  - 后续实验要按 `round1.1` 新版本单独记账

### 3. `round1.1` 下 split 推荐没有翻车
- `hybrid_stratified_blocked` 仍然是最稳的口径：
  - target validation `66`
  - target special_eval `8`
  - source validation `54`
- 这说明：
  - 当前做数据升级，不会把之前的拆分逻辑前提直接打坏

## 当前建议
- 若用户准备正式切到 `round1.1`：
  - 下一步优先 materialize `round1.1` 的 `hybrid_stratified_blocked`
  - 然后初始化第一份 `round1.1` 实验
- 若用户还想先守住 `round1`：
  - 当前 `round1.1` 这些产物也已经在磁盘上，后面随时可以接着走

先说人话：
- 现在不是还在“准备切 B”。
- 是 B 已经把数据底座搭起来了，只差你拍板要不要正式拿它开第一轮实验。
