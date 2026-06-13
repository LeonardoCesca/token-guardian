from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from InquirerPy import inquirer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from app.models.schemas import AnalyzePromptRequest, CompareModelsRequest
from app.providers.registry import get_catalog_snapshot, list_models
from app.providers.sync_service import UnsupportedProviderError, sync_model_catalog
from app.services.analyzer_service import analyze_prompt, compare_models
from app.services.metrics_service import get_metrics
from app.services.optimizer_service import optimize_prompt

CONSOLE = Console()
ASCII_LOGO = r"""
 _______    _                 _____                     _ _
|__   __|  | |               / ____|                   | (_)
   | | ___ | | _____ _ __   | |  __ _   _  __ _ _ __ __| |_  __ _ _ __
   | |/ _ \| |/ / _ \ '_ \  | | |_ | | | |/ _` | '__/ _` | |/ _` | '_ \
   | | (_) |   <  __/ | | | | |__| | |_| | (_| | | | (_| | | (_| | | | |
   |_|\___/|_|\_\___|_| |_|  \_____|\__,_|\__,_|_|  \__,_|_|\__,_|_| |_|
"""


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    parser = _build_parser()
    if len(raw_args) == 0:
        return _default_command()
    args = parser.parse_args(raw_args)
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

    sync_models_parser = subparsers.add_parser(
        "sync-models",
        help="Atualiza o catalogo JSON local a partir dos adapters por provider.",
    )
    sync_models_parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Sincroniza apenas o provider informado. Repita a flag para incluir mais de um.",
    )
    sync_models_parser.set_defaults(func=_sync_models_command)

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
    snapshot = get_catalog_snapshot()
    print(f"Catalogo atualizado em {snapshot.last_updated_at}")
    print(f"Origem atual: {snapshot.catalog_path}\n")
    print("## Modelos Suportados\n")
    for item in sorted(list_models(), key=lambda model: (model.provider, model.model)):
        print(
            f"- {item.display_name} ({item.provider}/{item.model}) | "
            f"contexto {item.context_limit} | "
            f"in ${item.input_cost_per_1k}/1k | "
            f"out ${item.output_cost_per_1k}/1k | "
            f"velocidade {item.speed_estimate} | "
            f"fonte {item.source_url}"
        )
    return 0


def _sync_models_command(args: argparse.Namespace) -> int:
    try:
        snapshot = sync_model_catalog(args.provider)
    except UnsupportedProviderError as exc:
        print(str(exc))
        return 1

    print("## Catalogo Sincronizado\n")
    print(f"Catalogo atualizado em {snapshot.last_updated_at}")
    print(f"Arquivo: {snapshot.catalog_path}")
    print(f"Modelos sincronizados: {len(snapshot.models)}")
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


def _default_command() -> int:
    if _supports_interactive_ui():
        return _interactive_menu()

    print("Token Guardian CLI\n")
    print("Use um dos comandos abaixo:\n")
    print("- token-guardian analyze --provider anthropic --model claude-sonnet-4 --prompt \"Seu prompt\"")
    print("- token-guardian compare --prompt \"Seu prompt\"")
    print("- token-guardian optimize --prompt \"Seu prompt\"")
    print("- token-guardian models")
    print("- token-guardian sync-models")
    print("- token-guardian metrics")
    print("\nDica: rode `token-guardian --help` para ver todas as opcoes.")
    return 0


def _interactive_menu() -> int:
    _render_cover()

    choice = inquirer.select(
        message="Escolha o fluxo",
        choices=[
            {
                "name": "Revisar prompt",
                "value": "analyze",
            },
            {
                "name": "Comparar modelos",
                "value": "compare",
            },
            {
                "name": "Otimizar prompt",
                "value": "optimize",
            },
            {
                "name": "Listar modelos",
                "value": "models",
            },
            {
                "name": "Sincronizar catalogo",
                "value": "sync-models",
            },
            {
                "name": "Ver metricas",
                "value": "metrics",
            },
            {
                "name": "Sair",
                "value": "exit",
            },
        ],
        pointer="›",
        border=True,
        qmark="",
        instruction="Use as setas para navegar e Enter para confirmar.",
        long_instruction=(
            "Preflight elegante para tokens, custo e contexto antes da chamada da LLM."
        ),
        amark="●",
    ).execute()

    if choice == "analyze":
        return _interactive_analyze()
    if choice == "compare":
        return _interactive_compare()
    if choice == "optimize":
        return _interactive_optimize()
    if choice == "models":
        return _models_command(argparse.Namespace())
    if choice == "sync-models":
        return _interactive_sync_models()
    if choice == "metrics":
        return _metrics_command(argparse.Namespace())
    return 0


