from __future__ import annotations

import torch


def build_streaming_student_proxy_acoustic(outputs: dict[str, torch.Tensor]) -> torch.Tensor:
    energy_log = outputs["energy"].to(torch.float32)
    voiced_prob = torch.sigmoid(outputs["vuv_logits"].to(torch.float32))
    aper_proxy = torch.sigmoid(outputs["aperiodicity"].to(torch.float32))
    event_presence = outputs["event_probs"].to(torch.float32).amax(dim=-1, keepdim=True)

    rms_like = torch.sqrt(torch.pow(10.0, energy_log).clamp_min(1.0e-8))
    abs_mean = (0.82 * rms_like + 0.06 * event_presence + 0.04 * voiced_prob).clamp(0.005, 0.6)
    zero_cross = (0.07 + (1.0 - voiced_prob) * 0.14 + aper_proxy * 0.08).clamp(0.02, 0.45)
    delta_energy = torch.zeros_like(energy_log)
    delta_energy[:, 1:] = energy_log[:, 1:] - energy_log[:, :-1]
    delta_energy = delta_energy.clamp(-0.5, 0.5)
    return torch.cat([energy_log, abs_mean, zero_cross, delta_energy], dim=-1)


def build_streaming_student_proxy_acoustic_for_export(outputs: dict[str, torch.Tensor]) -> torch.Tensor:
    energy_log = outputs["energy"].to(torch.float32)
    voiced_prob = torch.sigmoid(outputs["vuv_logits"].to(torch.float32))
    aper_proxy = torch.sigmoid(outputs["aperiodicity"].to(torch.float32))

    rms_like = torch.sqrt(torch.pow(10.0, energy_log).clamp_min(1.0e-8))
    # Export-side proxy audio should stay quiet in silence; unlike the training-side helper,
    # do not let voiced/event priors add a fixed floor when energy is near zero.
    activity = ((rms_like - 0.0015) / (0.012 - 0.0015)).clamp(0.0, 1.0)
    abs_mean = (rms_like * (0.9 + 0.08 * voiced_prob)).clamp(0.0, 0.6)
    abs_mean = abs_mean * activity
    zero_cross = (0.05 + (1.0 - voiced_prob) * 0.16 + aper_proxy * 0.08).clamp(0.02, 0.45)
    zero_cross = 0.02 + (zero_cross - 0.02) * activity
    delta_energy = torch.zeros_like(energy_log)
    delta_energy[:, 1:] = energy_log[:, 1:] - energy_log[:, :-1]
    delta_energy = (delta_energy.clamp(-0.5, 0.5)) * activity
    return torch.cat([energy_log, abs_mean, zero_cross, delta_energy], dim=-1)
