# 2026-03-24 端到端 VC demo buzz 来源复盘与真实可听 smoke 计划

## 结论
- 当前 `run-offline-mvp-teacher-first-vc-demo`
  导出成 buzz，
  根因不在：
  - wav 写盘
  - OLA apply mode
  - predicted gate 开关
- 更准确的根因链条是：
  1. 当前用户线喂给 Stage5 的并不是设计态 vocoder 语义，
     而是一组缺少
     `f0_hz / r_res / final_vocoder_waveform`
     的 proxy 控制；
  2. 当前 Stage5 训练主线也没有用真实 source-driven path 训练，
     而是把同一条 target audio
     同时当 teacher 输入和训练 target；
  3. 当前 no-res waveform head
     与
     `L1 + single-resolution log-STFT + RMS guard`
     目标
     允许模型长期停在
     `template-buzz + envelope-following`
     假解里。
- 所以：
  - `teacher_first_vc_demo`
    现在导出的 buzz
    不是 export bug，
    而是当前 contract/scaffold/train-objective/checkpoint
    共同产出的真实失败形态。

## 本轮顺着端到端 demo 读到的代码事实

### 1. 用户线 demo 的最终导出非常直接
- `src/v5vc/teacher_first_vc_demo.py`
  里
  `run_offline_mvp_teacher_first_vc_demo(...)`
  做的事是：
  1. 导出 teacher downstream contract
  2. 构建 consumer-side scaffold
  3. 从 Stage5 checkpoint
     加载
     `NoResidualSourceFilterVocoderScaffold`
  4. 前向得到
     `waveform_frames`
  5. 用
     `reconstruct_waveform_from_frames(...)`
     做 overlap-add
  6. 直接写
     `decoded.wav`
- 关键代码点：
  - `teacher_first_vc_demo.py:421-493`
- 这说明：
  - 当前导出链没有额外的“神秘后处理”；
  - 导出的 buzz
    就是当前 checkpoint
    对当前 scaffold
    的直接解码结果。

### 2. teacher contract 明确缺少设计态关键语义
- `src/v5vc/offline_teacher_downstream_contract.py`
  明确把以下项标成缺失：
  - `f0_hz`
  - `r_res`
  - `final_vocoder_waveform`
- 关键代码点：
  - `offline_teacher_downstream_contract.py:232-249`
- 当前实际提供的是：
  - `z_art`
  - `event_probs`
  - `energy_log / abs_mean / zero_cross_rate / delta_energy`
  - 以及从它们导出的：
    `energy_proxy / voiced_proxy / aperiodicity_proxy / event_presence_proxy / energy_change_proxy`
- 也就是说：
  - 当前用户线并没有把
    “显式周期结构 + 残差噪声结构”
    交给 vocoder，
  - 而是在用一组代理控制量
    近似替代。

