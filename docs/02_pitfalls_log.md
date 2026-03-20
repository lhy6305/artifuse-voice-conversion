# 开发踩坑记录

## 使用说明
- 每次发现新的环境问题、数据异常、实现陷阱或设计偏差，都要追加到本文档。
- 旧问题若已解决，不删除，改为补充“处理结果”。

## 2026-03-14
### 1. Python 解释器必须固定为仓库根目录 `python.exe`
- 现象：
  - 仓库根目录已经提供专用解释器。
- 风险：
  - 如果误用系统 Python，后续训练、音频处理和依赖导入很可能直接失败，且问题不可复现。
- 处理要求：
  - 所有 Python 命令统一显式调用 `.\python.exe`。

### 2. 业务型音频与训练任务必须提权运行
- 现象：
  - 用户已明确要求声音处理、Torch 训练、native 调用等业务代码走沙盒提权。
- 风险：
  - 在普通沙盒里运行时，可能出现假卡死、资源限制或不完整结果。
- 处理要求：
  - 相关命令默认按提权流程执行。

### 3. 当前数据目录体量较大，不能依赖人工目检
- 现象：
  - `data_convert/dataset_firefly_raw/` 下存在大量 `.wav/.lab` 文件。
- 风险：
  - 手工检查容易遗漏配对异常、命名异常和长度异常。
- 处理要求：
  - 下一阶段优先实现自动扫描和 manifest 生成。

### 4. 设计落地必须先验证无残差主干
- 现象：
  - 风险评估文档明确指出，无残差主干是整个系统成败关键。
- 风险：
  - 如果过早实现 `r_res`，会掩盖 `z_art` 和 `e_evt` 失效的问题。
- 处理要求：
  - MVP 必须先做无残差版本，并把消融检查纳入正式验收。

### 5. Teacher 伪标签不是物理真值
- 现象：
  - 主设计稿与风险文档都指出 Teacher 只产生伪标签和置信度。
- 风险：
  - 若把伪标签当真值，会把 Teacher 偏差直接固化到 Student。
- 处理要求：
  - 后续实现必须保留置信度统计、过滤和分段分析，尤其检查辅音保留率。

### 6. 临时文件必须显式管理
- 现象：
  - 项目刚进入开发阶段，后续容易快速出现一次性脚本、临时导出和中间报告。
- 风险：
  - 如果临时文件直接散落在根目录，后续很快失去结构可维护性。
- 处理要求：
  - 临时文件只能放入专门位置并带明显标记，使用后要么升级为正式文件，要么及时清理。

### 7. 方案分歧不能跳过用户决策
- 现象：
  - 数据清洗、文本规范化、静音裁剪、采样率统一、是否保留标点等都存在明确取舍。
- 风险：
  - 如果未经汇报直接定方案，后续很可能与用户目标不一致。
- 处理要求：
  - 必须先收集统计事实，再给用户报告优缺点和建议，由用户做最终判断。

### 8. 源说话人录音包含大量静音和少量突发噪声
- 现象：
  - 用户明确说明 `dataset_ly65_raw.wav` 存在大量静音片段，并可能有少量突发杂音。
- 风险：
  - 如果后续直接拿来训练或对齐，会污染内容边界、时长统计和能量建模。
- 处理要求：
  - 下一阶段必须优先做静音占比和异常片段检测，再决定切分和清洗策略。

### 9. 目标文本带标点，不能先验移除
- 现象：
  - `dataset_firefly_raw` 的 `.lab` 文本带标点且为 UTF-8 无 BOM。
- 风险：
  - 直接去标点可能破坏停连、节奏和事件建模线索；直接保留也可能增加文本规范化复杂度。
- 处理要求：
  - 先做文本统计和样本检查，再向用户汇报保留/归一化策略的优缺点。

### 10. 目标数据集存在采样率与声道不一致
- 现象：
  - 首轮扫描发现目标数据集并非全量 44.1 kHz 单声道。
  - 存在 48 kHz、32 kHz、36 kHz、16 kHz 以及少量双声道样本。
- 风险：
  - 如果直接进入统一预处理或训练，特征提取缓存和训练输入格式会不稳定。
- 处理要求：
  - 在用户确认统一策略前，先保持原始数据不动，并在 manifest 中显式标记异常样本。

### 11. 源录音静音占比远高于可直接训练水平
- 现象：
  - 首轮扫描下，`dataset_ly65_raw.wav` 在 `-40 dBFS` 阈值下约 81.90% 的 100 ms 窗低于阈值。
- 风险：
  - 若不先做切分和静音清洗，源数据会严重拖累后续训练集构建效率和质量。
- 处理要求：
  - 在用户确认静音裁剪策略前，只保留统计，不直接删除或覆盖原始数据。

### 12. 源录音存在需要二次复核的高峰值片段
- 现象：
  - 首轮扫描发现 1221.9 秒、1665.0 秒、2327.1 秒、2369.9 到 2371.4 秒、3049.6 秒附近存在显著高峰值窗。
- 风险：
  - 这些片段可能是正常高能语音，也可能夹杂突发噪声；若不复核，后续容易把异常段直接带入训练副本。
- 处理要求：
  - 后续应支持对指定时间段做片段导出或局部检查。

### 13. 文本应进入训练辅助链路，但不进入当前推理硬依赖
- 现象：
  - 用户确认当前阶段文本不作为推理输入，但同意纳入训练和数据处理。
- 风险：
  - 如果后续实现里把文本完全忽略，会削弱清洗、对齐和内容评估；如果错误地强制进入推理，又会偏离当前 MVP 范围。
- 处理要求：
  - 在 manifest 和训练辅助模块中保留原始文本与清洗文本字段，不为当前推理链路增加文本必选输入。

### 14. 当前 round1 未检测到足够强的稳定底噪
- 现象：
  - round1 预处理估计底噪约为 `-74.184 dBFS`，未达到当前“稳定底噪存在”判定线。
- 风险：
  - 若后续误以为底噪问题已经处理完，可能忽略局部片段中的瞬时环境噪声。
- 处理要求：
  - 先让用户试听峰值片段和部分内容段，再决定是否下调噪声判定阈值。

### 15. 源录音峰值导出规则必须限量
- 现象：
  - 预处理初版曾导出过多峰值片段，人工复核不可用；已修正为限量导出。
- 风险：
  - 若后续调参时忘记限量，试听目录会再次失去可用性。
- 处理要求：
  - 峰值导出必须限制总量，并保持可人工试听规模。

### 16. 边界静区规则会显著压缩源训练候选片段数量
- 现象：
  - 在 `-38 dBFS` 与 `500 ms` 边界静区规则下，源片段从 823 条降到 537 条。
- 风险：
  - 规则过严时，可能误伤本可使用的正常人声片段。
- 处理要求：
  - 在进入训练前，必须明确这是有意接受的过滤强度，而不是隐性数据损失。

### 17. `peak_010` 的“保留后半段”在当前边界规则下未落成训练片段
- 现象：
  - 虽然人工决策仅排除了 `2051.385s` 到 `2051.770s` 的短异常区间，但当前边界规则没有保留该区域附近的训练片段。
- 风险：
  - 如果不记录，后续容易误以为这段“已经成功保留后半段”。
- 处理要求：
  - 文档必须显式说明当前实际结果，后续若要保留该后半段，需要单独调整边界规则或局部例外策略。

### 18. 标准 manifest 的音频路径必须与派生目录严格一致
- 现象：
  - manifest 标准化初版曾出现目标音频路径少一层 `round1/` 的拼接错误，已修正。
- 风险：
  - 如果不及时发现，后续训练加载会在运行期才失败。
- 处理要求：
  - 每次生成 manifest 后都要抽样核对真实路径。

### 19. 数据完整性检查必须作为 manifest 生成后的固定步骤
- 现象：
  - 标准 manifest 在第一次生成后，通过完整性检查立即暴露了目标音频路径错误。
- 风险：
  - 如果只生成 manifest 不做检查，这类错误会延后到训练阶段才暴露。
- 处理要求：
  - 每次重建标准 manifest 后，固定执行 `check-round1-data`。

### 20. scaffold 命令跑通不等于真实训练已实现
- 现象：
  - 当前 `evaluate-round1-baseline` 和 `train-offline-mvp --dry-run` 都已可执行。
- 风险：
  - 如果后续忽略它们只是 scaffold，很容易误判为“训练系统已完成”。
- 处理要求：
  - 文档里必须明确区分：
    - 已实现的评估/训练脚手架
    - 尚未实现的真实模型、真实训练循环和消融执行逻辑

### 21. `torch.frombuffer` 读取只读 buffer 会触发警告
- 现象：
  - 真实 dry-run 首次运行时，音频加载使用 `torch.frombuffer(raw, ...)` 触发了只读 buffer 警告。
- 风险：
  - 虽不阻断执行，但会污染日志，也说明底层实现不够稳妥。
- 处理要求：
  - 使用可写副本再转 tensor，避免把该警告带入后续训练日志。

### 22. 单步训练验证需要显式保护开关
- 现象：
  - `train-offline-mvp` 已从 dry-run 扩展到真实单步训练，会执行反向传播、优化器 step 和 checkpoint 写入。
- 风险：
  - 如果没有显式保护，后续可能在“只是想看计划”时误触真实训练写盘。
- 处理要求：
  - 训练配置必须保留 `single_step_validation_enabled` 开关。
  - 非 `--dry-run` 执行前，必须检查该开关已显式开启。

### 23. 当前最小验证集只是固定切片，不是正式评估拆分
- 现象：
  - 多步训练当前使用 manifest 尾部固定切片作为目标与源验证子集。
- 风险：
  - 这种做法适合做回归监控，但不足以代表正式泛化能力，也可能受样本顺序偏差影响。
- 处理要求：
  - 后续必须补正式训练集/验证集拆分方案，并由用户确认后再作为阶段性评估依据。

### 24. 大规模训练前必须先有带时间记录的小规模验证
- 现象：
  - 训练任务容易因为数据读取、日志写盘、checkpoint、硬件吞吐或提权环境差异而产生错误的速度预估。
- 风险：
  - 如果不先跑通小规模训练并记录时间，后续很容易高估或低估硬件速度，导致训练计划和资源判断失真。
- 处理要求：
  - 每次进入更大规模训练前，必须先完成小规模训练验证。
  - 训练日志或报告中必须显式记录开始时间、结束时间和耗时。
  - 未完成小规模验证前，不把任何大规模训练耗时估计当作可靠结论。

### 25. 大规模训练必须显式引用成功的小规模实验
- 现象：
  - 当前训练入口已加入 `training.run_stage` 与 `training.prerequisite_experiment_id` 门禁。
- 风险：
  - 如果后续把训练规模放大但不保留前置实验引用，文档和代码会再次脱节。
- 处理要求：
  - `run_stage = small_scale_validation` 只能用于小规模验证。
  - `run_stage = large_scale` 时，必须引用一个状态成功的小规模实验 metrics 文件，否则训练直接拒绝执行。
  - 若后续修改训练入口，必须保留这条受控失败路径，并重新验证一次。

### 26. 当前固定尾部验证切片已确认存在严重分布偏差
- 现象：
  - 目标侧尾部 8 条全部来自 `no_text_voice` 子组。
  - 源侧尾部 8 条全部集中在录音尾部。
- 风险：
  - 如果继续把它当作正式验证集，会把特殊子组和时间尾部偏差误当成模型整体表现。
- 处理要求：
  - 在用户确认正式拆分方案前，只把当前固定切片用于临时回归检查。
  - 不再把当前尾部切片结果当作正式泛化评估结论。

### 27. `data.split_dir` 存在时，训练入口不再使用 fallback 验证计数
- 现象：
  - 当前训练配置仍保留 `target_validation_count` 和 `source_validation_count` 字段，但在 `data.split_dir` 指向正式 split 时，这两个字段只作为 fallback 保留。
- 风险：
  - 如果后续误以为这两个数字仍控制当前正式验证集规模，会对训练结果产生错误理解。
- 处理要求：
  - 读取训练结果时，应以 `split_strategy` 和 `split.counts` 为准。
  - 只有在 `split_dir` 为空时，才使用 fallback tail split 计数。

### 28. 当前 `target_special_eval` 是 punctuation-only challenge slice
- 现象：
  - 当前 `target_special_eval` 的 8 条都来自 `no_text_voice`，且 `clean text` 全为单个标点。
- 风险：
  - 如果把它当成正常内容验证集，会错误解读模型内容保持能力。
- 处理要求：
  - 当前只把它解释为 challenge-only stress slice。
  - 后续若做模型级 special eval，结论必须与常规 validation 分开汇报。

### 29. 新控制融合结构会使旧 checkpoint 与当前模型定义不兼容
- 现象：
  - 为了让 `z_art / e_evt` 真正参与下游输出，offline MVP 模型新增了控制融合层。
- 风险：
  - 旧实验生成的 checkpoint 不能直接用于当前消融评估或继续训练，否则会因参数结构不匹配而失败或产生错误结论。
- 处理要求：
  - 每次模型结构调整后，都必须重新生成兼容 checkpoint。
  - 评估与训练报告中必须明确引用本轮实际使用的 checkpoint 路径。

### 30. `torch.load` 的默认反序列化行为未来会变化
- 现象：
  - 首次运行控制消融评估时，`torch.load(..., weights_only=False)` 触发了 FutureWarning。
- 风险：
  - 若继续依赖默认行为，后续 PyTorch 版本变化可能导致日志污染，甚至出现不必要的兼容问题。
- 处理要求：
  - 本地自有 checkpoint 读取优先显式使用 `weights_only=True`。
  - 若需要兼容旧版本接口，再做受控 fallback，而不是依赖默认参数。

### 31. 默认训练采样方案现已切到 seeded-shuffle
- 现象：
  - 用户已明确拍板，默认训练模板改为基于固定 seed 的 shuffled 采样。
- 风险：
  - 如果后续阅读训练结果时忽略 `sampler_mode / seed / sampler seeds`，会把不同采样方案的结果混在一起比较。
- 处理要求：
  - 所有正式训练报告必须显式记录：
    - `sampler_mode`
    - `seed`
    - `target_sampler_seed`
    - `source_sampler_seed`
  - 若使用顺序采样做回退或对照，必须在实验名和报告标题中明确写出 `sequential`。

### 32. `e_evt` 在 large-scale 后期出现依赖回落现象
- 现象：
  - 在 `EXP-20260314-011-offline-mvp-large-scale-500` 中，`zero_e_evt.delta_target_loss_total` 从 `step25` 的 `1.79018` 回落到 `step500` 的 `0.286237`。
- 风险：
  - 这说明 `e_evt` 虽仍有效，但后期可能被其他路径部分替代。
  - 若继续扩训练步数而不跟踪此现象，可能误把“控制链已接通”当成“控制链会持续被依赖”。
- 处理要求：
  - 后续继续训练前，优先补 early-vs-late focused 分析。
  - 后续报告必须把 `z_art` 与 `e_evt` 分开解释，不能只汇报一个总的“控制消融通过”。

### 31. 模型级评估里的输出统计必须按特征维度正确归一
- 现象：
  - 首次运行 `target_special_eval` 模型级评估时，`event_prob_mean` 一度大于 `1`，暴露出 masked mean 的分母没有覆盖特征维度。
- 风险：
  - 虽然不影响 loss 计算，但会直接误导对 `z_art / event / acoustic` 输出量级的解读。
- 处理要求：
  - 所有带 frame mask 的输出统计都必须按展开后的权重求均值。
  - 看到概率均值超出 `0-1` 范围时，应优先排查统计口径而不是先怀疑模型本身。

### 32. `no_text_voice` 子集经人耳复核不含完整音节
- 现象：
  - 用户确认目标音频的 `no_text_voice` 子集里没有任何完整音节，基本都是喘气等非完整发声。
- 风险：
  - 如果把该子集当成正常语音验证或内容保持验证，会高估模型在真实短语音上的泛化能力。
- 处理要求：
  - `target_special_eval` 只能作为 nonverbal / near-nonverbal challenge slice 汇报。
  - 不得把其结果与常规内容 validation 直接平均。

### 33. seed 与 shuffle 是训练能力，不是未经确认的默认方案
- 现象：
  - 当前已经接入 `training.seed` 与 `training.shuffle_train_records`，并跑通了 seeded-shuffle 小规模训练。
- 风险：
  - 如果直接把 shuffle 结果视为必然优于顺序采样，会绕过“方案决策交由用户判断”的协作规范。
- 处理要求：
  - 文档应区分：
    - 功能已实现并可复现
    - 是否作为默认训练方案，仍需用户根据报告做判断

### 34. shuffled 与 sequential 的 step loss 不能做简单逐步对照
- 现象：
  - 引入 shuffle 后，每一步读取到的样本组合不同，训练 step loss 波动会更明显。
- 风险：
  - 如果直接用 step 号对齐比较单步 loss，很容易把样本差异误判成训练策略优劣。
- 处理要求：
  - 比较 shuffled 与 sequential 时，应优先看：
    - 固定 validation 历史
    - checkpoint-series 消融趋势
    - 最终 checkpoint 的正式评估

### 35. special slice 会在训练推进中发生“易到难”的解释翻转
- 现象：
  - `EXP-011` 的 special-eval series 显示：
    - `step25` 时 `delta_loss_total = -3.877301`
    - `step100` 后转为正值，并在 `step500` 保持 `0.365976`
- 风险：
  - 如果只看单个 checkpoint，很容易把 special slice 误判为一直“更容易”或一直“更难”。
- 处理要求：
  - 后续涉及 challenge slice 的判断，优先使用 series 视角，而不是只截 final checkpoint。

### 36. 工作区默认离线，网络动作必须交由用户手动执行
- 现象：
  - 当前协作规范已明确：除助手内置搜索能力外，工作区默认离线运行。
- 风险：
  - 如果把联网下载、安装依赖、拉模型等动作混进自动流程，会破坏可控性，也会违背用户的显式约束。
- 处理要求：
  - 需要联网时，必须暂停自动执行。
  - 直接向用户说明用途，并给出建议命令。
  - 等待用户手动完成后，再继续本地工作。

### 37. 技术说明如果只讲术语，用户很难快速判断方向
- 现象：
  - 当前任务已经进入控制路径、消融、checkpoint-series 这类高抽象阶段。
- 风险：
  - 如果只保留专业术语，不补通俗解释，用户在拍板方案时会更难判断“这一步实际在解决什么问题”。
- 处理要求：
  - 后续说明必须保持两层口径：
    - 专业术语层
    - 大白话层
  - 尤其在需要用户决策时，必须把“这个选项到底会带来什么实际后果”说清楚。
### 38. `A1` 这种“中后期增加 event 权重”的温和约束增强，不保证会带来更好的整体训练
- 现象：
  - 在 `EXP-20260314-013-offline-mvp-evt-a1-large-scale` 中：
    - `zero_e_evt.delta_target_loss_total` 从 baseline `0.286237` 提高到 `0.378181`
    - 但 final validation `loss_total` 从 `3.321292` 恶化到 `5.714126`
    - 同时 `zero_z_art.delta_target_loss_total` 从 `1.410600` 降到 `0.949323`
- 风险：
  - 如果只看 `e_evt` 单项敏感度，会误以为方案有效。
  - 实际上它可能只是把控制份额从 `z_art` 抢走，并拖坏总体收敛。
- 处理要求：
  - 后续评估 `e_evt` 约束增强时，必须同时看：
    - final / best validation `loss_total`
    - `zero_e_evt` 变化
    - `zero_z_art` 是否被明显压弱
  - 不允许只凭 `e_evt` 单项回升就判定方案通过。
### 39. 当前启发式 `event_target` 与基础声学特征高度冗余，且存在明显源/目标分布错位
- 现象：
  - `reports/data/offline_mvp_event_targets/event_target_analysis.md` 显示：
    - `energy_norm` 与 `energy` 相关性高达 `0.972414 / 0.935493`
    - `energy_gate` 与 `energy` 相关性高达 `0.914112 / 0.743154`
    - `delta_energy_rise / fall` 与 `delta_energy` 也高度相关
    - `high_zero_cross_voiced_like` 在 target 为 `0.193547`，在 source 仅 `0.000216`
- 风险：
  - 如果继续把这组启发式标签当成稳定事件监督，模型后期绕开 `e_evt` 并不奇怪。
  - 继续放大这类监督权重，可能只会放大冗余和域错位。
- 处理要求：
  - 后续所有 `e_evt` 路线决策，都要先参考正式分析产物：
    - `reports/data/offline_mvp_event_targets/event_target_analysis.md`
  - 如果继续做 `A` 系实验，必须承认它是在“问题标签上调约束”。
  - 若要治本，应优先考虑 `B` 路线的标签/监督升级。
### 40. 方案 `B` 当前只能立即升级目标侧文本监督，不能假装源侧已具备同等级标签
- 现象：
  - `reports/data/b1_supervision_inventory/b1_supervision_inventory.md` 已确认：
    - 目标侧 `624` 条全有文本与标点停顿线索
    - 源侧 `537` 条文本覆盖仍为 `0`
- 风险：
  - 如果后续把 `B` 误写成“源/目标两边都已具备文本级事件监督”，训练和文档都会高估当前可用监督质量。
- 处理要求：
  - 当前 `B1` 只能先做 target-side text-aware supervision。
  - source-side 仍须明确标记为：
    - audio-only heuristic supervision
    - or future transcript/alignment required
### 41. 源侧办公录音不适合强行做与目标侧同粒度的正字文本+标点标注
- 现象：
  - 用户已明确指出：
    - 源侧语速、发音、停顿和非规范口语现象较多
    - 很难把这些混乱特征稳定映射到统一标点体系
- 风险：
  - 如果硬做源侧全文本标注，标注噪声可能比监督收益更大。
  - 后续模型学到的可能是标注习惯，而不是稳定的内容/事件边界。
- 处理要求：
  - 当前 round1 不给源侧做手工全文本+标点标注。
  - `B1` 明确采用不对称监督：
    - target-side text-aware supervision
    - source-side audio-only supervision
### 42. `B1-offline-minimal` 在 20 step 看到的优势，不等于到 100 step 仍会继续扩大
- 现象：
  - `EXP-20260314-014-offline-mvp-b1-smallscale` 在 `20 step` 时：
    - `zero_z_art.delta_target_loss_total = 0.207014`
    - `zero_e_evt.delta_target_loss_total = 1.733871`
    - 相比无 `B1` 的 20 step 小规模基线，看起来更强
  - 但到 `EXP-20260314-015-offline-mvp-b1-100step-calibration step100`：
    - `target_loss_total = 2.676195`
    - 无 `B1 step100 = 2.667123`
    - `zero_z_art.delta_target_loss_total = 1.332663`
    - 无 `B1 step100 = 1.306952`
    - `zero_e_evt.delta_target_loss_total = 1.407506`
    - 无 `B1 step100 = 1.404717`
- 风险：
  - 如果只看早期 checkpoint，很容易高估 `B1-offline-minimal` 这版特征的长期收益。
  - 直接据此放大到 `500 step`，可能只是把“方向成立”误判成“当前特征版本已经足够强”。
- 处理要求：
  - 后续评估 `B1` 时，必须至少对照到 `step100` 级别，不能只看 `20 step`。
  - 若 `step100` 仍仅与无 `B1` 打平，应优先考虑 `B1.1` 细化，而不是默认直接放大。
### 43. 依赖训练产物的评估不能与训练本体并行启动
- 现象：
  - 在 `EXP-20260314-016-offline-mvp-b1-1a-100step-calibration` 中，首次把：
    - 训练
    - ablation
    - checkpoint-series
    - special-eval
    - special-eval-series
  - 一起并行启动，导致评估在 `experiment metrics` 里的 `checkpoint_path / checkpoint_paths` 尚未写完时提前读取，直接报错。
- 风险：
  - 如果后续继续把这类强依赖训练产物的命令并行启动，会反复出现“训练已成功，但评估读不到 checkpoint”的假失败。
- 处理要求：
  - 训练必须先完成并确认 `experiment metrics` 已写入 `artifacts.checkpoint_path / checkpoint_paths`。
  - 之后再启动依赖 checkpoint 的评估命令。
  - 可并行的是多个评估命令彼此之间，不是“训练 + 评估”混跑。
### 44. `C1` 这条弱事件提示路线，单靠 `weak_event` 在 `0.1` 到 `0.2` 之间微调，不足以形成新的明确突破
- 现象：
  - `EXP-20260314-017-offline-mvp-c1-1-100step-calibration` 与 `EXP-20260314-018-offline-mvp-c1-2-100step-calibration` 对比显示：
    - `C1.1 target_loss_total = 2.716403`
    - `C1.2 target_loss_total = 2.699184`
    - `C1.1 zero_e_evt.delta_target_loss_total = 1.433922`
    - `C1.2 zero_e_evt.delta_target_loss_total = 1.419051`
  - 两者都没有超过 `B1.1-A target_loss_total = 2.680581`。
- 风险：
  - 如果后续继续把主要时间投入到 `weak_event = 0.05 / 0.1 / 0.15 / 0.2` 这类小步扫参，容易把“接线稳定”误当成“监督升级已经足够有效”。
  - 这会拖慢真正更有信息量的下一步调查。
- 处理要求：
  - 若继续推进 route-C，应优先改变：
    - 弱事件监督的注入方式
    - 或弱标签本身的表达形式
  - 不能把 `0.1` 到 `0.2` 的标量调权，当成当前阶段的主要下一手。
### 45. 对 route-C 来说，弱边界提示的“接法”比 `weak_event` 标量大小更关键
- 现象：
  - `EXP-20260314-019-offline-mvp-c1-3-100step-calibration` 把弱边界提示从“独立 `weak_event` 辅助损失”为主，改成“event loss bias + 温和 event target override”后：
    - `target_loss_total = 2.683692`
    - 相比 `C1.1 = 2.716403`、`C1.2 = 2.699184` 明显更好
    - 并且几乎追平 `B1.1-A = 2.680581`
- 风险：
  - 如果后续还把 route-C 的主要问题理解成“`weak_event` 分数不对”，就会继续在次要矛盾上浪费时间。
  - 真正更有价值的工作会被拖后。
- 处理要求：
  - 后续继续 route-C 时，优先考虑：
    - 主 event loss 的偏置方式
    - boundary label 的表达粒度
    - pause / terminal 的差异化表达
  - 不要把 route-C 继续简化成“再调一个辅助损失权重”。
### 46. `C1.4` 这类 boundary pre/post target 微调，目前只带来极小幅度收益
- 现象：
  - `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 相比 `C1.3`：
    - `target_loss_total` 从 `2.683692` 到 `2.681003`
    - `target_special_eval.delta_loss_total` 从 `0.182364` 到 `0.181996`
    - `zero_e_evt.delta_target_loss_total` 从 `1.409978` 到 `1.410986`
- 风险：
  - 如果把这种量级的改善误读成“route-C 已经出现明确突破”，后续很容易继续沉迷于同一份 sidecar 周边的小步常数微调。
  - 这样会拖慢更有信息量的下一步工作。
- 处理要求：
  - 当前应把 `C1.4` 解释为：
    - route-C 的最新参考版本
    - 但不是已经清晰胜出的版本
  - 若继续 route-C，优先改标签表达或监督结构，不把主要时间继续花在当前常数微调上。
### 47. route-C 的中期依赖回落问题，还没有被 `C1.4` 解决
- 现象：
  - `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 的 checkpoint-series 仍显示：
    - `step50 zero_z_art.delta_target_loss_total = -0.173311`
    - `step50 zero_e_evt.delta_target_loss_total = -0.519136`
  - 到 `step80/90/100` 才重新回升到较强依赖。
- 风险：
  - 如果只看 final checkpoint，会误以为当前 route-C 已经稳定解决事件路径依赖问题。
  - 实际上中期训练行为仍不稳，说明问题并不只是 final 常数设得不够好。
- 处理要求：
  - 后续判断 route-C 是否值得继续，必须继续保留 checkpoint-series 视角。
  - 不得只凭 final checkpoint 的轻微改善，就宣称 route-C 已完成稳定化。
### 48. `manifest_round1_excluded.jsonl` 当前是格式隔离区，不是坏样本垃圾桶
- 现象：
  - 复核 `47` 条隔离样本后确认：
    - 没有 `missing_lab`
    - 没有 `empty_cleaned_text`
    - 排除原因全部来自非 `44100 Hz` 或非单声道
  - 其中约 `42` 条 lexical 样本理论上可通过：
    - resample
    - 或 downmix + resample
    回收
- 风险：
  - 如果继续把这份清单笼统理解成“坏样本”，后续很容易错过一批其实可用的数据。
  - 这会让数据层优化空间被错误掩盖。
- 处理要求：
  - 后续文档与汇报里，必须把这份清单解释为：
    - format quarantine
    - 而不是 junk bin
  - 若要做数据层升级，应优先讨论格式回收方案，而不是重复把它们当成内容异常样本。
### 49. `no_text_voice` 的格式隔离样本，不应因为可 resample 就直接混回正常训练
- 现象：
  - 当前隔离样本中有 `5` 条 `no_text_voice`：
    - 清洗后文本都为 `，`
    - 仍属于近非言语 / 非完整音节片段
- 风险：
  - 如果仅因格式修复可行，就把它们直接并回 lexical train split，会污染正常训练分布，并模糊 challenge slice 的解释边界。
- 处理要求：
  - 即使未来做 `round1.1` format normalization：
    - 也只优先回收 lexical 样本
    - `no_text_voice` 继续保持 isolated 或 special-use
### 50. `target_special_eval` 如果只看 `loss_text_aux` 和总 `event_prob_mean`，会低估真正的运行态差异
- 现象：
  - 在补强前，模型级 `special_eval` 主要只输出：
    - `loss_*`
    - `z_art_abs_mean`
    - `event_prob_mean`
    - `acoustic_abs_mean`
    - `text_aux_abs_mean`
  - 但在 `EXP-20260314-020-offline-mvp-c1-4-100step-calibration` 的补强结果里，新指标额外揭示：
    - `event presence / fall / energy` 平均值更低
    - `acoustic energy` 更低
    - `z_art` 时序变化更小
    - `event presence peak ratio` 反而更高
- 风险：
  - 如果继续只看旧口径，会把 special slice 误读成“主要是文本辅助更难”。
  - 这样会看不见它在真正运行态上“更稀疏、更低能量、但峰值更尖”的特点。
- 处理要求：
  - 后续 `target_special_eval` 汇报默认保留非文本运行态统计。
  - 不再把总 `event_prob_mean` 当作唯一事件侧解释指标。
### 51. `round1` 与 `round1.1` 的实验结果不能直接串成同一条基线曲线
- 现象：
  - `round1.1` 当前已经额外回收 `42` 条 lexical target 样本，target 记录数从 `624` 增到 `666`。
- 风险：
  - 如果后续把 `round1` 和 `round1.1` 的训练结果直接并排当作“同一数据线上的继续优化”，会把数据版本变化误读成模型改动收益。
- 处理要求：
  - 后续实验名、报告和汇总结论里，必须显式标记：
    - `round1`
    - 或 `round1.1`
  - 不得把两者直接画成同一条连续趋势线。
### 52. `round1.1` 当前是 target-only 升级，不应误写成 source 侧也重做了一版
- 现象：
  - 当前 `round1.1` 只新增 target 侧 recovery。
  - source 侧仍直接复用：
    - `data_prep/round1/source_segments`
- 风险：
  - 如果后续文档把 `round1.1` 误写成“整套数据全重做”，会夸大当前工作量，也会混淆数据变动来源。
- 处理要求：
  - 后续所有 `round1.1` 说明都应明确写成：
    - target-only data upgrade
    - source unchanged
### 53. 新实验如果没有预先建立 `.metrics.json`，训练会落计划和日志，但不会自动补 metrics 主文件
- 现象：
  - `train_entry.update_experiment_metrics()` 只会更新已存在的：
    - `reports/experiments/<experiment_id>.metrics.json`
  - 如果该文件不存在，训练照样会完成，但：
    - `train_plan`
    - step logs
    - checkpoints
    - 都会有
  - 唯独 experiment metrics 主文件不会被自动创建。
- 风险：
  - 后续 `special_eval / ablation / checkpoint_series` 这类依赖 `--experiment-metrics` 解析 checkpoint 的命令会直接失败。
  - 还容易造成“训练已经跑完，但汇总链条断了”的假性中断。
- 处理要求：
  - 新实验开跑前，必须先在：
    - `reports/experiments/`
  - 建立对应的 `.md` 和 `.metrics.json` 骨架。
  - 如果忘了建，补壳文件后需要重跑同实验一次，才能让训练入口把 `training_run` 正式写回 metrics。
### 54. 对当前 route-C 来说，纯事件约束小修补只能改善终点，不足以修复 `step50` 稳定性
- 现象：
  - `EXP-021` 已显示 `round1.1` 的终点 special slice 更顺，但 `step50` 依赖回落更重。
  - `EXP-022` 进一步用“只加 `event_dimension_weights`”验证后：
    - final `target_special_eval.delta_loss_total` 确实继续改善：
      - `0.028766 -> -0.025956`
    - 但 `step50 zero_e_evt.delta_target_loss_total` 基本没变：
      - `-0.854462 -> -0.846723`
    - `step50 zero_z_art.delta_target_loss_total` 也仍为负：
      - `-0.273851 -> -0.265417`
- 风险：
  - 如果后续继续主要投入在：
    - `event_dimension_weights`
    - `event_weight_schedule`
    - 或同层级的小步改权
  - 很容易把“终点更顺一点”误读成“中期稳定性已经在被修复”。
- 处理要求：
  - 后续若继续推进 route-C，优先级应转向：
    - 标签表达升级
    - 监督定义升级
  - 不再把同层纯约束小修补当成主线。
### 55. 当前 `C1` sidecar 如果只有边界点，没有 clause 级结构，标签表达会偏扁
- 现象：
  - `round1.1` 重建后的 `C1` sidecar 统计显示：
    - `multi_clause_single_terminal = 307`
    - `multi_terminal = 174`
    - `clause_count.mean = 3.010511`
  - 说明 target 台词里大量记录本身就带多分句和多终止结构。
- 风险：
  - 如果后续训练仍只消费：
    - `pause_boundaries`
    - `terminal_boundaries`
  - 而完全不利用 clause 级结构，就容易把复杂句内节律继续压扁成“几个边界点”。
- 处理要求：
  - 后续 route-C 的下一轮监督升级，优先考虑消费：
    - `clause_spans`
    - `utterance_structure_type`
    - `role`
  - 而不是只继续调边界点附近的 loss 权重。
### 56. 第一版 clause-aware 接线如果只给 clause body 做温和 floor，很可能接上但不解决 `step50`
- 现象：
  - `EXP-023` 已经真实消费：
    - `clause_spans`
    - `utterance_structure_type`
  - 但 `step50 zero_e_evt.delta_target_loss_total` 仍为：
    - `-0.853283`
  - 与 `EXP-021 / EXP-022` 基本同量级。
- 风险：
  - 如果后续把“结构化标签已经接上”误读成“结构化标签这条路已经有效”，就会继续在错误接法上浪费时间。
- 处理要求：
  - 后续 clause-aware 继续试时，优先盯：
    - clause end
    - inter-clause transition
    - final-vs-middle transition 差异
  - 不再把主要注意力放在：
    - clause body 上的温和 `presence / energy` floor
### 57. 如果 clause-end / transition 监督仍只是叠在现有 `event_boundary_bias` 上，新增信号可能会被原有边界监督吞掉
- 现象：
  - `EXP-024` 已经真实消费：
    - `clause_transition_target_overrides`
    - `clause["frame_end_index"]`
    - `middle / final / single` 的差异化 pre/post target
  - 但结果与 `EXP-021` 几乎重合：
    - final `target_special_eval.delta_loss_total`
      - `0.028766 -> 0.028482`
    - final `zero_e_evt.delta_target_loss_total`
      - `1.781482 -> 1.781535`
    - `step50 zero_e_evt.delta_target_loss_total`
      - `-0.854462 -> -0.854465`
    - `step50 zero_z_art.delta_target_loss_total`
      - `-0.273851 -> -0.273854`
- 风险：
  - 如果把这轮直接解读成“clause end 方向也没用”，就会过早否掉真正可能有效的监督方向。
  - 更合理的解释是：
    - 当前接法仍然依附在原有 punctuation boundary bias 上
    - 新增监督没有从旧信号里分离出来
- 处理要求：
  - 后续若继续做 clause-transition，优先考虑：
    - 独立 auxiliary loss
    - 或单独抽样的 clause-end frame supervision
    - 或单独的结构化监督通道
  - 不再主要依赖：
    - 在同一 `event_boundary_bias` 上继续叠更多 override 常数
### 58. 即使已经拆出独立 clause-transition auxiliary loss，在当前 uniform sampler 下也未必足以改写 `step50`
- 现象：
  - `EXP-025` 已经把 clause-transition 监督拆成独立 aux loss：
    - final `target_validation.loss_clause_transition_aux = 0.051682`
    - final `target_special_eval.loss_clause_transition_aux = 0.0`
  - 说明它确实形成了新信号，而不是假接线。
  - 但核心指标仍没改善：
    - `step50 zero_e_evt.delta_target_loss_total`
      - `-0.854462 -> -0.854869`
    - `step50 zero_z_art.delta_target_loss_total`
      - `-0.273851 -> -0.274127`
- 风险：
  - 如果后续继续主要做：
    - aux weight 常数微调
    - target value 常数微调
  - 很容易又回到“有一点独立信号，但训练动力学没变”的循环里。
- 处理要求：
  - 后续若继续沿独立 auxiliary loss 推进，优先考虑：
    - multi-clause / transition-rich 目标样本的 targeted sampling
    - 前中期 curriculum
    - 或单独提高这类记录的出现密度
  - 不再把“独立 aux loss 已经接上”误读成“问题已经从监督定义层面解决”。
### 59. targeted sampling / curriculum 是强杠杆，但当前会在 main validation、special slice 和 `step50` 之间形成明显 tradeoff
- 现象：
  - `EXP-026` aggressive 版把 priority 池提高到：
    - `priority_ratio = 0.75`
    - until `step70`
  - 得到：
    - final `target_validation.loss_total = 2.648178`
      - 当前最好
    - final `target_special_eval.delta_loss_total = 0.101163`
      - 明显变差
    - `step50 zero_e_evt.delta_target_loss_total = -0.933602`
      - 更差
  - `EXP-027` soft curriculum 版改成：
    - `priority_ratio = 0.5`
    - until `step40`
  - 得到：
    - final `target_special_eval.delta_loss_total = -0.075832`
      - 当前最好
    - `step50 zero_e_evt.delta_target_loss_total = -0.688658`
      - 明显改善
    - 但 final `target_validation.loss_total = 2.813174`
      - 当前较差
- 风险：
  - 如果后续只盯一个指标，很容易把另两个拖坏。
  - 尤其容易出现：
    - 主验证更好，但 special / `step50` 更差
    - 或 special / `step50` 更好，但主验证更差