def _interactive_analyze() -> int:
    provider = _select_provider()
    model = _select_model_for_provider(provider)
    prompt = _prompt_text("Cole o prompt", multiline=True)
    estimated_output_tokens = _prompt_optional_int(
        "Tokens de saida estimados", default=None
    )
    return _analyze_command(
        argparse.Namespace(
            provider=provider,
            model=model,
            prompt=prompt,
            estimated_output_tokens=estimated_output_tokens,
        )
    )


def _interactive_compare() -> int:
    prompt = _prompt_text("Prompt para comparar", multiline=True)
    estimated_output_tokens = _prompt_optional_int(
        "Tokens de saida estimados", default=None
    )
    return _compare_command(
        argparse.Namespace(
            prompt=prompt,
            estimated_output_tokens=estimated_output_tokens,
        )
    )


def _interactive_optimize() -> int:
    prompt = _prompt_text("Prompt para otimizar", multiline=True)
    return _optimize_command(argparse.Namespace(prompt=prompt))


def _interactive_sync_models() -> int:
    provider_choices = sorted({item.provider for item in list_models()})
    selected = inquirer.checkbox(
        message="Selecione os providers para sincronizar",
        choices=[
            {"name": f"Todos ({len(provider_choices)})", "value": "__all__"},
            *[
                {"name": provider.title(), "value": provider}
                for provider in provider_choices
            ],
        ],
        pointer="›",
        border=True,
        qmark="",
        instruction="Use espaco para marcar e Enter para confirmar.",
        amark="●",
    ).execute()
    providers = [] if "__all__" in selected or not selected else selected
    return _sync_models_command(argparse.Namespace(provider=providers))


def _select_provider() -> str:
    providers = sorted({item.provider for item in list_models()})
    return inquirer.select(
        message="Escolha o provider",
        choices=[{"name": provider.title(), "value": provider} for provider in providers],
        pointer="›",
        border=True,
        qmark="",
        instruction="Selecione o provedor do fluxo.",
        amark="●",
    ).execute()


def _select_model_for_provider(provider: str) -> str:
    models = [item for item in list_models() if item.provider == provider]
    return inquirer.select(
        message="Escolha o modelo",
        choices=[
            {
                "name": (
                    f"{item.display_name} | contexto {item.context_limit} | "
                    f"in ${item.input_cost_per_1k}/1k | out ${item.output_cost_per_1k}/1k"
                ),
                "value": item.model,
            }
            for item in models
        ],
        pointer="›",
        border=True,
        qmark="",
        instruction="Selecione o modelo para analisar o prompt.",
        amark="●",
    ).execute()


def _prompt_text(message: str, *, multiline: bool) -> str:
    instruction = (
        "Pressione Alt+Enter para quebrar linha e Enter para concluir."
        if multiline
        else "Pressione Enter para confirmar."
    )
    return str(
        inquirer.text(
            message=message,
            multiline=multiline,
            instruction=instruction,
            qmark="",
            validate=lambda value: len(str(value).strip()) > 0,
            invalid_message="Informe um valor antes de continuar.",
            long_instruction="O texto sera usado diretamente no fluxo selecionado.",
        ).execute()
    ).strip()


def _prompt_optional_int(message: str, *, default: int | None) -> int | None:
    value = inquirer.text(
        message=message,
        default="" if default is None else str(default),
        instruction="Deixe vazio para estimativa automatica.",
        qmark="",
        validate=lambda raw: str(raw).strip() == "" or str(raw).strip().isdigit(),
        invalid_message="Digite um numero inteiro positivo ou deixe vazio.",
    ).execute()
    stripped = str(value).strip()
    return int(stripped) if stripped else None


def _supports_interactive_ui() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _render_cover() -> None:
    header = Text.from_markup("[bold bright_cyan]Token Guardian CLI[/bold bright_cyan]")
    subtitle = Text.from_markup(
        "[cyan]Prompt intelligence before the LLM call.[/cyan]"
    )
    body = Text.from_markup(f"[bright_cyan]{ASCII_LOGO}[/bright_cyan]")
    CONSOLE.print(
        Panel(
            Text.assemble(body, "\n", header, "\n", subtitle),
            border_style="bright_cyan",
            box=box.ROUNDED,
            title="[bold white]token-guardian[/bold white]",
            subtitle="[cyan]interactive preflight[/cyan]",
            padding=(1, 2),
        )
    )
    stats = Table.grid(expand=True)
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_row(
        "[bold white]tokens[/bold white]\n[cyan]estimate[/cyan]",
        "[bold white]cost[/bold white]\n[cyan]preview[/cyan]",
        "[bold white]context[/bold white]\n[cyan]risk[/cyan]",
    )
    CONSOLE.print(stats)
    CONSOLE.print()


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
