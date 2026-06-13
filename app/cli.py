from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from app.models.schemas import AnalyzePromptRequest, CompareModelsRequest
from app.providers.registry import list_models
from app.services.analyzer_service import analyze_prompt, compare_models
from app.services.metrics_service import get_metrics
from app.services.optimizer_service import optimize_prompt


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="token-guardian",
        description="CLI para revisar prompts antes de chamar uma LLM.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analisa um prompt para um provider/modelo especifico.",
    )
    analyze_parser.add_argument("--provider", required=True)
    analyze_parser.add_argument("--model", required=True)
    analyze_parser.add_argument("--prompt", required=True)
    analyze_parser.add_argument("--estimated-output-tokens", type=int)
    analyze_parser.set_defaults(func=_analyze_command)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compara o mesmo prompt em modelos suportados.",
    )
    compare_parser.add_argument("--prompt", required=True)
    compare_parser.add_argument("--estimated-output-tokens", type=int)
    compare_parser.set_defaults(func=_compare_command)

    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Remove duplicacoes e espacos excedentes do prompt.",
    )
    optimize_parser.add_argument("--prompt", required=True)
    optimize_parser.set_defaults(func=_optimize_command)

    models_parser = subparsers.add_parser(
        "models",
        help="Lista os modelos suportados.",
    )
    models_parser.set_defaults(func=_models_command)

    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Mostra metricas locais de uso.",
    )
    metrics_parser.set_defaults(func=_metrics_command)

    return parser


def _analyze_command(args: argparse.Namespace) -> int:
    response = analyze_prompt(
        AnalyzePromptRequest(
            provider=args.provider,
            model=args.model,
            prompt=args.prompt,
            estimated_output_tokens=args.estimated_output_tokens,
        )
    )
    print(_render_analysis_markdown(response))
    return 0


def _compare_command(args: argparse.Namespace) -> int:
    response = compare_models(
        CompareModelsRequest(
            prompt=args.prompt,
            estimated_output_tokens=args.estimated_output_tokens,
        )
    )
    print("## Comparacao de Modelos\n")
    print(f"Prompt length: {response.prompt_length}\n")
    for item in response.comparisons:
        print(
            f"- {item.provider}/{item.model}: "
            f"custo ${item.estimated_cost_usd:.6f}, "
            f"tokens {item.estimated_total_tokens}, "
            f"risco {item.risk_level}, "
            f"velocidade {item.speed_estimate}"
        )
    return 0


def _optimize_command(args: argparse.Namespace) -> int:
    response = optimize_prompt(args.prompt)
    print("## Prompt Otimizado\n")
    print(f"Reducao estimada: {response.estimated_reduction_percent}%\n")
    print("Padroes removidos:")
    for item in response.removed_patterns:
        print(f"- {item}")
    print("\nPrompt otimizado:\n")
    print(response.optimized_prompt)
    return 0


def _models_command(_args: argparse.Namespace) -> int:
    print("## Modelos Suportados\n")
    for item in sorted(list_models(), key=lambda model: (model.provider, model.model)):
        print(
            f"- {item.display_name} ({item.provider}/{item.model}) | "
            f"contexto {item.context_limit} | "
            f"in ${item.input_cost_per_1k}/1k | "
            f"out ${item.output_cost_per_1k}/1k | "
            f"velocidade {item.speed_estimate}"
        )
    return 0


def _metrics_command(_args: argparse.Namespace) -> int:
    metrics = get_metrics()
    print("## Metricas Locais\n")
    print(f"Total de requisicoes: {metrics.total_requests}")
    print(f"Total de tokens: {metrics.total_tokens}")
    print(f"Custo estimado acumulado: ${metrics.total_cost_estimated:.6f}")
    print(f"Top modelos: {_format_ranked(metrics.top_models)}")
    print(f"Top providers: {_format_ranked(metrics.top_providers)}")
    return 0


def _format_ranked(items: list[dict[str, int]]) -> str:
    if not items:
        return "nenhum dado ainda"
    return ", ".join(f"{name} ({count})" for item in items for name, count in item.items())


def _render_analysis_markdown(response) -> str:
    payload = {
        "provider": response.provider,
        "model": response.model,
        "input_tokens": response.input_tokens,
        "estimated_output_tokens": response.estimated_output_tokens,
        "estimated_total_tokens": response.estimated_total_tokens,
        "context_limit": response.context_limit,
        "context_usage_percent": response.context_usage_percent,
        "estimated_cost_usd": response.estimated_cost_usd,
        "risk_level": response.risk_level,
        "context_health_score": response.context_health_score,
        "cost_score": response.cost_score,
        "complexity_score": response.complexity_score,
        "suggestions": response.suggestions,
    }
    return "## Analise do Prompt\n\n```json\n" + json.dumps(payload, ensure_ascii=False, indent=2) + "\n```"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