- 处理要求：
  - 后续 targeted sampling 继续试时，优先做：
    - 中间档位 schedule
    - 只改 sampling / curriculum，不回去混入新的 loss 变量
  - 不要把当前实验简单理解成：
    - “采样越强越好”
    - 或“只要 softer 就一定更优”
### 60. 在当前 targeted sampling 路线里，简单做 ratio / duration 的中间插值，不会自动得到更好的平衡点
- 现象：
  - `EXP-028` 把 schedule 调到：
    - `priority_ratio = 0.625`
    - until `step55`
  - 也就是显式站在 `EXP-026` 和 `EXP-027` 中间。
  - 得到：
    - final `target_special_eval.delta_loss_total = -0.093905`
      - 当前最好
    - `step50 zero_e_evt.delta_target_loss_total = -0.778543`
      - 比 `EXP-026` 好
      - 但不如 `EXP-027`
    - final `target_validation.loss_total = 2.861962`
      - 比 `EXP-027` 还差
- 风险：
  - 如果后续继续默认“强版和软版之间取平均就会更稳”，很容易继续浪费轮次在被支配的中间点上。
  - 当前这条路更像是非线性 tradeoff，不是简单旋钮平均。
- 处理要求：
  - 后续若继续做 targeted sampling / curriculum，优先考虑：
    - 两段式 handoff
    - 更明确的 phase 切换
    - 或按训练阶段动态调度
  - 不再把“中间档位 schedule”默认当成首选平衡方案。
### 61. 在 `batch_size = 4` 的 `priority_interleave` 下，`priority_ratio` 实际上是离散槽位，不是连续旋钮
- 现象：
  - 当前 target `batch_size = 4`。
  - `priority_ratio` 最终会落成离散的 `priority_slots`：
    - `0.75 -> 3 slots`
    - `0.5 -> 2 slots`
    - `0.625 -> 2 slots`
    - `0.25 -> 1 slot`
  - 这意味着 `EXP-028` 的 `0.625` 并不是一个真正新的“中间槽位强度”，它和 `EXP-027` 一样都是 `2 slots`，只是持续时间更长。
- 风险：
  - 如果后续忽略这个离散化效应，只在小 batch 上继续扫小数 ratio，很容易误以为自己在试很多不同强度，实际上多数轮次只是重复同一档位。
- 处理要求：
  - 后续继续做 targeted sampling 时，优先从“实际 priority slots 是否变化”来定义实验，而不是只看表面的 ratio 小数。
  - 若想得到真正不同的 schedule，优先考虑：
    - `3 -> 1 -> 0` 这类 phase handoff
    - 或能实际改变 slot 数的 ratio 档位
### 62. 两段式 targeted-sampling handoff 可以同时改善 main validation 和 `step50`，但 final special slice 仍可能单独回退
- 现象：
  - `EXP-029` 用两段式 handoff：
    - `step1-25`: `3 priority slots`
    - `step26-45`: `1 priority slot`
    - `step46+`: 普通采样
  - 得到：
    - final `target_validation.loss_total = 2.702175`
      - 明显优于 `EXP-027 / EXP-028`
    - `step50 zero_e_evt.delta_target_loss_total = -0.463404`
      - 当前最好
    - `step50 zero_z_art.delta_target_loss_total = -0.163512`
      - 当前最好
    - 但 final `target_special_eval.delta_loss_total = 0.102328`
      - 几乎回到 `EXP-026` 的坏侧
- 风险：
  - 如果只看 `step50` 和 main validation，很容易误判为“schedule 已经找到答案”。
  - 实际上 special slice 说明：当前 priority pool 的组成仍可能把模型推离 punctuation-only challenge slice。
- 处理要求：
  - 后续若继续沿两段式 handoff 推进，优先考虑：
    - 收窄 priority pool
    - 重定义 priority 记录条件
    - 先保留 schedule，不优先继续扫 ratio / duration
  - 不要把“前中段动力学改善”误读成“special slice 已经一起解决”。
### 63. 把 `multi_terminal` 从 priority pool 里整体拿掉，虽然能救 final special slice，但会把 `step50` 和 main validation 一起拉坏
- 现象：
  - `EXP-030` 把 pool 改成：
    - `clause_count >= 3`
    - `exclude_structure_types = ["multi_terminal"]`
  - 得到：
    - final `target_special_eval.delta_loss_total = -0.012386`
      - 明显好于 `EXP-029`
    - 但 final `target_validation.loss_total = 2.828666`
      - 明显更差
    - `step50 zero_e_evt.delta_target_loss_total = -0.823020`
      - 也明显更差
- 风险：
  - 如果把 `multi_terminal` 简单当成噪声整体删除，很容易把真正帮到前中段动力学的那部分信号也一起删掉。
- 处理要求：
  - 后续不要再把“去掉 `multi_terminal`”当成默认清洗方向。
  - 若继续动它，优先考虑：
    - 限额
    - 分阶段暴露
    - 而不是整类清零
### 64. 只去掉 `multi_terminal-only` 的尾巴，也不足以保住 `step50` 和 main validation
- 现象：
  - `EXP-031` 只保留：
    - `clause_count >= 4`
  - 也就是只去掉原来 `OR multi_terminal` 额外补进来的那批短 `multi_terminal` 记录。
  - 得到：
    - final `target_special_eval.delta_loss_total = -0.029908`
      - 比 `EXP-030` 再略好
    - 但 final `target_validation.loss_total = 2.843136`
      - 仍差
    - `step50 zero_e_evt.delta_target_loss_total = -0.843525`
      - 仍差
- 风险：
  - 如果后续把问题简单归因成“就是那 49 条额外 `multi_terminal-only` 样本在捣乱”，会误判收益来源。
- 处理要求：
  - 后续应默认：
    - 长句里的 `multi_terminal` 子集本身也参与了收益和副作用
  - 不再把“删掉尾巴”视作足够的修正。
### 65. phase2 再做 pool cleanup，救不回 phase1 已经写下来的 final special 回归
- 现象：
  - `EXP-032` 做了 phase-specific pool handoff：
    - phase1: `clause>=4 OR multi_terminal`
    - phase2: `clause>=4-only`
  - 得到：
    - final `target_validation.loss_total = 2.672052`
      - 很强
    - `step50 zero_e_evt.delta_target_loss_total = -0.556712`
      - 也保住了大半
    - 但 final `target_special_eval.delta_loss_total = 0.103108`
      - 仍几乎和 `EXP-029` 一样差
- 风险：
  - 如果后续继续主要指望 phase2 或后段 cleanup 解决 final special，基本还会重复无效轮次。
- 处理要求：
  - 后续若继续推进，优先考虑：
    - 直接改 phase1 的 `multi_terminal` 暴露方式
    - 单独限制 phase1 的 `multi_terminal` 份额
    - 或把 `multi_terminal` 再拆成独立子池
  - 不再把“后段切 pool”当成主要救火手段。
### 66. 在当前 route-C 线上，phase1 给 `multi_terminal` 做 batch-level 限额，也未必能明显改变 final special
- 现象：
  - `EXP-033` 把额外 `multi_terminal-only` 尾巴限制为：
    - phase1 每 batch 最多 `1` 条
  - 得到：
    - final `target_validation.loss_total = 2.663196`
    - `step50 zero_e_evt.delta_target_loss_total = -0.549967`
    - final `target_special_eval.delta_loss_total = 0.111542`
  - `EXP-034` 进一步把所有 `multi_terminal` 都限制为：
    - phase1 每 batch 最多 `1` 条
  - 得到：
    - final `target_validation.loss_total = 2.669992`
    - `step50 zero_e_evt.delta_target_loss_total = -0.556362`
    - final `target_special_eval.delta_loss_total = 0.105375`
- 风险：
  - 如果后续继续默认“再把 phase1 配额调小一点，final special 就会回来”，很容易继续消耗轮次在低价值微变体上。
- 处理要求：
  - 后续不要再把 phase1 `multi_terminal` 配额微调当成优先方向。
  - 若继续推进，优先考虑：
    - 改 special slice 定义或监督方式
    - 或换一条和当前采样轴不同的杠杆
### 67. punctuation-oriented `text_aux reweight` 如果整段训练常开，可能会把 special 收益留在后段 checkpoint，却在 final checkpoint 反向翻车
- 现象：
  - `EXP-035` 保持 `EXP-032` 的 sampler 不变，只改 `text_aux` 监督：
    - 降低 lexical-heavy 维度权重
    - 提高 punctuation / structure 维度权重
  - 得到：
    - `step90 target_special_eval.delta_loss_total = -0.2803`
      - 很强
    - 但 final `target_special_eval.delta_loss_total = 0.39305`
      - 反而明显更坏
    - 同时 final `target_validation.loss_total = 2.889709`
      - 也差于 `EXP-032`
    - final `zero_e_evt.delta_target_loss_total = 0.931855`
      - 也明显更弱
- 风险：
  - 如果后续只看 final checkpoint，容易误判成“text_aux reweight 完全没用”。
  - 反过来，如果只看 `step90` 或中后段 special，也容易误判成“这版已经可以直接升级为默认配置”。
- 处理要求：
  - 后续若继续沿这条监督走，默认不要再用“整段常开”的固定 reweight。
  - 优先考虑：
    - 有阶段的 `text_aux_reweight` schedule
    - 前中段开启、后段衰减或关闭
    - 直接围绕 `step80-90` 附近的 late checkpoint 行为设计收口策略
### 68. `text_aux reweight` 的 late shutdown 即使真正执行，也可能几乎改不动 final checkpoint
- 现象：
  - `EXP-036`
    - `step81-100` 线性衰减到普通 `text_aux`
  - `EXP-037`
    - `step61-90` 线性衰减到普通 `text_aux`
  - 两轮训练日志都确认：
    - `reweight_strength` 确实在后段下降到了 `0.0`
  - 但 final 结果仍几乎与 `EXP-035` 重合：
    - `EXP-036 final delta_loss_total = 0.393366`
    - `EXP-037 final delta_loss_total = 0.392194`
    - `EXP-035 final delta_loss_total = 0.39305`
- 风险：
  - 如果后续只看“schedule 已接线”，很容易误以为继续微调 decay 起止步数就能慢慢救回来。
  - 实际证据更像：这类 late shutdown 对 final 行为几乎没有杠杆。
- 处理要求：
  - 后续不要继续优先扫：
    - `step60+` 才开始关
    - `step80+` 才开始关
    - 这类纯时间尾段 decay 小变体
  - 更合理的下一步应默认是：
    - 更早的 phase handoff
    - 或直接改 supervision target 拆分方式，而不是继续只做 late schedule
### 69. 把 lexical `text_aux` 组权重直接打成 `0.0`，若仍共用同一个 head，也未必能解除 lexical 对共享表示的拖拽
- 现象：
  - `EXP-038` 把 `text_aux` 明确拆成：
    - structural 组
    - lexical 组
  - 并设置：
    - `structural_weight = 1.0`
    - `lexical_weight = 0.0`
  - 结果 final 仍然几乎没有改善：
    - final `target_validation.loss_total = 2.89193`
    - final `target_special_eval.delta_loss_total = 0.398875`
    - final `zero_e_evt.delta_target_loss_total = 0.935605`
  - 同时新指标显示 lexical 组仍明显漂移：
    - validation `loss_text_aux_lexical = 0.359214`
    - special `loss_text_aux_lexical = 0.621452`
- 风险：
  - 如果后续只在 loss 权重上继续扫 `0.0 / 0.1 / 0.2` 这类小数，很容易继续陷进低价值微调。
  - 因为当前证据更像：真正的问题不是“loss 计不计分”，而是 lexical / structural 仍共用同一个 head 和共享梯度路径。
- 处理要求：
  - 后续不要优先继续做 lexical group 权重微调。
  - 更值得试的是：
    - lexical 头走 detached hidden
    - 或拆成独立 head / 独立梯度路径
    - 直接验证 lexical supervision 是否在拖 shared trunk
### 70. `detached lexical head` 能压住 lexical special gap，但不会自动修好 structural special gap 或 `step50` 控制回落
- 现象：
  - `EXP-039` 把 lexical prediction 改成单独 head，并让 lexical head 只吃 `pooled_hidden.detach()`
  - 结果 final `target_special_eval.delta_loss_total` 从：
    - `EXP-038` 的 `0.398875`
    - 降到 `0.354963`
  - 更关键的是：
    - final `delta_loss_text_aux_lexical = 0.007416`
      - 已经很小
    - 但 final `delta_loss_text_aux_structural = 0.143281`
      - 仍明显偏高
  - 同时：
    - final `target_validation.loss_total = 2.911644`
      - 仍弱
    - `step50 zero_z_art.delta_target_loss_total = -0.358804`
    - `step50 zero_e_evt.delta_target_loss_total = -0.532724`
      - 中段控制回落仍在
- 风险：
  - 如果后续把 `EXP-039` 误读成“问题已经基本解决，只差再调一点 lexical 权重”，会继续浪费轮次在低价值方向上。
  - 实际上它更像是在告诉我们：
    - lexical 拖拽确实存在
    - 但现在剩下的主矛盾已经转到 structural supervision 本身
- 处理要求：
  - 后续不要再把重点放回 lexical 权重小数微调或 late schedule。
  - 更合理的下一步应默认是：
    - structural head 也做独立路径
    - 或把 structural supervision 再细分成更贴近 runtime 的子目标
    - 直接围绕 structural gap 和 `step50` 稳定性继续打
### 71. 在 lexical head 已经 detach 后，再把 structural head 也 detach，可能几乎是零增量
- 现象：
  - `EXP-040` 在 `EXP-039` 基础上进一步设置：
    - `structural_detach_shared_input = true`
    - `lexical_detach_shared_input = true`
  - 结果 final 几乎与 `EXP-039` 重合：
    - `EXP-039 final target_validation.loss_total = 2.911644`
    - `EXP-040 final target_validation.loss_total = 2.91453`
    - `EXP-039 final target_special_eval.delta_loss_total = 0.354963`
    - `EXP-040 final target_special_eval.delta_loss_total = 0.349915`
    - `EXP-039 final zero_e_evt.delta_target_loss_total = 0.949482`
    - `EXP-040 final zero_e_evt.delta_target_loss_total = 0.949163`
  - `step50` 的 `zero_z_art / zero_e_evt` 也几乎不变
- 风险：
  - 如果后续继续默认“只要再切一点 `text_aux` head 梯度，structural gap 就会继续收缩”，大概率会继续消耗轮次在低价值结构手术上。
  - 当前证据更像：
    - `text_aux` head 路径已经不是主瓶颈
    - 剩余问题在 runtime 主干本身的结构行为学习
- 处理要求：
  - 后续不要再优先做 detached head 变体。
  - 更合理的下一步应默认是：
    - 直接改 `event / clause_transition_aux` 等 runtime 代理监督
    - 或做更直接的 punctuation-only consistency / structural proxy 设计
### 72. 新增 loss 如果只在 validation slice 生效、在 special slice 上为零，会制造“delta_loss_total 变好”的假象
- 现象：
  - `EXP-041` 新增了 `boundary_contrast_aux`
  - final 看起来：
    - `target_special_eval.delta_loss_total = 0.342355`
      - 比 `EXP-039` 的 `0.354963` 略好
  - 但拆开看：
    - validation `loss_boundary_contrast_aux = 0.050434`
    - special `loss_boundary_contrast_aux = 0.0`
  - 同时其余核心行为指标几乎完全不变：
    - `delta_loss_text_aux_structural = 0.143281`
    - `delta_loss_text_aux_lexical = 0.007416`
    - `step50 zero_z_art / zero_e_evt` 也与 `EXP-039` 一样
- 风险：
  - 如果后续继续把 `delta_loss_total` 当成唯一主指标，很容易把“validation 多了一项专属 loss”误判成“special 行为真的改善了”。
  - 这会让很多看起来“略好一点”的实验其实只是换了会计口径。
- 处理要求：
  - 后续评估新增 aux 时，默认必须同时看：
    - 该 aux 在 validation 和 special 上是否都激活
    - 输出统计和 ablation 依赖是否真的改变
  - 如果新 loss 在 special 上恒为 `0`，就不要把 `delta_loss_total` 的改善当成行为结论。
### 73. 即使新 aux 在 special slice 上真实激活，也未必会形成新杠杆
- 现象：
  - `EXP-042` 的 `punctuation_profile_aux` 同时在两边生效：
    - validation `loss_punctuation_profile_aux = 0.01164`
    - special `loss_punctuation_profile_aux = 0.001526`
  - 所以它已经不是 `EXP-041` 那种“只改记账口径”的情况
  - 但行为结果仍几乎不变：
    - final `target_validation.loss_total = 2.910157`
    - final `target_special_eval.delta_loss_total = 0.356926`
    - final `zero_e_evt.delta_target_loss_total = 0.948263`
    - `step50 zero_z_art / zero_e_evt` 也仍旧接近 `EXP-039`
- 风险：
  - 如果后续继续默认“只要换一个更 special-facing 的 aux，总会慢慢碰到正确方向”，很容易继续消耗轮次在低收益 proxy 上。
  - 当前证据更像：
    - 当前 scaffold 下，auxiliary-loss 这条线本身已经接近天花板
- 处理要求：
  - 后续不要再优先继续堆新的小 auxiliary loss。
  - 更合理的下一步应默认转向：
    - checkpoint 选择 / 训练流程层
    - 或更强的数据视角改造
### 74. 在当前 round1.1 late window 里，checkpoint 选择不是单轴优化，而是至少三路 tradeoff
- 现象：
  - `EXP-035 / 039 / 042` 在 `step80 / 90 / 100` 上呈现出几乎同构的分叉：
    - `step80`
      - special 最好
      - `zero_z_art / zero_e_evt` 都仍为正
      - 但 validation 明显更差
    - `step90`
      - validation 更强
      - `zero_e_evt` 也更强
      - 但 `zero_z_art` 已接近 `0`
    - `step100`
      - validation 达到本实验最好
      - 但 special 翻回正值
      - `zero_e_evt` 也较 `step90` 回落
  - 例如 `EXP-042`：
    - `step80`
      - `target_validation.loss_total = 4.282626`
      - `target_special_eval.delta_loss_total = -0.553492`
      - `zero_e_evt.delta_target_loss_total = 0.66439`
      - `zero_z_art.delta_target_loss_total = 0.550914`
    - `step90`
      - `target_validation.loss_total = 3.522161`
      - `target_special_eval.delta_loss_total = -0.295714`
      - `zero_e_evt.delta_target_loss_total = 1.520532`
      - `zero_z_art.delta_target_loss_total = 0.005477`
    - `step100`
      - `target_validation.loss_total = 2.910157`
      - `target_special_eval.delta_loss_total = 0.356926`
      - `zero_e_evt.delta_target_loss_total = 0.948263`
      - `zero_z_art.delta_target_loss_total = 0.178659`
- 风险：
  - 如果只看 validation：
    - 很容易机械选到 `step100`
    - 但会错过 late-window 已经出现过的更好 special 行为
  - 如果只看 special：
    - 很容易机械选到 `step80`
    - 但 validation 代价会被低估
  - 如果只看 `zero_e_evt`：
    - 很容易选到 `step90`
    - 但会忽略 `z_art` 已经接近塌缩
- 处理要求：
  - 后续 checkpoint 选择不能只看单一指标。
  - 至少要联合约束：
    - `target_validation.loss_total`
    - `target_special_eval.delta_loss_total`
    - `zero_e_evt.delta_target_loss_total`
    - `zero_z_art.delta_target_loss_total`
  - 在把 early checkpoint 升为默认模型前，必须先明确它到底是在“用 validation 换 special”，还是“用 z_art 换 e_evt”。
### 75. 当前 checkpoint gate replay 只能在 `step80 / step90 / final` 三种 tradeoff 之间切换，不能单独救回主线
- 现象：
  - `checkpoint gate replay` 对 `EXP-032 / 035 / 039 / 042` 的回放显示：
    - `late_special_unconstrained`
      - 会把 `035 / 039 / 042` 全选到 `step80`
    - `late_special_validation_guard_1p25`
      - 会把 `035 / 039 / 042` 全选到 `step90`
    - `late_special_strict_positive_control`
      - 会把它们重新选回 final
  - 也就是说：
    - 当前 gate 不是在创造新解
    - 而是在现有三种已知 tradeoff 之间做切换
- 风险：
  - 如果后续把 gate 直接接进训练主流程，很容易制造一种假象：
    - 好像已经找到“自动更优”的 checkpoint 规则
  - 但当前证据更像：
    - 只是把“选 `step80` 的代价”或“选 `step90` 的代价”写死进流程
  - 尤其关键的是：
    - 对非 `EXP-032` 实验，目前没有任何 gate 选出的 checkpoint 能整体打赢 `EXP-032 final`
- 处理要求：
  - 当前 gate 应先保留为离线诊断工具。
  - 在没有新证据前，不把它直接升为默认训练 checkpoint 选择器。
  - 下一轮优先级应转向：
    - 更强的数据视角改造
    - 或监督定义层级的更实质变化
  - 不再优先继续围绕 `80 / 90 / 100` 的选点规则打转。
### 76. `target_special_eval` 的真正近邻是“短、非终止、标点驱动片段”，不能和大规模结构池混成一个 bucket
- 现象：
  - 新增的 `target special supervision blueprint` 已确认：
    - `target_special_eval` 本身仍是 `8` 条纯 nonverbal challenge
    - 训练/验证中最接近它的 `challenge_proxy_core` 只有 `16` 条
    - 这 `16` 条的画像非常集中：
      - lexical char 中位数 `1`
      - 时长中位数 `0.920998`
      - clause 中位数 `1`
      - pause / terminal 中位数 `1 / 0`
      - `final_terminal_type = none` 全部成立
    - 但另外几条常被口头统称为 structural 的池子，其实量级和形态完全不同：
      - `structural_multi_terminal = 174`
      - `structural_question_exclaim = 144`
      - `structural_clause_ge4 = 206`
      - 它们的 lexical / 时长中位数都明显更高
- 风险：
  - 如果下一轮把：
    - `challenge_proxy_core`
    - `multi_terminal`
    - `question/exclaim`
    - `clause_ge4`
    直接混成一个统一加权的大 pool，
    那么真正接近 special 的近邻信号会再次被更大规模的复杂句样本稀释。
  - 这样很容易重复最近几轮的老问题：
    - 看起来 supervision 更“special-facing”
    - 实际上模型学到的仍主要是广义结构复杂度，而不是 special 邻域压力。
- 处理要求：
  - 后续数据/监督实验至少要把两层信号分开：
    - `challenge_proxy_core / relaxed`
    - 大规模结构 supervision bucket
  - 如果只做一轮最小实验，优先先上：
    - `challenge_proxy_core`
    - 再额外单选一条结构轴
  - 不要一开始就把所有结构池混成一个总权重。
### 77. `phase_priority_record_count` 在 pool-aware sampling 下统计的是 primary 和 secondary 的 union，不是 primary 单池大小
- 现象：
  - 新的 `D1` dry-run 中：
    - 主池 `challenge_proxy_core` 只有 `16`
    - 但 phase1 `priority_record_count` 显示为 `172`
  - 这是因为 phase1 同时配置了：
    - primary: `challenge_proxy_core`
    - secondary: `structural_multi_terminal`
  - 当前训练计划里的 `phase_priority_record_counts` 口径统计的是：
    - `priority_union_records`
    - 也就是主池和次池合并后的去重总数
- 风险：
  - 如果后续直接把 `phase_priority_record_count` 当成“主池规模”，
    很容易误判：
    - `challenge_proxy_core` 已经被放大到上百条
  - 这会让我们对实际抽样压力来源失真。
- 处理要求：
  - 后续看 pool-aware sampling 配置时，至少同时区分：
    - primary pool size
    - secondary pool size
    - phase priority union size
  - 不要把 union 计数直接当成 `challenge_proxy_core` 的规模。
### 78. `challenge_proxy_core` 本身会改 late-window 形状，但搭错 secondary 结构轴仍然会回到“tradeoff 改形不夺冠”
- 现象：
  - `EXP-20260315-017` 采用：
    - primary `challenge_proxy_core`
    - secondary `structural_multi_terminal`
  - final 仍明显不如 `EXP-032`：
    - final `target_validation.loss_total = 2.846479`
    - final `target_special_eval.delta_loss_total = 0.412091`
    - final `zero_e_evt.delta_target_loss_total = 0.86209`
    - final `zero_z_art.delta_target_loss_total = 0.271847`
  - 但它的 `step80` 与 `035 / 039 / 042` 的 `step80` 已经不是同一种 tradeoff：
    - validation 代价更小
    - `e_evt` 更强
    - special 改善更浅
- 风险：
  - 如果后续只盯 final，很容易误判成：
    - `challenge_proxy_core` 没价值
  - 但当前证据更像：
    - primary 已经在改轨迹
    - 只是当前 secondary `multi_terminal` 还没有和它形成正确互补
- 处理要求：
  - 后续沿 pool-aware sampling 继续时，优先保留 primary：
    - `challenge_proxy_core`
  - 下一轮优先换 secondary 结构轴，而不是推翻 primary。
  - 默认优先级：
    - 先比 secondary axis
    - 再考虑是否需要改 phase schedule
### 79. `structural_question_exclaim` 在当前 schedule 下几乎只是 `multi_terminal` 的近似重跑，不值得继续横向扩展
- 现象：
  - `EXP-20260315-018`
    - primary `challenge_proxy_core`
    - secondary `structural_question_exclaim`
  - 与 `EXP-20260315-017`
    - secondary `structural_multi_terminal`
    相比，final 和 late-window 几乎重合：
    - `D1 final = 2.846479 / 0.412091 / 0.86209 / 0.271847`
    - `D2 final = 2.848954 / 0.411368 / 0.855047 / 0.26885`
    - `D1 step80 = 3.823698 / -0.411991 / 1.223908 / 0.471141`
    - `D2 step80 = 3.821265 / -0.40801 / 1.216376 / 0.472709`
- 风险：
  - 如果后续继续横向扫更多“名字不同但分布相近”的 secondary 结构池，
    很可能只会重复 `D1 / D2` 这种：
    - 结果数值不同不到可用程度
    - 但会消耗实验预算
  - 这样会拖慢真正有信息增益的方向：
    - phase schedule
    - handoff 设计
    - 或真正不同分布的 secondary axis
- 处理要求：
  - 在当前 `25 / 45 / shuffle` 骨架下，
    暂不继续优先扩展 `question_exclaim` follow-up。
  - 后续 secondary 选择应优先关注：
    - 是否真的改变 final/late-window 形状
    - 而不是标签语义上看起来更贴近表达。
### 80. `structural_clause_ge4` 是当前首个真正改变 pool-aware final 行为的 secondary，但它仍然没有解决 validation / z_art 约束
- 现象：
  - `EXP-20260315-019`
    - primary `challenge_proxy_core`
    - secondary `structural_clause_ge4`
  - final 变成：
    - `2.901056 / 0.133206 / 1.135895 / 0.179408`
  - 对比 `D1 / D2`：
    - special 明显更好
    - `e_evt` 明显更强
    - validation 更差
    - `z_art` 更弱
  - 联合 selection 里：
    - `best_positive_control_late_special_experiment = EXP-019 step80`
  - 但联合 gate replay 里：
    - `non_anchor_joint_beating_count = 0`
- 风险：
  - 如果只看到 `D3` 的 special 回升，
    容易误判成：
    - secondary 已经选对，直接换 checkpoint 或直接升主线即可
  - 但当前真实约束仍然在：
    - validation 没回来
    - `z_art` 也没有恢复到 anchor 附近
- 处理要求：
  - 把 `structural_clause_ge4` 视为当前 secondary 主线候选，
    但不要把 `EXP-019` 直接升为新 anchor。
  - 下一轮优先围绕它调：
    - phase ratio
    - phase handoff
    - late shuffle 起点
  - 不再把重点放在：
    - 继续横向换更多 secondary 名称
    - 或继续用 gate 试图从现有 `80 / 90 / 100` 中“选出”新主线
### 81. `clause_ge4` 线的收益不是“phase 越晚越好”，而是存在很窄的 handoff sweet spot
- 现象：
  - `D4` 把 `clause_ge4` 的 early pressure 收软，并把 primary-only handoff 延到 `60`，
    得到：
    - final `2.729466 / -0.00228 / 1.527013 / 0.199795`
  - `D5` 再把 handoff 从 `60` 延到 `70`，
    得到：
    - final `2.810181 / -0.031687 / 1.462891 / 0.137204`
  - `D5` 只在 final special 上更强，
    但 validation、`e_evt`、`z_art` 全部回退
- 风险：
  - 如果后续继续把 handoff 越拖越晚，
    很容易落入一种错觉：
    - special 还在继续变好
    - 所以方向仍然单调正确
  - 但当前证据更像：
    - 这条线已经进入 very narrow tradeoff zone
    - 继续往一个方向推，只是在拿整体平衡去换 special
- 处理要求：
  - 现阶段把 `D4` 视为 `clause_ge4` 线的 schedule 基线。
  - 不再优先横向扩展更晚 handoff 的纯 schedule 变体。
### 82. 当 `clause_ge4` 线已经把 final special 拉回负值区间后，剩余主瓶颈不再是 sampler 覆盖，而是 `z_art` 保留
- 现象：
  - `D4 final` 已经做到：
    - validation 接近 anchor
    - final special 优于 anchor
  - 但 `z_art` 仍只有：
    - `0.199795`
  - anchor `EXP-032 final` 则是：
    - `1.275259`
  - 即使 `D5` 进一步追 final special，
    也没有把 `z_art` 拉回去，反而更弱：
    - `0.137204`
- 风险：
  - 如果继续把注意力放在 sampler schedule 本身，
    很可能只会继续制造：
    - special 更好一点
    - 但 `z_art` 继续掉队
  - 这会让我们误把“剩余控制瓶颈”当成“覆盖还不够”。
- 处理要求：
  - 后续 `clause_ge4` 线的主要 follow-up 应从：
    - 继续调 schedule
    转向：
    - `z_art` 保留
    - 或更明确的 dual-control 约束
  - 在没有新证据前，不把 `D5` 这类“更强 special / 更弱 balance”的变体升为默认方案。
### 83. `z_smooth` 权重 schedule 可以技术上完全生效，但对当前 `z_art` 瓶颈几乎没有行为杠杆，不要把“schedule 在跑”误判成“方向有效”
- 现象：
  - `D6`
    - 在 `D4` sampler 不变的前提下，
    - 只引入 `z_smooth_weight_schedule`
      - `step60 = 0.1`
      - `step70 = 0.07`
      - `step80 = 0.03666666666666668`
      - `step90 = 0.02`
      - `step100 = 0.02`
  - 训练 history 已确认 schedule 确实执行。
  - 但 `D6 final = 2.728306 / -0.001608 / 1.52269 / 0.20107`
    对比 `D4 final = 2.729466 / -0.00228 / 1.527013 / 0.199795`：
    - 只有极小量级漂移
  - late-window 也几乎重合：
    - `D4 step80/90/100 = 3.688603 / -0.30717 / 1.315593 / 0.412683 ; 3.427096 / -0.343128 / 1.522258 / -0.184007 ; 2.729466 / -0.00228 / 1.527013 / 0.199795`
    - `D6 step80/90/100 = 3.688544 / -0.307189 / 1.315578 / 0.412773 ; 3.428308 / -0.344274 / 1.520919 / -0.185088 ; 2.728306 / -0.001608 / 1.52269 / 0.20107`
- 风险：
  - 如果后续只看到：
    - loss schedule 被正确记录
    - effective weight 随 step 变化
  - 很容易误判成：
    - 已经命中真实控制杠杆
    - 或只需要继续细扫 schedule 参数
  - 但当前证据更像：
    - late `z_smooth` decay 对这条轨迹的影响近乎可忽略
    - 当前 `z_art` 问题不太可能靠平滑权重微调单独解决
- 处理要求：
  - 后续不要把“schedule 生效”本身当成实验正信号。
  - 纯 `z_smooth` schedule sweep 暂不再作为高优先级主线。
  - 若继续沿 `clause_ge4` 主线推进，优先转去：
    - 更显式的 `z_art` 保留机制
    - 或更明确的 dual-control-preservation 约束
### 84. `z_art_influence_aux` 在 eval slices 上显示为 `0.0`，不代表机制没有生效；判断应看 ablation sensitivity，而不是只看 eval 里有没有记到 aux
- 现象:
  - `D7 / D8` 的 final validation 与 final `target_special_eval` 都显示:
    - `loss_z_art_influence_aux = 0.0`
  - 但同时 final ablation 明显变化:
    - `D7 final`
      - `zero_e_evt.delta_target_loss_total = 3.489725`
      - `zero_z_art.delta_target_loss_total = 0.59961`
    - `D8 final`
      - `zero_e_evt.delta_target_loss_total = 3.480331`
      - `zero_z_art.delta_target_loss_total = 0.611369`
  - 对比 `D4 final = 1.527013 / 0.199795`，提升非常明确
- 原因:
  - 当前 `z_art_influence_aux` 只挂在:
    - `challenge_proxy_core`
  - formal validation 和 `target_special_eval` 切片里并不包含这些样本
  - 因而 eval 汇总里 aux 项自然记为 `0.0`
  - 但训练期间机制已经改变了模型的控制使用方式
- 风险:
  - 如果后续只看 eval markdown 里 aux 项是不是非零，容易误判为:
    - 机制没有生效
    - 或收益只是被别的 loss 波动偶然带出来
  - 另一种反向误判是:
    - 只要 ablation 变强，就怀疑是把 aux loss 直接算进了 eval
  - `D7 / D8` 恰好说明两种误判都可能发生
- 处理要求:
  - 对这类 target-pool-aware aux，优先看:
    - final / late-window ablation deltas
    - 与基线的 validation / special 是否仍守住
  - 不要把“eval 里 aux=0.0”直接等同于“机制无效”
  - 也不要把 ablation 变强直接当成“评估口径污染”
### 85. 在同一 target pool 上继续抬 `min_influence`，很容易很快进入 `D7` 的近似重跑区，不要把微小 `z_art` 增益误判成新 regime
- 现象:
  - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `D8 final = 2.730527 / -0.003362 / 3.480331 / 0.611369`
  - `D8` 只比 `D7`:
    - `z_art` 略好 `+0.011759`
    - validation / special / `e_evt` 都略回退
  - late-window 也近乎重合:
    - `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
    - `D8 step90 = 3.427309 / -0.342909 / 2.798612 / 0.520328`
- 风险:
  - 如果继续在同一配置上只扫更高 floor，很容易把:
    - 很小的 `z_art` 回升
    误读成:
    - 找到了新的轨迹方向
  - 这会让实验资源继续消耗在“同形细抠”上，而不是去验证更有信息增益的变化维度
- 处理要求:
  - 当前 explicit-control 线默认基线保持为:
    - `D7`
  - `D8` 作为边界确认保留，不升为新默认
  - 后续若继续沿 `z_art_influence` 推进，优先改:
    - influence 覆盖范围
    - influence 覆盖层级
  - 不再优先继续做同一 target pool 上的纯 `min_influence` sweep
### 86. 仅把 `z_art_influence_aux` 的 pool 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + structural_clause_ge4`，并不会自动把轨迹推进到新 regime
- 现象:
  - `D9`
    - 相比 `D7` 只改了:
      - `pool_memberships = ["challenge_proxy_core", "structural_clause_ge4"]`
  - 但 final 结果仍与 `D7 / D8` 近乎重合:
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
    - `D8 final = 2.730527 / -0.003362 / 3.480331 / 0.611369`
    - `D9 final = 2.730334 / -0.003173 / 3.486028 / 0.605922`
  - late-window 也基本同形:
    - `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
    - `D8 step90 = 3.427309 / -0.342909 / 2.798612 / 0.520328`
    - `D9 step90 = 3.427322 / -0.342677 / 2.804947 / 0.511672`
- 风险:
  - 如果后续把“coverage 变广”天然等同于“信号终于推广到主线”，很容易误判为:
    - 只要再多加一点 pool
    - 或再多纳入一点 structural bucket
    就能自然演化出新的最优解
  - `D9` 已经说明:
    - 在当前 influence-hinge 目标形状下，coverage 扩大本身并不足以改写最终轨迹
- 处理要求:
  - 当前 explicit-control family 暂以 `D7` 作为默认基线
  - `D8 / D9` 视作边界与复现确认，不再优先沿同一家族继续做纯 coverage sweep
  - 若后续继续追 `z_art`，优先改变:
    - 目标形状
    - 或训练 phase / handoff 机制
  - 不要把“pool 范围更大”本身当成新的强正信号
### 87. 在 explicit-control 条件下，`clause_ge4` handoff 的有效区间可能非常窄；不要把 `60-70` 当成可平滑插值的连续调参轴
- 现象:
  - `D10 (handoff 70)`
    - `final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
  - `D11 (handoff 65)`
    - `final = 2.762797 / 0.14741 / 2.706989 / 0.536627`
  - `D12 (handoff 68)`
    - `final = 2.965061 / 0.16957 / 2.31394 / 0.465272`
  - 也就是说:
    - `70` 还能保住 final special 为负
    - `65 / 68` 的 final special 都已经翻成明显正值
- 风险:
  - 如果把 handoff 当成平滑轴继续细扫，容易预设:
    - 介于 `60` 和 `70` 之间的点会形成平顺折中
  - 但当前证据更像:
    - 这条轴存在 cliff
    - 并不是越密扫越能逼近更优点
  - 这会让实验预算继续消耗在低信息增益的插值搜索上
- 处理要求:
  - 当前把 `D10` 视为这条 explicit-control handoff 线里唯一有新信息的点
  - `D11 / D12` 作为“sweet spot 很窄”的反证保留
  - 暂不继续在 `60-70` 区间做更密的 handoff 微调
  - 下一步若继续，应优先换:
    - 目标形状
    - 或更高层级的 phase 机制
