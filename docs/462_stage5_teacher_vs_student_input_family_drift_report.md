# 462 Stage5 teacher vs student input-family drift report

## 结论
- 当前 fixed Stage5 handoff 中，teacher 和 student package 的 `conditioning` 族并没有差异。
  - `alpha`
  - `s_spk_target`
  - `s_geom_target`
  - 在 3 条对照记录上都是逐项一致。
- 差异几乎全部集中在动态控制族，而不是静态条件族。
  - 最大 drift: `noise:e_evt`
  - 其次是 `periodic/noise:vuv`
  - 然后是 `periodic:f0_hz_log_norm`
  - 再后是 `periodic/noise:E_log_rms_norm`
  - `noise:aper` 有中等 drift
  - `periodic:z_art` 反而很小
- 这和前面的 handoff / structure 诊断是闭环的。
  - teacher 和 student 在同一 Stage5 ckpt 下都 still buzz
  - 但 student hidden/template collapse 更重
  - 而输入统计显示真正把 student 拉离 teacher manifold 的，主要不是 speaker/geom/alpha，也不是大幅错误的 `z_art`
  - 而是 `e_evt + vuv + f0 + energy` 这一组动态控制

## 对象
- student package root:
  - `reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/packages/validation`
- teacher counterpart root:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_packages_teacher_validation3_counterpart_round1_1/packages/validation`
- records:
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

## family layout
- `periodic_branch_features` dim layout:
  - `z_art = 8`
  - `f0_hz_log_norm = 1`
  - `vuv = 1`
  - `E_log_rms_norm = 1`
  - `alpha = 1`
  - `s_spk_target = 16`
  - `s_geom_target = 8`
- `noise_branch_features` dim layout:
  - `e_evt = 8`
  - `aper = 1`
  - `vuv = 1`
  - `E_log_rms_norm = 1`
  - `alpha = 1`
  - `s_spk_target = 16`
  - `s_geom_target = 8`

## 3-record aggregate family drift
- columns:
  - `mean_abs_diff`
  - `rmse`
  - `cosine`
  - `student_mean`
  - `teacher_mean`
  - `student_std`
  - `teacher_std`

| family | mean_abs_diff | rmse | cosine | student_mean | teacher_mean | student_std | teacher_std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `periodic:z_art` | 0.032139 | 0.038262 | 0.998771 | -0.138288 | -0.155392 | 0.616391 | 0.634407 |
| `periodic:f0_hz_log_norm` | 0.183166 | 0.303838 | 0.900204 | 0.709308 | 0.607156 | 0.067290 | 0.264819 |
| `periodic:vuv` | 0.186788 | 0.269177 | 0.930370 | 0.741709 | 0.656085 | 0.232243 | 0.325681 |
| `periodic:E_log_rms_norm` | 0.129393 | 0.185290 | 0.971841 | 0.687085 | 0.707125 | 0.293198 | 0.368711 |
| `periodic:alpha` | 0.000000 | 0.000000 | 1.000025 | 1.150000 | 1.150000 | 0.000000 | 0.000000 |
| `periodic:s_spk_target` | 0.000000 | 0.000000 | 0.999999 | -0.074922 | -0.074922 | 0.399750 | 0.399750 |
| `periodic:s_geom_target` | 0.000000 | 0.000000 | 1.000006 | -0.000000 | -0.000000 | 0.427149 | 0.427149 |
| `noise:e_evt` | 0.206598 | 0.248894 | 0.735822 | 0.230432 | 0.246784 | 0.252184 | 0.239077 |
| `noise:aper` | 0.118243 | 0.181676 | 0.898682 | 0.314089 | 0.312219 | 0.286423 | 0.343001 |
| `noise:vuv` | 0.186788 | 0.269177 | 0.930370 | 0.741709 | 0.656085 | 0.232243 | 0.325681 |
| `noise:E_log_rms_norm` | 0.129393 | 0.185290 | 0.971841 | 0.687085 | 0.707125 | 0.293198 | 0.368711 |
| `noise:alpha` | 0.000000 | 0.000000 | 1.000025 | 1.150000 | 1.150000 | 0.000000 | 0.000000 |
| `noise:s_spk_target` | 0.000000 | 0.000000 | 0.999999 | -0.074922 | -0.074922 | 0.399750 | 0.399750 |
| `noise:s_geom_target` | 0.000000 | 0.000000 | 1.000006 | -0.000000 | -0.000000 | 0.427149 | 0.427149 |

## record-level top drifts
- `target::chapter3_3_firefly_162`
  - `noise:e_evt`
    - `mad = 0.198363`
    - `rmse = 0.240013`
    - `cos = 0.761366`
  - `periodic/noise:vuv`
    - `mad = 0.105397`
    - `rmse = 0.174206`
    - `cos = 0.977395`
  - `periodic/noise:E_log_rms_norm`
    - `mad = 0.100140`
    - `rmse = 0.163388`
    - `cos = 0.982654`
- `target::chapter3_3_firefly_138`
  - `periodic:f0_hz_log_norm`
    - `mad = 0.220211`
    - `rmse = 0.324299`
    - `cos = 0.876127`
  - `periodic/noise:vuv`
    - `mad = 0.205417`
    - `rmse = 0.309687`
    - `cos = 0.922806`
  - `noise:e_evt`
    - `mad = 0.203390`
    - `rmse = 0.244946`
    - `cos = 0.745181`
  - `noise:aper`
    - `mad = 0.136984`
    - `rmse = 0.197469`
    - `cos = 0.891937`
- `target::chapter3_4_firefly_106`
  - `periodic/noise:vuv`
    - `mad = 0.249551`
    - `rmse = 0.323639`
    - `cos = 0.890910`
  - `periodic:f0_hz_log_norm`
    - `mad = 0.233551`
    - `rmse = 0.376334`
    - `cos = 0.869437`
  - `noise:e_evt`
    - `mad = 0.218042`
    - `rmse = 0.261722`
    - `cos = 0.700920`
  - `periodic/noise:E_log_rms_norm`
    - `mad = 0.160311`
    - `rmse = 0.209051`
    - `cos = 0.956799`

## interpretation
- `conditioning` 完全一致，直接排除了：
  - speaker embedding mismatch
  - geom embedding mismatch
  - alpha mismatch
- `z_art` drift 很小，说明 student->Stage5 的主要问题也不是 articulation latent 整体崩坏。
- `noise:e_evt` 是最值得优先处理的族：
  - aggregate `cosine = 0.735822`
  - 是所有 family 里最不像 teacher 的
  - 这和前面 family zero probe 里 `event_family=zero` 能减轻 buzz 是一致的
- `vuv` 与 `f0_hz_log_norm` 也有显著 drift：
  - `vuv` aggregate `mad = 0.186788`
  - `f0_hz_log_norm` aggregate `mad = 0.183166`
  - 这解释了为什么只动 `event/aper` 不能真正打开 route，因为 periodic side 的 voicing/f0 manifold 也在偏
- `E_log_rms_norm` 和 `aper` 是次级但真实存在的 drift：
  - 它们更像是在和上面的 `e_evt/vuv/f0` 一起，把 decoder 推向错误 operating region

## updated next step
- 下一步不该继续碰 supervision-side contract 名字。
- 更合理的最小 probe 顺序是：
  1. 对真正进入 fixed Stage5 forward 的 `noise:e_evt` 做 `reference_mean / affine_match / partial swap`
  2. 再对 `periodic/noise:vuv` 与 `periodic:f0_hz_log_norm` 做同口径 override
  3. 只在前两步有明显正反馈时，再处理 `E_log_rms_norm` 与 `aper`
- 换句话说，下一条主线已经很明确：
  - `先修输入流形偏移最大的动态控制族`
  - 而不是继续做新的 Stage3 loss 搜索或继续改 Stage5 supervision-side target contract
