# 2026-03-24 teacher-first audible smoke 主听包与边界 probe 拆分报告

## 结论
- 本轮已根据试听反馈，
  把
  `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
  的默认行为拆成两类：
  - `main_listening`
    默认 profile
  - `boundary_probe`
    显式 profile
- 当前默认主听包
  不再混入
  `high_silence_segment_0061`
  这类近极端高静音 case
- 同时，
  当前默认 target reference
  也回到更正常的可听长度：
  - `3.0s`
  而不是之前为了快速 smoke
  人为截到
  `1.0s`

## 本轮代码变更
- 文件：
  - `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
- 新增参数：
  - `-BundleProfile main_listening|boundary_probe`
- 当前默认：
  - `main_listening`
- profile 语义：
  - `main_listening`
    - `regular_segment_0001`
    - `peak_011`
  - `boundary_probe`
    - `high_silence_segment_0061`

## 为什么要拆
- 用户实际试听后，
  反馈这批输出
  “要么静音要么极短且全 buzz”
- 重新核对 bundle
  后确认：
  - buzz
    的确仍是普遍现象
  - 但
    “极短/近静音”
    这部分，
    有一块是我把
    高静音边界 case
    直接混进了默认主听包
  - 另外，
    我当时为了快跑 smoke
    还把
    target reference
    截成了
    `1.0s`
- 这会导致：
  - 主听默认包
    自己也显得“很短”
  - 用户很难把：
    - 模型持续 buzz
    - 边界 case
      本来就接近静音
    这两件事分开判断

## 本轮验证

### 1. 默认主听包
```powershell
.\scripts\run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_main_listening_round1_1 `
  -Device cpu `
  -SkipFullPassVerify
```

### 结果
- summary:
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_main_listening_round1_1/teacher_first_vc_audible_smoke_bundle.json`
- 关键字段：
  - `case_count = 2`
  - `decoded_high_risk_count = 2`
  - `shared_target_reference.audio_sec = 3.0`
- 两条 case
  时长：
  - `regular_segment_0001`
    - source / passthrough:
      `1.53s`
    - decoded:
      `1.528333s`
  - `peak_011`
    - source / passthrough:
      `1.40s`
    - decoded:
      `1.398333s`

### 2. 边界 probe 包
```powershell
.\scripts\run_teacher_first_single_target_audible_smoke_bundle.ps1 `
  -BundleProfile boundary_probe `
  -OutputDir reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_boundary_probe_round1_1 `
  -Device cpu `
  -SkipFullPassVerify
```

### 结果
- summary:
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundle_boundary_probe_round1_1/teacher_first_vc_audible_smoke_bundle.json`
- 关键字段：
  - `case_count = 1`
  - `decoded_high_risk_count = 1`
  - `shared_target_reference.audio_sec = 3.0`
- 当前边界 case：
  - `high_silence_segment_0061`
    - source / passthrough:
      `0.510021s`
    - decoded:
      `0.508333s`

## 当前意义
- 现在默认主听包
  至少解决了两件事：
  1. 不再把近静音边界 case
     混成主听默认内容
  2. 不再把 target reference
     截得过短
- 但与此同时，
  主听包里的
  experimental decoded
  仍然全部是
  `high_risk buzz`
- 所以当前更准确的阶段表述应是：
  - 主听交付物结构
    已修正
  - 模型听感
    仍未修正

## 一句话结论
- 默认 audible smoke
  现在已经拆成
  “主听包”
  和
  “边界 probe 包”，
  主听默认不再混入高静音短样本；
  但这只修正了交付组织方式，
  没有改变当前 decoded
  仍是 buzz
  的模型事实。