### 88. 在当前 explicit-control 主线上，`step71-100` 的全局 late LR decay 会把轨迹推向 under-converged final；不要把“special 维持更负”误判成更优终点
- 现象:
  - `D13 = D7 + late LR decay`
    - `final = 3.27992 / -0.22848 / 2.950196 / 0.683167`
  - `D14 = D10 + late LR decay`
    - `final = 3.307872 / -0.240493 / 2.892546 / 0.714912`
  - 对比原基线:
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
    - `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
  - 同时 step log 已确认 schedule 确实生效:
    - `step70 lr = 0.0003`
    - `step80 lr = 0.00022551724137931031`
    - `step90 lr = 0.00014275862068965515`
    - `step100 lr = 0.00006`
- 风险:
  - 如果只看到:
    - final special 变得更负
  - 很容易误判成:
    - 成功修复了 late overrun
  - 但当前证据更像:
    - validation 改善速度被整体截断
    - `e_evt` consolidation 也被削弱
    - final 只是停在一个更早、更粗糙的 late-window 状态
- 处理要求:
  - 不要继续优先扩展更多全局 `learning_rate_schedule` sweep
  - 对 optimizer-level late smoothing，必须同时检查:
    - final validation
    - final `e_evt`
    - final `z_art`
    - 而不是只看 final special 是否更负
  - 若后续继续沿“更高层 phase 机制”推进，优先改成:
    - 不需要重训的新 phase 机制
    - 例如 late checkpoint averaging / weight interpolation
### 89. late checkpoint averaging 可以做出“更柔和的中间态”，但在当前 explicit-control 轨迹上不会自动创造新的 joint winner
- 现象:
  - `D7 step90+100 avg = 2.978639 / -0.098031 / 3.035429 / 0.569171`
  - `D10 step90+100 avg = 3.030039 / -0.090497 / 2.858374 / 0.59141`
  - 对比原 final:
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
    - `D10 final = 2.809966 / -0.0312 / 3.227099 / 0.603582`
- 风险:
  - 如果只看到 averaged checkpoint:
    - final special 更负
  - 很容易误判成:
    - late averaging 已经把 `step90` 的 special 和 `step100` 的 validation 真正合成了更优解
  - 但当前证据显示:
    - validation 明显回退
    - `e_evt` 也同步回退
    - averaging 只是停在已有 tradeoff 的中间位置
- 处理要求:
  - 可保留 checkpoint averaging 作为正式工具
  - 但不要继续优先做大规模 averaging sweep
  - 若 averaged checkpoint 不能同时改进:
    - validation
    - `e_evt`
    - `z_art`
    - 而只是把 special 拉得更负
    就不应把它视为新的主线候选
  - 在当前阶段，late mechanics 已基本验证完毕，下一步应转回:
    - 新的目标形状
    - 或更强的 supervision 变化
### 90. 对 `challenge_proxy_core` 的 sample-level profile 约束，如果只在 early/mid phase 生效，很容易看起来像“新目标形状无害但无用”；必须先区分是机制无效，还是 late exposure 不足
- 现象:
  - `D15 final = 2.730729 / -0.003582 / 3.489731 / 0.599471`
  - 与 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961` 近乎重合
  - 但进一步看 step log:
    - `step70 / 80 / 90 / 100` 的 `loss_challenge_proxy_profile_aux = 0.0`
- 风险:
  - 如果只看 final，很容易过早下结论说:
    - 这条 target-shape 完全没有信息增益
  - 但 `D15` 实际给出的更准确事实是:
    - 新机制没有在 late phase 持续参与优化
- 处理要求:
  - 对这类 pool-gated supervision，若 final 近似重跑，先核对:
    - late window 是否还在持续命中目标 pool
  - 不要把“late loss=0”直接误判成“实现无效”
### 91. 一旦让 `challenge_proxy_core` profile 约束持续进入 late phase，它可能会直接把 final special 翻坏，并同步削弱控制保留
- 现象:
  - `D16` 在 `step60-100` 保留 `priority_ratio = 0.125` 的 late proxy tail
  - `D16 final = 2.727232 / 0.157422 / 2.781072 / 0.533725`
  - 对比:
    - `D15 final = 2.730729 / -0.003582 / 3.489731 / 0.599471`
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
- 风险:
  - 如果只因为某条 supervision 在 proxy pool 上“更接近 special”，就把它继续拖进 late phase，
  - 很容易把 final 推向:
    - special 翻正
    - `e_evt / z_art` 同步回落
  - 也就是:
    - challenge 邻域目标形状开始抢占主线
- 处理要求:
  - 当前 `challenge_proxy_profile_aux` family 暂不继续优先扩展
  - 不要继续做更多:
    - pure late proxy tail sweep
    - pure weight sweep
  - 后续若继续改监督，应优先转向:
    - 更强的结构监督定义变化
    - 或 challenge proxy 与结构轴更明确的 phase 分离
### 92. 对 `structural_clause_ge4` 的 late-only sample-level profile 约束，如果训练日志里明确持续生效、但整条 late-window 仍近似复刻基线，就应把它判定为“目标形状无杠杆”，而不是继续做小 sweep
- 现象:
  - `D17 step70 / 80 / 90 / 100` 的 `loss_structural_clause_profile_aux` 都是非零
  - 且 effective `weight` 已按计划在 late phase 拉起
  - 但:
    - `D17 final = 2.730107 / -0.003152 / 3.491084 / 0.599597`
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `step80 / 90` 也近似数值级重合
- 风险:
  - 如果只因为“新 aux 已经 active”就继续扫:
    - weight
    - start_step
    - end_step
  - 很容易在一条已经被证明确实没有新杠杆的 family 上空转
- 处理要求:
  - 对这类 pool-gated target-shape，如果:
    - late exposure 已确认
    - 轨迹仍近似复刻强基线
  - 就应正式收口该 family
  - 后续结构监督应改去:
    - boundary-local
    - frame-local
    - 或更高分辨率的结构目标
### 93. 不要手工假定 `init-experiment` 生成的实验编号；若训练与 experiment record 编号错位，评估链会直接断开
- 现象:
  - 本轮 `init-experiment` 自动生成的是 `EXP-...033-d17`
  - 但训练命令手工使用了 `EXP-...043-d17`
  - 结果:
    - 训练正常完成
    - `reports/experiments/EXP-...043.metrics.json` 不存在
    - `special_eval / ablation / checkpoint_series / special_eval_series` 初次执行全部因为找不到 metrics 文件而失败
- 风险:
  - 如果训练与 experiment metrics 文件的 experiment id 不一致，
  - 后续所有依赖:
    - checkpoint 解析
    - metrics 回写
    - series 评估
    的命令都会断掉
- 处理要求:
  - 不要手工猜下一个实验编号
  - `init-experiment` 后必须先读取真实生成的 experiment id
  - 再把该 id 传给训练与评估命令
### 94. 对 pool-gated 的 boundary-local structural aux，如果 `D18` 只给出近似重跑，而 `D19` 在强制 late exposure 后反而推坏 final，就应把整个 family 收口，而不是继续怀疑“只是 exposure 还不够”
- 现象:
  - `D18`:
    - `step90 loss_structural_clause_transition_aux = 0.126826`
    - 说明新 aux 在 late phase 确实命中过 `structural_clause_ge4` batch
    - 但 `D18 final = 2.729923 / -0.002973 / 3.490768 / 0.599433`
    - 与 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961` 近乎重合
  - `D19`:
    - `step61-100` 新增 `priority_pool_memberships = ["structural_clause_ge4"]`
    - `phase_priority_record_counts` 末段达到 `185`
    - 训练时长从 `17.357207s` 提高到 `44.900339s`
    - 但 `D19 final = 2.84661 / 0.219234 / 2.363735 / 0.441742`
- 风险:
  - 如果看到 `D18` 只是近似重跑，就继续默认:
    - 只是命中太少
    - 只要再多补一点 late structural tail 就会自然长成新 regime
  - 很容易把实验资源继续消耗在:
    - 同一家族的 weight sweep
    - tail sweep
    - start/end step sweep
  - 而 `D19` 已经证明:
    - 即使强制增加 late structural exposure
    - 这条 family 也可能直接把 final 推向更差的 validation / special / control 平衡
- 处理要求:
  - 对这类 pool-gated boundary-local supervision，若:
    - `D18` 说明机制可命中
    - `D19` 说明强制曝光后仍无新解甚至更差
  - 就应正式收口整个 family
  - 后续若继续改 supervision，应优先转向:
    - 更高层级的 supervision-definition 跳变
    - 或不同的 phase / training decomposition
  - 不要继续把“exposure 可能还不够”当作默认解释
### 95. 即使把 `structural_clause_ge4` 拆成 `no_final_terminal` 子池，若 `D20` 的 final 与 late-window 仍整体弱于 `D7`，也不要继续把“再细拆 clause-rich bucket”当成高优先级路线
- 现象:
  - sidecar 已新增:
    - `structural_clause_ge4_no_final_terminal`
    - 记录数 `46`，其中 `target_train = 38`, `target_validation = 8`
  - `D20` 只把 `D7` 的 phase1 secondary 从 `structural_clause_ge4` 换成该新 pool
  - 但结果:
    - `D20 final = 2.792781 / 0.277193 / 2.448193 / 0.430398`
    - `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`
  - `D20 step90 = 3.508358 / -0.298419 / 2.730087 / 0.551189`
    也没有整体打赢 `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- 风险:
  - 如果看到“整包 `clause_ge4` 太脏”，就继续自然外推成:
    - 只要再切得更细一点
    - 或再做几轮子池 ratio / handoff 微调
    就能长成新主线
  - 很容易把实验预算继续消耗在:
    - clause-rich family 内的更细 bucket sweep
    - 而不是去验证更不同的 supervision 维度
- 处理要求:
  - 若一个更干净、可解释、且样本量足够的 `clause_ge4` 子池已经被验证仍打不赢 `D7`
  - 就应降低整个 clause-rich bucket-splitting 路线的优先级
  - 后续优先转向:
    - 更不同的 supervision-definition 维度
    - 或不同的 phase / training decomposition
  - 不要再把“可能只是 bucket 还不够细”当作默认解释
### 96. 对 teacher-consistency consolidation，如果 `D21 / D22` 都已证明机制在 target pool 上持续生效，但 formal special 仍保不住，默认解释应先转向“teacher gate 太窄”，而不是继续做窄 gate 的纯 weight sweep
- 现象:
  - `D21 = D10 init + D10 teacher`
    - `step30 loss_teacher_consistency = 0.28094`
    - `final = 2.441712 / 0.181901 / 2.919652 / 0.391864`
  - `D22 = D7 init + D10 teacher`
    - `step30 loss_teacher_consistency = 0.385431`
    - `final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
  - 也就是说:
    - teacher pull 持续存在
    - validation 很强
    - `e_evt` 也能保持较高
    - 但 formal special 仍翻正，`z_art` 仍不足
- 风险:
  - 如果看到 teacher consistency 已经 active，就继续默认:
    - 只要把 weight 再抬一点
    - 或 learning rate 再抠一点
    就能自然把 special 拉回负值
  - 很容易把实验资源继续耗在:
    - 同一窄 gate 上的纯强度微调
  - 而忽略了更关键的结构事实:
    - 当前 formal special slice 可能并不被 `challenge_proxy_core` 单独覆盖住
- 处理要求:
  - 若 teacher consistency 已确认持续 active，
  - 但 `D21 / D22` 仍表现为:
    - validation 明显改善
    - special 仍保不住
  - 就应优先改:
    - teacher gate 覆盖范围
  - 而不是继续优先做当前窄 gate 的纯 weight sweep
  - 下一轮优先考虑:
    - `challenge_proxy_core + challenge_proxy_relaxed`
    - 或 `challenge_proxy_core + short_pause_no_terminal`
### 97. 若 `D23` 已证明把 teacher gate 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + challenge_proxy_relaxed` 仍近似复刻 `D22`，就不要再把“更宽的 relaxed challenge coverage”当成高优先级方向
- 现象:
  - `D23`:
    - `teacher_consistency.pool_memberships = ["challenge_proxy_core", "challenge_proxy_relaxed"]`
    - `step30 loss_teacher_consistency = 0.387194`
    - `final = 2.442024 / 0.142199 / 3.289808 / 0.43533`
  - `D22`:
    - `final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
  - 也就是说:
    - broadened gate 持续 active
    - validation 只略好
    - special / `e_evt` / `z_art` 都没有形成新优势
- 风险:
  - 如果看到 `D21 / D22` 后默认以为“只要 teacher gate 再宽一点就行”，
  - 很容易继续自然外推成:
    - 再加更多 relaxed pool
    - 再做更多 coverage sweep
    - 再做轻微 weight 微调
    就能把 special 自动拉回负值
  - 这会把实验预算继续消耗在:
    - 低信息增益的 challenge-relaxed family
- 处理要求:
  - 若一个直接、可解释、且样本量更大的 relaxed gate 扩展已经被验证只会近似复刻 `D22`
  - 就应降低“更宽 challenge coverage”这条路线的优先级
  - 后续若继续 teacher-consistency family，应优先改去:
    - 更有结构差异的 teacher gate
    - 例如 `challenge_proxy_core + short_pause_no_terminal`
    - 或更不同的蒸馏目标形状
  - 不要再把“coverage 可能还不够宽”当作默认解释
### 98. 对 teacher-gate 实验，如果新增 pool 与现有 core 高度重叠，必须先区分“pool 名称变了”和“新增样本真的进训练了”这两件事
- 现象:
  - `short_pause_no_terminal = 19`
  - 与 `challenge_proxy_core` 重叠 `15`
  - 真正新增样本只有 `4`
  - `D24`:
    - teacher gate 已扩到 `["challenge_proxy_core", "short_pause_no_terminal"]`
    - 但 `4` 条 `short_pause_only` 样本在 30-step target batch 中一次都没出现
    - `D24 final` 也与 `D22 final` 数值级完全一致
- 风险:
  - 如果看到 pool 名称已经扩了，就默认以为“新 family 已被测试到”，
  - 很容易把一个实际上没有新增覆盖的实验误判成:
    - teacher gate 本身无效
    - 或 short-pause 方向本身无效
- 处理要求:
  - 对高重叠 pool，必须同时核对:
    - overlap 大小
    - truly new record 数量
    - 新 record 是否真的出现在 batch 中
  - 否则不能把结果当成对新 gate 的有效判决
### 99. 对 priority-pool 扩展实验，即使新增样本一条都没被采到，也可能通过 overlap-driven reordering 改变训练轨迹；不能只用“新增样本是否出现”来解释全部差异
- 现象:
  - `D25` 把 priority pool 从 `challenge_proxy_core` 扩到 `challenge_proxy_core + short_pause_no_terminal`
  - 但 `short_pause_only` 的 `4` 条样本在 30-step target batch 中仍一次都没出现
  - 与此同时，`D25` 的轨迹已经明显不同于 `D22 / D24`:
    - `D25 step20 = 2.523898 / 0.117894 / 3.27265 / 0.460259`
    - 对应形成了更偏 special / `z_art` 的新 tradeoff
- 风险:
  - 如果只检查“新增样本有没有进 batch”，就把 `D25` 直接归类成空跑，
  - 会漏掉一个更微妙但重要的机制:
    - priority pool 的组成变化会改变 overlap 样本的抽样顺序与组合
    - 即使没有采到 truly new records，也可能改变整体轨迹
- 处理要求:
  - 对 sampler 相关 follow-up，不只要核对:
    - new-only records 是否出现
  - 还要核对:
    - 轨迹是否已偏离旧基线
    - step-level tradeoff 是否出现新 family 点
  - 如果轨迹已变，就应把它当成有效实验结果，而不是简单记为“没采到新增样本所以无效”
### 100. 对 record-id forcing 实验，必须先用 formal split 去过滤候选；否则会把 validation record 写进 training config，却永远不可能在训练批次中出现
- 现象:
  - `short_pause_only` 候选原始上看有 `4` 条
  - 但 formal `hybrid_stratified_blocked` split 下:
    - `target::chapter3_2_firefly_212` 实际位于 `target_validation`
    - 真正可训练的 short-only 样本只有 `3` 条
  - 如果不先按 split 过滤，就会把一个永远不会出现在训练中的 record id 写进 `priority_record_ids`
- 风险:
  - 这会让后续核对变得含混:
    - 看起来像“有一条怎么都采不到”
    - 实际上它根本不在训练候选集里
- 处理要求:
  - 对所有 record-id 级别的 sampler 控制，
  - 必须先按 formal split 过滤到 `target_train`
  - 再写入 config
### 101. `D27` 已证明一旦 train-side short-only 样本被显式注入 priority slot，轨迹会明显推坏；不要再把“只要更强地喂 short_pause_only 就会更像 special”当成默认解释
- 现象:
  - `D27` 正式训练 step1/2/3 已分别命中:
    - `target::chapter3_2_firefly_191`
    - `target::chapter3_3_firefly_148`
    - `target::chapter3_3_firefly_125`
  - 说明 train-side short-only 样本已经真正进入训练
  - 但 `D27 final = 2.466208 / 0.206141 / 2.863938 / 0.356843`
  - 相对 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`
    - validation 略好
    - special / `e_evt` / `z_art` 全都更差
- 风险:
  - 如果把 `D24 / D25 / D26` 的结论继续自然外推成:
    - 只要更强地把 short_pause_only 塞进训练
    - 就能自然把模型往更好的 challenge 方向推
  - 很容易继续消耗实验预算在:
    - 更高 priority ratio
    - 更长 short-only consolidation
    - 更密的 short-only record-id sweep
- 处理要求:
  - 一旦 `D27` 这种“显式命中 train-side short-only”的实验已经给出负证据，
  - 就应降低整个 short-pause-only forcing family 的优先级
  - 后续 teacher-consistency family 应转去:
    - cross-anchor consolidation
    - 或更不同的 distillation target shape
### 102. 如果 `D30 event-only` 与 `D29` 近乎重合，就不要再把“teacher z_art 蒸馏项是 cross-anchor tradeoff 的主要元凶”当成默认解释
- 现象:
  - `D29 final = 2.397175 / 0.171769 / 2.978481 / 0.364927`
  - `D30 final = 2.399277 / 0.169748 / 2.982002 / 0.377184`
  - 两者几乎数值级重合
  - 同时 `D30` 已显式设置:
    - `teacher_consistency.z_art_weight = 0.0`
- 风险:
  - 如果看到 `D29` 的 control 仍有代价，就继续默认:
    - 只要把 teacher z_art 项拿掉
    - 就会自然把 `z_art` 保回来
  - 很容易把实验预算继续耗在:
    - event-only / z_art-only 的更多小拆分
- 处理要求:
  - 一旦 `D30` 已经证明 event-only 与 full teacher 基本同形，
  - 就应降低“继续拆 teacher loss 分量”的优先级
  - 后续更值得改的是:
    - distillation target shape
    - 或 anchor-level gate / selection
### 103. 当 teacher-consistency family 已经形成三锚且各自分食 `validation / special / e_evt / z_art` 领导位时，不要继续沿用早期的旧标签；必须重做 final-anchor selection
- 现象:
  - 三锚正式分析已表明:
    - `D29` 是 validation leader
    - `D26` 是 special / `z_art` leader
    - `D22` 是 `e_evt` leader
  - 同时:
    - `D22` 还是当前三锚里的 minimax anchor
  - 这已经与更早阶段把 `D22` 记作 validation-oriented 的口径不一致
- 风险:
  - 如果继续沿用旧标签，
  - 后续 route 设计、报告口径、甚至新实验目标都会被带偏:
    - 把 `D22` 当成 validation reference
    - 把 `D29` 误当成只是“middle anchor”
    - 高估单个小 tweak 同时并起 `D22` 和 `D26` control floor 的可能性
- 处理要求:
  - 一旦形成这种三锚分化结构，
  - 必须先做正式 anchor-selection 分析，
  - 然后更新 anchor 职责:
    - `D29 = validation anchor`
    - `D26 = special / z_art anchor`
    - `D22 = minimax default anchor`
  - 后续训练与评估都应基于这个更新后的结构，而不是继续继承旧阶段命名
### 104. 当三锚 route policy 已经被正式固化后，不要再在报告里只写“当前参考 anchor 是谁”；必须同时写出 route 前提
- 现象:
  - 三锚已经可以正式按 route 切换:
    - `validation_strict -> D29`
    - `default_minimax -> D22`
    - `special_push -> D26`
  - 切换条件也已经明确:
    - `0.047019`
    - `0.126723`
- 风险:
  - 如果后续报告继续只写:
    - “当前参考点是 D22”
    - 或“本轮更像 D26”
  - 却不写 route 前提，
  - 会把“预算约束”和“目标偏好”混在一起，导致:
    - 同一锚点在不同语境下被误读成默认方案
    - 也会让后续新实验看起来像在打错目标
- 处理要求:
  - 三锚阶段之后，所有评估/汇总都应先声明:
    - 当前 route 是什么
  - 然后再声明:
    - 该 route 下选中的 anchor 是什么
  - 不再接受脱离 route 前提的单独 anchor 描述
### 105. 当 route selector 已经存在时，不要再手工凭印象写 reference anchor；应先跑 selector，再记录 route 字段
- 现象:
  - 当前已经有正式命令:
    - `select-offline-mvp-anchor-route`
  - 且 experiment record 模板也已新增:
    - `route_policy`
    - `route_budget_or_floor`
    - `anchor_reference`
- 风险:
  - 如果后续仍手工写:
    - “这轮参考 D22”
    - “这轮更像 special_push”
  - 却不经过 selector，
  - 很容易把:
    - 实际 budget
    - special / z_art priority
    - e_evt / z_art floor 要求
  - 写错或漏掉
- 处理要求:
  - 三锚阶段之后，凡是新一轮实验立项、汇总或正式记录，
  - 默认先跑 selector
  - 再把 selector 输入与输出写入 experiment record
### 106. 当 `init-experiment` 已支持 `--route-selection` 后，不要再手工把 selector 结果复制进 experiment record
- 现象:
  - 当前 `init-experiment` 已可直接消费 selector json
  - 并自动填充:
    - `route_policy`
    - `route_budget_or_floor`
    - `anchor_reference`
- 风险:
  - 如果后续仍手工复制，
  - 很容易出现:
    - selector 输出已更新，但 experiment record 沿用旧 route
    - budget/floor 漏抄
    - anchor reference 与实际 selector 结果不一致
- 处理要求:
  - 新实验立项时，默认使用:
    - `select-offline-mvp-anchor-route`
    - `init-experiment --route-selection ...`
  - 不再优先接受手工抄写 route 字段的立项流程
### 107. 当 final comparison 已支持 `--route-selection` 后，不要再输出脱离 route anchor 的裸对比表
- 现象:
  - 当前已经有正式命令:
    - `compare-offline-mvp-final-experiments`
  - 且它已支持:
    - `--route-selection`
    - `delta_vs_route_anchor`
- 风险:
  - 如果后续 comparison 仍只按 validation 或 special 单列排序，
  - 却不说明当前 route anchor，
  - 很容易把:
    - `D29` 的 validation 优势
    - `D26` 的 special / `z_art` 优势
  - 从当前 route 前提里剥离出来误读
- 处理要求:
  - 三锚阶段之后，凡是 final comparison，
  - 默认优先带上 `--route-selection`
  - 并直接使用 `delta_vs_route_anchor` 来解释 gain / cost
### 108. 当 route recap 已可自动生成 summary/tradeoff 句子后，不要再在阶段汇总里手工重写同一套三锚取舍说明
- 现象:
  - 当前已经有正式命令:
    - `recap-offline-mvp-route-context`
  - 且它已能直接给出:
    - `summary_line`
    - `tradeoff_line`
- 风险:
  - 如果后续阶段汇总继续手工重写，
  - 很容易出现:
    - 当前 route 已变，但 summary 句子沿用旧锚点
    - validation alternative / special alternative 写反
    - 数值与最新 route anchor 不一致
- 处理要求:
  - 三锚阶段之后，凡是实验复盘或阶段总结，
  - 默认优先使用 route recap 产物
  - 手工补充只应用在更高层结论，不再重复底层 tradeoff 句子
### 109. 当 route-aware handoff 已存在时，不要再手工从 selector/comparison/recap 三处拼交接段落
- 现象:
  - 当前已经有正式命令:
    - `build-offline-mvp-route-handoff`
  - 且它已能直接输出:
    - `copy_ready_handoff`
    - alternatives
    - artifact bundle
- 风险:
  - 如果后续交接继续手工拼，
  - 很容易出现:
    - 当前 route 已更新，但 handoff 仍沿用旧 anchor
    - comparison delta 与 recap 用词不一致
    - 接班入口文件漏掉关键 artifact
- 处理要求:
  - 三锚阶段之后，凡是正式接班或阶段交接，
  - 默认优先使用 route-aware handoff 产物
  - 不再手工跨多个产物拼一段新的交接摘要
### 110. 当固定格式 handoff 文档流程已存在时，不要把 `route_handoff.md` 直接当最终交接成品
- 现象:
  - 当前已经新增正式命令:
    - `materialize-offline-mvp-route-handoff-doc`
  - 它会把 `route_handoff.json` 进一步物化为固定格式的正式交接文档。
- 风险:
  - 如果后续仍直接把原始 `route_handoff.md` 当最终交接件，
  - 很容易出现:
    - 交接入口缺少固定 metadata
    - source artifact 路径书写不一致
    - 不同批次 handoff 文档结构漂移
- 处理要求:
  - 三锚阶段之后，凡是要落正式交接文档，
  - 默认使用:
    - `build-offline-mvp-route-handoff`
    - `materialize-offline-mvp-route-handoff-doc`
  - `route_handoff.md` 保留为中间摘要产物，不再默认充当最终交接成品
### 111. 当固定格式 stage report 已存在时，不要再手工从 handoff document 里摘一段状态摘要
- 现象:
  - 当前已经新增正式命令:
    - `materialize-offline-mvp-stage-report`
  - 它会把 `handoff_document.json` 进一步物化为固定格式的阶段状态报告。
- 风险:
  - 如果后续阶段总结继续人工摘写，
  - 很容易出现:
    - executive status 与当前 route 不一致
    - primary tradeoff 引用了旧 anchor 或旧 delta
    - 手工周报与正式交接件口径分裂
- 处理要求:
  - 三锚阶段之后，凡是要落阶段汇总或固定状态报告，
  - 默认使用:
    - `materialize-offline-mvp-route-handoff-doc`
    - `materialize-offline-mvp-stage-report`
  - 不再优先接受手工从 handoff document 里二次摘写状态摘要的流程
### 112. 对 teacher-consistency family 来说，在同一条 `challenge_proxy_core` gate 上追加温和 acoustic consistency，不会自动形成新的 minimax 杠杆
- 现象:
  - `D31` 在 `D22` 骨架上把 distillation target shape 从 `event + z_art` 扩到 `event + z_art + acoustic`
  - 且 `loss_teacher_acoustic_consistency` 在训练全过程里持续非零
- 风险:
  - 如果看到“新 target shape 已接通”就默认它一定会显著推开 `D22`，
  - 后续很容易继续沉迷于:
    - 同一条 core gate 上的 `acoustic_weight` 微调
    - 近似同构的轻量 acoustic 加项 sweep
- 处理要求:
  - 当前把 `D31` 解释为:
    - 一个有效但低信息增益的 target-shape probe
    - 不是新的 anchor 候选
  - 若继续推进 distillation target-shape 路线，
  - 优先改“结构差异”本身，
  - 不再优先继续做同 gate 下的小幅 acoustic 权重微调
### 113. 即使 fused-hidden target shape 已把 `zero_e_evt` 推到当前 leader，只要它没补回 formal special gap，就不要急着把它升成新的 minimax anchor
- 现象:
  - `D32 final = 2.442393 / 0.143828 / 3.299576 / 0.434057`
  - 相对当前 route anchor `D22 = 2.444194 / 0.140001 / 3.299035 / 0.438936`
    - validation `-0.001801`
    - special `+0.003827`
    - `e_evt +0.000541`
    - `z_art -0.004879`
  - 同时 `D32` 已是当前 comparison 的 `zero_e_evt` leader
- 风险:
  - 如果看到“validation 更好且 `e_evt` 也更高”，
  - 就默认 fused-hidden 已经自然打赢 `D22`，
  - 很容易忽略:
    - 当前 minimax route 仍然把 formal special gap 视为硬代价
    - `D32` 的收益主要集中在 control-side
    - 不是四个指标同时往前推
- 处理要求:
  - 当前把 `D32` 解释为:
    - 一个比 `D31` 更有信息增益的 control-side reference
    - 但不是新的 minimax anchor
  - 若继续推进 fused-hidden 路线，
  - 优先改 gate / sampler 结构，
  - 例如和 `D26` 的 short-pause family 组合，
  - 不再优先继续做同一条 core gate 下的 fused_hidden 权重小 sweep
### 114. 一旦 `D33` 已正式替换 `D26` 成为新的 special/control anchor，就不要继续沿用旧 trio 的 selector、handoff 或 special budget 阈值
- 现象:
  - `D33 final = 2.52818 / 0.111677 / 3.312339 / 0.465828`
  - 相对 `D26 final = 2.523898 / 0.117894 / 3.27265 / 0.460259`
    - validation 只差 `+0.004282`
    - 但 special / `e_evt` / `z_art` 全部更强
  - 新 trio 已重算为:
    - `D29 = validation`
    - `D22 = default_minimax`
    - `D33 = special / e_evt / z_art`
  - 对应新的 special route budget 也已变成:
    - `0.131005`
- 风险:
  - 如果后续还继续引用旧的 `D22 / D26 / D29` selector 或 handoff 资产，
  - 很容易出现:
    - special-first 仍错误指向 `D26`
    - route budget 阈值沿用旧的 `0.126723`
    - 交接文档里把已过时的 special anchor 当成当前推荐方案
- 处理要求:
  - 从 `D33` 之后，凡是正式 route / handoff / stage report，
  - 默认改用 `D22 / D29 / D33` 新 trio 产物
  - `D26` 只保留为历史 reference，
  - 不再作为当前 special anchor 引用
### 115. 不要把 `D33 step10` 这种更极端的 special-only checkpoint，直接误记成新的 formal final anchor
- 现象:
  - `D33 step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
  - `D33 step20 = 2.52818 / 0.111677 / 3.312339 / 0.465828`
- 风险:
  - 如果只盯着 `step10` 的 special 数值更低，
  - 很容易误以为 final 应自动回退到更早 checkpoint，
  - 从而忽略:
    - `step20` 才是当前 special 与 dual-control 更平衡的 joint point
    - `step10` 更像 special-only 极端点，不是当前 formal special/control anchor
- 处理要求:
  - 当前把 `D33 step10` 解释为:
    - 一个值得记录的更激进 special checkpoint
    - 不是默认 final anchor
  - 除非后续明确切换到“special-only checkpoint 选择”目标，
  - 否则仍以 `D33 final / step20` 作为正式 special/control anchor
### 116. 即使 special-side anchor 已从 `D26` 升级到 `D33`，也不要默认“新两端 final anchor 互蒸”就会自然造出新的 joint winner
- 现象:
  - `D34 = D22 init + D33 teacher`
    - `2.3506 / 0.201536 / 2.633041 / 0.310002`
  - `D35 = D33 init + D22 teacher`
    - `2.395609 / 0.173543 / 2.967455 / 0.361794`
  - 两条线都没有打赢当前 trio:
    - `D34` 退化成更极端的 validation compressor
    - `D35` 近乎回到 `D29` 式中间锚点
- 风险:
  - 如果看到 `D33` 已经比 `D26` 更强，
  - 就默认“拿 `D22` 和 `D33` final 互蒸一下”会自然补出 minimax 中间点，
  - 很容易继续把预算耗在:
    - 同构 final-to-final cross-anchor 变体
    - 只是交换 init / teacher 方向的重复实验
- 处理要求:
  - 当前把 `D34 / D35` 解释为:
    - 对新 trio 的必要复核
    - 但不是新的 family breakout
  - 若继续推进 `D22 <-> D33` 路线，
  - 优先转向 checkpoint-level cross-anchor，
  - 尤其是显式利用 `D33 step10` 这类 special-only checkpoint，
  - 不再优先继续做 final-anchor 对 final-anchor 的同构互蒸
### 117. 即使把 `D33 step10` 这种 special-only checkpoint 拿来做 init 或 teacher，也不要默认它会自然成为新的 cross-anchor 入口
- 现象:
  - `D36 = D33 step10 init + D22 teacher`
    - `2.450632 / 0.144661 / 3.221708 / 0.407633`
  - `D37 = D22 init + D33 step10 teacher`
    - `2.35571 / 0.199699 / 2.652109 / 0.321586`
  - 两条线都没有形成新的 joint winner:
    - `D36` 只是比 `D22` 更差的近邻复制品
    - `D37` 再次退化成 validation compressor
- 风险:
  - 如果看到 `D33 step10` 的 special 更极端，
  - 就默认“只要把 step10 拿来互蒸”就能打开新的中间点，
  - 很容易继续把预算耗在:
    - step10 init / final teacher
    - final init / step10 teacher
    - 只是在 checkpoint 入口上来回交换方向的重复实验
- 处理要求:
  - 当前把 `D36 / D37` 解释为:
    - 对 checkpoint-level cross-anchor 假设的必要封口
    - 不是新的 family breakout
  - 若继续推进，
  - 优先转向更结构化的 checkpoint selection / routing，
  - 或更强的 target / gate 级重构，
  - 不再优先继续做 `step10` 与 final 之间的同构互蒸
### 118. 在推理音频导出链路尚未存在之前，不要把数据 leader 误当成已经通过人工听感审核的当前最优解
- 现象:
  - 当前 `src/v5vc/offline_mvp/model.py` 只输出 `acoustic` 等中间特征
  - 当前 `src/v5vc/cli.py` 没有 inference / synthesis / export-audio 命令
  - 全部训练配置仍显式写着 `vocoder_required = false`
- 风险:
  - 如果看到某个实验在 validation / special / `e_evt` / `z_art` 上领先，
  - 就直接把它升成“当前最优解”，
  - 很容易在完全没有人耳试听的情况下，把:
    - 数据侧最优候选
    - 听感侧最终最优
    混成同一个结论
- 处理要求:
  - 只要系统还没有推理音频导出链路，
  - 当前所有 leader 都只能解释为:
    - 数据侧最优候选
    - 不是完成了人工审核的最终最优
  - 一旦后续接入推理音频导出，
  - 每次出现数据突破/进化，
  - 必须追加用户人耳试听；
  - 在用户确认前，
  - 禁止把该分支直接升为当前最优解
### 119. 即使当前已能导出 `proxy audio`，也不要把它误当成完整 vocoder 试听结论
- 现象:
  - 当前新增的 `export-offline-mvp-proxy-audio`
  - 只是基于预测 `acoustic` 特征重建代理波形
  - 当前首轮试听包为:
    - `D22`
    - `D29`
    - `D33`
    各 `3` 段输入
- 风险:
  - 如果看到 `reports/audio/` 已经有 wav，
  - 就默认系统已经具备完整 runtime 音频导出能力，
  - 很容易把:
    - proxy audio 的相对审核价值
    - 最终 vocoder 级听感结论
    混为一谈
- 处理要求:
  - 当前把 proxy audio 明确解释为:
    - 人耳审核的最小代理音频
    - 不是最终 runtime-quality waveform
  - 用户试听结论仍然有效，
  - 但后续若要做正式音质判断，
  - 还需要继续补真正的 synthesis / vocoder 链路
### 120. 不要把 `zero_cross` 直接映射成可听主频，否则 `proxy audio` 会退化成高频啸叫，导致人工审核失效
- 现象:
  - 首版 `proxy audio` 在用户试听中几乎全部表现为高频啸叫
  - 几乎无法稳定比较 `D22 / D29 / D33` 的结构差异
  - 用户唯一还能听出的粗差异只剩:
    - 基准频率大致 `D22 < D29 < D33`
    - `D33` 略有不稳定感
- 风险:
  - 如果把 `zero_cross` 这类亮度 / 粗糙度指标直接当成 audible pitch，
  - 会让代理音频的可听内容被“高频尖叫”主导，
  - 从而把:
    - 节奏
    - 停顿
    - 句边界
    - 稳定性
    这些本来想审核的维度淹没掉
- 处理要求:
  - `proxy audio` 必须优先服务于相对结构审核，
  - 不是优先去“还原一个看似更亮的音色”
  - 当前重建器应把:
    - `zero_cross` 用作 brightness / noise mix 的弱控制
    - 不再直接决定可听主频
  - 若用户再次反馈“仍然主要只听到啸叫”，
  - 则该轮 bundle 直接记为无效，
  - 不得强行据此做分支判优
### 121. 即使已经把首版啸叫压低，如果不同分支仍主要靠“音调高低”区分，也不要把这种 proxy 差异误判成结构优势
- 现象:
  - 第二版 `proxy audio` 已经能让用户听到:
    - 停顿
    - 音量结构
    - 与原音频的粗对应关系
  - 但用户仍反馈:
    - `D22` 与 `D29` 差异细微到几乎无法区分
    - `D33` 的更高频率 / 更高音调仍是最显著差异
- 风险:
  - 如果在这种情况下把“谁更高音”直接解释成“谁更强”，
  - 就会把代理重建器残留的 pitch artifact，
  - 误当成:
    - 更好的边界控制
    - 更好的节奏结构
    - 或更强的 special 能力
- 处理要求:
  - 当前 proxy 音频必须进一步去音调化
  - audible pitch 应尽量在分支间统一
  - 用户试听时应继续忽略:
    - 基频更高
    - 听起来更尖
    - 更像带调制合成器
  - 若去音调化后 `D22 / D29` 仍然无法稳定区分，
  - 就应接受“当前 proxy 路线只够做粗结构校验，不够做细粒度 branch ranking”这个结论
### 122. 即使去音调化后的 `proxy audio` 已经能分出 `D33` 更不稳，也不要把这种不稳直接解释成“更真实”或“更差”
- 现象:
  - 第三轮用户试听反馈:
    - `D22 / D29` 几乎不可区分
    - `D29` 相对 `D22` 可能只是略柔和
    - `D33` 明显更不稳定
  - 但用户同时明确指出:
    - 当前代理音频与原音频结构相差仍较大
    - 因而无法确认 `D33` 的不稳是否更贴近原音频真实情况
- 风险:
  - 如果把 `D33` 的“不稳定”直接判成负面，
  - 可能错杀一个更贴近真实结构变化的分支
  - 反过来如果把它直接判成“更真实”，
  - 也可能只是把代理重建器失真误当成优势
- 处理要求:
  - 当前只保留最保守的听感口径:
    - `D22 / D29` 基本打平
    - `D33` 在 proxy 下更不稳
  - 不把这条结论继续翻译成:
    - 最终优劣
    - 更真实
    - 更差
  - 若后续要判断“是否更接近原音频真实结构”，
  - 必须继续补更接近 runtime 的 synthesis / vocoder 链路
### 123. 即使 phase-handoff routing 已能精确复刻 `D33 step10`，也不要默认“把它再 handoff 回 core”或“把 teacher 关掉”就能自然形成新的 minimax
- 现象:
  - `D38 step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
    - 与 `D33 step10` 完全一致
  - 但:
    - `D38 final = 2.494434 / 0.161978 / 3.096622 / 0.436892`
    - `D40 final = 2.492335 / 0.160804 / 3.102396 / 0.431034`
  - 同时:
    - `D39 final = 2.489906 / 0.169107 / 3.048095 / 0.407912`
- 风险:
  - 如果看到 phase routing 已经能把轨迹精确带到 `D33 step10`，
  - 就默认只要:
    - 后半段 handoff 回 `core`
    - 或把 teacher 在 checkpoint 之后关掉
    - 就能自然把 special-only checkpoint 收敛成新的 final joint winner
  - 很容易继续把预算耗在:
    - 各种 handoff 时点微调
    - sampler handoff 与 teacher-off 的排列组合
    - 但最终只会重放已知中间点
