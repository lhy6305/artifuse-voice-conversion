# 2026-03-27 Stage5 noise-energy+aper alignment variant dataset smoke 报告

## 结论
- 我没有把
  `noise energy + aper`
  联动去耦
  只停留在 probe 结论，
  而是已经把它落成
  一个可被现有 Stage5 训练 loop
  直接消费的候选数据集入口
- 新命令：
  - `materialize-offline-mvp-teacher-first-stage5-input-variant-dataset`
- 这条命令已经完成一次小规模 smoke：
  - 物化了
    `aper=time_shuffle + noise_E_log_rms_norm=time_shuffle`
    的 package 变体数据集
  - 然后用现有
    `run-offline-mvp-nores-vocoder-dataset-training-loop`
    在 CPU 上跑通了
    `1 step`

## 一、代码
- 入口与调度：
  - [cli.py](F:\proj_dev\tmp\workdir4\src\v5vc\cli.py)
- 物化实现与已有 probe 复用：
  - [teacher_first_vc_demo.py](F:\proj_dev\tmp\workdir4\src\v5vc\teacher_first_vc_demo.py)

这个新入口的作用是：
- 读取现有
  Stage5 dataset index
- 对 package `inputs`
  直接应用
  probe 已验证过的
  family override
- 写出一个替代 dataset index，
  让现有训练 loop
  无需改动就能直接训练

## 二、候选数据集 smoke
- 源索引：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 变体索引：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_inputvariant_noiseenergy_apershuffle_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 这次 smoke
  只物化了：
  - `2` 个 train packages
  - `1` 个 validation package
- 固化进去的输入变体是：
  - `aper = time_shuffle`
  - `noise_E_log_rms_norm = time_shuffle`

## 三、训练 loop smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_inputvariant_noiseenergy_apershuffle_smoke_round1_1/`
- 关键结果：
  - `device = cpu`
  - `num_steps = 1`
  - `packages_per_step = 1`
  - `loss_total = 1.801013`
  - latest checkpoint:
    - `checkpoints/offline_mvp_nores_vocoder_dataset_loop.step1.pt`

读法：
- 这一步不是要证明
  候选已经有效，
  而是证明：
  - 当前最小候选
    已经从 user-line probe
    结论
    成功转成了
    一个现有训练基础设施
    能直接消费的训练入口

## 四、当前状态
- 到这一层为止，
  主线已经收敛成：
  1. 训练/结构候选
     不再泛写成
     `energy family`
  2. 当前最小候选就是：
     - `noise_E_log_rms_norm`
       与
       `aper`
       的联动时间对齐去耦
  3. 这条候选
     已经具备：
     - package 物化入口
     - 训练 loop smoke

## 一句话结论
- 当前主线已经从“诊断”推进到“可训练候选落地”：
  - `noise energy + aper`
    的联动 time-shuffle
    数据集变体已可物化，
  - 且现有 Stage5 dataset training loop
    已在该变体上 smoke 跑通。 
