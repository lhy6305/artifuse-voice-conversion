# offline MVP final experiment comparison

- experiment_count: 5
- route_context: {'route_selection_path': 'F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_default_minimax/anchor_route_selection.json', 'inputs': {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}, 'selected_policy': 'default_minimax', 'selected_anchor_id': 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration'}

## leaders
- validation: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927)
- special: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)
- zero_e_evt: EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration (val=2.442393, special_delta=0.143828, zero_e_evt=3.299576, zero_z_art=0.434057)
- zero_z_art: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259)

## rows
- EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927) [vs_route={'target_validation_loss_total': -0.047019, 'delta_loss_total': 0.031768, 'zero_e_evt_delta_target_loss_total': -0.320554, 'zero_z_art_delta_target_loss_total': -0.074009}]
- EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration: EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration (val=2.442393, special_delta=0.143828, zero_e_evt=3.299576, zero_z_art=0.434057) [vs_route={'target_validation_loss_total': -0.001801, 'delta_loss_total': 0.003827, 'zero_e_evt_delta_target_loss_total': 0.000541, 'zero_z_art_delta_target_loss_total': -0.004879}]
- EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration: EXP-20260315-048-offline-mvp-d31-round1-1-d7-init-d10-teacher-consistency-acoustic-30step-calibration (val=2.442793, special_delta=0.142472, zero_e_evt=3.298481, zero_z_art=0.436225) [vs_route={'target_validation_loss_total': -0.001401, 'delta_loss_total': 0.002471, 'zero_e_evt_delta_target_loss_total': -0.000554, 'zero_z_art_delta_target_loss_total': -0.002711}]
- EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [route_anchor] [vs_route={'target_validation_loss_total': 0.0, 'delta_loss_total': 0.0, 'zero_e_evt_delta_target_loss_total': 0.0, 'zero_z_art_delta_target_loss_total': 0.0}]
- EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration: EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration (val=2.523898, special_delta=0.117894, zero_e_evt=3.27265, zero_z_art=0.460259) [vs_route={'target_validation_loss_total': 0.079704, 'delta_loss_total': -0.022107, 'zero_e_evt_delta_target_loss_total': -0.026385, 'zero_z_art_delta_target_loss_total': 0.021323}]

## notes
- Rows are sorted by final target validation loss, then special delta, then e_evt.
- When route_context is present, delta_vs_route_anchor compares each final experiment against the selected route anchor.