- 处理要求:
  - 当前把 `D38 / D39 / D40` 解释为:
    - phase-handoff routing 假设的必要封口
    - 不是新的 breakout family
  - 若继续推进，
  - 优先转向:
    - 更强的 target / gate 级重构
    - 或更明确的 phase-specific teacher 机制
  - 不再优先继续做同 family 的 sampler-handoff / teacher-off 小变体
### 124. 即使 `docs/97` 已经落盘，如果固定 handoff / stage-report 仍停在旧实验集合，也不要默认接班入口已经自动更新到最新阶段
- 现象:
  - `docs/97_round1_1_d38_d39_d40_phase_handoff_routing_report.md` 已经完整记录了 `D38 / D39 / D40`
  - 但旧版固定交接件仍只覆盖:
    - `D22`
    - `D29`
    - `D33`
  - 若不重新物化:
    - `route_handoff`
    - `handoff_document`
    - `stage_report`
    接班时仍会优先看到旧版三锚入口
- 风险:
  - 如果看到固定 handoff / stage-report 还存在，
  - 就默认它们已经代表“当前最新阶段”，
  - 很容易让后来接手的人漏掉:
    - `D38 / D39 / D40` 已经做过
    - phase-handoff routing 已正式封口
  - 进而重复做:
    - 旧 family 的 handoff 小变体
    - 或重复查阅多份原始 comparison 才能拼出最新状态
- 处理要求:
  - 每当新增一轮会改变“当前阶段已覆盖实验集合”的结果后，
  - 不只更新专题报告，
  - 还要同步刷新:
    - 固定 `route_handoff`
    - 固定 `handoff_document`
    - 固定 `stage_report`
  - 接班时优先检查固定交接件里的 `experiment_metrics_path` 列表，
  - 确认它是否已经覆盖最新一轮实验
### 125. 即使 `teacher_consistency` 已经支持 phase-specific gate / target-shape 切换，也不要默认“同一条 D10 teacher family”就足以把 `D33 step10` 固化成新的 final winner
- 现象:
  - `D41 step10 = 2.621019 / 0.081505 / 3.224344 / 0.46347`
    - 仍与 `D33 step10` 完全一致
  - `step11` 日志也已明确显示:
    - `pool_memberships` 从 `challenge_proxy_core + short_pause_no_terminal`
      切到 `challenge_proxy_core`
    - `fused_hidden_weight` 从 `0.05`
      切到 `0.0`
  - 但 `D41 final = 2.493233 / 0.163597 / 3.088342 / 0.435649`
    - 仍落在和 `D38 / D40` 同型的中间点
- 风险:
  - 如果看到 phase-specific teacher 代码已经接上，
  - 就默认后面只要继续调:
    - gate 切换时点
    - fused-hidden 开关
    - 同一 teacher 下的权重配比
    就能自然把 `D33 step10` 固化成新的终点，
  - 很容易继续把预算耗在:
    - 同一 `D10 teacher` family 的 phase 微调
    - 但最后只是重复中间盆地附近的数值扰动
- 处理要求:
  - 当前把 `D41` 解释为:
    - 对“同一 teacher family 的 phase-specific gate-target handoff 是否足够”这件事的更强负结果
    - 不是新的 breakout family
  - 若继续走 teacher 路线，
  - 优先考虑:
    - phase-specific teacher checkpoint / teacher source
    - 或更强的 target-side supervision / gate 重构
  - 不再优先继续做同一 teacher 下的 gate / weight / fused-hidden 小排列组合
### 126. 即使 `teacher_consistency` 已经支持 phase-specific teacher checkpoint / source 切换，也不要默认“把 early teacher 换成 D33 step10、late teacher 换回 D22”就能自然长出新的 final winner
- 现象:
  - `D42` dry-run 已明确记录:
    - `teacher_checkpoint_paths = [D22 final, D33 step10]`
    - `step1-10` 与 `step11-20` 的 phase-specific teacher source 都已生效
  - 但:
    - `D42 step10 = 2.61436 / 0.085473 / 3.218836 / 0.455237`
      - 已经不是 `D33 step10`
    - `D42 final = 2.488031 / 0.15944 / 3.115116 / 0.417186`
      - 仍落在 `D38-D41` 同型的中间盆地附近
- 风险:
  - 如果看到 phase-specific teacher source 已经接入，
  - 就默认只要把:
    - 早段 teacher 改成 `D33 step10`
    - 晚段 teacher 改回 `D22`
    就能自然把轨迹收成新的 minimax，
  - 很容易继续把预算耗在:
    - handoff 时点微调
    - teacher checkpoint 排列组合
    - 但最终只是得到更靠近 `D22` 的中间点
- 处理要求:
  - 当前把 `D42` 解释为:
    - “最小 phase-specific teacher source handoff 是否足够”这件事的负结果
    - 不是新的 breakout family
  - 若继续走 teacher 路线，
  - 不再优先继续做同一结构下的最小 source 替换；
  - 应考虑更强的:
    - phase-specific teacher family / checkpoint 组合
    - 或 source 与 gate/filter 的联动设计
### 127. 即使 target-side `challenge_proxy_relaxed` 再叠一个 high-proximity 阈值，也不要默认它会低成本改写当前 special route
- 现象:
  - `D43` dry-run 已明确记录:
    - `priority_pool_memberships = ["challenge_proxy_relaxed"]`
    - `min_special_proximity_score = 0.8`
    - `priority_record_count = 24`
  - 但:
    - `D43 final = 2.46381 / 0.200946 / 2.927122 / 0.374309`
    - 相比 `D22`:
      - validation 只略差
      - `e_evt` 更强
      - 但 special 明显更差
      - `z_art` 也更弱
- 风险:
  - 如果觉得 `challenge_proxy_core` 太窄、
  - `challenge_proxy_relaxed` 太宽，
  - 就很容易把 “`relaxed + proximity>=0.8`” 想成一个低风险折中，
  - 进而默认它会同时改善:
    - validation
    - special
    - control
  - 但 `D43` 实际更像:
    - 一个 validation / `e_evt` 倾向的折中点
    - 不是新的 special or minimax winner
- 处理要求:
  - 当前把 `D43` 解释为:
    - “最小 high-proximity relaxed gate 是否足够”这件事的负结果
    - 不是新的 breakout family
  - 若继续走 target-side 路线，
  - 不再优先继续只调 proximity 阈值；
  - 应考虑更强的:
    - structure / terminal 显式 gating
    - 或独立的 special-target supervision 重构
### 128. 即使已经证明 `relaxed + proximity>=0.8` 会把 terminal 样本混进来，也不要默认“把它们筛掉”就会自然得到比 `D22` 更强的 relaxed special route
- 现象:
  - `D44` 仅在 `D43` 基础上新增:
    - `required_final_terminal_types = ["none"]`
    - `required_utterance_structure_types = ["other"]`
  - `priority_record_count` 从 `24` 变成 `19`
  - 同时 `D44 final = 2.504646 / 0.14823 / 3.100172 / 0.422595`
    - 相比 `D43`
      - special / `e_evt` / `z_art` 明显修复
    - 但相比 `D22`
      - 仍是四项全面更弱
- 风险:
  - 如果已经定位到 `D43` 的问题来自 terminal / single-clause contamination，
  - 就很容易进一步默认:
    - 只要把这些样本筛掉，
    - `relaxed` 路线就会自然长成新的更优 special gate
  - 但 `D44` 实际只说明:
    - `D43` 的退化来源找到了
    - 不代表 relaxed route 本身因此变成更强新分支
- 处理要求:
  - 当前把 `D44` 解释为:
    - 一个定位性负结果
    - 不是新的 breakout family
  - 若继续走 target-side 路线，
  - 不再优先继续做 relaxed gate 的轻量筛样排列组合；
  - 应考虑更明确的:
    - `none / nonverbal` 目标监督
    - 或独立的 target-side supervision 重构
### 129. 即使 `D33 step10 -> D29 final` 的 phase-specific teacher family handoff 能形成新 tradeoff，也不要默认它已经足以改写当前 default route
- 现象:
  - `D45` dry-run 已明确记录:
    - `teacher_checkpoint_paths = [D29 final, D33 step10]`
  - `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
    - 相比 `D22`
      - special 略好
      - 但 validation / `e_evt` / `z_art` 都更差
    - 相比 `D33`
      - validation 更好
      - 但 special / control 都更差
- 风险:
  - 如果看到 `D45` 已经第一次在 `post-D41` 路线里做出一个像样的新 compromise，
  - 就很容易过早把它解释成:
    - 新 minimax 候选
    - 或已经足够替换 `D22`
  - 但当前 route policy 仍要求:
    - 更严格的 validation 预算
    - 与更强的 control 保留
  - `D45` 仍没有满足这些门槛
- 处理要求:
  - 当前把 `D45` 解释为:
    - 一个值得继续沿线推进的新 non-dominated tradeoff
    - 不是已经定型的新 route
  - 若继续走 teacher 路线，
  - 优先沿 `D45` 继续增强:
    - phase-specific teacher family + phase-specific filter 联动
    - 或 late teacher family 的更强 gate 约束
### 130. 即使把 `D45` 的 late phase 改成更“像 special”的 relaxed none-other filter，也不要默认它会保住 `D45` 的 compromise 优势
- 现象:
  - `D46` 仅在 `D45` 基础上把 late phase teacher / sampler gate 联动切到:
    - `challenge_proxy_relaxed`
    - `required_final_terminal_types = ["none"]`
    - `required_utterance_structure_types = ["other"]`
    - `min_special_proximity_score = 0.8`
  - 结果:
    - `D46 final = 2.484944 / 0.158502 / 3.091893 / 0.392083`
    - 相比 `D45`
      - validation 更低
      - 但 special / `e_evt` / `z_art` 全部更差
- 风险:
  - 如果看到 `D44` 已经证明 relaxed gate 里的 terminal contamination 是问题，
  - 就很容易默认:
    - 把 `D45` 的 late phase 也切到更干净的 relaxed-none-other set
    - 会顺理成章保住 special 并继续降 validation
  - 但 `D46` 说明这条推理并不成立；
  - late filter linkage 会把 `D45` 沿前沿推向 validation-first，
    同时回吐其 special-compromise 价值
- 处理要求:
  - 当前把 `D46` 解释为:
    - `D45` 路线上的前沿形状补充
    - 不是新的更优 compromise
  - 若继续沿 `D45` 路线推进，
  - 不再优先继续做 late gate 的 pool 替换 / linkage 小变体
### 131. 即使继续提高 `relaxed none-other` 的 late proximity 阈值，也不要默认更小更纯的 late set 会自然带来更好的 special-compromise
- 现象:
  - `D47` 在 `D46` 基础上只把 late `min_special_proximity_score` 从 `0.8` 提到 `0.84`
  - late priority count 从 `19` 变成 `15`
  - 结果:
    - `D47 final = 2.480151 / 0.170562 / 3.014662 / 0.378469`
    - 相比 `D46`
      - validation 再低
      - 但 special / `e_evt` / `z_art` 再差
- 风险:
  - 如果已经接受 `D46` 只是往 validation 方向滑，
  - 就很容易继续赌:
    - 再把 late set 缩小一点
    - 也许就能在更“纯”的 special-like 样本上重新找回平衡
  - 但 `D47` 说明当前趋势相反；
  - 更小更硬的 late set 只会继续放大这种 validation-first 漂移
- 处理要求:
  - 当前把 `D47` 解释为:
    - `D45` 路线上的 late-threshold 封口实验
    - 不是新的 breakout family
  - 若继续推进，
  - 不再优先继续做 `D45` 上的 late proximity threshold sweep；
  - 应转向更强的:
    - late target-shape 联动
    - 或 formal special 对齐监督
### 132. 即使把 `D45` 的 late teacher pull 改成更“聪明”的 soft target-shape weighting，也不要默认它会自然把 `D45` 推成新的 compromise
- 现象:
  - `D48` 在 `D45` 基础上只改 late teacher consistency 的 sample weighting:
    - `base_sample_weight = 0.35`
    - `proximity_weight_scale = 1.0`
    - `final_terminal_type_weight_overrides = {"none": 0.2}`
    - `utterance_structure_type_weight_overrides = {"other": 0.15, "nonverbal": 0.15}`
  - 但结果:
    - `D48 step10 = 2.578968 / 0.161176 / 2.97141 / 0.42042`
    - `D48 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
  - 与 `D45 step10 / final` 在当前精度下完全相同
- 风险:
  - 如果已经接受:
    - late filter shrinkage 不够
  - 就很容易继续默认:
    - 只要让 late teacher 按 proximity / none / structure 再“聪明”一点加权
    - 就能自然把 `D45` 推成更好的点
  - 但 `D48` 说明:
    - 当前这类 softweight 只是在重放 `D45`
    - 没有形成新的优化杠杆
- 处理要求:
  - 当前把 `D48` 解释为:
    - `D45` 路线上的 softweight 封口实验
    - 不是新的 breakout family
  - 若继续沿 `D45` 推进，
  - 不再优先继续做:
    - late teacher sample-weight 小数微调
    - proximity / terminal / structure bonus 的软加权 sweep
### 133. 即使 late-only `punctuation_profile_aux` 已经在 validation 和 special 上都真实激活，也不要默认它会把 `D45` 变成新的 route 候选
- 现象:
  - `D49` 保持 `D45` 的 teacher family 与 sampler，
    只新增:
    - `punctuation_profile_aux.weight = 0.2`
    - `weight_schedule = step11 -> step15 linear ramp`
  - 日志已确认:
    - `step10 / 11 effective weight = 0.0`
    - `step15 / 20 effective weight = 0.2`
  - final:
    - validation `loss_punctuation_profile_aux = 0.017141`
    - special `loss_punctuation_profile_aux = 0.002731`
    - `D49 final = 2.507186 / 0.130834 / 3.196306 / 0.407234`
- 风险:
  - 如果看到 punctuation supervision 在两边都真实命中，
  - 就很容易过早解释成:
    - 这条 formal-special 对齐线已经找到了新杠杆
  - 但 `D49` 的实际变化只是:
    - special 略好
    - validation 略差
    - `e_evt / z_art` 基本不变
  - 也就是:
    - 它形成了极轻微 tradeoff
    - 但还远不足以改写当前 route
- 处理要求:
  - 当前把 `D49` 解释为:
    - `punctuation_profile_aux` 在 `D45` family 上的有效但弱杠杆验证
    - 不是新的 route 候选
  - 若继续推进 formal special supervision，
  - 不再优先继续做:
    - `punctuation_profile_aux` 纯 weight sweep
    - `punctuation_profile_aux` 纯 ramp step sweep
  - 更值得转向:
    - frame-local / boundary-local 的 formal special supervision
    - 而不是继续停留在 utterance-level punctuation profile
### 134. 即使把现成的 `structural_clause_transition_aux` 直接接到 `D45` 路线上，只要 late 命中稀疏且 final 近似重跑，就不要默认“这条 boundary-local 监督在更好底座上就会自然起杠杆”
- 现象:
  - `D50` 保持 `D45` 的 teacher family 和 sampler，
    只新增:
    - `structural_clause_transition_aux.pool_memberships = ["structural_clause_ge4"]`
    - `weight_schedule = step11 -> step15`
  - 训练日志里:
    - `step14 loss_structural_clause_transition_aux = 0.182235`
  - 但结果:
    - `D50 final = 2.503763 / 0.133735 / 3.196203 / 0.407221`
    - 与 `D45 final = 2.503755 / 0.133716 / 3.196309 / 0.407233`
    - 仍是数值级重合
- 风险:
  - 如果已经看到:
    - `D45` 是更好的 compromise 底座
  - 就很容易自然外推成:
    - 以前在 `D7` 上没杠杆的 boundary-local aux，
    - 挂到 `D45` 上也许就会长出来
  - 但 `D50` 说明:
    - 这条推理默认并不成立
    - 现有 sidecar-pool boundary-local supervision 本身仍然很弱
- 处理要求:
  - 当前把 `D50` 解释为:
    - `D45` 路线上 boundary-local structural aux 的最小封口实验
    - 不是新的 breakout family
  - 不再优先继续做:
    - `D50` 纯 weight sweep
    - `D50` 纯 ramp step sweep
### 135. 即使补最小 late structural exposure，让 `structural_clause_transition_aux` 在 `D45` 路线上稳定吃到样本，也不要默认它会产生更好的 special-compromise
- 现象:
  - `D51` 在 `D50` 基础上只补:
    - late `priority_ratio = 0.5`
    - primary 仍是 `challenge_proxy_core + short_pause_no_terminal`
    - `secondary_sampling.max_slots = 1`
    - `secondary_sampling.priority_pool_memberships = ["structural_clause_ge4"]`
  - dry-run 已确认 late `phase_priority_record_count = 204`
  - 训练日志里:
    - `step12 loss_structural_clause_transition_aux = 0.128683`
    - `step19 = 0.166892`
    - `step20 = 0.194475`
  - 但结果:
    - `D51 final = 2.493466 / 0.148358 / 3.130833 / 0.403129`
    - 相比 `D45`
      - validation 更低
      - 但 special / `e_evt` / `z_art` 都更差
- 风险:
  - 如果 `D50` 只是近似重跑，
  - 就很容易继续默认:
    - 只是 late structural exposure 还不够
    - 补一个最小 secondary slot 之后就会自然长出更好 compromise
  - 但 `D51` 说明:
    - 一旦这条 family 真正稳定进入 late phase
    - 它仍然只是把轨迹推向 validation-first
    - 没有把 `D45` 推成更优 joint winner
- 处理要求:
  - 当前把 `D51` 解释为:
    - `D45` 路线上现有 sidecar-pool boundary-local family 的正式封口实验
    - 不是新的可扩展分支
  - 若继续推进 formal special supervision，
  - 不再优先继续做:
    - late structural secondary slot sweep
    - 现有 `structural_clause_transition_aux` 小变体
  - 更值得转向:
    - 更强的 late teacher family decomposition
    - 或真正新的 frame-local formal special supervision 定义
### 136. 即使把 `D45` 的 late teacher 从 `D29 step20` 换成 `D29 step10`，得到一点 special / control 回拉，也不要默认 late checkpoint 微分解已经形成新杠杆
- 现象:
  - `D52` 保持 `D45` 的 early `D33 step10` anchor 和 sampler，
    只把 late teacher 改成 `D29 step10`
  - `step11 effective_teacher_consistency.teacher_checkpoint_path`
    - 已真实切到 `D29 step10`
  - final:
    - `D52 = 2.506383 / 0.131541 / 3.201443 / 0.411876`
  - 相比 `D45 = 2.503755 / 0.133716 / 3.196309 / 0.407233`
    - validation 略差
    - special / `e_evt` / `z_art` 略好
- 风险:
  - 看到 `D52` 没有简单退化成 validation-first，
  - 很容易继续默认:
    - 只要把 late checkpoint 再切细一点
    - `D45` 就会自然长成新的 breakout route
  - 但 `D52` 的变化量级只有 epsilon 级，
    仍远不足以改写 route policy
- 处理要求:
  - 当前把 `D52` 解释为:
    - `D45` 路线上的 late checkpoint micro-decomposition 验证
    - 不是新的 route 候选
  - 不再优先继续做:
    - `D29 step20 -> step10` 的单点替换小变体
    - 纯 late checkpoint 时点 sweep
### 137. 即使三段式 `D29 step10 -> D29 step20` handoff 已真实切换，也不要默认这种渐进 decomposition 会把 `D52` 进一步推成新前沿
- 现象:
  - `D53` 在 `D52` 基础上进一步拆成:
    - `step11-15 = D29 step10`
    - `step16-20 = D29 step20`
  - 日志已确认:
    - `step15` 仍用 `D29 step10`
    - `step16` 已切到 `D29 step20`
  - final:
    - `D53 = 2.505593 / 0.132377 / 3.198097 / 0.410493`
  - 相比 `D52`
    - validation 略好
    - 但 special / `e_evt` / `z_art` 略回吐
- 风险:
  - 如果已经接受:
    - `D52` 有一点点可见 tradeoff
  - 就很容易继续默认:
    - 再做一个更平滑的 late teacher 渐进 handoff
    - 就能把这条线真正推开
  - 但 `D53` 说明:
    - 这类三段式 checkpoint decomposition 目前仍只是在 `D45 / D52` 附近做微小再平衡
    - 没有形成新的 breakout
- 处理要求:
  - 当前把 `D53` 解释为:
    - late checkpoint decomposition family 的进一步封口实验
    - 不是下一条应继续细抠的主线
  - 若继续走 teacher 路线，
  - 更值得转向:
    - teacher family 与 phase-specific target shape / gate 的更强联动
    - 或真正新的 formal special supervision
### 138. 即使在 `D29 step10` 晚段继续保留 `fused_hidden` 能给 `D45 / D52` 带来一点 special / control 回拉，也不要默认这已经是可持续放大的新杠杆
- 现象:
  - `D54` 在 `D52` 基础上只改:
    - `step11-20 teacher = D29 step10`
    - `fused_hidden_weight = 0.05`
  - `step11` 日志已确认:
    - late teacher 已切到 `D29 step10`
    - `fused_hidden_weight = 0.05`
  - final:
    - `D54 = 2.505569 / 0.131888 / 3.199683 / 0.412614`
  - 相比 `D45`
    - validation 略差
    - special / `e_evt` / `z_art` 略好
- 风险:
  - 看到 `D54` 比 `D45` 有一点点更均衡，
  - 很容易继续默认:
    - 只要再给 late `fused_hidden` 做小权重 sweep
    - 就能把这条线逐步推成新的 route 候选
  - 但 `D54` 的变化仍然只有 epsilon 级，
    远不足以支撑这种外推
- 处理要求:
  - 当前把 `D54` 解释为:
    - `late fused_hidden on D29 step10` 的有效但很弱杠杆验证
    - 不是新的 breakout family
  - 不再优先继续做:
    - `D54` 的 late fused_hidden 小权重 sweep
    - `D54` 的常规时点小微调
### 139. 即使更强的 phase-specific teacher/gate/target linkage 已全部真实切换，也不要默认“联动更完整”就一定会优于较弱版本
- 现象:
  - `D55` 把 `D53` 升级成:
    - `step11-15 = D29 step10 + short_pause gate + fused_hidden`
    - `step16-20 = D29 step20 + core-only gate + no fused_hidden`
  - dry-run 已确认:
    - targeted sampling `phase_priority_record_counts = 19 -> 16`
  - `step16` 日志也已确认:
    - teacher 切到 `D29 step20`
    - `fused_hidden_weight = 0.0`
    - gate 缩回 `challenge_proxy_core`
  - 但 final:
    - `D55 = 2.506311 / 0.133216 / 3.190822 / 0.405426`
    - 被 `D54` 直接压住
- 风险:
  - 如果已经接受:
    - `D54` 至少有一点收益
  - 就很容易继续默认:
    - 只要把 teacher / gate / sampler / fused_hidden 联动切得更精细
    - 收益就会自然放大
  - 但 `D55` 说明:
    - 更强 linkage 在当前 family 下并不会自动放大收益
    - 反而可能把微小改进重新抹平
- 处理要求:
  - 当前把 `D55` 解释为:
    - `phase-specific gate-target linkage` 在当前 teacher family 上的正式负结果
    - 不是下一条应继续细抠的配置主线
  - 若继续推进，
  - 更值得转向:
    - 真正新的 frame-local formal special supervision
    - 或更强的 teacher family + supervision 联合定义
### 140. 即使新的 frame-local formal special supervision 已经能真实消费 `clause_spans / clause_transition`，也不要默认“接上线”就等于“形成了持续杠杆”
- 现象:
  - `D56 / D57` 新增了 `formal_special_clause_shape_aux`
  - `dry-run step0` 已确认:
    - `D56 loss_formal_special_clause_shape_aux = 0.02187`
    - `D57 loss_formal_special_clause_shape_aux = 0.025937`
  - 但 early effective `weight = 0.0`
  - late 命中主要集中在:
    - `D56 step15 = 0.031738`
    - `D57 step15 = 0.036294`
  - final validation / final special_eval 都回到:
    - `loss_formal_special_clause_shape_aux = 0.0`
- 风险:
  - 看到新 supervision 已能真实读到 frame-local sidecar，
  - 很容易继续默认:
    - 既然不是空实现，
    - 只要再调一点权重 / role 组合
    - 它就会自然长成新的主线杠杆
  - 但 `D56 / D57` 说明:
    - 当前问题不在“接没接上”
    - 而在“late exposure 太稀疏，无法稳定渗透成 final behavior”
- 处理要求:
  - 当前把 `D56 / D57` 解释为:
    - 第一版 `clause-span` formal special supervision 的正式打通验证
    - 同时也是“仅靠当前 exposure 方式不够”的负证据
  - 若继续推进，
  - 应优先考虑:
    - 更稳定命中的 frame-local target
    - 或先改 sampler / gate 让这类 supervision 在 late phase 持续出现
### 141. 即使把 `middle` clause 一起纳入 frame-local formal special supervision，也不要默认覆盖面更大就一定能跳出 `D54` 盆地
- 现象:
  - `D56` 只管 `single + final`
    - final `= 2.505586 / 0.131862 / 3.19987 / 0.412639`
  - `D57` 再加入 `middle` role 与一点 `other / none` weighting
    - final `= 2.505587 / 0.131861 / 3.199882 / 0.41264`
  - 两者都与 `D54 = 2.505569 / 0.131888 / 3.199683 / 0.412614` 近乎重合
- 风险:
  - 看到 `D57` 数字比 `D56` 还略动一点，
  - 很容易继续默认:
    - 只要再把 `middle/final/single` 的 frame-local shape 排列切得更细
    - 就能慢慢把 `D54` 推开
  - 但当前差异已经只有万分位级，
    不足以支撑这种外推
- 处理要求:
  - 当前把 `D57` 解释为:
    - `middle` clause 扩展没有形成新 regime 的正式负结果
    - 不是下一条应继续细抠的 role 组合主线
  - 不再优先继续做:
    - `single/final/middle` 小排列
    - `formal_special_clause_shape_aux` 的常规权重 sweep
### 142. 即使已经把 formal special supervision 的 late hit 从“偶发”推成“step11-20 全覆盖”，也不要默认这就会自然转化成 special-route 收益
- 现象:
  - `D58` 把 late priority cohort 从 `19` 条收紧到显式 3 条:
    - `chapter3_2_firefly_191`
    - `chapter3_3_firefly_125`
    - `chapter3_3_firefly_148`
  - `step11-20` 的 `loss_formal_special_clause_shape_aux` 全部非零
    - 约为 `0.032209 -> 0.030982`
  - 但 final:
    - `D58 = 2.480056 / 0.171798 / 2.994445 / 0.374825`
  - 相比 `D57`
    - validation 更低
    - 但 special / `e_evt` / `z_art` 都更差
- 风险:
  - 看到“命中率问题终于解决了”，
  - 很容易继续默认:
    - 只要继续把同一 cohort 喂得更稳定
    - special-route 收益就会随之出现
  - 但 `D58` 说明:
    - 稳定命中并不等于命中的是对的 cohort
    - 当前这批短样本更像 validation-first 杠杆
- 处理要求:
  - 当前把 `D58` 解释为:
    - `formal special exposure` 稳定化的正式验证
    - 同时也是“当前 3 条 short-pause cohort 方向不对”的负证据
  - 不再优先继续做:
    - 这 3 条样本的 priority ratio sweep
    - 同一 short-pause cohort 的再细 sampler 微调
### 143. 即使再把 late teacher gate 完全对齐到同一 3 条样本上，也不要默认 teacher alignment 会自动打开新的 regime
- 现象:
  - `D59` 完全继承 `D58`
  - 只额外把 late `teacher_consistency` 收紧到:
    - `pool_memberships = ['short_pause_no_terminal']`
    - `min_clause_count = 2`
    - `required_within_special_duration_ceiling = true`
  - `step11-20` teacher loss 也全程真实非零:
    - `0.12287 -> 0.018237`
  - 但 final:
    - `D59 = 2.480048 / 0.171791 / 2.994481 / 0.374835`
    - 与 `D58` 近乎重合
- 风险:
  - 在 `D58` 已经稳定命中之后，
  - 很容易继续默认:
    - 再把 teacher pull 也锁到同一 cohort
    - 就能把这条线真正推开
  - 但 `D59` 说明:
    - 当 cohort 本身方向不对时，
    - teacher alignment 也只会得到 epsilon 级重放
- 处理要求:
  - 当前把 `D59` 解释为:
    - `sampler + formal gate + teacher gate` 三者对齐后的正式封口实验
    - 不是下一条应继续细抠的 teacher micro-tuning 主线
  - 若继续推进，
  - 更值得转向:
    - 与 final special slice 更接近的新 cohort
    - 或新的 frame-local special supervision 定义
### 144. 即使已经找到了 train 侧“最接近”的微短句代理，也不要默认现有 `clause-shape` 监督原则仍然成立
- 现象:
  - `post-D59` special-slice 诊断显示:
    - `target_special_eval` 的 `8` 条样本全部满足:
      - `nonverbal_only = true`
      - `lexical = 0`
      - `pause = 0`
      - `terminal = 0`
      - `clause = 0`
      - `clause_span = 0`
  - 但 `target_train = 592` 条里:
    - `nonverbal_only_count = 0`
    - `lexical_char_count_zero = 0`
    - `clause_span_count_zero = 0`
    - `special_signature_count = 0`
  - 当前最接近的启发式 cohort 变成:
    - `micro_pause_none_singleton_strict`
    - `count = 8`
    - `mean_special_distance = 2.047626`
  - 可它仍然是:
    - `lexical = 1`
    - `pause = 1`
    - `terminal = 0`
    - `clause = 1`
    - `clause_span = 1`
- 风险:
  - 看到已经找到了比 `challenge_proxy_core / short_pause_no_terminal` 更近的代理，
  - 很容易继续默认:
    - 只要把 sampler / gate / teacher 再对准这批微短句
    - 现有 `clause-shape` formal special 监督就还能继续放大
  - 但这轮诊断说明:
    - 当前最近邻和 final special slice 的核心差异
    - 不是连续数值上的“小一点点”
    - 而是:
      - `has lexical` vs `no lexical`
      - `has clause_span` vs `no clause_span`
      - `spoken singleton` vs `nonverbal sparse slice`
- 处理要求:
  - 当前把这轮 special-slice 诊断解释为:
    - `D56-D59` family 的原则级分叉点
    - 不是下一条 sampler 微调线索
  - 若继续推进 formal special supervision，
  - 应优先转向:
    - `clause-free singleton sparse-frame supervision`
    - 或更贴近 `nonverbal_only / zero-clause-span` 的新 proxy principle
### 145. 不要把 `200 step` long-window probe 的 final 直接并入当前 quick-screen handoff selector
- 现象:
  - `D22 / D33 / D59` 的 `200 step` probe 都把 validation 明显压低到 `2.12x`
  - 但同时把 special delta 推高到 `0.23x ~ 0.25x`
  - 六实验 mixed-horizon selector 在 `max_validation_budget_over_best = 0.05` 下直接给出:
    - `selected_policy = validation_strict`
    - `selected_anchor = D33(200step)`
    - `budget_to_minimax_anchor = 0.321495`
- 风险:
  - 如果把这结果误读成“当前正式默认 route 应立刻刷新到 D33-200”，
  - 就会把:
    - `20/30 step` quick-screen anchor
    - `200 step` trajectory probe final
  - 错误混成一套 selector 语义
  - 最终让 handoff 口径被 horizon 差异直接拖成 pure validation routing
- 处理要求:
  - 当前把 `200 step` 结果解释为:
    - trajectory probe
    - 用于回答 late dynamics 是否继续变化
    - 不作为当前 fixed handoff 的直接替换锚点
  - 当前正式 handoff / stage-report 继续保持 quick-screen route
  - 若后续要做长窗选点，优先使用:
    - matched-horizon comparison
    - 或 checkpoint-selected late stop
### 146. 当 late targeted sampling 已经把 batch 主体锁成 strict singleton cohort 时，再把 teacher gate 从 relaxed 收紧到 strict 可能是近似 no-op
- 现象:
  - `D60` 与 `D61` 唯一差异是 late `teacher_consistency` gate:
    - `D60 = micro_pause_none_singleton_strict`
    - `D61 = short_pause_no_terminal + within_special_duration_ceiling + other + none`
  - 但两者:
    - 训练 step loss 轨迹逐点重合
    - final 四项也完全一致
      - `2.52274 / 0.112137 / 3.260251 / 0.435391`
  - 同时 `D60 / D61 step11-20`
    - `loss_singleton_sparse_proxy_aux` 都全程非零
    - late batch 明显已被 singleton priority 主导
- 风险:
  - 看到 `D60` 明显优于 `D59`，
  - 很容易继续把功劳归到:
    - strict late teacher gate
    - 或 teacher pool 再收窄
  - 然后继续沿这个轴做更多 gate sweep
  - 但 `D61` 说明:
    - 当前收益更主要来自
      - singleton sparse proxy principle
      - late singleton targeted sampling
    - 不是 teacher gate 这一步在单独起杠杆
- 处理要求:
  - 当前把 `D60 / D61` 解释为:
    - principle pivot 已成立
    - strict-vs-relaxed late teacher gate 在这轮设置下不是主变量
  - 若继续推进，优先做:
    - 更强 validation backbone 上的 singleton sparse 集成
    - 或削减 validation tax 的 schedule 设计
  - 不再优先做:
    - `D60 / D61` 同骨架下的 late teacher gate 小排列
### 147. 不要把 `singleton sparse` principle 直接 graft 到 `D22` 后半段，并假设“再把 late teacher gate 对齐”就能自动变成新的 minimax anchor
- 现象:
  - `D62` 把 `singleton_sparse_proxy_aux + step21-30 singleton late pulse` 接到 `D22 backbone`
  - 得到:
    - `2.42375 / 0.234048 / 2.603584 / 0.316145`
  - 相对 `D22 = 2.444194 / 0.140001 / 3.299035 / 0.438936`
    - validation 虽更低
    - 但 special / `zero_e_evt` / `zero_z_art` 全面明显恶化
  - `D63` 再把 late `teacher_consistency` 也对齐到 `micro_pause_none_singleton_strict`
    - final 四项仍与 `D62` 完全一致
    - checkpoint series、step loss、late singleton aux 也逐点一致
- 风险:
  - 看到 `D60` 证明 singleton principle 有效后，
  - 很容易默认:
    - 只要把这条 principle 接到 `D22`
    - 再把 late teacher gate 跟上
    - 就能同时拿到
      - `D22` 的 validation backbone
      - 和 `D60` 的 special-aware 收益
  - 但 `D62 / D63` 说明:
    - 当前并不是一个“teacher gate 还没对齐”的浅层问题
    - `D22 backbone + singleton late pulse` 这条集成形状本身就会把终点拖成
      - 更低 validation
      - 更差 special/control floor
- 处理要求:
  - 当前把 `D62 / D63` 解释为:
    - `D22 graft` 失败
    - `teacher-aligned late gate` 也是 no-op
  - 暂停继续做:
    - `D22 backbone + singleton late pulse`
    - 这条 family 的 late teacher gate 小排列
  - 若继续削减 singleton principle 的 validation tax，
  - 优先回到:
    - `D60` 一类已验证有效的 post-`D59` backbone
    - 再做更短、更弱或 checkpoint-selected 的 tail
### 148. 在 `D60` family 上，late singleton sampler ratio 是主杠杆；单纯缩短 tail 或微降 aux weight 不是削 validation tax 的有效旋钮
- 现象:
  - `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - `D64(short-tail) = 2.539564 / 0.154003 / 3.012511 / 0.400641`
  - `D65(weaker-tail) = 2.482579 / 0.172447 / 2.980073 / 0.375719`
  - `D66(auxlighter) = 2.522723 / 0.11214 / 3.260339 / 0.435397`
  - `D67(samplerlighter) = 2.482594 / 0.172458 / 2.979895 / 0.375695`
- 风险:
  - 看到 `D60` 相对 `D22` 还有 validation tax，
  - 很容易默认:
    - tail 再短一点
    - aux 再轻一点
    - 或 sampler ratio 稍微往下拧一点
    - 就能平滑地拿到更好的 validation / special tradeoff
  - 但这轮说明:
    - `short-tail` 会同时伤 validation 与 special/control floor
    - `aux weight 0.10 -> 0.08` 基本是 no-op
    - 真正有杠杆的是 late singleton sampler ratio
    - 但这个杠杆一旦下调，special-aware 收益会明显回吐
- 处理要求:
  - 当前把 `D60 family` 解释为:
    - `D60` 是当前 local optimum
    - simple tail-strength sweep 已基本收口
  - 暂停继续做:
    - short-tail
    - aux-weight 微调
    - sampler-ratio 下调 sweep
- 若继续削减 validation tax，
  - 下一手应离开这条 simple tail-strength 轴，
    转向:
    - 更上游的 backbone / handoff 形状
    - 或 matched-horizon / checkpoint-selected 设计
### 149. 不要把 `D60` 的 late teacher source 改成 `D22`，或把 late handoff 形状调成更 `D22-like`，就外推成新的 breakout route
- 现象:
  - `D68` 在 `D60` 基础上只把 late teacher source 改成 `D22 step30`
    - 得到 `2.522315 / 0.112037 / 3.26795 / 0.434833`
  - `D69` 再进一步把 late handoff shape 调成更 `D22-like`
    - late pool 改回 `challenge_proxy_core`
    - late `fused_hidden_weight = 0.0`
    - 得到 `2.523948 / 0.111144 / 3.271397 / 0.434243`
- 风险:
  - 看到 `D68 / D69` 都没有简单退化，
  - 很容易继续默认:
    - `D60` 的 validation tax 主要只是 late teacher source / handoff shape 没选对
    - 只要再往 `D22` 靠一点，
      就会自然长成新的 minimax anchor
  - 但这轮说明:
    - 两条线都只是在 `D60` 周围做 epsilon 级再平衡
    - 没有形成新的 regime
    - 也没有证据表明当前 validation tax 会沿这条轴自然消失
- 处理要求:
  - 当前把 `D68 / D69` 解释为:
    - upstream D22 late-handoff axis 的正式弱杠杆验证
    - 不是下一条应继续细抠的主线
  - 暂停继续做:
    - `D60 -> D22 late teacher source` 小变体
    - `D60 -> D22-like late handoff shape` 小变体
  - 若继续推进 singleton sparse 主线，
    优先转向:
    - matched-horizon / checkpoint-selected
    - 或更强的 backbone 级变化
### 150. route-analysis 不应把“某 policy 当前无 eligible anchors”当成致命异常
- 现象:
  - 在纳入 `D68 / D69` 后，
    `select-offline-mvp-anchor-route` 一度因:
    - `Policy z_art_push has no eligible anchors`
    - 直接中断
  - 原因不是默认 route 失效，
    而是:
    - `best_z_art_floor = D33`
    - `budget_to_special_anchor` 已被 `D69` 的 special leader 降到 `0.126773`
    - 导致 `z_art_push` 同时要求:
      - `val <= best_validation + 0.126773`
      - `zero_z_art >= 0.465828`
    - 当前没有任何 anchor 同时满足
- 风险:
  - 如果 route-analysis 工具链把这种“policy 不可行”直接解释成异常，
  - 后续只要候选集一变化，
    就可能把:
    - selector
    - final comparison
    - 文档落盘
    全部阻断
  - 还会误导人为“实验结论不完整”，
    实际上只是某个备用 policy 当前无可行锚点
- 处理要求:
  - `anchor_route_analysis / selector` 应把这种情况记为:
    - policy unavailable
    - `selected_anchor = null`
  - 而不是直接抛异常
  - 当前代码已按这个方向修正，
    后续如新增 policy，也应保持同样的健壮性
### 151. 不要把 `D60` family 的当前问题先验解释成“需要 checkpoint-selected late stop”
- 现象:
  - `D60 / D68 / D69 step10` 完全同轨:
    - `2.578968 / 0.161176 / 2.97141 / 0.42042`
  - 而各自 `step20` 都同时改善:
    - validation
    - special
    - `zero_e_evt`
    - `zero_z_art`
- 风险:
  - 看到上一阶段一直在讨论:
    - matched-horizon
    - checkpoint-selected
  - 很容易自然默认:
    - `D60` family 也许只是 final checkpoint 选得不对
    - 只要回到 `step10` 或做 early-stop，
      就能削掉 validation tax
  - 但这轮说明:
    - 这条主线没有出现值得利用的 early-stop tradeoff
    - `step20` 本身就是更强点
- 处理要求:
  - 当前把 `D60 / D68 / D69` 解释为:
    - 不值得继续做 checkpoint-selected late stop 的 family
  - 若继续推进，
    应优先转向:
    - matched-horizon 制度比较
    - 而不是这条 family 内的 step10/20 选点
### 152. 当前 `D22 = default_minimax` 的口径带有明显 horizon advantage；不要把它误读成 matched-horizon 下仍然占优
- 现象:
  - 物化 `D22 step20` 后，
    matched20 比较集变成:
    - `D29`
    - `D22-step20`
    - `D33`
    - `D60`
    - `D68`
    - `D69`
  - 结果:
    - `D22-step20 = 2.470626 / 0.178101 / 3.021211 / 0.398439`
    - `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
  - matched20 route-analysis 给出:
    - `minimax = D68`
    - `budget_to_minimax_anchor = 0.12514`
  - 在沿用当前 `budget = 0.05` 时，
    selector 直接退化成:
    - `validation_strict = D29`
