from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ModelConfig:
    provider: str
    model: str
    display_name: str
    context_limit: int
    input_cost_per_1k: float
    output_cost_per_1k: float
    speed_estimate: str
    source_url: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelConfig":
        return cls(
            provider=str(payload["provider"]).strip().lower(),
            model=str(payload["model"]).strip().lower(),
            display_name=str(payload["display_name"]).strip(),
            context_limit=int(payload["context_limit"]),
            input_cost_per_1k=float(payload["input_cost_per_1k"]),
            output_cost_per_1k=float(payload["output_cost_per_1k"]),
            speed_estimate=str(payload["speed_estimate"]).strip().lower(),
            source_url=str(payload["source_url"]).strip(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "display_name": self.display_name,
            "context_limit": self.context_limit,
            "input_cost_per_1k": self.input_cost_per_1k,
            "output_cost_per_1k": self.output_cost_per_1k,
            "speed_estimate": self.speed_estimate,
            "source_url": self.source_url,
        }


@dataclass(frozen=True, slots=True)
class CatalogSnapshot:
    last_updated_at: str
    models: tuple[ModelConfig, ...]
    catalog_path: Path

