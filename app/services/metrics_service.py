from __future__ import annotations

from collections.abc import Sequence

from app.models.schemas import MetricsResponse
from app.services.database import get_connection, init_db


def record_analysis(
    provider: str,
    model: str,
    total_tokens: int,
    estimated_cost_usd: float,
) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO prompt_metrics (provider, model, total_tokens, estimated_cost_usd)
            VALUES (?, ?, ?, ?)
            """,
            (provider, model, total_tokens, estimated_cost_usd),
        )
        conn.commit()


def get_metrics() -> MetricsResponse:
    init_db()
    with get_connection() as conn:
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total_requests,
                COALESCE(SUM(total_tokens), 0) AS total_tokens,
                COALESCE(SUM(estimated_cost_usd), 0) AS total_cost_estimated
            FROM prompt_metrics
            """
        ).fetchone()
        top_models = _as_ranked_list(
            conn.execute(
                """
                SELECT model, COUNT(*) AS count
                FROM prompt_metrics
                GROUP BY model
                ORDER BY count DESC, model ASC
                LIMIT 5
                """
            ).fetchall()
        )
        top_providers = _as_ranked_list(
            conn.execute(
                """
                SELECT provider, COUNT(*) AS count
                FROM prompt_metrics
                GROUP BY provider
                ORDER BY count DESC, provider ASC
                LIMIT 5
                """
            ).fetchall()
        )

    return MetricsResponse(
        total_requests=int(totals["total_requests"]),
        total_tokens=int(totals["total_tokens"]),
        total_cost_estimated=round(float(totals["total_cost_estimated"]), 6),
        top_models=top_models,
        top_providers=top_providers,
    )


def _as_ranked_list(rows: Sequence[object]) -> list[dict[str, int]]:
    ranked: list[dict[str, int]] = []
    for row in rows:
        mapping = dict(row)
        key = "model" if "model" in mapping else "provider"
        ranked.append({str(mapping[key]): int(mapping["count"])})
    return ranked