- 风险:
  - 如果继续把当前官方口径直接外推到公平 horizon，
  - 很容易误以为:
    - `D22` 之所以还是 minimax，
      只是因为还没把 post-`D59` 新线继续微调够
  - 但这轮说明:
    - 一旦把 `D22` 拉回 `20 step`
    - 它已经不再是 matched-horizon 的 minimax
    - 当前问题更像:
      - horizon policy 不对称
      - 与默认 validation budget `0.05` 过紧
- 处理要求:
  - 当前把这轮 matched20 解释为:
    - horizon-policy 诊断
    - 不是立即刷新 fixed handoff 的授权
  - 若要正式改写 anchor，
    必须先明确:
    - 是否采用 matched-horizon 制度
    - 是否同步重设 validation budget
### 153. 不要在同一轮里同时把 `horizon + validation budget + minimax anchor` 一起改成官方口径
- 现象:
  - 当前三套制度已经很清楚:
    - 现口径 quick-screen -> `default_minimax = D22`
    - `matched20@0.05` -> `validation_strict = D29`
    - `matched20@0.13` -> `default_minimax = D68`
- 风险:
  - 如果因为 matched20 诊断结果很强，
    就在同一轮里直接宣布:
    - selector 改成 matched-horizon
    - default budget 从 `0.05` 改成 `0.13`
    - 官方 minimax anchor 从 `D22` 改成 `D68`
  - 那后续很难判断:
    - 到底是模型路线真正换代了
    - 还是 selector contract 被整体重写了
  - 这会让阶段结论失去可追踪性
- 处理要求:
  - 当前更合理的制度迁移顺序应是:
    - 官方口径先保持旧 quick-screen
    - matched20 先作为 shadow policy 并行跟踪
    - 等 matched20 minimax 与新 budget 都稳定后，再决定是否正式迁移
### 154. 不要把“接受 step20 只负责 quick-screen”偷换成“以后默认都看 500”
- 现象:
  - `1.md` 的制度方向是对的:
    - quick-screen 和 long-horizon 必须拆开
  - 但字面表述里容易把:
    - “long-horizon 应更大”
    偷换成:
    - “以后默认就是 500”
- 风险:
  - 如果把 `500` 写成默认标准，
    会把:
    - trajectory probe
    - official fixed handoff challenge
    - 实验预算控制
    三件事不必要地绑死
  - 也会和当前已经跑过、且信息明确的 `200 step` probe 制度冲突
- 处理要求:
  - 当前正式口径应写成:
    - matched long horizon(`200+`)
  - 必要时再更长，
    但不把 `500` 预写成默认唯一答案
### 155. matched20 shadow policy 一旦决定长期保留，就不要继续手工拼 checkpoint-anchor / selector / recap 产物
- 现象:
  - `matched20` 相关产物之前已经手工跑过一轮:
    - checkpoint anchor materialize
    - route-analysis
    - selector
    - comparison
    - route recap
  - 当前这些步骤已经被整合进:
    - `build-offline-mvp-matched-horizon-shadow`
- 风险:
  - 如果后续仍靠手工串命令，
    很容易出现:
    - 某个 budget 忘跑
    - selector / recap 路径不一致
    - anchor step 或输入候选集不一致
  - 最终让 shadow policy 失去可比性
- 处理要求:
  - 只要目标是生成标准 matched-horizon shadow 产物，
    默认优先使用:
    - `build-offline-mvp-matched-horizon-shadow`
  - 不再手工逐个拼 route-analysis / selector / recap，
    除非是在调试工具本身
### 156. 看到 Python 运行时异常时，先核对是否误用了系统解释器；不要在未确认解释器路径前直接把问题升级成兼容性修复
- 现象:
  - 仓库规范要求所有 Python 命令统一使用:
    - `.\python.exe`
  - 但实际执行时如果误写成:
    - `python ...`
    很容易悄悄落到系统解释器
  - 随后出现的异常会被误判成:
    - 代码兼容性问题
    - 依赖缺失
    - 或实现本身损坏
- 风险:
  - 如果在未确认解释器路径前就开始改代码，
    很容易做出与真实问题无关的补丁，
    还会把环境误用固化成新的代码分叉
- 处理要求:
  - 任何 Python 命令默认显式写成:
    - `.\python.exe ...`
  - 一旦出现异常，先检查:
    - `where.exe python`
    - `.\python.exe --version`
  - 只有确认已经使用仓库解释器后，
    才继续判断是否属于真实实现问题
### 157. 不要把“更强 validation backbone + D60 主线”外推成单调改进；`D26-init` 和 `D29-init` 之间已经出现明显过冲边界
- 现象:
  - `D70(D26-init) = 2.399035 / 0.168635 / 2.941607 / 0.365565`
  - `D71(D29-init) = 2.340197 / 0.190968 / 2.634231 / 0.320415`
  - 相对 `D70`，
    `D71` 虽然 validation 更低，
    但 special / `e_evt` / `z_art` 全面明显回退
- 风险:
  - 看到 `D70` 相对 `D60` 明显削掉 validation tax 后，
    很容易默认:
    - backbone 越强越好
    - 只要继续把 init 往 `D29` 靠，
      就会自然得到更强 minimax
  - 但 `D71` 已经说明:
    - 这条轴不是单调改进
    - 很容易直接过冲成 validation-first
- 处理要求:
  - 当前把 `D70 / D71` 解释为:
    - `D26-init` 可能是新的 sweet spot
    - `D29-init` 已经是过冲边界
  - 若继续推进，优先围绕:
    - `D70`
    做 control restoration
  - 暂不继续沿:
    - 更强 validation-first init backbone
    继续外推
### 158. 当新 validation leader 把 `best_validation` 大幅拉低时，不要把 selector 自动塌成 `validation_strict` 直接解释成 fixed handoff 已刷新
- 现象:
  - 将 `D70 / D71` 并入 official quick-screen 后，
    route-analysis 仍给出:
    - minimax = `D22`
  - 但因为:
    - validation leader 变成 `D71 = 2.340197`
    - `budget_to_minimax_anchor` 抬到 `0.103997`
  - 导致现有 `budget=0.05` selector 自动变成:
    - `validation_strict = D71`
- 风险:
  - 如果只看 raw selector 输出，
    很容易误判成:
    - `D71` 已经取代 `D22`
    - 或官方 fixed handoff 应立刻切成 validation-first
  - 实际上这更主要是:
    - 旧 budget contract 被更强 validation leader 挤穿
    - 而不是 minimax 自身已经稳定换人
- 处理要求:
  - 看到这类结果时，
    先分开确认:
    - raw validation leader 是谁
    - minimax 是谁
    - selector 是否只是因为 budget 太紧而退化
  - 在完成这三层区分前，
    不把 raw selector 塌缩直接写成正式 fixed handoff 刷新
### 159. 对“必须使用仓库 `.\python.exe`”这类高频环境纪律，不要只写在文档里；入口层应提供即时 warning
- 现象:
  - 即使 `docs/00_context_bootstrap.md` 和本文已经明确要求:
    - 只能使用仓库根目录 `.\python.exe`
  - 实际推进时仍可能因为手滑写成:
    - `python manage.py ...`
  - 从而先落到系统解释器，再把异常误判成实现问题
- 风险:
  - 这类错误发生频率高，
    但靠人工每轮重读文档并不可靠
  - 如果入口没有即时反馈，
    错误会在后续若干命令后才暴露，
    还容易引出无关的排障动作
- 处理要求:
  - 对这类高频环境纪律，
    尽量加到程序入口做轻量 warning
  - 当前 `manage.py` 已增加:
    - 路径不是仓库 `python.exe` 时告警
    - 版本低于项目基线 `3.10` 时告警
  - 后续若再出现类似“必须满足的启动前条件”，
    优先考虑入口提醒，而不是只补文档
### 160. 不要并行执行 `init-experiment`；它按现有文件计数分配实验编号，并发下会抢同一个 `EXP-...` 前缀
- 现象:
  - 本轮并行初始化 `D72 / D73` 时，
    两个 experiment record 都拿到了:
    - `EXP-20260316-027`
  - 后续必须人工清理错误占位记录，
    再顺序重建 `D73 = EXP-...029`
- 风险:
  - 如果 `init-experiment` 并发抢号，
    很容易出现:
    - 训练 id 与 experiment metrics 文件错位
    - selector / eval 读取到错误 experiment record
    - 后续文档和产物引用混乱
- 处理要求:
  - `init-experiment` 一律顺序执行，
    不参与并行化
  - 只有在 experiment id 已经明确固定之后，
    才允许并行跑:
    - dry-run
    - 评估链
### 161. 上下文恢复时，不要只按“最新文档编号”推断当前主线；必须同时核对 official quick-screen 与 matched20 shadow 产物
- 现象:
  - 本轮恢复时，最新实验文档已经明确写到:
    - `D72 / D73` 是 `D70 family` 内的 epsilon 级再平衡
  - 但如果只看文档标题或只记一个“最新赢家”，
    很容易误读成:
    - `D72` 已经整体替代 `D22`
    - 或 `D71` 就是当前全口径最佳
- 风险:
  - 当前项目同时存在两套不同问题口径:
    - official quick-screen / fixed handoff
    - matched20 shadow / early matched horizon
  - 如果恢复时不直接看 json 产物，
    容易把:
    - official 仍是 `D22`
    - shadow 已到 `D72`
    混写成一句模糊结论
- 处理要求:
  - 每次接班恢复都至少核对:
    - official `anchor_route_analysis.json`
    - matched20 shadow `anchor_route_analysis.json`
    - 当前预算下的 `anchor_route_selection.json`
  - 汇报“当前最好”时必须先说清:
    - 是 official
    - 是 shadow
    - 还是 `D70 family` 内部比较
### 162. `init-experiment` 的顺序编号不能按“当日已有 md 数量 + 1”；只要历史目录有缺号，就会顺序重用旧前缀
- 现象:
  - 本轮已经不是并发执行，
    仍然出现:
    - 新建 `D74` 时拿到 `EXP-...029`
  - 原因不是同时初始化，
    而是:
    - 之前删除过错误占位记录
    - 当日实验目录存在缺号
    - `build_experiment_id(...)` 仍按 `len(existing) + 1` 分配编号
- 风险:
  - 即使完全顺序执行，
    也会重用已有 `EXP-...NNN` 前缀
  - 这会继续带来:
    - experiment record / metrics / 文档引用歧义
    - 训练与评估链难以肉眼区分同前缀不同 slug
- 处理要求:
  - 编号必须改成:
    - 扫描当日已有 `EXP-YYYYMMDD-NNN-*`
    - 取最大 `NNN`
    - 再 `+1`
  - 当前 `src/v5vc/experiment.py` 已完成该修复
  - 若再清理错误实验记录，
    不需要额外人工补号；入口会自动跳到未使用的新序号
### 163. quick-screen 实验汇报里的 `zero_e_evt / zero_z_art` 常写 raw ablation loss，而 long-horizon route 工具统一使用 ablation delta；两种口径不能直接混算
- 现象:
  - 本轮在复核 `D76` 时，
    如果直接照抄 final `ablation_eval.ablation_modes.zero_*.*.loss_total`，
    会得到:
    - `zero_e_evt = 4.040875`
    - `zero_z_art = 2.52776`
  - 但 `anchor_route_analysis`、`selector`、`docs/109` 这类 long-horizon route 文档使用的是:
    - `zero_e_evt_delta_target_loss_total = 1.937766`
    - `zero_z_art_delta_target_loss_total = 0.424651`
- 风险:
  - 如果把 raw ablation loss 和 delta 混在一张表里，
    容易误判:
    - 某条线是否真的更强
    - `budget_to_minimax_anchor` 的意义
    - 与旧 quick-screen 报告是否“数值对不上”
- 处理要求:
  - 凡是 route / selector / recap / long-horizon comparison，
    统一优先使用:
    - validation
    - special delta
    - `zero_e_evt_delta`
    - `zero_z_art_delta`
  - 若实验报告要继续沿用 quick-screen 口径，
    必须明确写出:
    - 当前使用的是 raw ablation loss
    - 不能与 route-analysis 的 `zero_*_delta` 直接横向比较
### 164. `late_step_ratio = 0.8` 不能机械复用到所有 horizon；对 `200-step` 且 `checkpoint_interval = 50` 的实验，它会把 late window 压成只剩 final
- 现象:
  - 本轮 `D76` 只有:
    - `step50 / 100 / 150 / 200`
  - 如果继续沿用 checkpoint-selection 默认:
    - `late_step_ratio = 0.8`
  - 会得到:
    - `ceil(200 * 0.8) = 160`
    - late window 只剩 `step200`
- 风险:
  - 表面上像是“分析显示没有 late-stop 候选”，
    实际上只是:
    - `step150` 根本没被纳入候选
  - 会把:
    - 稀疏 checkpoint 采样问题
    误读成:
    - 轨迹上没有 late tradeoff
- 处理要求:
  - 运行 checkpoint-selection / gate replay 前，
    先检查:
    - `max_step`
    - `checkpoint_interval`
    - 实际保存的 checkpoint steps
  - 若目标是比较 `150 vs 200` 这类末段 tradeoff，
    应把 `late_step_ratio` 调整到能覆盖最后两个保存点；
    对当前 `200-step + 50step interval`，更合适的是:
    - `late_step_ratio = 0.75`
### 165. 不要把所有 synthetic checkpoint anchor 一概当成“正式 route 候选”；必须先区分它是在补 horizon 对称性，还是在引入新的 checkpoint-option 类别
- 现象:
  - `D22 step20 anchor` 被用于 matched20 shadow 时，
    解决的是:
    - `30step vs 20step` 的 horizon mismatch
  - `D76 step150 anchor` 被用于 pure long-horizon route 时，
    改写的则是:
    - leader 归属
    - minimax 归属
    - `budget_to_minimax_anchor`
- 风险:
  - 如果把两者都笼统写成:
    - “checkpoint anchor 可以进 route”
  - 很容易把:
    - shadow 工具
    误用成:
    - 正式制度切换
  - 最终导致:
    - handoff / stage-report 的 anchor 集失控膨胀
    - 一条实验轨迹同时冒出多个“默认候选”
- 处理要求:
  - 先判定 synthetic anchor 的角色:
    - horizon-equalization
    - checkpoint-option
  - 只有前者可默认进入 matched-horizon shadow
  - 后者默认只保留给:
    - checkpoint-selection
    - gate replay
    - option study
  - 若要让 checkpoint-option 进入正式 route，
    必须把它视为制度升级单独讨论
### 166. 只在文档里写 governance 结论不够；如果 handoff/stage-report 生成器不显式渲染 anchor class，人工汇报时仍会把 shadow option 写成 formal default
- 现象:
  - `docs/123` 已经把:
    - `horizon_equalization_anchor`
    - `checkpoint_option_anchor`
    拆开
  - 但旧版 handoff / stage-report 生成器仍只会输出:
    - 当前 route anchor
    - validation/special alternatives
  - 不会提示:
    - 哪个 alternative 只能用于 matched-horizon shadow
    - 哪个 alternative 只能用于 checkpoint option study
- 风险:
  - 人工复制 `copy_ready_handoff` 或 `executive_status` 时，
    容易把:
    - `D22 step20`
    - `D76 step150`
    这种 synthetic anchor
    写成:
    - “当前可切换的正式默认点”
  - 最终又会回到:
    - official / shadow / option 三套口径混写
- 处理要求:
  - handoff summary / handoff document / stage report 必须显式输出:
    - route governance summary
    - governance guardrail
    - current anchor governance
    - alternative governance
  - `next_step_guidance` 也应按 anchor class 改写:
    - natural final = formal default eligible
    - horizon equalization = shadow only
    - checkpoint option = option only
### 167. 准备公开 GitHub 备份仓时，不要只看工作区文件名；必须同时核对“是否被忽略”“是否已入索引”“是否已有历史提交”
- 现象:
  - 根目录后来新增了敏感文件:
    - `ssh-key-private`
  - 单看磁盘状态只能知道:
    - 文件存在
  - 但真正影响上传边界的还有三层:
    - `.gitignore` 是否命中
    - `git ls-files` 是否已跟踪
    - `git rev-list --count --all` 是否已有提交历史
- 风险:
  - 如果只确认“现在被忽略了”，
    却不查:
    - 之前是否已经 `git add`
    - 之前是否已经提交
  - 就可能误把:
    - 已入索引
    - 已入历史
    的敏感文件当成“安全未上传”
- 处理要求:
  - 新增敏感文件或扩大公开边界时，
    至少检查:
    - `git status --short --ignored`
    - `git ls-files`
    - `git rev-list --count --all`
  - 结论必须拆开写:
    - 是否被忽略
    - 是否被跟踪
    - 是否已有提交历史
### 168. 跑 `evaluate-offline-mvp-ablations` / `evaluate-offline-mvp-special-eval` / `checkpoint_series` / `special_eval_series` 时，不能只给 `--experiment-metrics`；非模板实验必须显式传对应 `--config`
- 现象:
  - `D77` 的 checkpoint 是按:
    - `text_aux_dim = 13`
    训练出来的
  - 如果评估命令只传:
    - `--experiment-metrics`
  - CLI 会回落到默认:
    - `configs/offline_mvp_train_template.json`
  - 于是 eval 端会把 model 实例化成:
    - `text_aux_dim = 3`
- 风险:
  - `model.load_state_dict(...)` 会直接报 shape mismatch:
    - `text_aux_head.weight`
    - `text_aux_head.bias`
  - 表面上像 checkpoint 坏了，
    实际上只是:
    - 评估配置没跟训练配置对齐
- 处理要求:
  - 对所有 experiment-specific eval 命令，
    默认显式传:
    - `--config <该实验训练配置>`
  - 不要依赖 CLI 的默认模板 config
### 169. 对 `D76` 近邻这类“局部 special/control 看起来更好”的候选，不能只看 pairwise 差值；必须并入 full long-horizon route 再判断是否真是更好的 default/minimax 候选
- 现象:
  - `D78` 相对 `D76` 的 final 结果是:
    - validation `+0.033381`
    - special `-0.014199`
    - `z_art` `+0.090059`
  - 单看 pairwise，
    很容易把它读成:
    - “`D76` 的 control restore 成功版”
  - 但一旦把它并入:
    - `D22 / D33 / D59 / D76 / D77`
    的 pure long-horizon route，
    minimax 会直接从:
    - `D76`
    切回:
    - `D33`
- 风险:
  - 如果只看:
    - `vs D76`
    的局部 tradeoff，
    不看 full route，
    就会把:
    - special-oriented probe
    误写成:
    - 更好的 default/minimax 近邻
  - 最终又会把:
    - local improvement
    和
    - route-level upgrade
    混为一谈
- 处理要求:
  - 对所有 `D76` 近邻或类似 default-anchor 近邻，
    至少完成:
    - final `ablation/special_eval`
    - 并入 full long-horizon `anchor_route_analysis / selector / recap`
  - 只有当:
    - pairwise tradeoff
    和
    - route-level selected role
    两边都站得住，
    才能写成“更好的 default/minimax 候选”
### 170. 当 best `e_evt` floor 与 best `z_art` floor 分别落在不同 natural final anchors 上时，`e_evt_guard` 这类组合 guard 可能直接不可行；不能把“guard infeasible”误读成某个候选无价值
- 现象:
  - `D79` 并入 full long-horizon route 后:
    - best `e_evt` floor = `D79`
    - best `z_art` floor = `D33`
  - route analysis 里的:
    - `e_evt_guard`
    会同时要求:
      - `min_zero_e_evt_delta_target_loss_total = best_e_evt_floor`
      - `min_zero_z_art_delta_target_loss_total = minimax_z_art_floor`
  - 结果 eligible anchors 直接为空
- 风险:
  - 如果把这种:
    - guard infeasible
    直接读成:
    - `D79` 没有信息量
    或
    - `D79` 完全失败
  - 就会忽略它其实已经拿到了:
    - special leader
    - `e_evt` leader
  - 只是当前没有任何单一 anchor
    能同时满足两条 floor
- 处理要求:
  - 看到 route guard infeasible 时，
    先拆开确认:
    - best `e_evt` floor 属于谁
    - best `z_art` floor 属于谁
  - 再判断问题是:
    - 候选本身无价值
    还是
    - 多目标 guard 过于刚性、当前不存在单点可行解
### 171. 在 `D79` 这类已经通过“提高 late teacher 总权重”拿到 `special + e_evt` 收益的骨架上，不要默认以为再小幅提高 `teacher_consistency.z_art_weight` 就能补齐 `z_art`
- 现象:
  - `D80` 唯一改动是:
    - late `z_art_weight: 1.0 -> 1.25`
  - 结果相对 `D79` 反而变成:
    - validation `+0.002092`
    - special `+0.001664`
    - `e_evt` `-0.039331`
    - `z_art` `-0.027894`
- 风险:
  - 如果把当前缺口简化成:
    - “只差一点 `z_art` 蒸馏强度”
  - 就会在 `z_art_weight` 这条轴上继续做低信息量微调
  - 但真实结果说明:
    - 这条轴至少在当前 `D79` 骨架下不是有效补法
- 处理要求:
  - 当一个候选已经证明:
    - 提高 late teacher 总权重有效
    - 但 `z_art` 仍落后
  - 不要默认优先继续调:
    - `teacher_consistency.z_art_weight`
  - 若首个轻量 `z_art_weight` probe 已被同骨架候选完整支配，
    应直接转向:
    - 非 teacher-per-head 权重类的 `z_art` restoration 机制
### 172. 在 `D79` 这类 long-horizon late micro-pause 骨架上，即使把 `z_art_influence_aux` 显式 retarget 到当前主战场 pool，也不能默认认为它会补回 `z_art`
- 现象:
  - `D81` 相对 `D79` 的唯一主改动是:
    - `z_art_influence_aux.pool_memberships`
      从:
      - `challenge_proxy_core`
      改到:
      - `micro_pause_none_singleton_strict`
    - 并把 schedule 改成:
      - `step11-25` late ramp
  - 训练后段日志里:
    - `loss_z_art_influence_aux`
      持续非零，
      说明机制确实命中了 late pool
  - 但 final 结果相对 `D79` 仍变成:
    - validation `-0.000869`
    - special `+0.003318`
    - `e_evt` `-0.165104`
    - `z_art` `-0.046887`
- 风险:
  - 如果看到当前缺口主要剩 `z_art`，
    就把问题简化成:
    - “把 explicit influence floor 对准当前 late pool 就行”
  - 会继续在 `z_art_influence_aux` 的 coverage / late retarget 上做低信息量扫参
  - 但 `D81` 已说明:
    - 即使机制真实激活，
      这条轴也不足以改写当前 `D79` tradeoff
- 处理要求:
  - 当一个 explicit-control / influence 类 auxiliary
    已经在日志中证明确实生效，
    但 final 仍被父骨架压制时，
    不要再把后续优先级继续给:
    - 同类 late-pool retarget
    - 或其 coverage 近邻 sweep
  - 应直接转向:
    - 更外层的 `z_art` restoration 机制
### 173. 不要只按 `D79 / D80 / D81` 目录名去找最新产物；这几轮训练主产物在 shared `offline_mvp` 目录，评估目录也主要按 `exp035 / exp036 / exp037` 命名
- 现象:
  - `D79 / D80 / D81` 的训练主产物没有像部分旧实验那样落到:
    - `reports/training/offline_mvp_d79_*`
    - `reports/training/offline_mvp_d80_*`
    - `reports/training/offline_mvp_d81_*`
  - 而是统一落在:
    - `reports/training/offline_mvp/`
    - 其中 experiment id 分别是:
      - `EXP-20260316-035` = `D79`
      - `EXP-20260316-036` = `D80`
      - `EXP-20260316-037` = `D81`
  - 对应评估目录也主要按:
    - `offline_mvp_ablations_exp035/036/037`
    - `offline_mvp_special_eval_exp035/036/037`
    - `offline_mvp_checkpoint_series_exp035/036/037`
    - `offline_mvp_special_eval_series_exp035/036/037`
    命名，而不是把 `d79 / d80 / d81` 直接写进目录名
- 风险:
  - 如果恢复上下文时只按:
    - `Get-ChildItem reports/training | Select-String d79`
    - 或只找 `reports/eval/*d79*`
  - 很容易误判成:
    - `D79-D81` 没有完整落盘
    - 或训练/评估链路中断
- 处理要求:
  - 检索最新实验时优先同时用两套键:
    - `D` 编号
    - `EXP-YYYYMMDD-xxx` experiment id
  - 对 `D79-D81` 这一段，默认直接检查:
    - `reports/training/offline_mvp/`
    - `reports/training/offline_mvp/checkpoints/`
    - `reports/eval/offline_mvp_*exp035`
    - `reports/eval/offline_mvp_*exp036`
    - `reports/eval/offline_mvp_*exp037`
  - 再结合:
    - `docs/128`
    - `docs/129`
    - `docs/130`
    做编号与 experiment id 的映射
### 174. 在 `D79` 这类 late singleton sparse 骨架上，把 singleton targeted sampling 直接拉到 full-priority，会把这条线继续推成 special-only 近邻，但仍不会自然补回 `z_art`
- 现象:
  - `D82` 相对 `D79` 的唯一改动是:
    - late `targeted_sampling.priority_ratio`
      `0.75 -> 1.0`
  - final 结果相对 `D79` 变成:
    - validation `+0.010498`
    - special `-0.013765`
    - `e_evt` `-0.043837`
    - `z_art` `-0.03322`
  - full long-horizon route 里:
    - special leader 从 `D79` 切到 `D82`
    - 但 `zero_e_evt` 仍是 `D79`
    - `zero_z_art` 仍是 `D33`
    - default/minimax 仍是 `D33`
- 风险:
  - 如果把当前缺口继续简化成:
    - “singleton cohort 曝光再强一点，`z_art` 就会自己回来”
  - 就会沿:
    - full-priority
    - stronger-exposure
    - 或更激进 late batch 偏置
    继续做低信息量 sweep
  - 但 `D82` 已说明:
    - 曝光更强确实会继续推 low special
    - 却不会把 `z_art` 一起带回来
- 处理要求:
  - 当一个候选已经证明:
    - 强化当前 proxy cohort 的 exposure 会继续改善 special
    - 但 `z_art` 与 validation 同时回吐
  - 不要再把后续优先级继续给:
    - late `priority_ratio` 上调
    - full-priority singleton exposure
    - 同类 stronger-exposure 近邻 sweep
  - 应直接转向:
    - 新 proxy principle
    - 或真正直接面向 `z_art` 的更外层 supervision 机制
### 175. 不要把 model-level eval 的输出目录只命名成 `..._exp038` 这类裸三位序号；跨日期实验会和历史同序号目录碰撞
- 现象:
  - `D82 = EXP-20260316-038`
  - 但仓库里已存在更早日期的:
    - `EXP-20260315-038`
  - 当前几类 eval 默认输出目录只写:
    - `offline_mvp_ablations_exp038`
    - `offline_mvp_special_eval_exp038`
    - `offline_mvp_checkpoint_series_exp038`
    - `offline_mvp_special_eval_series_exp038`
  - 结果会出现:
    - 新实验直接覆写旧实验同序号目录
    - 或把旧目录里不在本轮 `--steps` 里的 checkpoint 子目录删成缺口
- 风险:
  - 恢复上下文时会误把不同日期、不同实验的产物混成同一份评估
  - 还会把历史已落盘的 eval 目录弄脏
- 处理要求:
  - 后续 model-level eval / series 输出目录，
    不要只用裸 `expNNN`
  - 至少要带上:
    - 日期
    - 或 `D` 编号 / slug
  - 更稳的写法应类似:
    - `offline_mvp_special_eval_d82_exp20260316_038`
    - `offline_mvp_checkpoint_series_d82_exp20260316_038`
### 176. 在 `D79` 这类 late singleton sparse 骨架上，即使把 late teacher source 拆成 `D33 -> D22` phase-specific handoff，也不要默认它能把前半段拉起的 `z_art` 留到 final
- 现象:
  - `D83` 相对 `D79` 的唯一主改动是:
    - late `teacher_consistency` 从单段 `D22`
    - 改成:
      - `step11-100 = D33 step10`
      - `step101-200 = D22 step30`
  - 训练日志明确显示:
    - `step100 effective_teacher_consistency.teacher_checkpoint_path = D33 step10`
    - `step101 ... = D22 step30`
  - 但 `D83` 的关键轨迹变成:
    - `step100 = 2.256422 / 0.190305 / 2.428461 / 0.530758`
    - `step150 = 2.174416 / 0.221924 / 2.197493 / 0.463976`
    - `step200 = 2.140033 / 0.23583 / 2.011104 / 0.42172`
  - final 相对 `D79` 反而变成:
    - validation `+0.001627`
    - special `+0.003836`
    - `e_evt` `-0.15919`
    - `z_art` `-0.047709`
- 风险:
  - 如果看到 `D78` 的 early-late `z_art` 更高、
    又看到 `D79` 的收尾更稳，
    就很容易把问题简化成:
    - “那把 source 在中途切一下就能两头兼得”
  - 然后继续沿:
    - handoff step 前后平移
    - `D33 -> D22` / `D22 -> D33` 近邻编排
    做低信息量 sweep
  - 但 `D83` 已说明:
    - handoff 本身不是没作用
    - 真问题是 `D22` 收尾会把前半段积累的大部分 control 再洗掉
- 处理要求:
  - 当 phase-specific source handoff 已经在日志里证明确实生效，
    但 final 仍被父骨架完整支配时，
    不要再把后续优先级继续给:
    - handoff 时点微调
    - 同一条 `D33 -> D22` late source 近邻 sweep
  - 应直接转向:
    - 不依赖 late teacher source handoff 的更外层 `z_art` restoration 机制
### 177. 不要从训练目录命名模式反推当前实验的 checkpoint 实际位置；一律以 `experiment metrics` 或 route 产物里的 `checkpoint_path` 为准
- 现象:
  - 当前 long-horizon 产物里已经同时存在两类 checkpoint 路径:
    - `D76 / D77` 这类实验使用专门子目录，例如:
      - `reports/training/offline_mvp_d76_singleton_sparse_d26_init_d22late_fusedhidden_boost_200step_exp032/checkpoints/...`
    - `D78 / D79 / D80 / D81 / D82 / D83` 这类实验则直接落在:
      - `reports/training/offline_mvp/checkpoints/...`
  - 也就是说，继续按某个 family 的旧命名规律去猜:
    - `reports/training/offline_mvp_dXX_.../checkpoints/...`
    并不可靠。
- 风险:
  - 恢复上下文或补跑评估时，
    如果直接凭目录名模式拼 checkpoint 路径，
    很容易:
    - 读错 checkpoint
    - 误以为产物缺失
    - 或把不同实验 family 的文件混起来
  - 这类错误尤其容易发生在:
    - route recap
    - final comparison
    - 手工补跑 `special_eval / ablation / checkpoint_series`
- 处理要求:
  - 任何需要 checkpoint 路径的操作，
    一律先读取:
    - `reports/experiments/<EXP...>.metrics.json`
    - 或 route/recap 产物中的 `checkpoint_path`
  - 不要再用“看起来像之前那一批实验的目录名”来猜真实文件位置。
### 178. 不要把包含 strict singleton 本体的并集 micro cohort 直接拿来做外层 supervision pool；先拆出差分 outer pool
- 现象:
  - `micro_singleton_anypunct_relaxed`
    确实比 `micro_pause_none_singleton_strict` 更大，
    但它会把 strict pool 自身也一起包含进去。
  - 当前正式统计里:
    - `micro_pause_none_singleton_strict = 8`
    - `micro_singleton_anypunct_relaxed = 13`
    - 其中真正“新增”的只有 `5` 条
- 风险:
  - 如果直接把并集 pool 拿去挂新的 outer supervision，
    就会让:
    - strict sparse proxy loss
    - 和新 outer loss
    在同一批 strict 样本上直接叠加
  - 这样很难判断:
    - 新机制到底是在补外层
    - 还是只是在把内层 strict 样本重新推向另一种目标
- 处理要求:
  - 当一个新候选 cohort 只是“strict pool 加上一圈邻域”时，
    不要直接用并集做新 supervision。
  - 先显式拆出:
    - 并集 pool
    - 差分 expansion pool
  - outer supervision 优先挂到差分 expansion pool 上。
### 179. 不要因为某个 loss config 里写了 `pool_memberships`，就默认它已经真实消费 sidecar gate；必须核对 loss 实现本身
- 现象:
  - 本轮在设计 `D84` 时，
    一开始按其他 aux 的经验，
    以为 `punctuation_profile_aux` 也已经支持:
    - `pool_memberships`
  - 但实际核对 `src/v5vc/offline_mvp/losses.py` 后发现:
    - 它原先只看 `texts`
    - 并没有读取 `target_special_supervision`
    - 也没有真正按 sidecar pool 过滤样本
- 风险:
  - 如果只看 config 字段名或 resolver，
    很容易把“配置里写得出来”误判成“训练时真的生效了”。
  - 这样会制造:
    - 假 gate
    - 假实验设计
    - 以及对负结果或正结果的错误解释
- 处理要求:
  - 当实验核心依赖某个 loss 的新 gate 行为时，
    先直接核对:
    - loss 函数签名
    - 调用点是否透传 sidecar
    - 函数体是否真正消费对应字段
  - 只有这三步都成立，
    才能把该机制当成真实实验变量。
### 180. 当一个新 quick-screen probe 只改写 matched20 shadow、但没改写 official quick-screen 时，不能把它直接写成 official anchor 刷新
- 现象:
  - `D84` 相对 `D75` 的 final 结果变成:
    - validation `+0.007910`
    - special `-0.010571`
    - `zero_e_evt` `+0.128880`
    - `zero_z_art` `+0.015925`
  - 并入 full official quick-screen route 后，
    正式角色仍保持:
    - validation = `D71`
    - special = `D69`
    - `zero_e_evt / zero_z_art = D33`
    - minimax = `D22`
  - 但并入 matched20 shadow 后，
    minimax 已从 `D75` 切到:
    - `D84`
- 风险:
  - 如果只看:
    - `D84 vs D75`
    - 或只看它在当前 family 内的局部改善
  - 很容易误写成:
    - “official quick-screen 已被新 outer punctuation 路线刷新”
  - 这样会把:
    - official quick-screen
    - matched20 shadow
    两套制度口径重新混写
- 处理要求:
  - 对所有新的 quick-screen probe，
    只要它看起来比当前 shadow representative 更强，
    都必须同时完成:
    - official quick-screen route-analysis / selector
    - matched20 shadow bundle
  - 只有两边都改写，
    才能写成 official anchor 刷新；
    若只改写 matched20 shadow，
    就只能写成:
    - shadow representative 前移
### 181. `update_experiment_metrics` 不能只按短 `experiment_id` 去找 `metrics.json`；`init-experiment` 可能落的是带 slug 的文件名
- 现象:
  - `D85 = EXP-20260316-041` 的正式训练已经完整写出了:
    - `train_plan`
    - checkpoints
    - step logs
  - 但 `reports/experiments/EXP-20260316-041-offline-mvp-d85-...metrics.json`
    一度仍停在:
    - `status = initialized`
  - 根因是训练结束后的 `update_experiment_metrics(...)`
    只查找:
    - `reports/experiments/EXP-20260316-041.metrics.json`
    而不会匹配实际由 `init-experiment` 生成的:
    - `reports/experiments/EXP-20260316-041-<slug>.metrics.json`
- 风险:
  - 会造成“训练已完成，但实验卡片仍像没跑”的假死状态。
  - 后续如果据此判断，会进一步引发:
    - 误以为训练没写回
    - 误以为 eval 产物和 experiment state 脱节
    - 补跑评估或 route 时引用错误状态
- 处理要求:
  - `experiment metrics` 回写时，先尝试:
    - 精确短名 `EXP-....metrics.json`
  - 若不存在，再尝试唯一匹配:
    - `EXP-...-*.metrics.json`
  - 若训练已完成但历史 metrics 未回写，
    可直接基于现有 `train_plan.json` 做一次回填，
    不需要整轮重训。
