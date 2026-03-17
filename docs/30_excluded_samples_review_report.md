# round1 隔离样本复核报告

## 目的
- 复核 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中的 `47` 条隔离样本。
- 确认这些样本到底是：
  - 纯格式隔离
  - 还是已经存在文本/标签/内容层面的明显坏样本问题
- 为后续是否做 `round1.1` 的 target format normalization 准备事实基础。

先说人话：
- 这一步是在确认“隔离区里放的是废料，还是其实放了不少还能用的货”。

## 复核方法
- 读取：
  - `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl`
  - `reports/data/preprocess_round1/target_dataset_report.json`
  - `src/v5vc/preprocess.py`
- 核对：
  - exclusion reason 分布
  - 采样率/声道分布
  - 时长分布
  - 文本清洗结果
  - `preprocess.py` 中真实排除逻辑

## 关键事实
### 1. 当前 47 条样本全部是“格式隔离”，没有发现别的硬伤
- 代码里当前纳入 round1 的硬条件只有：
  - `sample_rate == 44100`
  - `channels == 1`
  - `lab` 存在
  - `cleaned_text` 非空
- 这 47 条样本里没有出现：
  - `missing_lab`
  - `empty_cleaned_text`
- 也就是说，当前被排除的原因全部来自：
  - 非 `44100 Hz`
  - 或非单声道

### 2. 排除原因分布很集中
- `sample_rate=48000`: `22`
- `sample_rate=32000`: `12`
- `sample_rate=36000`: `8`
- `sample_rate=16000`: `4`
- `channels=2`: `5`

组合上只有 5 种情况：
- `sample_rate=48000` 单独出现：`22`
- `sample_rate=32000` 单独出现：`12`
- `sample_rate=36000` 单独出现：`8`
- `sample_rate=16000 + channels=2`：`4`
- `channels=2` 单独出现：`1`

解释：
- 这不是“各种奇怪坏样本混在一起”。
- 更像是几个来源批次的格式没有统一进当前 round1 主规则。

### 3. 按可回收性分组，主体是可格式修复的 lexical 样本
- `mono_resample_only`: `37` 条，合计 `216.241s`
- `stereo_downmix_plus_resample`: `5` 条，合计 `19.230s`
- `no_text_voice_keep_isolated`: `5` 条，合计 `7.854s`

若只看 lexical 样本，理论上可通过格式统一回收的总时长约为：
- `235.471s`

对比当前 round1 target 主集：
- 当前 round1 target 总时长约 `3826.050s`
- 若全部回收上述 lexical 样本，增幅约为 `6.2%`

### 4. 当前隔离样本集中在少数章节，不是全局零散分布
- `chapter4_7`: `18`
- `chapter3_6`: `11`
- `chapter3_2`: `5`
- `no_text_voice`: `5`
- 其余章节合计：`8`

这说明：
- 当前隔离更像“少数批次的格式源头不同”，而不是数据集全局随机破碎。

### 5. `no_text_voice` 这 5 条不适合直接并回主训练
- 这 5 条全部为：
  - `cleaned_text = "，"`
  - 非完整音节
  - 仍属于 `no_text_voice` 近非言语片段
- 它们即使做了格式统一，也更适合：
  - 继续保持 isolated
  - 或作为 challenge / special slice 候选
- 不适合直接混入正常 lexical training split

### 6. 其余 lexical 样本没有发现额外文本层硬伤
- 未发现空文本。
- 未发现缺 lab。
- 清洗后文本仍有正常标点结构。
- 存在少量重复或近重复文本，但数量不大，不构成当前主要阻塞。

额外观察：
- 隔离样本里有 `2` 条 `，嗯。`
- 有 `2` 条 `那真是太好了。`
- `no_text_voice` 的 `，` 出现 `5` 条

这说明：
- 这里面确实有少量重复文案。
- 但当前更大的事实仍然是“格式没进主规则”，不是“文本本身烂掉了”。

## 当前解释
### 可以明确下的结论
- `manifest_round1_excluded.jsonl` 当前更像：
  - format quarantine
  - 不是 junk bin
- 也就是说：
  - 这 47 条不是“坏样本清理结果”
  - 而是“当前 round1 为了稳定先只吃 44.1k 单声道，于是暂时放到旁边的格式隔离区”

### 不能直接下的结论
- 不能仅凭这份复核，就直接说：
  - “应该立刻全部并回 round1”
- 原因是：
  - 一旦并回，会改变 target 数据分布
  - 会影响 split
  - 会打断当前 `B1.1-A / C1.4` 这批实验的横向可比性

## 风险与取舍
### 方案 1：保持当前 round1 冻结
优点：
- 不破坏现有实验可比性
- 当前训练与报告口径继续稳定
- 适合马上继续做 route-B / route-C 的模型侧验证

缺点：
- 明知还有约 `235.471s` 的 lexical 样本可回收，却继续闲置
- 后续如果再做数据层升级，还是得回头处理

### 方案 2：做 `round1.1` target format normalization
优点：
- 能系统回收大部分被格式隔离的 lexical 样本
- 数据增幅约 `6.2%`
- 更像是在修数据入口，而不是继续围绕小权重做模型侧细抠

缺点：
- 会改变 target 训练集边界
- 需要重建 manifest、重新物化 split，并重新解释后续实验基线
- 不适合与当前 round1 结果直接混成一条时间线比较

### 方案 3：只回收 lexical，继续隔离 `no_text_voice`
优点：
- 是当前最干净的折中路线
- 既回收绝大多数可用样本
- 又不会把近非言语 challenge 样本混入正常训练

缺点：
- 仍然属于一次新的数据版本升级
- 依旧需要新 split 和新的实验基线

## 当前建议
- 当前更合理的口径是：
  - 把这 47 条的复核结论正式确认掉；
  - 不再把它们笼统叫“坏样本”；
  - 若后续做数据层升级，优先走：
    - lexical-only recovery
    - `no_text_voice` 继续隔离
- 如果用户希望保持当前实验链的严格可比性：
  - 就保持 round1 冻结，先不动数据
- 如果用户希望优先从数据层拿更大增益，而不是继续围绕 `C1.3 / C1.4` 做小步调参：
  - 那下一步最值得做的是：
    - `round1.1` target format normalization
    - 只回收 `37 + 5 = 42` 条 lexical 样本
    - `5` 条 `no_text_voice` 继续隔离

先说人话：
- 现在已经能确认，隔离区里大部分不是废料。
- 但要不要回收，已经不是“能不能”的问题，而是“现在值不值得打断当前实验口径”的问题。
