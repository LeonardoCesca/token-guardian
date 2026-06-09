from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelConfig:
    provider: str
    model: str
    display_name: str
    context_limit: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    speed_estimate: str