### 182. 不要把会回写同一个 `experiment metrics` 文件的 eval 命令并行跑；会出现 last-writer-wins 覆写
- 现象:
  - `D86 = EXP-20260316-042` 这一轮里，
    我把以下四类评估并行跑到了同一个 metrics 文件上:
    - `evaluate-offline-mvp-ablations`
    - `evaluate-offline-mvp-special-eval`
    - `evaluate-offline-mvp-checkpoint-series`
    - `evaluate-offline-mvp-special-eval-series`
  - 每个命令内部都会:
    - 先读 `reports/experiments/<EXP...>.metrics.json`
    - 再回写自己新增的字段
  - 结果是后写入的进程把先写入进程的新增字段覆盖掉，
    出现:
    - `checkpoint_series_eval` 在
    - 但 `special_eval_series` 丢失
  - 随后直接触发:
    - `analyze-offline-mvp-checkpoint-selection`
    - `analyze-offline-mvp-checkpoint-gates`
    报错缺少 `special_eval_series or checkpoint_series_eval`
- 风险:
  - 会把实验状态伪装成“某类 eval 没跑”或“checkpoint review 数据不全”。
  - 更糟的是，
    因为各 eval 自身的输出目录已经落盘，
    很容易误判成:
    - 分析命令有 bug
    - 或 metrics 文件本身损坏
- 处理要求:
  - 只要多个 eval 命令会回写同一个 `experiment metrics` 文件，
    就必须顺序执行，
    不能并行。
  - 若已经并行误跑，
    不要重训；
    直接顺序补跑缺失字段对应的 eval 即可。
### 183. 对只有 `step50/100/150/200` 的 long-horizon 实验，做 checkpoint-selection / gate replay 时不能沿用默认 `late_step_ratio = 0.8`
- 现象:
  - `analyze-offline-mvp-checkpoint-selection`
    与 `analyze-offline-mvp-checkpoint-gates`
    默认使用:
    - `late_step_ratio = 0.8`
  - 对只有:
    - `step50 / step100 / step150 / step200`
    的实验，
    这会把 late window 缩成只剩:
    - `step200`
  - 本轮 `D86` 一开始就因此被误分析成:
    - “late-stop 没有候选，所有 gate 都选 final”
  - 但改回:
    - `late_step_ratio = 0.75`
    之后，
    真实 late window 才变成:
    - `step150 + step200`
    并正确恢复出:
    - `D86 step150`
- 风险:
  - 会把真实存在的 `step150` late-stop option
    误判成不存在。
  - 连带会把:
    - synthetic anchor 是否值得物化
    - checkpoint-option 是否能改写 route 角色
    一起看错。
- 处理要求:
  - 只要当前实验的 checkpoint 粒度是:
    - `50 / 100 / 150 / 200`
  - 做 late-stop 复核时一律显式传:
    - `--late-step-ratio 0.75`
  - 不要偷用默认值，
    也不要把输出目录名写成 `late075`
    却实际跑了默认 `0.8`。
### 184. 旧实验“看起来 checkpoint review 产物齐了”不等于 `experiment metrics` 真的已经具备统一复核条件
- 现象:
  - 本轮对 `D76-D87` 旧 `200-step` 实验逐个检查后发现：
    - `checkpoint_series_eval` 都已存在
    - 但 `special_eval_series` 全部缺失
  - 这导致:
    - 单看各自已有的 `reports/eval/...` 目录，
      很像“历史评估已经做完了”
    - 但一旦拿它们去跑联合:
      - `checkpoint_selection`
      - `checkpoint_gate_replay`
      就会统一报:
      - missing `special_eval_series or checkpoint_series_eval`
- 风险:
  - 会误以为:
    - 某个单实验损坏
    - 或分析命令有 bug
  - 实际上更常见的是:
    - 历史 metrics 只补了一半字段
    - 还没有进入“可统一 checkpoint review”的状态
- 处理要求:
  - 对任何准备纳入联合 checkpoint review 的历史实验，
    先直接检查 `experiment metrics` 里是否同时存在:
    - `checkpoint_series_eval`
    - `special_eval_series`
  - 若缺其中之一，
    不要重训；
    直接顺序补跑对应 eval。
  - 不要仅凭 `reports/eval/` 下“目录看起来都在”
    就判断该实验已经完成统一复核准备。
### 185. Stage3 `streaming_student` scaffold 阶段必须继续保持与 `offline_mvp` 的帧级合同对齐，且不能提前打开 `r_res`
- 现象:
  - 当前 Stage3 scaffold 已正式落地，
    但它的下一步仍是:
    - 建 eval bridge
    - 定 calibration asset
    - 再进入真实训练
  - 本轮模板已固定:
    - `frame_length = 400`
    - `hop_length = 160`
    - `model.r_res_enabled = false`
- 风险:
  - 如果在 eval bridge 与 contract 还没稳定前，
    就先改动 frame contract
    或提前打开 `r_res`，
    后续会同时失去:
    - 与 `offline_mvp` 的帧级可比性
    - 对“主控制链是否独立成立”的阶段边界
  - 这样很容易把:
    - 新骨架接线问题
    - `r_res` 结构风险
    混成一类问题
- 处理要求:
  - Stage3 scaffold 阶段继续固定:
    - `frame_length / hop_length` 与 `offline_mvp` 一致
    - `r_res_enabled = false`
  - 等:
    - eval bridge
    - calibration asset
    - 基础 Student supervision
    都稳定后，
    再决定是否改变 frame contract 或打开 `r_res`
### 186. Stage3 当前只能复用 `offline_mvp` 的数据拆分与 metrics 解析能力，不能把这理解成“真实 Student 训练可以直接复用旧训练循环”
- 现象:
  - 当前 `streaming_student/plan_entry.py` 只复用了:
    - `load_training_split(...)`
    - `resolve_experiment_metrics_path(...)`
  - 它没有复用:
    - `offline_mvp` 的真实训练 step
    - loss 定义
    - teacher consistency runtime
- 风险:
  - 如果因为两边都能读同一份 split，
    就直接把 Stage3 塞进旧训练循环，
    很容易得到:
    - 看起来能跑
    - 实际监督目标和 contract 全不对齐
    的假进展
- 处理要求:
  - 当前只把:
    - split 读取
    - experiment metrics 定位
    视为可安全复用的基础设施
  - 等 Stage3 的:
    - teacher label 数据格式
    - calibration asset
    - eval bridge
    明确后，
    再单独设计真实 Student 训练入口
### 187. Stage3 校准子集选择不能只追求结构覆盖；必须同时满足最小有效时长
- 现象:
  - 本轮第一版 calibration subset selector
    过度偏向:
    - 新标签覆盖
    - 特殊池覆盖
  - 结果虽然结构很多样，
    但只选出了:
    - `12` 条
    - `29.189887 sec`
  - 这明显低于设计稿期望的:
    - `1-3` 分钟校准语料
- 风险:
  - 如果只看“标签覆盖很多”，
    会误以为 calibration subset 已经够用。
  - 但真实问题是:
    - 时长不够
    - 稳态统计不够
    - 根本不足以支撑后续校准估计
- 处理要求:
  - calibration subset selector 需要两阶段目标:
    - 先做必要覆盖
    - 再补足最小有效时长
  - 后续汇报 calibration subset 时，
    必须同时写:
    - 覆盖摘要
    - 总时长
  - 不能只汇报其中一项
### 188. Stage3 eval bridge 当前使用 placeholder conditioning；不能把其摘要当作真实校准效果
- 现象:
  - 当前 `build-streaming-student-eval-bridge`
    默认读取的是:
    - `streaming_student_calibration_asset_template.json`
  - 其中:
    - `s_spk_target`
    - `s_geom_target`
    仍是 zero vector
    - `alpha = 1.0`
  - 也就是说，
    当前 bridge 只是用 placeholder conditioning
    检查输出汇总链路
- 风险:
  - 如果把当前 bridge 的:
    - `target_validation`
    - `target_special_eval`
    delta
    直接解释成“校准已生效”
  - 就会把:
    - plumbing check
    和
    - 真实校准质量
    混成一件事
- 处理要求:
  - 在真实 calibration asset 出来前，
    当前 bridge 结论统一解释成:
    - contract / summary wiring 已打通
  - 不解释成:
    - 目标说话人校准已经有效
### 189. Stage3 heuristic calibration estimate 的 `alpha` 很容易命中边界值；不能把边界命中本身当成强结论
- 现象:
  - 当前 `waveform_feature_bootstrap_v1`
    在 `11` 条、`135.964922 sec` calibration subset 上，
    估计出的:
    - `alpha = 1.15`
  - 该值正好命中当前建议上界
- 风险:
  - 如果把这个数直接读成:
    - “目标说话人确定需要上界强度的 warp”
  - 就会把:
    - 启发式映射的饱和
    误读成
    - 真实 calibration objective 的明确结论
- 处理要求:
  - 当前阶段把 `alpha = 1.15` 解释为:
    - heuristic bootstrap prior
    - 且当前映射有上界饱和倾向
  - 不把它直接升级成正式 calibration 参数结论
### 190. 只要会重写同一个 managed 输出目录，就不要把“生成命令”和“读取结果文件”并行执行；否则极易读到旧产物
- 现象:
  - 本轮 `build-streaming-student-eval-bridge`
    与结果文件读取一度被并行触发，
    导致我先读到了上一轮 bridge 的旧 markdown，
    一度误判成 estimated asset 没有被消费
- 风险:
  - 会把:
    - 旧产物缓存
    - 真正的代码逻辑错误
    混在一起
  - 进而误判:
    - 资产加载失败
    - 或 bridge 没切到 estimated asset
- 处理要求:
  - 只要命令会覆盖 managed 输出目录，
    生成和读取必须顺序执行
  - 先跑命令，
    再读产物；
    不要并行
### 191. Stage3 teacher-label 是 formal offline MVP anchor 导出的 pseudo labels；不能把它们升级成“真实监督真值”
- 现象:
  - 当前 `build-streaming-student-teacher-labels`
    默认从:
    - `reports/eval/offline_mvp_route_handoff_round1_1_longwindow_final/route_handoff.json`
  - 解析 teacher anchor，
    实际落到:
    - `EXP-20260316-043 ... D87 ... step200`
  - 导出的 `hidden / fused_hidden / z_art / event / acoustic / frame_confidence`
    都是旧 Teacher 的推断结果
- 风险:
  - 如果后续把这些资产直接当成:
    - 真实物理标签
    - 或不可质疑的最终监督
  - 就会把:
    - Teacher 偏差
    - route 选择偏差
    - confidence 估计偏差
    一起固化进 Stage3
- 处理要求:
  - 当前统一把 teacher-label 解释成:
    - pseudo-label training assets
  - 后续 Student loss、过滤、加权设计，
    都要保留“Teacher 可能有偏”的假设
  - 不把导出产物写成:
    - ground truth
    - 或正式目标说话人物理真值
### 192. `build-streaming-student-teacher-labels` 会重建 managed 输出目录；不要把人工文件混放进去
- 现象:
  - 当前 teacher-label 导出入口在开始时会:
    - `reset_managed_directory(data_output_dir)`
    - `reset_managed_directory(report_output_dir)`
  - 也就是会先删后建:
    - `data_prep/round1_1/streaming_student_teacher_labels`
    - `reports/data/streaming_student_teacher_labels`
- 风险:
  - 如果把:
    - 手工补充说明
    - 临时分析文件
    - 额外人工标注
    混放在这些目录里，
    下次重跑时会被整批覆盖清空
- 处理要求:
  - teacher-label 命令管理的目录
    只放它自己生成的正式产物
  - 人工分析或临时文件放到:
    - 独立报告目录
    - 或其他非 managed 位置
  - 任何需要长期保留的补充资产，
    都不要直接丢进该命令的 managed 输出目录
### 193. Stage3 一旦开始消费 teacher labels，就不能随手对训练音频做截断；否则 frame 对齐会直接失真
- 现象:
  - 当前 `prepare-streaming-student-training-data`
    dry-run 已确认:
    - teacher frame count
    - Student 前端 frame count
    在三类 slice 上逐样本完全一致
  - 这个前提依赖的是:
    - 读取完整音频
    - `frame_length = 400`
    - `hop_length = 160`
    与 teacher 导出时一致
- 风险:
  - 如果后续为了省时，
    在 Stage3 训练入口里直接加:
    - `max_duration_sec`
    - 任意 waveform 截断
  - 又不重导 teacher labels，
    就会马上出现:
    - batch 能拼
    - 但监督帧数和模型帧数不再对应
    的假运行
- 处理要求:
  - 只要训练还消费当前这套 teacher-label 资产，
    默认读取完整音频
  - 若必须改音频长度策略，
    要么同步重导 teacher labels，
    要么重新定义对应的 frame 对齐合同
### 194. Stage3 当前的 frontend proxy losses 只是 bootstrap supervision；不能把它们误写成最终语义定义
- 现象:
  - 当前最小 supervision dry-run
    除了 `z_art / event / event_prior`
    这类直接 teacher 对齐项外，
    还引入了:
    - `energy -> teacher_acoustic[...,0]`
    - `vuv_logits -> teacher_event_probs[...,3]`
    - `aperiodicity -> teacher_event_probs[...,2]`
    这类 proxy 监督
- 风险:
  - 如果把这些 proxy 映射直接当成:
    - 设计稿最终语义
    - 或正式物理定义
  - 后续就会过早锁死:
    - 前端头的解释
    - 以及 loss contract
- 处理要求:
  - 当前统一把这些项解释成:
    - minimal bootstrap supervision
  - 后续若要长期保留，
    必须再核对:
    - 语义合理性
    - 与设计稿目标的一致性
  - 在此之前，
    不把这些 proxy 名称升级成正式理论结论
### 195. Stage3 单步训练 scaffold 的 loss 和 grad_norm 只能说明 plumbing 通了；不能把它当作训练稳定性结论
- 现象:
  - 当前 `run-streaming-student-training-step`
    已成功完成:
    - forward
    - loss
    - backward
    - optimizer
    - checkpoint
  - 但本轮只有:
    - `1` 个 train step
    - `1` 个 validation step
  - 当前还观测到:
    - `grad_norm = 64.267143`
- 风险:
  - 如果把这次单步结果直接解释成:
    - learning rate 已合理
    - loss 权重已稳定
    - Stage3 训练已经基本成型
  - 后续很容易在多 step 时才暴露:
    - 梯度不稳
    - proxy loss 失衡
    - confidence weighting 行为异常
- 处理要求:
  - 当前只把单步训练 scaffold 解释成:
    - 训练闭环 wiring 已打通
  - 不解释成:
    - 已经得到稳定训练策略
  - 下一步必须通过多 step 训练循环
    再观察:
    - loss 轨迹
    - grad_norm
    - validation 变化
### 196. Stage3 最小多 step 循环里的 validation 目前只是 sampled batches；不能把它当成完整 validation slice 指标
- 现象:
  - 当前 `run-streaming-student-training-loop`
    默认只在每次 validation 时:
    - 采样 `validation_batches`
    - 对这些 batch 求平均
  - 本轮 `streaming_student_stage_loop_scaffold_v1`
    使用的是:
    - `validation_batches = 2`
    - `validation_batch_size = 3`
- 风险:
  - 如果直接把当前:
    - `validation loss_total 13.13162 -> 9.656614`
    读成完整 validation slice 的稳定改善，
    很容易高估当前训练策略的可靠性
- 处理要求:
  - 当前统一把这类 validation
    解释成:
    - sampled validation trajectory
  - 不是:
    - full-slice validation result
  - 若后续要做更正式判断，
    必须先补更完整的 validation 口径
### 197. 当前 Stage3 最小多 step 循环按 split 顺序顺推取 batch；短程轨迹对记录顺序敏感
- 现象:
  - 当前训练 loop 的 batch 选择
    是按 `target_train` 顺序
    以固定 batch size 顺推
  - 本轮 `4 step` 依次消耗的是:
    - `archive_firefly_1 ~ 20`
    这一小段前缀样本
- 风险:
  - 如果把当前短程 loss 下降
    直接解释成“模型已经稳定收敛”，
    会忽略:
    - 样本顺序
    - 局部样本难度
    对短程轨迹的强影响
- 处理要求:
  - 当前把这条短程曲线
    解释成:
    - training loop plumbing 已可观察
  - 不把它直接升级成:
    - 与未来真实 sampler 等价的训练结论
  - 后续若进入更正式短程训练，
    应明确 sampler 策略
### 198. Stage3 checkpoint 若不保存训练元数据，后验 eval 很容易把 `teacher_confidence` 用法读错
- 现象:
  - 第一版 Stage3 checkpoint
    只保存了:
    - `config`
    - `model_state_dict`
    - 若干 step 指标
  - 没有明确保存:
    - `training.use_teacher_confidence`
    - `training.loss_weights`
    - `config_path`
  - 结果 fuller checkpoint eval
    一度把 `no_conf` checkpoint
    错按 `teacher_confidence = true`
    来评估
- 风险:
  - 会把:
    - 训练时真实策略
    - 后验评估时假定策略
    混成同一件事
  - 导致对照结论失真
- 处理要求:
  - 之后所有 Stage3 checkpoint
    都必须随 payload 一起保存:
    - 训练超参摘要
    - `use_teacher_confidence`
    - `loss_weights`
    - `config_path`
  - 后验 eval 优先读取 checkpoint 自带训练元数据，
    不要默猜默认值
### 199. full-slice eval 不能沿用会回绕的训练取 batch 逻辑；否则末尾样本会被重复计入
- 现象:
  - Stage3 第一版 fuller checkpoint eval
    直接复用了:
    - `select_streaming_student_batch_records`
  - 该逻辑服务于训练，
    会在 batch 跨末尾时回绕
  - 导致 `target_special_eval = 8`、
    `batch_size = 6` 时，
    第二个 batch 把前面的样本又取了一遍
- 风险:
  - 会把:
    - full-slice evaluation
    误做成
    - 带重复样本的 pseudo-full eval
  - 使 special slice 指标偏移
- 处理要求:
  - full-slice eval 必须使用:
    - 不回绕
    - 不重复
    的连续切片逻辑
  - 训练采样 helper
    与 fuller eval helper
    必须分开
### 200. 只要后续命令依赖“本轮刚生成的新 checkpoint / 新 summary”，就不要和生成命令并行触发
- 现象:
  - 本轮 `12 step` baseline run 时，
    我一度把:
    - `run-streaming-student-training-loop`
    和
    - `evaluate-streaming-student-checkpoint --checkpoint ...step12.pt`
    放在同一批并行执行
  - 结果 eval 在 `step12.pt`
    还没落盘时就先启动，
    直接报 `FileNotFoundError`
- 风险:
  - 容易把:
    - 调度顺序错误
    误判成:
    - 训练失败
    - checkpoint 没写出
- 处理要求:
  - 只要后续命令依赖本轮刚生成的新产物，
    就必须顺序执行:
    - 先生成
    - 再读取/评估
  - 不要把这类强依赖链路并行化
### 201. sampled validation 选出的“best checkpoint”不能直接升级成正式默认选点；必须先过 fuller ranking
- 现象:
  - 当前训练 loop summary
    已经会基于 sampled validation
    给出一个 `best_checkpoint`
  - 但 sampled validation
    仍只覆盖少量 batch
  - 本轮真正用于 baseline12 默认选点的，
    已经改成:
    - fuller checkpoint selection
    - 即 `step4 / step8 / step12` 全量比较
- 风险:
  - 如果后续直接把 loop summary 里的:
    - `best_checkpoint`
    当成正式默认点，
    会把:
    - sampled validation 的便利性
    误当成
    - fuller checkpoint ranking 的可靠性
- 处理要求:
  - 当前 sampled `best_checkpoint`
    只解释成:
    - loop 内部快速参考
  - 真正要固定正式默认 checkpoint 时，
    必须再跑:
    - `select-streaming-student-best-checkpoint`
    这类 fuller ranking
### 202. 只要 loss 权重不同，就不能直接横向比较 `loss_total`；必须回到统一参考权重或看未加权分项
- 现象:
  - 本轮开始加入
    - `--loss-weight-overrides`
    后，
    `eventprior025`
    的 `loss_total`
    明显低于 baseline
  - 但这其中既包含:
    - 模型预测变化
  - 也包含:
    - `teacher_event_prior`
      权重从 `0.5` 降到 `0.25`
      带来的目标缩放
- 风险:
  - 如果直接把不同权重配置的
    - `loss_total`
    当成同一标尺，
    很容易把:
    - 目标函数变小
    误判成
    - 模型本身更好
- 处理要求:
  - 以后只要比较不同 loss 权重配置，
    必须优先使用:
    - `loss_total_default_reference`
    - 或各项未加权 component loss
  - checkpoint / summary
    还必须保存:
    - `loss_weight_overrides_path`
    以免后验比较时不知道
    当时到底改了哪组权重
### 203. Stage3 loop 若切到 `validation_mode = full`，其 `target_validation` 数值应与外部 checkpoint eval 对齐；若不对齐，优先怀疑 loop 内 validation 回归
- 现象:
  - 本轮已把
    `run-streaming-student-training-loop`
    扩成支持:
    - `--validation-mode full`
  - 在
    `streaming_student_stage_loop_baseline12_fullval_v1`
    上，
    loop 内 `step12`
    的:
    - `target_validation.loss_total = 8.134648`
  - 与外部
    `evaluate-streaming-student-checkpoint`
    对同一 checkpoint 的:
    - `target_validation.loss_total = 8.134648`
    完全一致
- 风险:
  - 如果后续有人改了 loop 内 validation helper，
    导致 full 模式重新出现:
    - 回绕
    - 重复样本
    - mask / weight 口径不一致
  - 很容易让人误以为:
    - 模型训练变了
  - 实际上只是:
    - validation 实现回归了
- 处理要求:
  - 之后凡是改 Stage3 loop 的 full validation，
    都应至少复核一次:
    - loop summary 里的 `target_validation`
    - 与外部 checkpoint eval
    是否一致
  - 若不一致，
    优先排查:
    - batch slicing
    - frame weighting
    - metric averaging
    的实现差异，
    不要先改模型结论
### 204. 把 `teacher_energy_proxy` 权重调轻后，run 自己的 `loss_total` 可能明显更好看；若统一参考指标没同步变好，就不能把它当成优于 baseline
- 现象:
  - 在
    `streaming_student_stage_loop_energyproxy015_fullval_v1`
    中，
    把:
    - `teacher_energy_proxy`
      从 `0.25`
      降到 `0.15`
  - run 自己的:
    - `loss_total`
    - loop 内 full validation `loss_total`
    都明显低于 baseline
  - 但把结果换回
    - `loss_total_default_reference`
    后，
    `step12`
    的:
    - `target_validation = 8.17354`
    - `target_special_eval = 8.164811`
    都略差于 baseline12 fullval 的:
    - `8.134648`
    - `8.11794`
- 风险:
  - 如果只看覆盖后权重下的
    - `loss_total`
  - 会误把:
    - 目标函数本身更轻
  - 当成:
    - 模型预测更好
  - 尤其 `teacher_energy_proxy`
    本身 raw loss mass
    不小，
    更容易放大这种错觉
- 处理要求:
  - 以后凡是动
    - `teacher_energy_proxy`
    这类 proxy 项权重，
    正式比较时都必须回到:
    - `loss_total_default_reference`
    - baseline 同口径 checkpoint eval
  - 若统一参考指标没有同步提升，
    只能记为:
    - 有效对照
    - 未胜出候选
  - 不要因为 run 内 `loss_total`
    更低，
    就直接升级默认基线
### 205. 若 `eventprior025` 在更长 horizon 下仍是 validation 略差、special 略好，就应继续按 validation-first 保留 baseline，而不是把“几乎打平”误判成完成反超
- 现象:
  - 在
    `24-step full validation`
    下:
    - baseline24
      `target_validation.loss_total_default_reference = 7.292622`
    - eventprior025 fullval24
      `target_validation.loss_total_default_reference = 7.30326`
  - 同时:
    - baseline24
      `target_special_eval.loss_total_default_reference = 7.804316`
    - eventprior025 fullval24
      `target_special_eval.loss_total_default_reference = 7.803009`
  - 也就是:
    - validation
      `eventprior025`
      仍略差
    - special
      `eventprior025`
      仍略好
  - 而且这种关系
    与 `12-step`
    结果一致，
    只是整体数值一起下降了
- 风险:
  - 如果只看到:
    - special 稍微更低
  - 或只看到:
    - `eventprior025`
      的有效 `loss_total`
      更小
  - 容易把:
    - 接近持平
  - 误读成:
    - 已经完成反超
  - 进而过早切掉默认 baseline
- 处理要求:
  - 只要当前正式规则
    还是:
    - validation-first
    - special 作次级排序
  - 那么像这类:
    - validation 落后约 `0.01`
    - special 领先约 `0.001`
    的结果，
    仍应保留:
    - baseline 为默认主线
    - `eventprior025`
      为近似平手候选
  - 只有当 `eventprior025`
    在统一参考指标下
    明确翻过 validation，
    才考虑升级默认基线
### 206. 不要因为 `eventprior025` 与 baseline 连续接近，就默认它迟早一定会反超；如果更长 horizon 仍是同向略差，应及时停止在近邻权重上反复消耗
- 现象:
  - 到 `48-step full validation`
    为止，
    `eventprior025`
    仍然没有超过 baseline:
    - baseline48 validation:
      `7.141462`
    - eventprior025 fullval48 validation:
      `7.152429`
    - baseline48 special:
      `7.572382`
    - eventprior025 fullval48 special:
      `7.573954`
  - 而且它与 baseline
    在 `24 -> 48`
    的改善幅度也几乎一致
- 风险:
  - 如果只因为
    `eventprior025`
    很接近，
    就继续无限追加:
    - 72-step
    - 96-step
    - 更多近邻 sweep
  - 很容易把资源都消耗在
    小差值权重比较上，
    却迟迟不推进:
    - 试听导出
    - 更接近成品链路的门槛
- 处理要求:
  - 当某个 override
    已经在多个 horizon
    上稳定表现为:
    - 高接近
    - 但不反超
  - 就应把它降为:
    - 影子候选
  - 默认主线继续沿当前 best checkpoint
    推进
  - 后续资源优先投向:
    - 更长主线稳定性
    - 或试听/导出链路
### 207. 即使 Stage3 已能导出 `input / teacher_proxy / student_proxy`，也不要把它误读成最终用户试听；它本质上仍是结构代理
- 现象:
  - 本轮新增了
    - `export-streaming-student-proxy-audio`
  - 当前可从 Stage3 checkpoint
    正式导出:
    - `input.wav`
    - `teacher_proxy.wav`
    - `student_proxy.wav`
  - 其中:
    - `teacher_proxy`
      来自 teacher `acoustic`
      标签重建
    - `student_proxy`
      则来自 Stage3 预测头
      经保守映射后的结构代理重建
- 风险:
  - 如果用户看到:
    - wav 已经能导出
  - 很容易误以为:
    - Stage3 已经有最终成品试听
    - teacher_proxy 可以当 ground truth audio
    - student_proxy 可以直接拿来判断最终音质
  - 这些都不成立
- 处理要求:
  - 以后凡是引用 Stage3 proxy bundle，
    都必须先明确:
    - 它只适合粗结构审核
    - 适合看 `student vs teacher`
      的结构 gap
    - 不适合下最终音质、音色、
      speaker identity 结论
  - 当前最合理的听法是:
    - `input`
    - `teacher_proxy`
    - `student_proxy`
    三者相对比较，
    而不是单独听 `student_proxy`
    判“好不好听”
### 208. 工作区里已经出现独立 GUI 脚本，不等于人工听审工作流已经正式接好
- 现象:
  - 当前工作区新增了:
    - `src/v5vc/audio_audit_gui.py`
  - 该脚本本身可解析 `--help`
  - 也能读取当前 `proxy_audio_export.json`
    的 bundle 格式
  - 但目前没有接到:
    - `manage.py`
    - `src/v5vc/cli.py`
    的正式命令入口
  - 也没有发现正式 GUI 导出产物目录:
    - `reports/audio/audio_audit_gui_exports/`
- 风险:
  - 如果只看到仓库里“已经有 GUI 文件”，
    很容易误以为:
    - 听审流程已经正式集成
    - 交接已经完整
    - 下一位接手者不需要再补入口和文档
  - 实际上这会把:
    - 独立脚本 scaffold
    和
    - 正式可接手工作流
    混为一谈
- 处理要求:
  - 后续若继续使用该 GUI，
    至少要补齐:
    - 正式入口
    - 使用文档
    - 一次真实 review 导出样例
  - 在此之前，
    文档口径应统一解释为:
    - GUI scaffold 已存在
    - 但人工听审工作流尚未正式闭环
### 209. GUI 若在 filter 后不重算当前索引，记录列表与右侧详情会发生错位，严重时会越界
- 现象:
  - `audio_audit_gui.py`
    初版在刷新过滤列表时，
    会重新选择一个可见项
  - 但没有同步回写
    `current_index`
  - 结果是:
    - 左侧选中的记录
    - 与右侧实际展示的记录
      可能不一致
    - filter 收窄得更厉害时，
      还可能把右侧详情推进到越界状态
- 风险:
  - 在人工听审时，
    这会直接污染 review 记录
  - 用户以为自己在给 A 样本打分，
    实际保存的却可能是 B 样本
- 处理要求:
  - 每次 filter 变化后，
    都必须:
    - 先保存当前记录状态
    - 再刷新列表
    - 同步重算 `current_index`
    - 再刷新右侧详情
### 210. GUI 如果不能仅凭 progress 文件恢复上次 bundle 列表，真实听审会话就会变成一次性工具
- 现象:
  - `audio_audit_gui.py`
    初版即使已有:
    - `audio_audit_progress.json`
  - 重新打开 GUI 时，
    若没有再次显式传入 `--bundle`
    就无法自动恢复上次会话
- 风险:
  - 听审往往不是一次完成，
    会跨多次会话
  - 如果每次都要重新手工选 bundle，
    很容易:
    - 换错 bundle
    - 丢失上下文
    - 让 progress 文件形同虚设
- 处理要求:
  - GUI 重新启动时，
    若当前没有传入 bundle，
    应优先尝试从:
    - `audio_audit_progress.json`
    恢复 bundle 列表
  - 在这条恢复链没验证前，
    不要把 GUI 当成正式听审工作流
### 211. Stage3 proxy bundle 若不先做 teacher/student 响度对齐，人耳很容易把音量差误判成结构优劣
- 现象:
  - 当前 Stage3 听审阶段实际试听时发现:
    - `teacher_proxy`
    - `student_proxy`
      的总体音量并不总是一致
  - 在修复前的 validation bundle 中，
    同记录 teacher/student
    曾出现大约:
    - `3.8 dB`
    - `4.2 dB`
    - `4.7 dB`
      的 RMS 差
- 风险:
  - 人耳会先被
    - “谁更响”
      带偏
  - 进而把:
    - 全局音量差
    误判成:
    - 节奏更稳
    - 边界更清楚
    - 整体更好
  - 这会污染人工 gate 记录
- 处理要求:
  - Stage3 proxy audio 导出时，
    对同一条记录的:
    - `teacher_proxy`
    - `student_proxy`
      默认先做成对 loudness match
  - 匹配信息要写回:
    - `proxy_audio_export.json`
    - `proxy_audio_export.md`
  - 后续人工听审必须以
    - 重导后的正式 bundle
      为准，
    不再拿旧的未对齐 wav
    做主观比较
### 212. 当前 Stage3 proxy 若使用固定低频载波，人耳听到“单调嗡声”不是 teacher/student 错位，而是代理本身的设计边界
- 现象:
  - 当前 `synthesize_proxy_waveform`
    使用固定:
    - `carrier_frequency = 185.0`
  - 实际复核当前正式 bundle 后，
    同记录 teacher/student
    的 dominant frequency
    为:
    - `delta = 0.000 Hz`
  - 同时 proxy 主体能量
    超过九成集中在:
    - `150-230 Hz`
- 风险:
  - 如果只凭耳朵觉得
    - “怎么都是单调频率”
  - 很容易误判成:
    - teacher/student pitch 没对齐
    - 模型没学到结构
  - 但这两件事并不等价
  - 当前更真实的情况是:
    - proxy 本身只够承载
      粗粒度包络与稳定性信息
    - 不够承载
      音节级结构感
- 处理要求:
  - 继续使用当前 Stage3 proxy
    做人工听审时，
    结论只允许落在:
    - 停顿
    - 能量包络
    - 稳定性
  - 不把当前 proxy
    当成:
    - 音节结构代理
    - 可懂度代理
  - 若后续任务真的需要判断
    - 音节级结构
    则必须先改 proxy 设计
    或补非音频可视化手段
### 213. GUI 听审里未填写的维度如果实际上表示“平手”，必须在正式结论里显式写明，不能事后被误读成漏评
- 现象:
  - 当前 Stage3 首轮人工听审导出中，
    多条记录的:
    - `best_rhythm`
    - `best_boundary`
      保持空白
  - 用户已明确补充:
    - 未填的条目即为平手
- 风险:
  - 如果只看导出的 `review.json/.md`
    而不知道这条人工约定，
    很容易把空白误读成:
    - 没听完
    - 忘记填
    - 数据缺失
  - 进而错误低估
    teacher / student
    在这些维度上的接近程度
- 处理要求:
  - 后续只要 GUI 允许空白代表平手，
    就必须在:
    - 会话报告
    - 阶段总结
    里显式写出这条解释规则
  - 若以后希望避免二次解释，
    可以考虑把 GUI 的空白和平手分成两个不同状态，
    但在改之前，
    当前报告必须保留这条人工解释
### 214. Stage3 新增 temporal supervision 时，不能照搬普通 proxy loss 的权重量级；先看 raw loss 尺度再定权重
- 现象:
  - 本轮新增:
    - `teacher_proxy_temporal`
      后，
    raw loss
    只有约:
    - `0.005`
  - 而常规:
    - `teacher_energy_proxy`
    - `teacher_proxy_acoustic`
      往往在:
    - `1 ~ 5`
      量级
  - 结果:
    - `teacher_proxy_temporal = 0.2`
      时，
      对训练几乎没有可观影响
- 风险:
  - 如果只看“这个新 loss 已经接上了”，
    却不先核对 raw scale，
    很容易误判成:
    - 方向没用
  - 实际上更可能只是:
    - 权重太小，
      优化器几乎感知不到
- 处理要求:
  - 以后 Stage3 若新增新类型 loss，
    尤其是:
    - temporal
    - delta
    - second-order
      这类数值天然偏小的项，
    必须先记录:
    - raw loss 量级
  - 再决定权重，
    不要机械照搬:
    - `0.1`
    - `0.2`
      这种普通 proxy 权重
### 215. `loss_teacher_proxy_acoustic` 下降不等于人耳毛刺一定更少；值对齐和动态平滑不是一回事
- 现象:
  - 本轮
    `proxyacoustic020`
    在 `12-step full validation`
    下，
    明显拉低了:
    - `loss_teacher_proxy_acoustic`
  - 同时 validation / special
    的统一参考 loss
    也有所改善
  - 但追加的 proxy-jitter probe
    没有同步显示
    明确更稳，
    甚至略变差
- 风险:
  - 如果只看到:
    - proxy_acoustic loss
      更低
  - 很容易把它直接解释成:
    - 人耳毛刺已经变少
  - 这会把:
    - 静态值更接近
    和
    - 时序动态更平滑
      混成一件事
- 处理要求:
  - 后续凡是宣称
    Stage3 “更稳 / 毛刺更少”，
    至少还要再过一关:
    - 人耳复听
    - 或更直接的动态指标
  - 不允许只凭
    - `loss_teacher_proxy_acoustic`
      单项下降
    就直接下“更平滑”的结论
