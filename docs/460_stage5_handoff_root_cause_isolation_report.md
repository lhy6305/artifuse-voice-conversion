# 460 Stage5 handoff root-cause isolation report

## 结论
- 这轮把 Stage5 fail-fast handoff 的根因范围明显压缩了。
- 当前最准确的判断是：
  - `event_family` 与 `aper` 确实会加重当前 buzz/template-collapse
  - `E_log_rms_norm` 不能直接拿掉，拿掉只会更差
  - `proxy_family` 在当前 student synthetic route 上基本不起作用
  - 但即使同时拿掉 `event_family + aper`，三条 route 仍然全部落在同一个 `auto_reject_obvious_buzz` 失败族
- 这说明：
  - 当前 buzz 不是“某一个 noise-side 控制族单独触发”的
  - 更像是 Stage5 decoder 在这条 student contract 下本身就有很强的 collapse attractor
  - `event/aper` 只是在调制这个 attractor 的严重程度，而不是唯一根因

## 对象
- 基础候选：
  - averaged checkpoint from
    - `vuvbalancedgate24`
    - `warm6_18.step15`
- 基础 handoff probe：
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/`
- Stage5 checkpoint family：
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
  - `selection_target = best_validation`

## A. 第一轮 family zero isolation

### 变体
- `event_family=zero`
- `aper=zero`
- `E_log_rms_norm=zero`
- `proxy_family=zero`

### `decoded_post_ola_gate` 聚合
- base
  - `centroid = 10169.897`
  - `high_band = 0.752179`
  - `template_cos = 0.943517`
  - `adjacent_cos = 0.997297`
  - `rms_corr = 0.900798`
  - `rms_cv = 0.196465`
- eventzero
  - `10044.574 / 0.753863 / 0.939788 / 0.997177 / 0.911484 / 0.195669`
- aperzero
  - `10138.567 / 0.750517 / 0.947786 / 0.99733 / 0.921948 / 0.164578`
- energyzero
  - `10553.553 / 0.786886 / 0.978184 / 0.998079 / 0.888553 / 0.20612`
- proxyzero
  - `10169.897 / 0.752179 / 0.943517 / 0.997297 / 0.900798 / 0.196465`

### 判断
- `event_family=zero`
  - 降低了 `centroid`
  - 降低了 `template_cos`
  - 提高了 `rms_corr`
  - 说明 `event_family` 是有害项
- `aper=zero`
  - 降低了 `high_band`
  - 明显提高了 `rms_corr`
  - 明显降低了 `rms_cv`
  - 但 `template_cos` 反而更高
  - 说明 `aper` 更像在推动 brightness / hiss / harshness，而不是唯一 collapse 源
- `E_log_rms_norm=zero`
  - 全面更差
  - 说明能量控制不是应该直接拿掉的项
- `proxy_family=zero`
  - 与 base 完全一致
  - 说明当前 synthetic route 下 proxy family 不是主要作用点

## B. 第二轮 timing-vs-magnitude isolation

### 变体
- `event_family=time_shuffle`
- `aper=time_shuffle`
- `event_family=zero + aper=zero`

### `decoded_post_ola_gate` 聚合
- eventshuffle
  - `10155.265 / 0.751314 / 0.943897 / 0.997234 / 0.894494 / 0.206009`
- apershuffle
  - `10191.177 / 0.755085 / 0.949869 / 0.995995 / 0.911062 / 0.183001`
- eventzero+aperzero
  - `10012.932 / 0.752247 / 0.94446 / 0.997216 / 0.931435 / 0.158367`

### 判断
- `event_family`
  - `zero` 明显优于 `time_shuffle`
  - 说明问题不只是时序对齐
  - 更像是这组 event 控制的存在/幅值本身在推动错误 decode
- `aper`
  - `zero` 也明显优于 `time_shuffle`
  - 说明 `aper` 的问题同样主要不是 timing
  - 而是数值本身在推动 brightness / collapse
- `eventzero + aperzero`
  - 是这轮里 `rms_corr` 最好的变体
  - `rms_cv` 也最低
  - 但 `template_cos` 仍然高
  - `high_band` 也没有真正脱离 buzz 族
  - 所以它只是“减轻症状”，没有改掉失败机理

## C. route-level check on `eventzero + aperzero`
- 三条 route：
  - `decoded_no_gate`
  - `decoded_pre_ola_gate`
  - `decoded_post_ola_gate`
- 全部仍为 `3/3 auto_reject_obvious_buzz`
- 这很关键：
  - 说明不是只有 `predicted_activity_gate` 或 `post_ola` 在放大问题
  - collapse 在更早阶段就已经存在

## D. broad family zero

### 变体
- `acoustic_state_family=zero`
- `conditioning_family=zero`

### `decoded_post_ola_gate` 聚合
- acousticzero
  - `10635.803 / 0.789293 / 0.985813 / 0.998198 / 0.930197 / 0.164725`
- conditioningzero
  - `11428.589 / 0.818738 / 0.905247 / 0.996857 / 0.912246 / 0.096908`

### 判断
- `acoustic_state_family=zero`
  - 直接把 brightness 和 template-collapse 推得更严重
  - 说明 periodic/voicing/energy 这组 state 不是多余项，至少对抑制更差 attractor 是有作用的
- `conditioning_family=zero`
  - 输出变得更亮、更高频
  - 虽然 `template_cos` 数值下降了一点
  - 但仍然是明显 buzz 族
  - 说明 conditioning 也不是简单应被拿掉的项

## 当前最准确的根因表述
- 当前 Stage5 failure 不应再表述成：
  - “student event 不对”
  - “aper 不对”
  - “gate 放大了问题”
- 更准确的说法应是：
  - Stage5 decoder 在当前 student contract 下有很强的默认 collapse attractor
  - `event_family` 与 `aper` 会把这个 attractor 再推坏
  - `energy / acoustic_state / conditioning` 虽然不完美，但不是可以直接移除的病灶
  - `proxy_family` 在这条 route 上基本没有形成有效影响

## 最终判断
- 当前已经找到“buzz 加重因子”，但还没有找到一个能把 route 打开的单点控制。
- 这轮后最合理的下一步不再是继续做 family zero/shuffle：
  - 应转去 Stage5 decoder-side / contract-side更深的 probe
  - 例如：
    - decoder hidden / logits / frames 哪一层开始模板化
    - `legacy_proxy` 目标合同是否本身把 student packet 映成了错误 attractor
    - 是否要为 student synthetic package 单独做更弱的 Stage5 contract，而不是复用当前 `legacy_proxy`
