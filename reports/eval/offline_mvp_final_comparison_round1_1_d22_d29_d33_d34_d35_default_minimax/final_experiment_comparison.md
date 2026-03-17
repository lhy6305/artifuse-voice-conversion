# offline MVP final experiment comparison

- experiment_count: 5
- route_context: {'route_selection_path': 'F:/proj_dev/tmp/workdir4/reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_default_minimax/anchor_route_selection.json', 'inputs': {'max_validation_budget_over_best': 0.05, 'special_priority': False, 'z_art_priority': False, 'require_best_e_evt_floor': False, 'require_best_z_art_floor': False}, 'selected_policy': 'default_minimax', 'selected_anchor_id': 'EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration'}

## leaders
- validation: EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration (val=2.3506, special_delta=0.201536, zero_e_evt=2.633041, zero_z_art=0.310002)
- special: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- zero_e_evt: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)
- zero_z_art: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828)

## rows
- EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration: EXP-20260315-051-offline-mvp-d34-round1-1-d22-init-d33-teacher-cross-anchor-fused-hidden-20step-calibration (val=2.3506, special_delta=0.201536, zero_e_evt=2.633041, zero_z_art=0.310002) [vs_route={'target_validation_loss_total': -0.093594, 'delta_loss_total': 0.061535, 'zero_e_evt_delta_target_loss_total': -0.665994, 'zero_z_art_delta_target_loss_total': -0.128934}]
- EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration: EXP-20260315-052-offline-mvp-d35-round1-1-d33-init-d22-teacher-cross-anchor-fused-hidden-20step-calibration (val=2.395609, special_delta=0.173543, zero_e_evt=2.967455, zero_z_art=0.361794) [vs_route={'target_validation_loss_total': -0.048585, 'delta_loss_total': 0.033542, 'zero_e_evt_delta_target_loss_total': -0.33158, 'zero_z_art_delta_target_loss_total': -0.077142}]
- EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration (val=2.397175, special_delta=0.171769, zero_e_evt=2.978481, zero_z_art=0.364927) [vs_route={'target_validation_loss_total': -0.047019, 'delta_loss_total': 0.031768, 'zero_e_evt_delta_target_loss_total': -0.320554, 'zero_z_art_delta_target_loss_total': -0.074009}]
- EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration: EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration (val=2.444194, special_delta=0.140001, zero_e_evt=3.299035, zero_z_art=0.438936) [route_anchor] [vs_route={'target_validation_loss_total': 0.0, 'delta_loss_total': 0.0, 'zero_e_evt_delta_target_loss_total': 0.0, 'zero_z_art_delta_target_loss_total': 0.0}]
- EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration: EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration (val=2.52818, special_delta=0.111677, zero_e_evt=3.312339, zero_z_art=0.465828) [vs_route={'target_validation_loss_total': 0.083986, 'delta_loss_total': -0.028324, 'zero_e_evt_delta_target_loss_total': 0.013304, 'zero_z_art_delta_target_loss_total': 0.026892}]

## notes
- Rows are sorted by final target validation loss, then special delta, then e_evt.
- When route_context is present, delta_vs_route_anchor compares each final experiment against the selected route anchor.