### 216. Stage3 新候选 bundle 导出后，如果不立刻建立独立 GUI 会话目录，后续上下文恢复很容易把真实停点误判回上一轮听审
- 现象:
  - 本轮恢复前，
    `proxytemporal50`
    的两个 bundle
    已经正式存在:
    - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
    - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`
  - 但当时还没有对应的:
    - `reports/audio/audio_audit_gui_stage3_proxytemporal50_session/`
  - 结果就是，
    只看目录很容易误以为
    当前工作还停在:
    - baseline48 首轮听审
    - 或更早的 GUI 接入阶段
- 风险:
  - 一旦新的候选 bundle
    没有马上对应一个正式会话目录，
    “最新实验候选已准备好，但尚未开始人工 gate”
    这个状态就不会被清楚地写在产物层
  - 后续上下文恢复时，
    容易把下一步错误回退成:
    - 重复核对旧 GUI 闭环
    - 重复打开上一轮 baseline 会话
    - 或错误判断为当前还没有新的正式听审入口
- 处理要求:
  - 以后凡是 Stage3
    导出新的候选试听包，
    尤其是:
    - baseline 替代候选
    - 新 supervision 候选
  - 都应立即补一条配套动作:
    - 建立独立
      `audio_audit_gui_*_session`
      目录
    - 至少跑一次
      `launch-audio-audit-gui --auto-close-ms ...`
      smoke test
    - 并在正式文档里写明:
      当前下一步就是进入该会话做人耳 gate
### 217. 当两次实验里的 `teacher_proxy` 人耳上无明显差别时，A/B 结论应显式投影到两个 `student_proxy` 的比较，不能把 teacher 继续混进胜负统计
- 现象:
  - 在 baseline48
    vs
    `proxytemporal50`
    的正式复听里，
    用户明确反馈:
    - 两个 `teacher_proxy`
      全程无明显差别
  - 真正被听出差异的，
    是两个:
    - `student_proxy`
- 风险:
  - 如果仍沿用
    “四个候选一起记胜负”
    的表述，
    很容易把当前问题说糊:
    - 到底是在比较
      teacher/student 对齐程度
    - 还是在比较
      两个 student 版本
      谁更好
  - 这会导致阶段结论
    容易被误读成:
    - `proxytemporal50`
      与 baseline48
      的 teacher/student 关系不同
    而不是更关键的:
    - 两个 student
      谁更稳、谁边界更清楚
- 处理要求:
  - 以后只要 A/B 听审里
    两个 teacher
    被确认无明显差别，
    正式报告就必须直接写明:
    - teacher 只作为锚点
    - 主结论只落在
      两个 student 之间
  - 汇总统计和文字结论
    也应优先翻译成:
    - baseline student 胜多少
    - candidate student 胜多少
    - 平手多少
### 218. Stage3 若开始尝试 temporal schedule，就必须把“每一步实际生效权重”落盘；只记录最终目标权重会让后验判断失真
- 现象:
  - 本轮新增
    `proxytemporal20 + warmup6`
    时，
    checkpoint 训练配置里的
    最终目标权重仍是:
    - `teacher_proxy_temporal = 20.0`
  - 但真实训练前 6 步
    实际经历的是:
    - `0 -> 4 -> 8 -> 12 -> 16 -> 20`
- 风险:
  - 如果 summary / validation / checkpoint
    只保留最终目标权重，
    后续很容易把这条 run
    误读成:
    - “从 step1 开始就是 20.0 常数权重”
  - 这样既不利于解释
    为什么副作用变小，
    也不利于后续复现实验
- 处理要求:
  - 以后只要 Stage3
    使用 loss-weight schedule，
    就必须同步落盘:
    - step 级 effective_loss_weights
    - validation 时对应的 effective_loss_weights
    - checkpoint metadata 里的 schedule 配置
  - 不允许只记:
    - 最终目标权重
    而丢失:
    - 实际生效轨迹
### 219. Stage3 proxy audio 若不先做静音泄漏量化，就可能把导出伪底噪误判成模型问题
- 现象:
  - 本轮用户继续试听前指出:
    - warm 版本有较大底噪
    - 连 `teacher_proxy`
      在静音段里
      也像在持续出声
  - 量化后确认:
    - 旧版 `teacher_proxy`
      确实在静音帧里
      被导出链抬出了
      `0.005 ~ 0.008`
      级别的 RMS
- 风险:
  - 如果不先拆开
    - 导出伪影
    和
    - 模型真实静音活动
  - 很容易把:
    - 合成器底噪
    - export 映射抬活
      误判成
    - 某个 checkpoint
      本身更差
- 处理要求:
  - 以后只要用户在 proxy 听审中
    报告:
    - 静音也在响
    - teacher/student 都有底噪
  - 必须先做静音帧量化，
    至少比较:
    - input 静音帧 RMS
    - teacher_proxy 静音帧 RMS
    - student_proxy 静音帧 RMS
  - 先确认问题属于:
    - 导出链
    - 还是模型
    再决定是否继续试听
### 220. Stage3 默认参数 rerun 时，checkpoint 文件哈希不同不能直接判成训练漂移；要先拆开 metadata 差异和模型内容差异
- 现象:
  - 本轮按默认参数
    重跑
    `baseline48 full-validation`
    后，
    直接比较四个 `.pt`
    checkpoint 的
    `SHA256`
    都与原始 run 不同
  - 但进一步逐项比较后确认:
    - step 级样本顺序一致
    - step 级 loss 一致
    - validation 级样本顺序一致
    - validation 级 loss 一致
    - `model_state_dict`
      逐元素完全一致
- 风险:
  - 如果只看文件哈希，
    很容易误判成:
    - 训练不可复现
    - rerun 产生了新模型
  - 实际上这次差异
    主要来自:
    - `experiment_id`
    - run 名称相关 metadata
- 处理要求:
  - 以后只要做
    “同参 rerun”
    的复现检查，
    不要只比:
    - checkpoint 文件哈希
  - 至少同步比较:
    - step / validation
      样本顺序
    - step / validation
      关键 loss
    - `model_state_dict`
      是否逐元素一致
  - 只有内容层也漂移时，
    才能正式判断:
    - 训练过程不可复现
### 221. teacher runtime wrapper 若在 stream 结束时无条件 flush 尾部残样，会比原 teacher full pass 多出一帧
- 现象:
  - 本轮初版
    `run-offline-mvp-teacher-runtime`
    在 stream 结束时，
    会把尾部不足一帧的残样
    pad 成最后一帧
  - 结果导致:
    - `streaming_frame_count`
      比 full pass
      多 `1`
- 风险:
  - 如果不先把
    runtime wrapper
    的尾帧语义
    对齐原模型，
    后续下游模块会在:
    - 帧数
    - 帧时间戳
    - control / target 对齐
      上全部错位
- 处理要求:
  - 以后只要给
    现有 offline teacher
    做 streaming 包装，
    flush 逻辑必须与
    `frame_waveform()` 的原始语义一致
  - 具体说:
    - 若整条音频
      已经产生过正常帧，
      尾部不足一帧的残样
      直接丢弃
    - 只有整条音频
      从头到尾都短于
      `frame_length`
      时，
      才允许 pad 出
      唯一一帧
### 222. teacher-first 下游合同若把当前 proxy 字段误写成最终 Stage5 vocoder 条件，会把接口风险前移并固化成错误假设
- 现象:
  - 当前 offline teacher
    真实稳定提供的是:
    - `z_art`
    - `event_logits / event_probs`
    - `acoustic = [energy_log, abs_mean, zero_cross_rate, delta_energy]`
  - 但设计稿中
    真正理想的 Stage5 条件
    是:
    - `z_art`
    - `e_evt`
    - `F0`
    - `vuv`
    - `aper`
    - `E`
    - 可选 `r_res`
- 风险:
  - 如果现在就把:
    - `zero_cross_rate`
      直接当成
      最终 `aper`
    - voiced-like event channel
      直接当成
      最终 `vuv`
  - 后续下游实现
    会在错误假设上继续长大，
    最终导致:
    - 条件语义错位
    - 中间层接口返工
    - 评估口径混乱
- 处理要求:
  - 以后只要使用
    teacher-first 下游合同，
    必须显式区分:
    - `provided_keys`
    - `derived_proxy_keys`
    - `missing_design_keys`
  - 绝不允许把当前 proxy 字段
    直接改名写成:
    - 最终设计稿字段
  - 真正进入 Stage5 vocoder 开发时，
    再单独升级合同，
    不要在当前过渡合同里偷换概念
### 223. 在 no-residual vocoder scaffold 阶段，不能因为 branch scaffold 已存在就误判为 waveform 解码链已经成立
- 现象:
  - 本轮已经新增:
    - `offline_teacher_vocoder_input_scaffold.py`
    - `offline_vocoder_scaffold.py`
  - 并且 dry-run
    已能输出:
    - `periodic_hidden`
    - `noise_hidden`
    - `harmonic_envelope`
    - `noise_envelope`
- 风险:
  - 如果把这类
    branch hidden / envelope
    直接等同于:
    - 最终声码器能力
  - 后续很容易误报:
    - “Stage5 已经接通”
  - 实际上当前仍缺:
    - waveform decoder
    - reconstruction loss
    - adversarial / feature matching
    - 最终音频导出
- 处理要求:
  - 以后只要汇报
    `offline_vocoder_scaffold`
    相关进展，
    必须明确写成:
    - code anchor / scaffold
    - dry-run shape verified
  - 不允许直接写成:
    - vocoder implemented
    - inference audio ready
### 224. Stage5 训练目标若不携带 teacher runtime 对齐元数据，后续 train-target builder 很容易在旧 scaffold 上失去帧语义
- 现象:
  - 本轮继续从
    `offline_teacher_vocoder_input_scaffold`
    往前补训练目标时，
    发现 train-target builder
    需要明确知道:
    - `sample_rate`
    - `frame_length`
    - `hop_length`
    - 以及源音频路径
  - 否则就只能猜:
    - teacher 每帧怎么切
    - STFT 应该对齐到多少样本
- 风险:
  - 如果这类元数据
    只存在于较早的 JSON/MD 报告，
    不存在正式 `.pt` payload，
    后续一旦只拿着 scaffold 文件接班，
    很容易:
    - 对错 frame 语义
    - 构错 target 长度
    - 或把旧 scaffold
      当成当前可直接训练的输入
- 处理要求:
  - 以后只要 Stage5
    需要从上游 payload
    继续构建训练目标，
    必须把:
    - 源音频路径
    - runtime sample_rate/frame_length/hop_length
      一起保存在正式张量 payload 里
  - 若历史 payload
    缺这些字段，
    就必须像当前实现一样:
    - 提供显式 override
    - 或者直接重导新 scaffold
### 225. Stage5 最小 loop 若直接复用 train package 做 validation，只能当 plumbing smoke，不能误报成泛化验证
- 现象:
  - 本轮新增
    `run-offline-mvp-nores-vocoder-training-loop`
    时，
    为了先验证:
    - validation history
    - checkpoint series
    - best checkpoint
      这条链，
    默认允许在未提供
    `--validation-targets`
    时复用 train package
- 风险:
  - 如果后续只看到:
    - validation loss 在下降
  - 很容易误以为:
    - 当前 Stage5
      已经有了正式泛化验证
  - 实际上这只能证明:
    - loop 本身能跑
    - 模型能在同一 package 上继续拟合
- 处理要求:
  - 以后只要 Stage5 loop
    使用:
    - `validation_source = train_targets_reused`
  - 正式汇报里必须明确写成:
    - plumbing-level validation
  - 不允许把这类结果
    当作:
    - 正式 validation
    - checkpoint 泛化优劣
      的结论依据
### 226. Stage5 dataset path 若只在超小 capped subset 上做 smoke，只能说明 split-backed plumbing 已成立，不能外推为全量训练吞吐已可接受
- 现象:
  - 本轮虽然已经把
    `build-offline-mvp-nores-vocoder-dataset-packages`
    与
    `run-offline-mvp-nores-vocoder-dataset-training-loop`
    接通，
    并基于正式 split
    跑通了:
    - `2 train + 1 validation`
      package smoke
  - 但当前导出路径
    仍会:
    - 按记录重跑 teacher runtime
    - 按记录写 package
    - 在 loop 中逐包加载
- 风险:
  - 如果只看到:
    - dataset index 已生成
    - 3-step loss 在下降
  - 很容易误以为:
    - Stage5 已可直接全量训练
    - throughput 已经不是问题
  - 实际上当前只能证明:
    - split-backed dataset path
      已成立
    - 小样本 package 采样 loop
      已成立
- 处理要求:
  - 以后只要 Stage5 dataset path
    使用:
    - `max_train_records`
    - `max_validation_records`
    - `selection_mode = shortest_duration`
      之类的 capped smoke
  - 正式汇报里必须明确写成:
    - dataset-plumbing smoke
    - tiny-subset verification
  - 不允许把这类结果
    直接写成:
    - full-split throughput validated
    - ready for large-scale vocoder training
### 227. Stage5 dataset throughput 若只看 `shortest_duration` capped probe，会系统性低估较长样本的包体积与导出成本
- 现象:
  - 本轮给 dataset index
    补了:
    - `package_build_sec`
    - `package_size_bytes`
  - 用
    `shortest_duration`
    跑 `8 train + 2 validation`
    时，
    得到:
    - `avg_package_build_sec ~= 0.078s`
    - `avg_package_size_bytes ~= 0.366MB`
  - 但切到
    `file_order`
    的较长样本对照后，
    很快就抬到:
    - `avg_package_build_sec ~= 0.629s`
    - `avg_package_size_bytes ~= 8.78MB`
- 风险:
  - 如果后续只拿 shortest probe
    做预算，
    很容易误判:
    - full split 导出会非常轻
    - 当前无需考虑 cache / packed loader
  - 实际上它更接近:
    - lower-bound
    - 最快子集
- 处理要求:
  - 以后只要 Stage5
    使用:
    - `selection_mode = shortest_duration`
      做 throughput 结论
  - 正式汇报里必须明确写成:
    - lower-bound probe
  - 至少再配一组:
    - file_order
    - 或更长样本 bucket
      的对照结果
### 228. Stage5 full-split 预算若只凭 single ratio 外推，容易把 per-package 固定开销和按时长增长项混在一起
- 现象:
  - 本轮为了估
    `target_train + target_validation`
    的 full-split 导出预算，
    没直接拿:
    - `sec_per_audio_sec`
    - 或 `bytes_per_package`
      单独外推
  - 而是用两组 probe
    拟了一个最小线性模型，
    把:
    - per-package 开销
    - per-audio-sec 增长
      拆开
- 风险:
  - 如果以后只拿单个比例
    直接乘 full split，
    很容易:
    - 用短句 probe
      严重低估长样本成本
    - 或用长句 probe
      反过来高估短句 bucket
  - 最终会把
    cache / packed loader
    的优先级判断搞偏
- 处理要求:
  - 以后只要做 Stage5
    full-split 预算，
    至少明确区分:
    - package-count 相关固定项
    - audio-duration 相关增长项
  - 若只有单组 probe，
    正式汇报里必须写明:
    - estimate confidence is low
### 229. Stage5 cache / loader 是否要立刻重构，不能只看首次 full export 的分钟级耗时，还要看 `skip-existing` 复用链是否已经足够快
- 现象:
  - 本轮 full-split 首次导出
    实测为:
    - `253.765723 sec`
    - `2.263 GiB`
  - 单看这个数字，
    很容易想直接把:
    - cache
    - packed loader
      提到最高优先级
  - 但同一路径下，
    `--skip-existing`
    复用实测只有:
    - `3.983004 sec`
- 风险:
  - 如果只看首次 full export，
    会高估“马上重构基础设施”的必要性
  - 反过来，
    如果只看复用速度，
    又会低估以后多 objective / 多版本包体积膨胀的风险
- 处理要求:
  - 以后只要评估
    Stage5 cache / loader
    的优先级，
    必须同时给出:
    - first-build cost
    - reuse cost
  - 不允许只拿其中一个数字
    直接做优先级判断
### 230. Stage5 一旦已经跑通 full-split baseline loop，就不该再把主线停在“是否先做 export/cache 重构”的重复讨论上
- 现象:
  - 本轮已经进一步跑通:
    - `592 train + 66 validation`
      的 full-split dataset-level baseline loop
  - 这说明当前工程主线
    已经从:
    - export readiness
      进入到了:
    - training readiness
- 风险:
  - 如果后续仍把主要时间
    用在反复讨论:
    - export 有没有
    - cache 要不要马上做
  - 就会把 Stage5
    又拖回前一停点，
    造成推进停滞
- 处理要求:
  - 以后只要 Stage5
    已具备:
    - full-split export
    - skip-existing reuse
    - full-split baseline loop
  - 默认主线就应切到:
    - proxy baseline 训练稳定化
  - 除非训练侧实测再次证明
    loader 已成为主要瓶颈，
    否则不要把 export/cache
    重新升回主线
### 231. Stage5 dataset loop 若只固定 sampler seed 而不固定 Torch / CUDA 初始化，长程对比会失去解释力
- 现象:
  - 本轮恢复时发现
    Stage5 dataset loop
    已有:
    - `--seed`
  - 但旧实现只把它用于:
    - `random.Random(...)`
      的 package 顺序
  - 没用于:
    - `torch.manual_seed(...)`
    - `torch.cuda.manual_seed_all(...)`
    - model initialization
- 风险:
  - 如果后续直接比较:
    - `12-step`
    - `24-step`
    - `48-step`
      或不同 device run
  - 很容易把
    初始化差异
    误当成:
    - horizon 收益
    - device 收益
    - objective 收益
- 处理要求:
  - 以后只要 Stage5
    训练入口对外暴露:
    - `seed`
  - 就必须让它至少同时覆盖:
    - sampler
    - Torch 初始化
    - CUDA 初始化
  - 正式报告里
    也应把:
    - `training.seed`
      或 `reproducibility.seed`
    写进 summary，
    不能只写 sampler_mode
### 232. Stage5 若看到 `48 -> 96` 仍在下降，就把“继续拉步数”误写成无限高收益主线，会把边际收窄信号吃掉
- 现象:
  - 本轮 seeded GPU
    baseline96
    结果为:
    - step48 = `0.441292`
    - step72 = `0.435399`
    - step96 = `0.432645`
  - 对比前一段:
    - `24 -> 48`
      改善:
      `-0.028352`
  - 后一段:
    - `48 -> 96`
      改善:
      `-0.008647`
- 风险:
  - 如果只看
    “96 比 48 更好”，
    很容易误判:
    - 继续翻倍步数
      仍然会有类似收益
  - 这样会把
    当前更值钱的动作
    从:
    - checkpoint review
    - objective 切换准备
    再次推迟
- 处理要求:
  - 以后只要 Stage5
    做更长 horizon probe，
    正式汇报里必须同时给出:
    - 绝对最优值
    - 与上一 horizon
      的 marginal gain
  - 若 marginal gain
    已明显收窄，
    下一步默认先做:
    - checkpoint review
    - 或低频更远程 probe
  - 不要只因为
    “数值还在降”
    就把无限拉长步数
    自动升格成主线
### 233. Stage5 若只看均值下降而不看 validation package 级分布，容易把 broad-based gain 与局部样本拉动混为一谈
- 现象:
  - 本轮新增
    Stage5 checkpoint review
    后，
    才进一步确认:
    - `24 -> 48`
      是 `66 / 66` validation package
      全量改善
    - `48 -> 72`
      是 `64 / 66`
      改善，
      仅 `2 / 66`
      轻微回退
    - `72 -> 96`
      又回到 `66 / 66`
      全量改善
- 风险:
  - 如果以后只看:
    - average validation `loss_total`
  - 很容易误判:
    - gain 只是少数包体在拉均值
    - 或反过来，
      忽略了局部回退
      正在累积
- 处理要求:
  - 以后只要 Stage5
    做 checkpoint review，
    正式汇报里至少同时给出:
    - checkpoint 级均值轨迹
    - improved / worsened package count
  - 当 gain 已收窄时，
    更必须补:
    - per-record 分布 review
  - 不能只靠单个平均值
    决定:
    - 是否继续拉长 horizon
    - 是否判断为过拟合
### 234. Stage5 若只看首尾 checkpoint 的全量改善，而不看相邻 checkpoint 的局部回退，容易低估尾段收敛信号
- 现象:
  - 本轮新增
    `192-step`
    low-frequency probe
    后，
    虽然:
    - `48 -> 192`
      仍是 `66 / 66`
      validation package
      全量改善
  - 但分段看时，
    已经出现:
    - `96 -> 144`
      `1 / 66`
      轻微回退
    - `144 -> 192`
      `2 / 66`
      轻微回退
- 风险:
  - 如果只看:
    - 首尾 `48 -> 192`
      的全量改善
  - 容易误写成:
    - 后段依然和中段一样稳健
    - 或继续翻倍 horizon
      仍是高收益主线
- 处理要求:
  - 以后只要 Stage5
    进入长程尾段，
    正式汇报里必须同时给出:
    - 首尾 improved / worsened
    - 相邻 checkpoint
      improved / worsened
  - 一旦相邻 checkpoint
    开始出现
    小比例回退，
    就要把它视为:
    - diminishing-return tail
      的证据
  - 不要只用
    “首尾仍全量改善”
    掩盖后段收敛信号
### 235. Stage5 waveform/STFT bootstrap 若只看 loss 下降而不看 decoded waveform RMS，容易把 loudness collapse 误判成正常收敛
- 现象:
  - 本轮新增
    minimal decoder +
    waveform/STFT objective
    后，
    `12-step`
    baseline 的
    validation:
    - `loss_total`
      `1.104648 -> 0.811442`
    - `loss_waveform`
      `0.172122 -> 0.105141`
    - `loss_stft`
      `0.797781 -> 0.447961`
  - 但同时:
    - `decoded_waveform_rms`
      `0.181111 -> 0.077280`
    - 目标 RMS
      仍约为
      `0.123402`
- 风险:
  - 如果以后只看:
    - waveform loss
    - STFT loss
    - 总 loss
  - 很容易误判:
    - decoder 已在稳定学真实波形
  - 实际上模型可能只是
    通过整体变小声
    换到更低损失
- 处理要求:
  - 以后只要 Stage5
    跑 waveform/STFT
    objective，
    正式汇报里必须同时给出:
    - loss_waveform
    - loss_stft
    - decoded_waveform_rms
    - target_waveform_rms
  - 当 decoded RMS
    明显偏离 target RMS
    时，
    优先补:
    - loudness / RMS guard
    - 或等价幅度约束
  - 不要在幅度失真
    还未处理前，
    把这类结果写成
    “decoder baseline 已稳定”
### 236. Stage5 waveform objective 即使已经补了 RMS guard，也不能默认“guard 越大越稳”，过强 guard 会把重建细节一起压坏
- 现象:
  - 本轮新增
    `RMS guard`
    后，
    `0.5` 权重
    虽然把
    validation RMS ratio
    拉到:
    - `1.220926`
  - 但同时:
    - `loss_total = 1.087844`
    - `loss_stft = 0.730605`
    明显差于
    `0.2` 权重的:
    - `loss_total = 0.907862`
    - `loss_stft = 0.547905`
- 风险:
  - 如果以后只因为
    “音量更接近”
    就继续加大 guard，
    很容易让模型
    过度优先保 RMS，
    反而牺牲:
    - 频谱细节
    - waveform 重建
    - 长程验证改善速度
- 处理要求:
  - 以后只要 Stage5
    调 loudness / RMS guard，
    正式汇报里必须至少同时给出:
    - `loss_total`
    - `loss_stft`
    - `loss_rms_guard`
    - `decoded_to_target_rms_ratio`
  - 不能只靠
    单个 RMS ratio
    选权重
  - 当 guard 已明显
    拉坏重建项时，
    默认先回退到
    较轻权重，
    而不是继续加大
### 237. Git 忽略规则若只图“仓库干净”而把 runtime 整体粗暴排除，会把真正难以恢复的 checkpoint 和正式元数据一起丢掉
- 现象:
  - 本轮检查时，
    旧 `.gitignore`
    同时存在:
    - 全局忽略 `*.pt`
    - `reports/runtime/**`
      仅放行
      `*.summary.json/md`
  - 这会误伤:
    - 正式训练 checkpoint
    - dataset index
    - checkpoint review
    - train-step / scaffold / contract
      等恢复元数据
- 风险:
  - 一旦发生
    本地误删、
    磁盘损坏、
    工作区丢失，
    仓库里虽然还剩文档，
    但真正能支撑恢复状态的
    关键件并不在
  - 结果会把仓库
    退化成
    “只能看报告，
     难以继续接班”
- 处理要求:
  - 以后新增忽略规则时，
    必须先判断:
    - 该文件是否敏感
    - 该文件是否可重建
    - 该文件是否属于
      高恢复价值状态
  - 默认保留:
    - 正式 summary / review
    - dataset index
    - 少量关键 checkpoint
  - 默认继续忽略:
    - 原始音频
    - 本地环境
    - 批量可重建 package payload
### 238. Stage5 在 CUDA 上若只设置随机 seed 而不显式开启 deterministic 配置，不能把“同 seed”误写成“严格可复现”
- 现象:
  - 本轮新增
    waveform
    `rms_guard = 0.2`
    `48-step`
    baseline 后，
    其 `step24`
    validation
    为:
    - `0.750610`
  - 而旧的
    standalone
    `24-step`
    报告记录为:
    - `0.749254`
  - 差异虽小，
    但说明:
    - 仅设置
      `torch.manual_seed`
      与
      `torch.cuda.manual_seed_all`
      还不足以保证
      strict deterministic
- 风险:
  - 若以后把
    “同 seed”
    直接写成
    “严格可复现”，
    会把 CUDA
    内核层面的
    微小漂移
    误判成:
    - 训练配方变化
    - 数据顺序变化
    - 或模型真实收益
- 处理要求:
  - 以后凡是
    Stage5 需要做
    严格对照、
    checkpoint 复盘、
    回归验证时，
    默认开启:
    - `--deterministic`
  - summary 中
    必须同时记录:
    - `training.deterministic`
    - `reproducibility.deterministic_algorithms`
  - 不再把
    “同 seed”
    单独当作
    strict reproducibility
    口径
### 239. Stage5 在 CUDA 上即使开启 deterministic algorithms，若没同时设置 `CUBLAS_WORKSPACE_CONFIG`，PyTorch 也可能只给 warning 而不真正满足严格确定性
- 现象:
  - 本轮第一次
    GPU deterministic smoke
    时，
    PyTorch 明确警告:
    - CUDA `>= 10.2`
      下需要
      `CUBLAS_WORKSPACE_CONFIG`
      才能为
      CuBLAS 相关算子
      提供确定性
- 风险:
  - 如果只调用:
    - `torch.use_deterministic_algorithms(True)`
  - 但漏掉
    CuBLAS workspace
    配置，
    很容易出现:
    - 代码里看起来
      已经 deterministic
    - 实际运行仍带 warning
      或仍有漂移
- 处理要求:
  - 以后只要
    Stage5 在 CUDA 上
    开启 deterministic，
    必须同时确保:
    - `CUBLAS_WORKSPACE_CONFIG=:4096:8`
      或等价值
  - 最好由代码在
    训练入口内
    自动补齐，
    不依赖手工命令记忆
  - 跑完后
    若仍出现
    deterministic warning，
    不得直接把该 run
    归类为
    strict reproducibility
### 240. Stage5 waveform route 若只看 `96-step` 平均 loss 继续下降而不看 `72 -> 96` 的 package 级回退，容易把尾段 mixed gain 误写成仍然稳定广覆盖
- 现象:
  - 本轮
    deterministic
    waveform baseline
    到 `96-step`
    时，
    validation
    `loss_total`
    从:
    - `0.625926`
      继续降到
      `0.616506`
  - 但 checkpoint review
    同时显示:
    - `72 -> 96`
      仅
      `42 / 66`
      improved
    - `24 / 66`
      worsened
- 风险:
  - 如果以后只看
    平均 validation loss，
    很容易误判:
    - `96`
      仍像
      `48 -> 72`
      一样稳健
    - 或继续把更长 horizon
      自动当作主线
- 处理要求:
  - 以后只要
    waveform route
    进入长程尾段，
    正式汇报里必须同时给出:
    - checkpoint 级平均轨迹
    - improved / worsened
      package count
  - 当均值仍在改善、
    但局部回退显著增多时，
    默认把它视为:
    - mixed tail gain
  - 不再把这种阶段
    直接写成
    stable broad-based gain
### 241. Stage5 waveform route 的 RMS guard 即使前段有效，后段也可能出现过冲；不能只因为 `72-step` 附近贴近 1.0，就默认更长 horizon 仍会维持同样幅度平衡
- 现象:
  - 本轮
    deterministic
    waveform baseline
    中:
    - step72
      `decoded_to_target_rms_ratio = 0.979730`
    - step96
      `decoded_to_target_rms_ratio = 1.051881`
  - 这说明:
    - 同一 guard 权重
      在更长 horizon
      下也可能从
      “接近目标”
      变成
      “轻微过冲”
- 风险:
  - 如果以后只看到
    前段 RMS
    已经贴近目标，
    就默认:
    - 后段无需再看
      RMS ratio
  - 很容易错过:
    - 振幅重新偏离
    - late-stop 更合适
      的信号
- 处理要求:
  - 以后只要
    waveform route
    继续拉长 horizon，
    每个 checkpoint
    都必须继续记录:
    - `loss_total`
    - `loss_stft`
    - `loss_rms_guard`
    - `decoded_to_target_rms_ratio`
  - 当 tail 段开始出现
    RMS 过冲
    与局部回退一起增加时，
    默认优先考虑:
    - late-stop
    - 或 objective 升级
  - 不把
    “前段 guard 有效”
    直接等同于
    “后段一定持续平衡”
### 242. Stage5 waveform route 不能把 `best_validation_checkpoint` 直接等同于默认工程 checkpoint；best-by-loss、best-by-RMS、stable late-stop 可能落在不同 step
- 现象:
  - 本轮
    deterministic
    `96-step`
    waveform route
    selector 明确给出:
    - `step96 = best validation`
    - `step48 = best RMS`
    - `step72 = stable late-stop`
- 风险:
  - 如果以后只保留
    一个
    `best_checkpoint`
    概念，
    很容易把:
    - 最低平均 loss
    - 最稳妥晚停
    - 幅度最平衡
    混成一件事
  - 结果会导致:
    - 选点口径混乱
    - 报告复盘困难
    - 后续路线难以比较
- 处理要求:
  - 以后凡是
    Stage5 waveform
    做 checkpoint 汇报，
    默认至少同时给出:
    - best validation checkpoint
    - stable late-stop
  - 当 RMS 也是核心风险时，
    额外给出:
    - best RMS checkpoint
  - 不再把
    单个 `best_checkpoint`
    直接当成
    唯一正式口径
### 243. Stage5 waveform route 的全量平均 `decoded_to_target_rms_ratio` 接近 1，不代表单样本幅度已经稳定；均值可能掩盖明显的 per-record 过低或过高
- 现象:
  - 本轮
    `step72`
    的全量 validation
    平均:
    - `decoded_to_target_rms_ratio = 0.979730`
  - 但导出的
    `6`
    条 validation 样本里，
    单样本 ratio
    约为:
    - `0.782090`
      到
      `1.283669`
- 风险:
  - 如果以后只看
    全局平均 RMS ratio，
    很容易误判:
    - 当前 loudness
      已经基本稳定
  - 实际上某些样本
    仍可能:
    - 偏小声
    - 偏大声
    - 听感不一致
- 处理要求:
  - 以后只要
    Stage5 waveform route
    进入音频导出或听审前，
    不仅要看:
    - 全量平均 RMS ratio
  - 还要补:
    - 样本级 RMS ratio
      抽查
    - 或至少导出一小组
      validation 音频
      做人工确认
  - 不再把
    “平均值接近 1”
    直接写成
    “样本级幅度已稳定”
### 244. Stage5 新增音频导出链路时，不能只产出自定义 json 名称；只要目标是复用现有人工听审 GUI，就必须同时满足既有 `proxy_audio_export` 契约或提供显式回退兼容
- 现象:
  - Stage5
    最初已经能导出:
    - `aligned_target.wav`
    - `decoded.wav`
  - 但只写了:
    - `nores_vocoder_audio_export.json`
  - 结果是:
    - 产物可看
    - 但 GUI 不能直接加载
- 风险:
  - 如果以后每条新路线
    都各写一份
    自己的 manifest 名称，
    很快会出现:
    - GUI / 工具侧兼容分叉
    - 听审入口不统一
    - 接班时还要重新猜
      哪个 json
      才能打开
- 处理要求:
  - 以后只要
    新路线目标是接入
    现有 audio audit GUI，
    默认至少满足其一:
    - exporter 直接同步产出
      `proxy_audio_export.json`
    - GUI 明确回退兼容
      新 manifest
  - 最稳妥做法是:
    - 两边都做
      最小兼容
  - 不再默认认为:
    - “能导出 wav”
      就等于
      “已经接通听审工作流”
### 245. 只要把任务推进到人工听审阶段，就不能只留抽象结论；必须明确给出命令、bundle 路径、输出目录和主对比目标，否则“可听审”只是口头状态，不是可执行状态
- 现象:
  - 即使已经有:
    - exporter
    - GUI
    - session 目录
  - 如果不把:
    - 启动命令
    - bundle 目录
    - 输出目录
    - 该比较谁
    明确写出来，
    用户仍然要自己猜
- 风险:
  - 很容易出现:
    - 用户打开错 bundle
    - 比较对象不一致
    - 听审结果无法复盘
    - 接班时不知道
      上一轮到底想让人听什么
- 处理要求:
  - 以后只要需要用户
    做人工听审，
    默认同时落盘:
    - 一条正式 CLI 命令
    - 一个固定输出目录
    - 本轮主对比目标
    - 本轮试听重点
  - 若命令较长，
    最好再补:
    - 一个脚本入口
  - 不再把
    “可以开始人工听审了”
    当成充分交接信息
### 246. Stage5 bootstrap `decoded.wav` 不能自动当成人工听审默认音频；如果它仍带持续活动或高刺激听感，应先在导出链改成更低频、带静音 gate 的 audit proxy，再恢复试听
- 现象:
  - 本轮用户在真正试听时
    明确指出:
    - 主观基频 / 载波感过高
    - 三条分支几乎全程不静音
  - 量化复核后，
    `step72`
    raw `decoded.wav`
    在目标静音帧上的平均 RMS
    约为:
    - `0.121756`
- 风险:
  - 如果把当前 bootstrap
    的 raw decoded
    直接当成人工听审默认音频，
    很容易出现:
    - 用户生理/心理不适
    - 静音泄漏污染判断
    - 把导出伪影误判成
      checkpoint 差异
- 处理要求:
  - 以后只要
    Stage5 raw decoded
    仍明显不适听，
    默认先切到:
    - 低频 audit proxy
    - 且用 target activity
      做静音 gate
  - 同时保留:
    - raw `decoded.wav`
    供技术排查
  - 不再把
    “有 wav 文件可放”
    自动等同于
    “适合作人工听审”
### 247. 听审 GUI 的说明文字如果过长、过口语化，会让评分标准变松；更稳妥的做法是收成少量判断词和当前优先关注项
- 现象:
  - 当 GUI 帮助区
    写成大段解释时，
    用户在真正试听时
    需要边读边翻译
    “到底该判什么”
- 风险:
  - 容易出现:
    - 同一个词
      每次理解都不一样
    - 评分时注意力
      被长说明分散
    - 听审口径漂移
- 处理要求:
  - GUI 帮助区
    默认优先写成:
    - 判断词
    - 当前优先关注项
    - 当前先不看项
  - 尽量避免
    大段口语解释
    占满主要空间
### 248. 当局部人工听审已经暴露出更大的模型级缺陷时，不必为了 checkpoint 排名强行补完整轮试听；应先把听感信号转成可量化工程问题，再继续推进
- 现象:
  - 本轮用户只听了
    前两条样本，
    并对
    `step48`
    给出更自然的
    局部偏好
  - 但对这两条样本的
    量化复核又显示:
    - `audit_proxy`
      三者差距很小
    - raw `decoded.wav`
      三者都明显缺乏
      动态跟随和静音控制
- 风险:
  - 如果此时继续把精力
    放在:
    - “48 / 72 / 96
       谁排名第一”
  - 很容易忽略
    当前真正更大的 blocker:
    - 模型级动态 / 静音控制缺陷
- 处理要求:
  - 以后若出现这种情况，
    默认先把局部听感
    转成:
    - 可量化诊断
    - 工程修正目标
  - 不强行要求
    用户先补完整轮试听
    才允许继续推进
### 249. Stage5 一旦把 predicted activity gate 接进 waveform 重建，后续训练验证、音频导出和人工听审都必须显式记录同一 decode 口径；否则新旧 route 的改善会被“配置不同”掩盖或夸大
- 现象:
  - 本轮
    activity-gate
    收益不只来自
    多一个 supervision
  - 还来自:
    - predicted activity
      参与 waveform-frame
      重建
  - 同样的 checkpoint，
    如果导出时
    没有把这层 decode
    设置写明，
    看起来就像
    “一会儿明显更安静，
     一会儿又没改善”
- 风险:
  - 很容易出现:
    - validation summary
      看到一套口径
    - 导出 bundle
      又是另一套口径
    - 人工听审时
      误把 decode 配置差异
      当成模型能力差异
  - 接班时也会说不清:
    - 这份 `decoded.wav`
      到底是不是
      activity-gated
- 处理要求:
  - 以后只要
    Stage5
    使用 predicted activity gate，
    默认同时落盘:
    - 训练 loss 配置
    - validation 口径
    - export / bundle
      的 decode 设置
  - manifest 和正式报告里
    必须明确写出:
    - `use_predicted_activity_gate`
    - 相关权重
  - 不再把
    “同一个 checkpoint 文件”
    自动视为
    “同一可听结果”
### 250. Stage5 activity-gate route 即使已经显著修复 dynamic / silence，也不能只看 validation loss_total 就宣布收口；必须继续同时盯住 loudness ratio，避免把“更安静了”误判成“整体都更好了”
- 现象:
  - 本轮
    `activitygate72`
    的 validation
    `loss_total`
    已降到:
    - `0.564671`
  - 且前两条样本上的
    dynamic-follow /
    silence-control
    继续明显改善
  - 但 validation aggregate
    的
    `decoded_to_target_rms_ratio`
    仍约为:
    - `0.917435`
- 风险:
  - 如果这时只看:
    - validation loss
    - 或局部前两条样本
      的 dynamic 指标
  - 很容易忽略:
    - 全量平均 loudness
      仍可能偏低
    - 后续更长 horizon
      可能把
      “更会静音”
      继续推成
      “整体偏小声”
- 处理要求:
  - 以后只要
    activity-gate route
    继续拉长 horizon，
    默认同时汇报:
    - validation loss_total
    - decoded_to_target_rms_ratio
    - dynamic-follow 指标
    - silence-control 指标
  - 不再把
    单一 loss
    或单一 front-sample
    指标
    当成足够收口证据
### 251. 当新 family 在 validation 上持续更强、但旧 stable-late-stop 规则因为 loudness/guard tradeoff 选不出结果时，不要为了“必须有一个 formal stable 点”强行改政策或硬选最早 best-RMS；应先把真正有信息量的候选收束出来做听审
- 现象:
  - 本轮
    activity-gate family
    在旧 selector 下得到:
    - `best_validation = step72`
    - `best_rms = step24`
    - `stable_late_stop = null`
  - 其中:
    - `step24`
      虽然 RMS 最贴近 1
      但 validation 太弱
    - `step60`
      虽未过
      `1.03x` guard，
      却只差
      `0.003043`
      且 loudness 更稳
- 风险:
  - 如果这时为了
    “文档里必须有个
     stable late-stop”
    直接私自改 policy，
    很容易把治理口径
    写死得过早
  - 如果反过来
    机械地把
    `best_rms = step24`
    当成人工听审主对象，
    又会把用户注意力
    浪费在
    已明显落后的早期点上
- 处理要求:
  - 遇到这种情况时，
    默认先做三件事:
    - 保留 selector 原始输出
    - 明确写出
      哪个候选是
      best validation
      哪个候选是
      loudness-balanced late candidate
    - 让人工听审
      直接比较
      真正有信息量的
      tradeoff 对
  - 不把
    “治理结果暂时为 null”
    误当成
    “不能继续推进”
### 252. 当用户主观觉得“新点更柔和、波动更少”时，不能直接把它等同于负面过平滑；应先区分“目标对齐起伏被抹掉了”还是“旧路线里不受控的噪声式抖动被压下去了”
- 现象:
  - 本轮用户对
    `activitygate60 vs 72`
    的主观反馈是:
    - 基本打平
    - `72`
      略柔和
    - 两者似乎都比
      旧第三条候选
      更平
  - 但对同批样本的
    `audit_proxy`
    aggregate 复核显示:
    - `60 / 72`
      的
      `audit_env_corr`
      和
      `audit_delta_corr`
      都高于旧
      `step48`
- 风险:
  - 如果把
    “听起来更柔和”
    直接翻译成
    “过平滑、一定更差”，
    很容易把
    有益的稳定化
    误判成回退
  - 反过来，
    如果只看
    更高的相关性，
    也可能忽略
    起伏幅度
    是否被收得过头
- 处理要求:
  - 以后遇到
    “更柔和 / 更平”
    的听感反馈，
    默认同时核对:
    - envelope correlation
    - delta correlation
    - dynamic std ratio
    - peak-to-peak ratio
  - 报告里必须分开写清:
    - 对齐程度
    - 起伏幅度
  - 不再把
    “更柔和”
    自动写成
    负面结论
### 253. 当当前导出链同时提供 `decoded.wav` 与 `audit_proxy.wav` 时，不能再让 `audit_proxy.wav` 默认主导人工听审；否则会把“辅助诊断音频”误当成“最接近成品的可听结果”
- 现象:
  - `audit_proxy.wav`
    的长处是:
    - 动态/静音问题更容易暴露
  - 但它本质上
    不是人耳日常处理的
    正常说话音频
  - 如果继续默认主听它，
    用户很容易:
    - 抓不住真正成品听感重点
    - 或被异常听感本身带偏
- 风险:
  - 容易把:
    - 辅助诊断结果
    当成
    主听感结论
  - 也容易让
    “proxy 更平 / 更刺激 / 更奇怪”
    这类特征
    误伤对真实输出的判断
- 处理要求:
  - 以后只要
    Stage5 bundle
    同时含有:
    - `decoded.wav`
    - `audit_proxy.wav`
  - 默认主听入口
    应切到:
    - `decoded.wav`
  - `audit_proxy.wav`
    仅保留为:
    - 动态/静音/边界
      诊断工具
  - 报告里必须明确写清:
    - 当前主听源
    - 当前诊断源
### 254. 当 exporter 已把“主听音频是谁”写进 manifest 后，GUI consumer 不能继续保留“看到 `decoded_audio_path` 就固定播 decoded”的硬编码；否则 `listening_audio_source` 会沦为假契约
- 现象:
  - 本轮
    `export-offline-mvp-nores-vocoder-audio`
    已新增:
    - `listening_audio_source`
    - `listening_audio_path`
  - 但 GUI
    的候选选择逻辑
    仍是:
    - 只要记录里有
      `decoded_audio_path`
    - 就直接返回
      `decoded`
- 风险:
  - 会导致:
    - `--listening-audio-source audit_proxy`
      在 bundle
      和文档里
      看起来已生效
    - 但 GUI
      实际播放的
      仍可能是
      `decoded.wav`
  - 这类问题最危险的地方
    不在于报错，
    而在于:
    - 一切都“看起来正常”
    - 只是人工听审
      基于错误音频
      做结论
- 处理要求:
  - 只要 producer
    新增了
    主听源字段，
    consumer
    必须同步优先读取:
    - `listening_audio_path`
  - 若要兼容旧 bundle，
    只能把:
    - `decoded_audio_path`
    - `audit_proxy_audio_path`
    - `proxy_audio_path`
    作为回退
  - 以后凡是
    “导出清单驱动 GUI”
    的链路改动，
    都至少补一次:
    - 函数级路径验证
    - 一次 GUI smoke
### 255. 当当前 `decoded.wav` 的主观音高明显偏高到足以引起心理不适时，不能机械坚持“既然它最接近成品就必须直接听 raw decoded”；应先为人工听评提供 listening-only 的 pitch-normalized 版本
- 现象:
  - 本轮 Stage5
    在切回
    `decoded.wav`
    主听后，
    用户明确反馈:
    - 音调太高
    - 已导致听评取消
  - 同批
    `activitygate72`
    validation 记录上，
    `decoded`
    的中位 voiced F0
    近似锁在
    `275.46 Hz`
  - 相对
    `aligned_target`
    的目标口径，
    aggregate
    ratio
    中位数约为
    `0.896792`
    即约
    `-1.9`
    semitones
- 风险:
  - 若继续强推
    raw `decoded`
    进人工听评，
    用户给出的结论
    会被:
    - 生理/心理不适
    - 绝对音高偏差
    直接污染
  - 但若反过来
    把 pitch-normalized
    听评结果
    当成
    “模型原始输出已经修好”
    也会误导
- 处理要求:
  - 当 raw `decoded`
    因音高问题
    已不适合继续主听时，
    应补一条
    listening-only
    分支，
    例如:
    - `decoded_pitch_matched.wav`
  - 该分支应:
    - 显式记录参考源
    - 显式记录 shift ratio /
      semitone
    - 保持时长不变
  - 报告里必须同时写清:
    - 它适用于什么判断
    - 它不适用于什么判断
  - raw `decoded.wav`
    仍需保留为:
    - 技术排查入口
### 256. 听审 GUI 不应把方向键绑定成切换记录；否则用户在备注框里移动光标时，会误切条目并污染当前记录状态
- 现象:
  - 本轮用户在实际使用
    audio audit GUI
    时明确反馈:
    - 方向键切条目
      会干扰备注输入
- 风险:
  - 容易出现:
    - 还在写当前条备注
    - 记录却已经被切到下一条
    - 导致评分和备注
      写串行
- 处理要求:
  - 以后 GUI
    不再用:
    - `Left / Right`
    - 或记录列表上的
      方向键
    做记录切换
  - 记录切换
    默认只走:
    - 明确按钮
    - 或鼠标选择
### 257. 长音频如果只能整段试听，人耳对细小差异的短时记忆会很快漂移；这会把“真差异”与“记忆误差”混在一起
- 现象:
  - 本轮
    `target::chapter3_4_firefly_106`
    这类较长记录
    在整段试听时，
    用户明确指出:
    - 后半段容易出现
      记忆不清
      或幻觉式比较
- 风险:
  - 如果继续默认整段听，
    很容易把:
    - 比较对象太长
    - 人耳短时记忆不足
    错判成:
    - 候选差异很小
    - 或某一方更自然
- 处理要求:
  - 以后只要
    听审记录较长，
    GUI
    默认应提供:
    - 自动切段试听
    - 同段位的
      输入/候选对照播放
  - 整段播放
    仅保留为回退选项
### 258. 在人工听审导出里，若记录已完成且可比较，评分字段留空不能再默认解释成“未填”；否则会把大量真实打平误读成缺失数据
- 现象:
  - 本轮
    `activitygate60 vs 72`
    pitch-matched
    听审里，
    用户明确要求:
    - 空着的项目
      视为打平
      而非未填
- 风险:
  - 若导出逻辑仍把空值
    当成缺失，
    会导致:
    - 汇总统计低估
      `打平`
    - 文档误写成
      “很多项没判”
    - 听审结论
      被人为夸大成
      有更明显的胜负
- 处理要求:
  - 以后对:
    - `completed = true`
    - `valid_for_comparison != no`
    的记录，
    评分字段留空
    默认按:
    - `打平`
    导出
  - 导出产物中
    应显式写出:
    - tie policy
### 259. 新增专项诊断模块如果只停留在单个 `.py` 文件里、没有正式 CLI 和 smoke 产物，接班时很容易被误判成“还没进入工程化状态”
- 现象:
  - 本轮接班时，
    `src/v5vc/stage5_low_activity_probe.py`
    已经存在主体实现，
    但此前仍缺:
    - `src/v5vc/cli.py`
      的正式命令入口
    - 一次真实 bundle smoke
    - 正式报告
- 风险:
  - 下一位接手者
    很容易误判为:
    - 这只是临时草稿
    - 还不能直接运行
    - 需要从头再补入口
  - 结果会拖慢真正有信息量的后续工作
- 处理要求:
  - 以后只要新增:
    - 分析模块
    - 排查模块
    - 听审辅助模块
  - 若预期会被重复使用，
    就不要只停在:
    - 单文件实现
  - 至少同步补齐:
    - 正式 CLI 入口
    - 一次真实 smoke
    - 磁盘文档里的调用命令和输出目录
### 260. 对 WAV 二进制内容直接使用 `torch.frombuffer(bytes, ...)`，会触发 non-writable buffer warning；如果不修，批量诊断时 stderr 会被无效噪声污染
- 现象:
  - 本轮
    Stage5
    低活动段 probe
    首次 smoke
    时，
    `read_wav_mono()`
    触发:
    - PyTorch
      non-writable buffer warning
- 原因:
  - 直接把
    `bytes`
    传给
    `torch.frombuffer(...)`
    时，
    buffer
    被视为只读
- 风险:
  - 虽然不一定影响结果，
    但会导致:
    - smoke 输出夹杂无效 warning
    - 真正异常更难被看见
    - 批量分析日志可读性下降
- 处理要求:
  - 后续若继续用
    `torch.frombuffer(...)`
    读二进制 wav payload，
    优先改成:
    - `bytearray(raw)`
    - 或其他可写 buffer
  - 重新 smoke，
    确认 stderr 干净
### 261. 不要把当前 bundle 里的 `listening` 想当然当成独立音源；它可能只是 `decoded_pitch_matched` 的别名
- 现象:
  - 本轮核对
    Stage5 bundle
    时发现:
    - `listening_audio_source = decoded_pitch_matched`
    - `listening_audio_path`
      直接指向
      `decoded_pitch_matched.wav`
- 风险:
  - 如果接班时
    不先看 manifest，
    很容易误以为:
    - 又多跑了一条新音源
  - 实际只是重复口径，
    会浪费时间，
    还可能把“多音源一致”
    错写出来
- 处理要求:
  - 后续只要要做
    cross-source
    结论，
    先看 bundle manifest
    里的:
    - `listening_audio_source`
    - `listening_audio_path`
  - 确认它是不是
    真独立音源
### 262. `audit_proxy` 的 aggregate 方向可能与 `decoded` 相反；它适合做低频辅助排查，不适合直接替代 decoded 主判断
- 现象:
  - 本轮
    low-activity probe
    在:
    - `decoded`
      上更偏向
      `step72`
      更差
    - `audit_proxy`
      上却更偏向
      `step60`
      更差
- 风险:
  - 如果直接把
    `audit_proxy`
    当成主听结论，
    很可能把方向看反
- 处理要求:
  - `audit_proxy`
    默认继续保留为:
    - 技术对照
    - 低频辅助排查
  - 主判断优先参考:
    - `decoded`
    - `decoded_pitch_matched`
    - 人耳定点复核
### 263. 诊断工具如果只能导出片段、不把它们转成 GUI 可读 bundle，后续人工复核仍会被手工拼路径拖慢
- 现象:
  - 本轮在
    low-activity probe
    跑出
    `top_windows`
    后，
    如果只保留:
    - `clips/`
      目录
    仍然需要人工找:
    - 哪个片段对应哪个 branch
    - 哪两个路径要一起喂给 GUI
- 风险:
  - 会把
    “自动定位问题”
    又退回成
    “人工拼装试听入口”
- 处理要求:
  - 后续这类专项 probe
    若预期要接人工复核，
    默认同时导出:
    - GUI 可读 manifest
    - 固定 bundle 目录
### 264. 如果某批 probe 产物已经确定要交给用户做正式听审，就不要继续只引用 `tmp/` 下的 smoke 目录；应升级到 `reports/audio/` 并给出固定脚本入口
- 现象:
  - 本轮
    low-activity probe
    最先是在:
    - `tmp/stage5_low_activity_fragmentation_probe_*`
      下做 smoke
  - 这些目录适合验证，
    但不适合作为
    用户正式听审入口
- 风险:
  - 如果继续把正式操作指向
    `tmp/`
    目录，
    后续很容易出现:
    - smoke 目录被覆盖
    - 用户不知道哪个是最终入口
    - 文档和真实可用目录脱节
- 处理要求:
  - 一旦确认
    这批 probe
    需要交给用户正式听审，
    就把产物升级到:
    - `reports/audio/`
      或其他正式目录
  - 同时补齐:
    - 固定 session 输出目录
    - 一条正式 CLI 命令
    - 一个脚本入口
### 265. 算法诊断窗不等于可听判断窗；如果只导出“低活动段本体 + 很小 padding”，人耳几乎无法判断
- 现象:
  - 本轮用户直接反馈:
    - 旧版切片太短
    - 几乎没有判断因素
  - 旧版 probe
    虽能定位可疑低活动段，
    但导出窗只接近:
    - 原 segment
    - 加少量 padding
- 风险:
  - 容易把
    “算法可疑窗口”
    错当成
    “足够支撑人耳结论的试听材料”
  - 进而把不稳的主观印象写成
    强结论
- 处理要求:
  - 以后凡是要接人工听审的专项 probe，
    默认区分:
    - 诊断 segment
    - audit window
  - audit window
    默认至少保证:
    - 前后约 `200ms` 上下文
    - 总长度约 `2s - 3s`
  - 若样本因音频边界限制仍明显短于该范围，
    默认只作为次要证据，
    不要当主样本
### 266. `fragmentation` 偏高不等于“模型单方新增毛刺”；breath / sigh / 清辅音自身的 target 能量突变会混进 low-activity 可疑窗
- 现象:
  - 本轮
    `windowed_v2`
    听审里，
    至少有两条样本显示:
    - target 本身存在明显辅音 / 爆破 / 清音能量突变
    - 或两路模型都在同一 breath-like 区间
      出现类似毛刺
- 风险:
  - 如果看到
    low-activity probe
    里的高
    `fragmentation_score`
    就直接写成
    “某 checkpoint 自己加了毛刺”，
    很容易误判
- 处理要求:
  - 后续解释
    `fragmentation`
    结果时，
    默认分开记录:
    - target-correlated
      的瞬态风险
    - model-added
      的局部毛刺风险
  - 对 target 自身已有明显
    breath / 爆破 / 清辅音突变的窗口，
    默认不要直接当
    “模型定罪样本”
### 267. `fragmentation` 低也不代表低活动段表现更好；持续底音泄漏会把 burst/toggle 指标压平
- 现象:
  - 当前 decoded low-activity probe
    上，
    `step60`
    的
    `mean_fragmentation_score`
    很低，
    但
    `mean_active_fraction = 1.0`
  - 人耳也同步指出:
    - `step60`
      的静音段底音仍然存在
- 风险:
  - 如果只看
    `fragmentation_score`
    这一条，
    会把
    “持续有底音所以不怎么 burst”
    误读成
    “低活动段更干净”
- 处理要求:
  - 后续 low-activity 结论
    默认至少同时看:
    - `fragmentation_score`
    - `mean_active_fraction`
  - 并把
    `mean_active_fraction`
    明确解释为:
    - 低活动段底音泄漏 / 活动残留指标
### 268. 任何主观结论如果不做量化回查，都会有较高概率混入错觉、暗示或错误解释
- 现象:
  - 本项目里已经多次出现:
    - 初听觉得某模型更差
    - 后续却发现
      片段过短、
      target 自身带瞬态、
      或指标解释方向错了
- 风险:
  - 如果把主观听感直接写成主结论，
    很容易把:
    - 错觉
    - 心理暗示
    - 选择性样本
    - tradeoff 误读
    固化进路线判断
- 处理要求:
  - 后续所有主观结论，
    默认都要补:
    - 可测假设
    - 对应量化指标
    - 样本范围
    - 主观与量化是否一致
  - 没有量化回查支撑时，
    结论默认只允许写成:
    - 听感观察
    - 听感趋势
  - 具体执行规范见:
    - `docs/213_subjective_conclusion_quant_validation_protocol.md`
### 269. “更毛刺”与“更不尊重原音量变化”不是同一类问题；如果只用一个指标，会把 tradeoff 混成单边输赢
- 现象:
  - 本轮 low-activity
    量化回查显示:
    - `step72`
      的
      `fragmentation_score`
      更高
    - 但
      `step72`
      的
      `mean_activity_alignment_mae`
      和
      `mean_activity_excess_mean`
      更低
    - 同时
      `step60`
      的
      `mean_active_fraction = 1.0`
- 风险:
  - 如果只看
    `fragmentation`
    会错把
    `step72`
    写成全面更差
  - 如果只看
    activity 对齐类指标，
    又会忽略
    `step72`
    的局部偶发毛刺风险
- 处理要求:
  - 后续 low-activity
    结论默认至少拆成两条:
    - 局部毛刺 / 断续风险
    - 低活动底音泄漏 / 动态跟随能力
  - 默认至少同时看:
    - `fragmentation_score`
    - `mean_active_fraction`
    - `mean_activity_alignment_mae`
    - `mean_activity_excess_mean`
### 270. target 上下文瞬态指标当前只能作“混淆提示”，还不能直接自动判定某窗口一定是 target-correlated
- 现象:
  - 本轮新增:
    - `target_context_toggle_mean`
    - `target_boundary_jump_max`
  - 它们确实能提示
    某窗口周围
    target
    自身存在较强边界变化
  - 但还没形成
    能稳定覆盖全部人耳判断的单一阈值
- 风险:
  - 如果过早把它们硬编码成
    自动排除规则，
    会把真实的模型问题窗口
    一起排掉
- 处理要求:
  - 当前阶段把它们保留为:
    - 风险提示字段
  - 暂不直接作为:
    - 自动排除
    - 自动定罪
    规则
### 271. 把 low-activity 指标接进 checkpoint governance 时，先做 sidecar，再决定是否改 selector 主策略；不要一上来把专项指标直接硬编码进自动选点
- 现象:
  - 本轮已经证明
    low-activity
    指标能稳定表达:
    - `step72`
      更贴 target
      能量轨迹
    - `step60`
      底音泄漏更重
  - 但它们表达的是
    tradeoff，
    不是单边绝对胜负
- 风险:
  - 如果直接把这类专项指标
    硬塞进 selector
    主排序，
    很容易:
    - 覆盖掉原本更稳定的 validation 约束
    - 把局部专项偏好
      误升格成全局主目标
- 处理要求:
  - 这类新指标
    默认先以:
    - governance sidecar
    - guardrail
    - rerank 候选解释
    的形式接入
  - 只有在样本覆盖、阈值和 tradeoff
    都更清楚后，
    才讨论是否升格为:
    - hard constraint
    - selector 主规则
### 272. 从 sidecar 升到 soft rerank 时，必须先把候选范围限定在 near-best late candidates；否则专项指标会把早期 checkpoint 重新拉回桌面
- 现象:
  - 本轮如果不加
    near-best validation
    门槛，
    那么 low-activity
    指标可能会把
    早期 checkpoint
    重新带回比较集合
- 风险:
  - 会把
    “在主候选之间做 tradeoff”
    变成
    “专项指标反向重开全量选点”
- 处理要求:
  - soft rerank
    默认只在:
    - late candidates
    - 且接近 best validation
      的候选
    内部生效
  - 当前默认门槛保留为:
    - `loss_total <= best_validation * 1.05`
  - 这条门槛
    若要调整，
    应单独记录
    调整理由和影响
### 273. 在只有两个候选的 low-activity soft rerank 里，min-max 归一化分数更像“权重投票”，不能把绝对分值当成可跨 family 复用的刻度
- 现象:
  - 当前
    `step60 vs step72`
    的 soft rerank
    只有两个候选
  - 并且四个核心指标上，
    两边几乎是一边倒:
    - `step72`
      赢
      alignment / excess / active_fraction
    - `step60`
      赢
      fragmentation
  - 因而当前
    `0.1`
    对
    `0.9`
    的分差，
    本质上主要来自:
    - 权重如何在
      三个“低活动跟随/泄漏”指标
      与
      一个
      `fragmentation`
      指标之间分配
- 风险:
  - 如果把这类分数
    误写成
    “跨 family
    可直接比较的绝对质量刻度”，
    很容易过度解读
- 处理要求:
  - 当前阶段默认把
    low-activity governance score
    解释为:
    - 当前候选集合内部的相对排序分数
  - 不直接拿
    `0.1`
    `0.9`
    这类数值
    做跨 family
    的强比较
### 274. 当前 `soft_validation_ratio = 1.05` 的稳定性证据，只能说明“没把当前推荐改坏”，不能说明“1.05 已经被系统性调优完成”
- 现象:
  - 本轮 ratio sweep
    显示:
    - `step60`
      的进入门槛
      实际是
      `1.035389`
    - 在
      `1.035389`
      和
      `1.05`
      下，
      推荐都仍是
      `step72`
- 风险:
  - 如果把这个结果
    直接写成
    “1.05 最优”，
    会把
    “当前没有翻车”
    误写成
    “已经完成调参”
- 处理要求:
  - 当前对
    `1.05`
    的正式口径，
    默认只能写成:
    - 暂行默认值
    - 当前候选对上相对稳健
  - 真正要讨论
    `1.05`
    是否合理，
    仍需:
    - 更多 family
    - 更多 checkpoint
    - 更多 low-activity probe
    共同回查
### 275. low-activity governance 如果在多 checkpoint 并列时还强行给单一 winner，会把“无法区分”误写成“某一步更优”
- 现象:
  - 本轮
    `36/48/60/72`
    四候选 probe
    显示:
    - `step36`
    - `step48`
    - `step60`
    在当前 6-record
      low-activity 切片上
      的核心指标完全并列
  - 如果 still
    只输出单一
    `best_fragmentation`
    或
    `worst_floor_leakage`
    branch，
    结果就会被字典序
    或遍历顺序
    偶然决定
- 风险:
  - 会把
    “当前 probe
    分不出来”
    误写成
    “当前 probe
    明确支持某一步”
- 处理要求:
  - 当前阶段
    low-activity governance
    对完全并列结果
    默认显式写成:
    - tie group
  - 不再把并列硬压成
    单 winner
### 276. 扩 checkpoint 覆盖不等于自动提升治理分辨率；如果新加入的 checkpoint 在现有低活动切片上是“指标克隆”，soft rerank 结论不会变
- 现象:
  - 本轮把
    `36`
    和
    `48`
    加回 low-activity probe
  - 但当前 decoded aggregate 上:
    - `36/48/60`
      的
      `fragmentation / active_fraction / alignment / excess`
      完全相同
  - 所以 ratio sweep
    虽然新增了:
    - `1.110966`
      和
      `1.259344`
      的入围点
  - 最终推荐仍没有变化
- 风险:
  - 如果只看
    “候选变多了，
    结果还是 `72`”，
    很容易误写成
    “当前策略已经跨更宽候选集稳健”
- 处理要求:
  - 当前看到这类现象时，
    默认先检查:
    - 新 checkpoint
      是否真的带来了
      新的 low-activity 信息
  - 若没有，
    下一步优先补:
    - 更广记录范围
    - 更多低活动窗口类型
    - 更能区分该族 checkpoint
      的指标
  - 不优先继续微调
    soft rerank
    权重
### 277. 如果 `6-record` 和 `validation12` 两轮扩样都显示同一组 checkpoint 的 low-activity 核心指标完全重合，就应默认把“分辨率不足”当成阶段性事实，而不是继续假设下一轮小调参会自己分开
- 现象:
  - 当前
    `activitygate72`
    family
    上，
    `36/48/60`
    在:
    - `6-record`
    - `validation12`
    两轮 low-activity probe
    里，
    都表现为:
    - `fragmentation = 0.0`
    - `active_fraction = 1.0`
    - `alignment / excess`
      完全相同
- 风险:
  - 如果在这种情况下
    还继续主要围绕
    当前四项权重
    做小调参，
    会把大量时间花在
    没有新增信息的参数面上
- 处理要求:
  - 当这种跨两轮复核的塌缩出现时，
    默认把问题重心切到:
    - 样本覆盖
    - 窗口类型
    - 新指标设计
  - 不再把
    “再微调一轮 soft rerank”
    当作默认主线
### 278. 当核心 low-activity 指标塌缩时，`mean_sample_delta_peak` 可以作为泄漏簇内部的次级平滑度排序，但不能误当作“更安静”或“更贴 target”的替代指标
- 现象:
  - 当前
    `validation12`
    probe
    上，
    `36/48/60`
    的:
    - fragmentation
    - active_fraction
    - alignment
    - excess
    完全重合
  - 但
    `mean_sample_delta_peak`
    仍给出较稳定排序:
    - `step60 < step48 < step36`
- 风险:
  - 如果直接把
    `sample_delta_peak`
    当成
    “更安静”
    或
    “更尊重原音量变化”，
    会把
    waveform edge roughness
    与
    low-activity leakage / alignment
    混为一谈
- 处理要求:
  - 当前阶段只把它作为:
    - 泄漏簇内部
      secondary smoothness sidecar
  - 只有在
    核心 low-activity
    指标已经塌缩时，
    才用它做次级排序
  - 不直接用它覆盖
    fragmentation /
    alignment /
    excess /
    active_fraction

### 279. 当 low-activity 的 frame-activity 指标在泄漏簇内全部饱和时，继续围绕 `active_fraction / activity_excess / alignment` 微调权重不会自己长出分辨率；需要回到 waveform 域补 `RMS` 这类泄漏强度 sidecar
- 现象:
  - 当前
    `validation12`
    low-activity
    probe
    上，
    `36/48/60`
    的:
    - `mean_active_fraction = 1.0`
    - `mean_activity_alignment_mae = 0.980059`
    - `mean_activity_excess_mean = 0.980059`
    完全重合
  - 但同一批窗口里，
    raw waveform
    的
    `mean_waveform_rms`
    仍稳定给出:
    - `step60 < step48 < step36`
- 风险:
  - 如果在这种 activity-bridge
    已饱和的状态下，
    还继续主要围绕
    `active_fraction`
    `activity_excess`
    的权重微调，
    会把
    “当前指标没信息”
    误当成
    “当前权重还不对”
  - 反过来，
    若把
    `waveform_rms`
    直接升格成
    新主目标，
    又会把
    leakage-strength
    与
    fragmentation
    风险
    混为一谈
- 处理要求:
  - 当前看到这类 activity 饱和时，
    默认先补:
    - `waveform_rms`
    - 或同类
      waveform-domain
      leakage-strength
      sidecar
  - 但该类指标
    默认只做:
    - 泄漏强度补充表达
    - tie group
      内部排序
  - 不直接覆盖:
    - fragmentation
    - alignment
    - excess

### 280. `waveform_rms` 虽然可以升为通用 leakage-strength sidecar，但不能因为它跨样本、跨音源都稳定，就把它误当成 fragmentation 或整体安全性的替代裁决器
- 现象:
  - 当前
    `waveform_rms`
    已在:
    - `6-record`
      四候选
    - `validation12`
      四候选
    - `60 vs 72`
      的
      `decoded / decoded_pitch_matched / audit_proxy`
    上都稳定给出
    一致 leakage-strength
    顺序
  - 但同一批
    `60 vs 72`
    对照里，
    fragmentation
    在:
    - `decoded`
    - `decoded_pitch_matched`
      上更支持
      `step60`
      安全
    - `audit_proxy`
      上甚至会偏向
      `step72`
      更安全
- 风险:
  - 如果只因为
    `waveform_rms`
    更稳定，
    就把它上升成
    “谁整体更安全”
    的裁决器，
    会把
    residual leakage strength
    和
    burst / toggle / fragmentation
    风险
    混成一条轴
  - 这会把
    `72`
    这种
    “泄漏更弱但 fragmentation 风险更高”
    的 checkpoint
    误写成
    单边更优
- 处理要求:
  - 当前阶段默认把
    `waveform_rms`
    写成:
    - 通用 leakage-strength sidecar
  - 默认不把它直接并入:
    - 主 soft rerank 权重
    - fragmentation 结论
    - overall safety
      结论
  - 汇报时必须显式分开写:
    - leakage-strength
    - fragmentation

### 281. 当治理制度已经是双轴时，如果正式产物仍只给一行压缩 summary，读者会自然把 tradeoff 误读成单一 winner；因此双轴口径必须模板化写进 probe 和 selection 输出
- 现象:
  - 在
    `waveform_rms`
    升级为
    通用 leakage-strength sidecar
    之后，
    实际制度已经变成:
    - fragmentation axis
    - leakage-strength axis
  - 但若产物只保留:
    - 一行 summary
    - 一段 branch aggregate
  - 读者仍很容易把
    “双轴 tradeoff”
    误读成
    “系统已经默认选出一个总 winner”
- 风险:
  - 会把
    `tradeoff`
    重新压回
    “单项最优”
    叙事
  - 进一步导致:
    - 报告间口径漂移
    - 人工听审目标错位
    - 后续 family
      误用单轴结论
- 处理要求:
  - 当前阶段默认要求
    probe
    和 selection
    都固定输出:
    - `fragmentation_axis`
    - `leakage_strength_axis`
    - `cross_axis_note`
    - `mode`
      (`convergent / partial_overlap / tradeoff`)
  - 不再允许只靠
    “读者自行综合”
    来恢复双轴制度

### 282. 当双轴治理已经模板化后，如果仍没有 fixed-format report 入口，后续 family 很容易重新退回“手工从 selection json 摘结论”的状态，导致口径再次漂移
- 现象:
  - 当前双轴制度
    已经写进:
    - probe
    - selection
  - 但如果没有
    单独的
    fixed governance report
    命令，
    后续 family
    仍可能回到:
    - 手工读 selection
    - 手工摘双轴结论
    - 手工再写专项报告
- 风险:
  - 会让:
    - 目录结构
    - 标题格式
    - 执行口径
    - 结论字段
    再次漂移
  - 也会让
    “这条线是否已有正式汇报入口”
    变得不确定
- 处理要求:
  - 当前阶段默认为
    Stage5 low-activity
    family
    保留:
    - 固定 report 命令
    - 固定模板
    - 固定 `stage_reports`
      输出目录
  - 后续扩新的
    low-activity family
    时，
    默认优先复用
    fixed report
    入口，
    而不是重新手写总结

### 283. 当听审交付已经依赖双轴治理时，如果 audit contract 里不显式挂上 fixed governance report，操作人仍会把这条线误看成“只需要开 GUI”
- 现象:
  - 当前
    Stage5 low-activity
    的正式判断，
    已经依赖:
    - fragmentation axis
    - leakage-strength axis
    - cross-axis note
  - 但如果听审契约
    只给:
    - bundle 路径
    - output 目录
    - 启动命令
  - 操作人仍会自然把它理解成:
    - “这是一次纯人工听感任务”
- 风险:
  - 会让听审时
    忽略:
    - 当前为什么是
      `tradeoff`
    - 当前一级问题
      和
      二级 fallback
      问题
      分别是什么
  - 也会让
    “先看量化 fixed report，
    再进 GUI”
    这条顺序
    重新丢失
- 处理要求:
  - 当前阶段只要
    听审任务
    建立在双轴治理之上，
    audit contract
    默认必须显式写出:
    - fixed governance report 路径
    - 当前 governance mode
    - 当前建议执行顺序

### 284. 当 GUI session 已启动但结果还停留在 `audio_audit_progress.json` 或原始 `audio_audit_review.json` 时，不能把这条线写成“听审结果已正式落盘”；还必须把 review 与 governance report 物化成 fixed audit result report
- 现象:
  - 当前
    `validation12`
    low-activity
    session
    里，
    只有:
    - `audio_audit_progress.json`
  - 尚未出现:
    - `audio_audit_review.json`
  - 即使后续
    review json
    已生成，
    如果不再继续物化，
    最终也仍只是:
    - GUI 原始导出
    - 不是正式汇报入口
- 风险:
  - 容易把
    “session 已启动”
    或
    “review json 已存在”
    误写成
    “听审结果已经正式收口”
  - 也会让
    人工听审结论
    再次脱离:
    - fragmentation axis
    - leakage-strength axis
    - cross-axis readout
    的固定口径
- 处理要求:
  - 当前阶段只有在同时满足以下条件时，
    才把听审结果写成
    “已正式落盘”:
    - `audio_audit_review.json`
      已生成
    - `materialize-stage5-low-activity-audit-result-report`
      已执行
    - fixed audit result report
      已落到
      `reports/stage_reports/`
  - 对
    `validation12`
    这条线，
    默认使用:
    - `scripts/materialize_stage5_low_activity_validation12_decoded_audit_result_report.ps1`
      做结果物化
  - 不再把:
    - `audio_audit_progress.json`
    - 或单独的
      `audio_audit_review.json`
    当作最终正式汇报入口

### 285. Windows 听审 GUI 下，深层候选 wav 绝对路径可能导致 `winsound` 静默失败；原音频能播不代表候选音频同样能播
- 现象:
  - 当前
    `validation12`
    low-activity
    听审里，
    原音频 clip
    绝对路径长度约:
    - `235`
  - 候选音频 clip
    绝对路径长度约:
    - `267`
  - 两者文件本身都存在，
    且候选 wav
    也是:
    - PCM16
    - RMS 正常
  - 但在
    Windows
    GUI
    里，
    会出现:
    - 原音频有声
    - 候选音频无声
    的用户侧现象
- 风险:
  - 容易误判为:
    - 模型输出静音
    - bundle 导出失败
    - 候选文件损坏
  - 实际上可能只是
    播放后端
    没成功打开
    过深路径
- 处理要求:
  - 听审 GUI
    默认不要直接把
    深层 bundle wav
    的原始绝对路径
    交给
    `winsound`
  - 应先把待播文件
    物化到:
    - 输出目录下的
      短路径缓存
    再播放
  - 当前修复已落到:
    - `src/v5vc/audio_audit_gui.py`

### 286. 听审 GUI 不能默认假设屏幕高度足以完整容纳右侧详情区；如果右侧面板本身不可滚动，下方备注区会直接掉出屏幕，导致流程卡死
- 现象:
  - 当前听审 GUI
    右侧会同时堆叠:
    - 播放区
    - 评分区
    - 帮助区
    - 单条备注
    - 会话备注
  - 在较矮屏幕上，
    下方备注区
    会溢出可见范围
  - 同时左侧记录列表
    若无滚动条，
    也会出现
    可见范围不足
- 风险:
  - 用户无法滚到
    备注区输入
  - 左侧记录也无法完整浏览
  - 最终会把
    GUI
    误判成
    “功能坏了”，
    实际上是
    布局没有给出滚动出口
- 处理要求:
  - 左侧记录列表
    默认必须带独立滚动条
  - 右侧详情区
    默认必须支持整体纵向滚动，
    不能只依赖
    文本框自身滚动
  - `单条备注`
    与
    `本次会话备注`
    文本框
    也应各自保留
    内部滚动条
  - 当前修复已落到:
    - `src/v5vc/audio_audit_gui.py`

### 287. 听审 GUI 左侧记录区如果是固定宽度，会把长 record id / 实验名截断到不可操作；这不是单纯的显示问题，而是会直接削弱人工听审定位能力
- 现象:
  - Stage5
    的记录标签、
    bundle 名和
    checkpoint 名
    普遍较长
  - 如果左侧区域
    宽度写死，
    用户会持续遇到:
    - 记录名看不全
    - 实验名看不全
    - 只能靠猜
      当前选中项
- 风险:
  - 容易误点
    记录
  - 也不利于
    将当前试听对象
    与文档里的
    record id
    对上
- 处理要求:
  - 主布局
    默认应支持
    横向可拖拽分栏，
    让左侧记录区
    可按需要拉宽
  - 当前修复已落到:
    - `src/v5vc/audio_audit_gui.py`

### 288. 即使人工听审主观结论已经高度一致，也不能把“没导出 review json”当成无关细节；否则后续只能写摘要，不能物化 fixed audit result report
- 现象:
  - 本轮
    `validation12`
    听审里，
    用户已经给出
    很清晰的一致结论:
    - `36 -> 72`
      底噪单调递减
    - forced choice
      选
      `72`
  - 但当前 session
    仍没有:
    - `audio_audit_review.json`
- 风险:
  - 这会导致
    后续只能写:
    - 人工听审摘要
  - 不能直接物化:
    - fixed audit result report
  - 也无法保留:
    - field aggregate
    - comparable / noncomparable
    - cross-axis readout
    这些结构化产物
- 处理要求:
  - 即使结论已经一致，
    也仍建议最终补一次:
    - GUI 导出
      `audio_audit_review.json`
  - 否则汇报口径必须明确写成:
    - 人工听审摘要
    - 而不是
      fixed-format
      audit result report

### 289. “底噪更弱”和“关键节点毛刺更少”在人耳上是两条独立轴；forced choice 选 `72` 不等于 `72` 在所有局部问题上都更安全
- 现象:
  - 本轮用户直接反馈:
    - `36/48/60/72`
      底噪强度
      单调递减
    - 但在
      清辅音渐变消失 /
      呼吸声
      这些代表性问题节点上，
      `60`
      与
      `72`
      都会出现
      相近程度的
      剧烈毛刺
    - 同时
      `36/48`
      在对应位置
      更正常
- 风险:
  - 如果只看到
    forced choice
    最后仍选
    `72`，
    就把它误写成
    “72 在局部安全性上也全面更优”，
    会把
    两条听感轴
    又压回单 winner
- 处理要求:
  - 后续汇报时，
    默认拆开写:
    - noise-floor / leakage-strength
    - local glitch / burst risk
  - 当前对
    `72`
    的正式口径应写成:
    - 四者里
      最合适的临时锚点
    - 但仍存在
      特定问题节点上的
      明显毛刺

### 290. 从 `36 -> 72` 的“频带更宽、听起来没那么刺耳”说明当前人耳还在感知一条独立于 low-activity 核心指标的频谱轴；如果后续完全不补频谱 sidecar，会丢掉一条真实的选择依据
- 现象:
  - 用户额外观察到:
    - 从
      `36`
      到
      `72`
    - 音频频带越来越宽
    - 听起来越来越不刺耳
- 风险:
  - 当前 low-activity
    量化治理
    主要覆盖:
    - fragmentation
    - alignment
    - excess
    - active_fraction
    - waveform_rms
  - 如果后续完全忽略
    这条频谱轴，
    会让
    主观上非常明显的
    “没那么刺耳 / 更开阔”
    缺少量化表达
- 处理要求:
  - 后续若继续扩
    Stage5 sidecar，
    可考虑补:
    - 频带宽度
    - 高频展开
    - 刺耳感相关
      的频谱指标
  - 但当前阶段
    先把它记为:
    - 新观察到的
      独立听感轴
    - 暂不直接替代
      low-activity
      双轴治理

### 291. 在 low-activity 片段上直接看绝对 centroid / 绝对高频能量，容易把高底噪 checkpoint 误判成“频带更宽”；这类频谱 sidecar 应优先做 target-relative gap，而不是只看 candidate 本身
- 现象:
  - 本轮实际试算时，
    若直接看
    absolute spectral centroid /
    high-frequency energy，
    `36`
    这类底噪更重的 checkpoint
    会因为
    高频噪声更多，
    看起来像
    “更宽”
- 风险:
  - 这种读法
    会把
    floor noise
    当成
    谱形优势，
    从而和人耳感受
    直接打架
- 处理要求:
  - 后续在
    low-activity
    家族里补
    频谱 sidecar
    时，
    默认优先使用:
    - candidate 相对
      aligned_target
      的 spectral gap
  - 例如:
    - centroid gap
    - bandwidth gap
    - rolloff gap
    - hf-ratio gap
  - 不要只看
    candidate
    的绝对高频量

### 292. `predicted_activity_gate` 在 low-activity 上若按逐帧硬乘直接重建，确实会压 leakage，但也会把边界毛刺一起放大；这类问题第一反应应是“先做 smoothing”，而不是直接关 gate
- 现象:
  - 本轮
    `step72`
    三条代表性 glitch record
    ablation
    显示:
    - 关 gate
      后，
      fragmentation
      会显著下降
    - 但
      `decoded_to_target_rms_ratio`
      明显反弹
- 风险:
  - 如果只盯
    glitch
    本身，
    很容易得出
    “那就把 gate 关了”
    的错误结论
- 处理要求:
  - 对这类
    gate-induced
    glitch，
    默认先尝试:
    - smoothing-only
  - 不要把
    “关 gate”
    当成首选修复

### 293. `predicted_activity_gate_floor` 虽然能把 fragmentation 很快压平，但也可能把低活动段重新推回“常亮低电平泄漏”；如果 active_fraction / alignment 同时塌回去，说明这是过修
- 现象:
  - `step72`
    smoothing + floor
    实验里，
    fragmentation
    可快速降到
    `0.0`
  - 但同时:
    - `mean_active_fraction`
      回到
      `1.0`
    - `mean_activity_alignment_mae`
      也回到
      高泄漏簇水平
- 风险:
  - 如果只看
    “毛刺没了”，
    会误把
    “常亮低电平”
    当成成功修复
- 处理要求:
  - 任何
    gate floor
    方案，
    都必须同时检查:
    - fragmentation
    - active_fraction
    - alignment_mae
    - waveform_rms
  - 若 floor
    让
    active_fraction
    重新塌回
    `1.0`，
    默认判为
    过修
