# 205. Stage5 listening-audio-source GUI contract fix 报告

## 背景
- `docs/204_stage5_decoded_primary_listening_contract_report.md`
  已把 Stage5
  的正式口径
  改成:
  - 默认主听
    `decoded.wav`
  - `audit_proxy.wav`
    退到诊断位
- 同时 exporter
  也已经新增:
  - `listening_audio_source`
  - `listening_audio_path`
- 但接班复核时发现，
  GUI consumer
  侧还残留旧逻辑:
  - 只要记录里存在
    `decoded_audio_path`
  - 就无条件把它
    当成候选音频

## 问题本质
- 这不是
  “默认值写错”
  的问题
- 而是:
  - producer
    已经把
    “当前主听应该是谁”
    写进 manifest
  - consumer
    却没有真正
    按 manifest
    执行

所以在修复前，
更准确的状态是:
- 当前主线 bundle
  因为默认主听
  本来就是
  `decoded`
  所以表面上
  看不出问题
- 但一旦后续有人
  想显式切到:
  - `audit_proxy`
  做主听实验
- GUI
  实际上仍可能
  偷偷播放
  `decoded`

先说人话:
- 菜单上写着
  “这次主菜换了”，
  后厨也把单子改了，
  但服务员端上来的
  还是老菜。
- 这次修的是
  服务员真的按单上菜。

## 本轮修复

### 1. `src/v5vc/audio_audit_gui.py`
- 在
  `build_candidate_map`
  里新增:
  - 优先读取
    `listening_audio_path`
- 若新字段不存在，
  再按兼容回退逻辑
  处理:
  - `listening_audio_source = decoded`
    时，
    回退到
    `decoded_audio_path`
  - `listening_audio_source = audit_proxy`
    时，
    回退到
    `audit_proxy_audio_path`
  - 再不行，
    才沿用旧
    `decoded_audio_path` /
    `proxy_audio_path`
    逻辑

### 2. 修复后的契约
- 现在对 Stage5 nores vocoder bundle，
  GUI 的真实主听源顺序为:
  1. `listening_audio_path`
  2. 结合
     `listening_audio_source`
     的字段级回退
  3. 旧字段兼容回退

## 验证

### 1. 现有主线 bundle 函数级验证
- 读取:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1/proxy_audio_export.json`
- 结果:
  - `listening_audio_source = decoded`
  - GUI candidate
    解析到的
    仍是
    `decoded.wav`

### 2. `audit_proxy` 主听 smoke bundle
- 导出命令:

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt --split-name validation --target-record-ids target::chapter3_3_firefly_162 --sample-count 1 --output-dir tmp/stage5_listening_source_audit_proxy_smoke --activity-gate-weight 0.2 --use-predicted-activity-gate --listening-audio-source audit_proxy
```

- 生成结果确认:
  - `tmp/stage5_listening_source_audit_proxy_smoke/proxy_audio_export.json`
    中:
    - `listening_audio_source = audit_proxy`
    - `listening_audio_path`
      指向
      `audit_proxy.wav`

### 3. GUI smoke
- 验证命令:

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle tmp/stage5_listening_source_audit_proxy_smoke --output-dir tmp/stage5_listening_source_audit_proxy_gui_smoke --auto-close-ms 1000
```

- 结果:
  - `exit code 0`

## 当前判断

### 1. 这次修复不改变当前 Stage5 主线结论
- 当前默认主听
  仍应是:
  - `decoded.wav`
- `audit_proxy.wav`
  仍应是:
  - 动态 / 静音 / 边界
    诊断位

### 2. 这次修复的价值在于把“文档口径”变成“真实运行口径”
- 现在
  `--listening-audio-source`
  不再只是
  exporter 里的描述字段
- 而是真正会影响
  GUI 播放对象
  的端到端参数

### 3. 后续工作流要求
- 以后凡是
  manifest
  新增这类
  “consumer 依赖的语义字段”，
  不能只改导出端
  就算完成
- 必须至少补:
  - 一次 consumer
    侧路径验证
  - 一次 GUI
    可启动 smoke

## 一句话结论
- 本轮补上的不是新的听审策略，
  而是
  `listening_audio_source`
  的端到端真实性；
  修复后，
  Stage5 bundle
  中声明的主听源
  才会被 GUI
  真正执行。
