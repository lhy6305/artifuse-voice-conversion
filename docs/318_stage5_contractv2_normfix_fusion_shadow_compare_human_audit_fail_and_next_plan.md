# 318. Stage5 `contractv2_normfix` fusion shadow compare 人工听审失败与下一步方案

## 结论
1. 用户已完成对以下四路 fixed-6 听审包的人工试听：
   - baseline:
     `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/baseline/`
   - `fusedbranch=0.15 + stft=0.55`:
     `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/fusedbranch015_stft055/`
   - `fusedbranch=0.20 + stft=0.575`:
     `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/fusedbranch020_stft0575/`
   - `fusedbranch=0.15 + stft=0.575`:
     `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_fusion_shadow_compare_round1_1/fusedbranch015_stft0575/`
2. 当前正式主观结论是：
   - **全部样本仍为纯 buzz**
   - **未出现任何像人声的部分**
3. 因而当前必须正式停下的不是：
   - “某一个 shadow 点”
4. 而是：
   - **整条 `fused_hidden_branch_mean + stft` loss-side 微调线**

## 一、这次听审意味着什么
1. 到
   `docs/314` ~ `docs/317`
   为止，
   这条线已经把几个事实确认得很清楚：
   - fusion-side `branch_mean`
     约束在当前强骨架上
     确实是有效的 objective-side Pareto 线
   - `waveform / stft`
     的税已经基本能被收回
   - 剩余矛盾收敛到了：
     - `rms_guard`
     - `decoded_to_target_rms_ratio`
2. 但本次人工听审把另一个更高优先级的事实钉死了：
   - **这些 objective-side 改善仍然不足以把系统推出 buzz-only 失败区**
3. 因此当前不能再把这条线解释成：
   - 只差更细 sweep
   - 或只差更久训练

## 二、为什么现在必须停掉这条微调线
1. 旧证据已经说明：
   - `branch_mean` loss-only
     听感失败
   - 线性
     `decoder_branch_mean_mix_alpha`
     forward-path
     也听感失败
2. 新证据又说明：
   - 在当前更强骨架上，
     即使把
     `fused_hidden_branch_mean + stft`
     调到非常细，
     仍然全部是纯 buzz
3. 所以现在最合理的判断已经不是：
   - “这个点还没调准”
4. 而是：
   - **单路 `fused_hidden` bottleneck + 轻量约束/线性混合**
     这一类方案，
     至少在当前 proxy contract 下，
     已没有继续微扫的价值

## 三、当前最合理的技术解释
1. `docs/299`
   和
   `docs/302`
   合起来已经给出一个更稳定的解释：
   - `fusion -> fused_hidden`
     是第一坍缩点
   - 但 decoder
     也已经围绕这个坏 manifold
     学到了一个稳定的 buzz 解
2. 这解释了为什么：
   - loss-side `branch_mean`
     有量化价值
   - 线性 forward-path mix
     也有量化价值
   - 但二者都不能把可听性推出
     pure buzz
3. 更准确的说法是：
   - 当前缺的不是
     “再把 `fused_hidden` 往 `branch_mean` 拉近一点”
   - 而是：
     **让 decoder 看到一种新的、非线性的、可稳态控制的 branch-conditioned 工作区**

## 四、下一步方案

### 主线方案：结构级 forward-path conditioning 最小验证
1. 当前最推荐的下一步不是继续改 loss，
   而是做一个新的结构分支：
   - 基于当前最强骨架：
     - `periodic_plus_noise_residual_shape_recurrent`
     - `periodic_waveform_frame_delta = 0.25`
     - `periodic_waveform_frame_adjacent_cosine = 0.01`
     - `periodic_waveform_frame_rms_floor = 0.65`
   - 新增**非线性 decoder conditioning**
2. 具体建议不是再做：
   - 固定 alpha 线性 mix
3. 而是做一个最小 learned adapter：
   - 输入：
     - `fused_hidden`
     - `branch_mean_hidden`
     - `fused_hidden - branch_mean_hidden`
   - 输出：
     - 一个逐帧 gate / residual correction
   - 形式上更像：
     - `decoder_input = fused_hidden + gate * adapter(...)`
     或
     - `decoder_input = (1-gate) * fused_hidden + gate * adapted_branch_mean`
4. 这个实验的目标不是：
   - 追求更多 objective 指标
5. 而是：
   - 验证“非线性、可控的 forward-path 干预”
     能否第一次让听感脱离 pure buzz

### 为什么这是下一步
1. 它直接回应了当前三条已知事实：
   - loss-only 不够
   - static linear mix 不够
   - 单纯继续扫 loss 权重也不够
2. 同时它仍保留了当前路线最有价值的先验：
   - fusion / branch-conditioned
     方向是对的

## 五、执行边界

### 立即停止的事
1. 停止继续扫：
   - `fused_hidden_branch_mean_weight`
   - `stft_weight`
   - 以及它们的同构交叉点
2. 停止把这条 loss-side 线继续写成：
   - near-success
   - 只差更细微调

### 下一轮只做的事
1. 只开一条新结构分支：
   - `branch-conditioned decoder adapter`
2. 只做最小 smoke：
   - 一个 baseline
   - 一个 adapter candidate
3. 只要 fixed-6 指标不明显退化到不可接受，
   就直接导 fixed-6 听审包
4. 不再允许：
   - 先扫 3 到 5 个结构超参
   - 再决定要不要听

## 六、若这条结构级 forward-path 仍失败
1. 如果新的 adapter 分支
   仍被人工听审判定为 pure buzz，
   那么当前应正式结束的不只是：
   - `branch_mean` 微调线
2. 而是：
   - **整个当前 proxy-contract no-res rescue 线**
3. 到那一步，
   下一主线应升级为：
   - `docs/280`
     里推荐的
     **方案 C**
   - 即：
     - Stage5 contract 升级到
       `F0 / vuv / aper / E`
       主语义
     - 重建 Stage5 package
     - 重训 no-res baseline

## 一句话结论
- 2026-03-24 这轮四路 fixed-6 听审已经把结论写死：
  当前 `fused_hidden_branch_mean + stft`
  微调线虽然 objective 上有推进，
  但可听性上仍全部是纯 buzz。
- 所以下一步不该再围着 loss 微调，
  而应直接做一次**非线性、结构级的 forward-path conditioning** 最小验证；
  若它仍失败，就正式切到
  Stage5 contract v2
  主线。