### 3. scaffold 用 proxy 直接拼成分支输入，并把缺失设计键硬置空
- `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  当前：
  - periodic branch
    只拼：
    `z_art + voiced_proxy + energy_proxy + alpha + s_spk_target + s_geom_target`
  - noise branch
    只拼：
    `event_probs + aperiodicity_proxy + event_presence_proxy + energy_change_proxy + energy_proxy + alpha + s_spk_target`
  - `f0_hz`
    被补成全零
  - `r_res`
    被补成空张量
- 关键代码点：
  - `offline_teacher_vocoder_input_scaffold.py:48-61`
  - `offline_teacher_vocoder_input_scaffold.py:63-79`
  - `offline_teacher_vocoder_input_scaffold.py:102-128`
- 这说明：
  - 当前 source-driven demo
    从进入 Stage5 之前，
    语义就已经和设计态 vocoder contract
    有明显缺口。

### 4. Stage5 训练 package 不是 source-to-target，而是 target self-reconstruction
- `src/v5vc/offline_vocoder_training.py`
  的
  `build_dataset_packages_for_split(...)`
  当前逻辑是：
  - 对 target split
    里的
    `audio_path`
    调
    `export_offline_mvp_teacher_downstream_contract(input_audio_path=audio_path, ...)`
  - 然后再把同一条
    `audio_path`
    作为
    `target_audio_path`
    构建训练 target
- 关键代码点：
  - `offline_vocoder_training.py:1214-1241`
- 所以当前 Stage5 训练看到的是：
  - target audio
    经过 teacher runtime
    生成的控制
    -> 再去重建同一条 target audio
- 这直接解释了：
  - 为什么此前
    `export-offline-mvp-nores-vocoder-audio`
    的 bundle
    不能代表真实 user-line；
  - 也解释了
    source-driven demo
    为什么更容易出分布外行为。

### 5. 模型结构本身就是“每帧生成波形模板，再 OLA”
- `src/v5vc/offline_vocoder_scaffold.py`
  中，
  `NoResidualSourceFilterVocoderScaffold`
  的 waveform 路径就是：
  - 两路 encoder
  - fusion
  - `waveform_decoder`
    直接输出每帧长度的 waveform
  - `torch.tanh(...)`
- 关键代码点：
  - `offline_vocoder_scaffold.py:29-45`
  - `offline_vocoder_scaffold.py:51-66`
- 之后在
  `offline_vocoder_training.py:1387-1452`
  里再用 Hann window overlap-add
  重建整条音频。
- 这类结构如果 loss
  不够强，
  非常容易学成：
  - “每帧都像同一个模板”
  - 只靠 gate / 包络
    控制强弱起伏

### 6. 训练 loss 现在确实允许这种假解活下来
- `src/v5vc/offline_vocoder_training.py`
  里的
  `compute_nores_vocoder_losses(...)`
  目前核心 waveform 约束是：
  - `loss_waveform`
  - `loss_stft`
  - `loss_rms_guard`
- 关键代码点：
  - `offline_vocoder_training.py:1645-1753`
- 而
  `docs/259`
  对应的 probe
  与
  `src/v5vc/stage5_waveform_objective_collapse_probe.py`
  已经给出构造性反例：
  - 固定模板
    + 目标 RMS 包络
    也能拿到比 baseline 更低的 waveform objective
- 也就是：
  - 当前 objective
    并没有强力要求
    “真实语音短时结构多样性”
  - 它更像是在奖励：
    - 包络别错太多
    - 粗频谱别太离谱
    - 全局 RMS 别差太远

## 当前对 buzz 来源的最终归因

### 不是主因的项
- 不是：
  - `post_ola_envelope`
    与
    `pre_overlap_add`
    的 apply-mode 选择
- 不是：
  - predicted activity gate
    开或关
- 不是：
  - export manifest / GUI
    播放路径搞错

### 主因链
1. source-driven user-line
   输入 contract
   语义缺关键设计键，
   只能用 proxy 拼 scaffold；
2. 当前 Stage5 checkpoint
   训练时又没见过真实 source-driven path，
   只见过 target-derived control 的 self-reconstruction；
3. 当前 waveform head
   与 objective
   允许
   `固定模板 + 包络跟随`
   长期作为低分路线存在；
4. 因此真正导出时，
   模型稳定产出的是
   template-buzz，
   export 只是在忠实写出这个结果。

## 真实可听 smoke 的目标重写
- 后续不应再把
  “命令成功 + 导出 wav”
  当作 smoke 成功。
- 新 smoke
  必须回答两件事：
  1. 整条 demo 流水线是否真的跑通
  2. 交付给人耳的主试听对象里，
     至少有明确的
     非 buzz、
     可辨识语音
     正样本

## 建议的新 smoke 设计

### 方案名
- `teacher-first audible smoke bundle`

### 核心原则
- 把
  “工程通路是否打通”
  和
  “当前 Stage5 decoded
   是否已经可听”
  明确拆开；
- 每次 smoke
  固定导出：
  - 正控制可听音频
  - 当前实验 decoded
  - 明确的 pass/fail 口径

### bundle 最少包含 4 条音频
1. `source_input.wav`
   - 原始输入音频直接复制或标准化重写
   - 作用：
     保证 smoke bundle
     本身一定有一条可听语音，
     同时校验输入读写链
2. `target_reference.wav`
   - 固定单目标预设附带的一条目标说话人参考音频
   - 作用：
     保证 bundle
     里有一条明确的“目标音色参考”
3. `decoded_experimental.wav`
   - 当前
     `run-offline-mvp-teacher-first-vc-demo`
     的真实输出
   - 作用：
     继续观察当前 Stage5 路线是否仍为 buzz
4. `smoke_baseline_passthrough.wav`
   - 先用 source 直接过路写出，
     或做最小 loudness-normalized passthrough
   - 作用：
     验证 bundle 主听路径、
     GUI、
     manifest、
     听审会话
     本身没有问题

### 为什么要保留 passthrough 正控制
- 现在如果 bundle
  只有
  `decoded.wav`，
  那 smoke 成功
  只表示：
  - 文件存在
- 但人耳听到的可能还是一团 buzz
- 加入 passthrough 正控制后，
  smoke 至少能保证：
  - 这次交付给用户的 bundle
    里有真能听的东西
  - GUI / review 脚本
    没有把路径或播放对象搞错

## 建议的 smoke 验收口径

### A. 工程成功
- 必须满足：
  - `teacher_first_vc_demo.json`
    写出成功
  - `source_input.wav`
  - `target_reference.wav`
  - `smoke_baseline_passthrough.wav`
  - `decoded_experimental.wav`
    全部存在

### B. 可听成功
- 必须满足：
  - 三条正控制音频
    都是可辨识语音
  - 它们不能被写成
    current VC quality success
- 这层通过，
  只说明：
  - smoke bundle
    已具备真实听审价值

### C. 模型成功
- 单独判断：
  - `decoded_experimental.wav`
    是否不再触发
    `high_risk buzzing heuristics`
  - 并在固定 3 条 smoke case
    上至少通过一次人工试听
- 在这层通过前，
  禁止把整轮 smoke
  写成：
  - “VC demo 已可听”

## 固定 smoke case 建议
1. 常规语音片段
   - `data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav`
2. peak case
   - `data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav`
3. 高静音边界
   - `data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav`

## 当前最合理的落地顺序
1. 先把
   `teacher-first audible smoke bundle`
   做成正式脚本或正式 CLI
2. 先只交付：
   - 正控制可听音频
   - 当前 experimental decoded
   - 明确 summary
3. 后续只有当
   `decoded_experimental.wav`
   脱离 buzz
   后，
   才允许把它升级成
   smoke 主听对象

## 一句话结论
- 当前端到端 demo 导出成 buzz，
  根因已经收敛到：
  - proxy 化 contract/scaffold
  - target self-reconstruction 训练口径
  - waveform objective 允许 template-buzz
- 所以下一版 smoke
  不能再只盯着
  `decoded.wav`
  是否生成，
  而必须显式带上
  可听正控制，
  让 smoke 本身先变成
  “真正能听的交付物”。
