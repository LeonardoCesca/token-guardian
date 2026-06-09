from __future__ import annotations

import re

from app.models.schemas import OptimizePromptResponse


SECTION_GAP_RE = re.compile(r"\n{3,}")
SPACE_RE = re.compile(r"[ \t]{2,}")


def optimize_prompt(prompt: str) -> OptimizePromptResponse:
    lines = [line.rstrip() for line in prompt.splitlines()]
    optimized_lines: list[str] = []
    seen_normalized: set[str] = set()
    removed_patterns: list[str] = []

    for line in lines:
        normalized = SPACE_RE.sub(" ", line.strip()).lower()
        if not normalized:
            optimized_lines.append("")
            continue
        if normalized in seen_normalized:
            if "Linhas duplicadas" not in removed_patterns:
                removed_patterns.append("Linhas duplicadas")
            continue
        seen_normalized.add(normalized)
        optimized_lines.append(SPACE_RE.sub(" ", line).strip())

    optimized = "\n".join(optimized_lines).strip()
    optimized = SECTION_GAP_RE.sub("\n\n", optimized)

    original_length = max(len(prompt), 1)
    reduced_length = max(original_length - len(optimized), 0)
    reduction_percent = int(round((reduced_length / original_length) * 100))

    if not removed_patterns:
        removed_patterns.append("Espacos e quebras excedentes")

    return OptimizePromptResponse(
        optimized_prompt=optimized,
        estimated_reduction_percent=reduction_percent,
        removed_patterns=removed_patterns,
    )

