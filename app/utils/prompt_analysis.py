from __future__ import annotations

from collections import Counter
import re

from app.models.schemas import ComplexityLevel, CostScore, RiskLevel


LINE_SPLIT_RE = re.compile(r"\r?\n")
WORD_RE = re.compile(r"\b[\w'-]+\b")
SPACE_RE = re.compile(r"\s+")


def calculate_context_usage_percent(total_tokens: int, context_limit: int) -> float:
    return round((total_tokens / context_limit) * 100, 2)


def classify_risk(usage_percent: float) -> RiskLevel:
    if usage_percent >= 95:
        return "critical"
    if usage_percent >= 75:
        return "high"
    if usage_percent >= 45:
        return "medium"
    return "low"


def score_cost(cost_usd: float) -> CostScore:
    if cost_usd >= 0.1:
        return "$$$$"
    if cost_usd >= 0.03:
        return "$$$"
    if cost_usd >= 0.01:
        return "$$"
    return "$"


def classify_complexity(prompt: str, input_tokens: int) -> ComplexityLevel:
    line_count = len(LINE_SPLIT_RE.split(prompt.strip()))
    if input_tokens >= 2500 or line_count >= 80:
        return "Very Complex"
    if input_tokens >= 1200 or line_count >= 35:
        return "Complex"
    if input_tokens >= 350 or line_count >= 12:
        return "Medium"
    return "Simple"


def context_health_score(prompt: str, input_tokens: int) -> int:
    normalized = SPACE_RE.sub(" ", prompt.strip())
    words = [word.lower() for word in WORD_RE.findall(normalized)]
    unique_ratio = (len(set(words)) / len(words)) if words else 1.0
    duplicate_penalty = int((1 - unique_ratio) * 35)
    long_prompt_penalty = min(input_tokens // 120, 35)
    repeated_line_penalty = min(_repeated_line_count(prompt) * 4, 20)
    score = 100 - duplicate_penalty - long_prompt_penalty - repeated_line_penalty
    return max(0, min(score, 100))


def prompt_suggestions(prompt: str, input_tokens: int) -> list[str]:
    suggestions: list[str] = []
    repeated_lines = _repeated_line_count(prompt)
    words = [word.lower() for word in WORD_RE.findall(prompt)]
    word_counts = Counter(words)
    repetitive_terms = [word for word, count in word_counts.items() if count >= 8]

    if input_tokens >= 800:
        suggestions.append("Prompt pode ser reduzido em 20% a 35% com maior objetividade.")
    if repeated_lines:
        suggestions.append("Remover blocos ou linhas duplicadas deve reduzir ruído de contexto.")
    if len(repetitive_terms) >= 5:
        suggestions.append("Consolidar instrucoes repetidas em uma unica secao pode ajudar.")
    if "exemplo" in word_counts and word_counts["exemplo"] >= 3:
        suggestions.append("Revise se todos os exemplos sao necessarios para a tarefa.")
    if not suggestions:
        suggestions.append("Prompt enxuto e com bom sinal; mantenha foco em objetivo, restricoes e saida.")
    return suggestions


def _repeated_line_count(prompt: str) -> int:
    lines = [line.strip().lower() for line in LINE_SPLIT_RE.split(prompt) if line.strip()]
    counts = Counter(lines)
    return sum(count - 1 for count in counts.values() if count > 1)

