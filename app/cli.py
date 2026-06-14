from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from InquirerPy import inquirer
from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.markdown import Markdown
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
ACTION_CARDS = (
    {
        "title": "Analisar",
        "subtitle": "1 provedor, 1 modelo, 1 prompt",
        "body": "Estime tokens, custo, pressao de contexto e qualidade do prompt antes da chamada para a LLM.",
        "accent": "bright_cyan",
        "value": "analyze",
    },
    {
        "title": "Comparar",
        "subtitle": "Mesmo prompt, varios modelos",
        "body": "Compare custo, total de tokens, velocidade e risco entre os modelos padrao.",
        "accent": "green",
        "value": "compare",
    },
    {
        "title": "Otimizar",
        "subtitle": "Limpeza do prompt",
        "body": "Remova instrucoes duplicadas e ruido de espacos em branco antes da execucao.",
        "accent": "magenta",
        "value": "optimize",
    },
    {
        "title": "Catalogo",
        "subtitle": "Modelos, sync e metricas",
        "body": "Navegue pelo snapshot JSON, atualize provedores e acompanhe a observabilidade local.",
        "accent": "yellow",
        "value": "catalog",
    },
)

RISK_LABELS = {
    "low": "baixo",
    "medium": "medio",
    "high": "alto",
    "critical": "critico",
}

COMPLEXITY_LABELS = {
    "Simple": "Simples",
    "Medium": "Media",
    "Complex": "Complexa",
    "Very Complex": "Muito complexa",
}

SPEED_LABELS = {
    "fast": "rapida",
    "medium": "media",
    "slow": "lenta",
}


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
    _render_analysis_view(response)
    return 0


def _compare_command(args: argparse.Namespace) -> int:
    response = compare_models(
        CompareModelsRequest(
            prompt=args.prompt,
            estimated_output_tokens=args.estimated_output_tokens,
        )
    )
    _render_compare_view(response)
    return 0


def _optimize_command(args: argparse.Namespace) -> int:
    response = optimize_prompt(args.prompt)
    _render_optimize_view(response)
    return 0


def _models_command(_args: argparse.Namespace) -> int:
    snapshot = get_catalog_snapshot()
    _render_result_header(
        "Modelos Suportados",
        f"Catalogo atualizado em {snapshot.last_updated_at}",
        "bright_cyan",
    )
    _render_info_strip(
        [
            ("Origem atual", str(snapshot.catalog_path)),
            ("Modelos", str(len(snapshot.models))),
            ("Snapshot", snapshot.last_updated_at),
        ]
    )
    table = _build_table(
        "Catalogo",
        ["Modelo", "Provedor", "Contexto", "Entrada", "Saida", "Velocidade"],
    )
    models = sorted(list_models(), key=lambda model: (model.provider, model.model))
    for item in models:
        table.add_row(
            item.display_name,
            f"{item.provider}/{item.model}",
            str(item.context_limit),
            f"${item.input_cost_per_1k}/1k",
            f"${item.output_cost_per_1k}/1k",
            _translate_speed(item.speed_estimate),
        )
    CONSOLE.print(table)
    source_panels = [
        Panel(
            Text(item.source_url, overflow="fold"),
            title=f"[bold]{item.display_name}[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
        )
        for item in models
    ]
    CONSOLE.print(Columns(source_panels, equal=True, expand=True))
    return 0


def _sync_models_command(args: argparse.Namespace) -> int:
    try:
        snapshot = sync_model_catalog(args.provider)
    except UnsupportedProviderError as exc:
        print(str(exc))
        return 1

    _render_result_header(
        "Catalogo Sincronizado",
        f"Snapshot atualizado em {snapshot.last_updated_at}",
        "green",
    )
    _render_info_strip(
        [
            ("Arquivo", str(snapshot.catalog_path)),
            ("Modelos sincronizados", str(len(snapshot.models))),
            ("Provedores", str(len({item.provider for item in snapshot.models}))),
        ]
    )
    return 0


def _metrics_command(_args: argparse.Namespace) -> int:
    metrics = get_metrics()
    _render_result_header(
        "Metricas Locais",
        "Observabilidade local para o uso do Token Guardian",
        "bright_cyan",
    )
    _render_info_strip(
        [
            ("Total de requisicoes", str(metrics.total_requests)),
            ("Total de tokens", str(metrics.total_tokens)),
            ("Custo acumulado", f"${metrics.total_cost_estimated:.6f}"),
        ]
    )
    table = _build_table("Ranking", ["Categoria", "Resumo"])
    table.add_row("Top modelos", _format_ranked(metrics.top_models))
    table.add_row("Top provedores", _format_ranked(metrics.top_providers))
    CONSOLE.print(table)
    return 0


def _default_command() -> int:
    if _supports_interactive_ui():
        return _interactive_menu()

    print("Token Guardian CLI\n")
    print("Use um dos comandos abaixo:\n")
    print('- token-guardian analyze --provider anthropic --model claude-sonnet-4 --prompt "Seu prompt"')
    print('- token-guardian compare --prompt "Seu prompt"')
    print('- token-guardian optimize --prompt "Seu prompt"')
    print("- token-guardian models")
    print("- token-guardian sync-models")
    print("- token-guardian metrics")
    print("\nDica: rode `token-guardian --help` para ver todas as opcoes.")
    return 0


def _interactive_menu() -> int:
    _render_cover()
    _render_quick_actions()
    _render_shortcuts_panel()

    choice = inquirer.select(
        message="Escolha o fluxo",
        choices=[
            {"name": "Revisar prompt", "value": "analyze"},
            {"name": "Comparar modelos", "value": "compare"},
            {"name": "Otimizar prompt", "value": "optimize"},
            {"name": "Listar modelos", "value": "models"},
            {"name": "Sincronizar catalogo", "value": "sync-models"},
            {"name": "Ver metricas", "value": "metrics"},
            {"name": "Sair", "value": "exit"},
        ],
        pointer=">",
        border=True,
        qmark="",
        instruction="Use as setas para navegar e Enter para confirmar.",
        long_instruction=(
            "Cada fluxo abre uma experiencia guiada. Comece por Revisar prompt para analisar um prompt com provedor e modelo definidos."
        ),
        amark="*",
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
    _render_provider_focus(provider)
    model = _select_model_for_provider(provider)
    _render_model_spotlight(provider, model)
    prompt = _prompt_text("Cole o prompt")
    return _analyze_command(
        argparse.Namespace(
            provider=provider,
            model=model,
            prompt=prompt,
            estimated_output_tokens=None,
        )
    )


def _interactive_compare() -> int:
    prompt = _prompt_text("Prompt para comparar")
    return _compare_command(
        argparse.Namespace(
            prompt=prompt,
            estimated_output_tokens=None,
        )
    )


def _interactive_optimize() -> int:
    prompt = _prompt_text("Prompt para otimizar")
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
        pointer=">",
        border=True,
        qmark="",
        instruction="Use espaco para marcar e Enter para confirmar.",
        amark="*",
    ).execute()
    providers = [] if "__all__" in selected or not selected else selected
    return _sync_models_command(argparse.Namespace(provider=providers))


def _select_provider() -> str:
    providers = sorted({item.provider for item in list_models()})
    preview = [
        Panel(
            f"[bold]{provider.title()}[/bold]\n{len([item for item in list_models() if item.provider == provider])} modelos",
            title=f"[cyan]{provider}[/cyan]",
            border_style="cyan",
            box=box.ROUNDED,
        )
        for provider in providers
    ]
    CONSOLE.print(Columns(preview, equal=True, expand=True))
    return inquirer.select(
        message="Escolha o provedor",
        choices=[{"name": provider.title(), "value": provider} for provider in providers],
        pointer=">",
        border=True,
        qmark="",
        instruction="Selecione o provedor do fluxo.",
        amark="*",
    ).execute()


def _select_model_for_provider(provider: str) -> str:
    models = [item for item in list_models() if item.provider == provider]
    _render_model_browser(provider, models)
    return inquirer.select(
        message="Escolha o modelo",
        choices=[
            {
                "name": (
                    f"{item.display_name} | contexto {item.context_limit} | "
                    f"ent ${item.input_cost_per_1k}/1k | sai ${item.output_cost_per_1k}/1k"
                ),
                "value": item.model,
            }
            for item in models
        ],
        pointer=">",
        border=True,
        qmark="",
        instruction="Selecione o modelo. O painel acima destaca o perfil recomendado e o contexto disponivel.",
        amark="*",
    ).execute()


def _prompt_text(message: str) -> str:
    return str(
        inquirer.text(
            message=message,
            multiline=False,
            instruction="Pressione Enter para enviar.",
            qmark="",
            validate=lambda value: len(str(value).strip()) > 0,
            invalid_message="Informe um valor antes de continuar.",
            long_instruction="O texto sera usado diretamente no fluxo selecionado.",
        ).execute()
    ).strip()


def _supports_interactive_ui() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def _render_cover() -> None:
    header = Text.from_markup("[bold bright_cyan]Token Guardian CLI[/bold bright_cyan]")
    subtitle = Text.from_markup(
        "[cyan]Inteligencia de prompt antes da chamada para a LLM.[/cyan]"
    )
    body = Text.from_markup(f"[bright_cyan]{ASCII_LOGO}[/bright_cyan]")
    CONSOLE.print(
        Panel(
            Text.assemble(body, "\n", header, "\n", subtitle),
            border_style="bright_cyan",
            box=box.ROUNDED,
            title="[bold white]token-guardian[/bold white]",
            subtitle="[cyan]preflight interativo[/cyan]",
            padding=(1, 2),
        )
    )
    stats = Table.grid(expand=True)
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_row(
        "[bold white]tokens[/bold white]\n[cyan]estimativa[/cyan]",
        "[bold white]custo[/bold white]\n[cyan]previa[/cyan]",
        "[bold white]contexto[/bold white]\n[cyan]risco[/cyan]",
    )
    CONSOLE.print(stats)
    CONSOLE.print()


def _render_quick_actions() -> None:
    cards = [
        Panel(
            Group(
                Text(card["title"], style=f"bold {card['accent']}"),
                Text(card["subtitle"], style="white"),
                Text(card["body"], style="bright_white"),
            ),
            border_style=card["accent"],
            box=box.ROUNDED,
            padding=(1, 1),
        )
        for card in ACTION_CARDS
    ]
    CONSOLE.print(Columns(cards, equal=True, expand=True))
    CONSOLE.print()


def _render_shortcuts_panel() -> None:
    shortcuts = Table.grid(expand=True)
    shortcuts.add_column(style="bold cyan")
    shortcuts.add_column(style="white")
    shortcuts.add_row("CIMA / BAIXO", "navegar entre opcoes")
    shortcuts.add_row("ENTER", "confirmar selecao ou executar")
    shortcuts.add_row("ESPACO", "marcar provedores no sync")
    shortcuts.add_row("CTRL+C", "sair a qualquer momento")
    CONSOLE.print(
        Panel(
            shortcuts,
            title="[bold white]Acoes Rapidas + Atalhos[/bold white]",
            border_style="bright_cyan",
            box=box.ROUNDED,
        )
    )
    CONSOLE.print()


def _render_provider_focus(provider: str) -> None:
    models = [item for item in list_models() if item.provider == provider]
    snapshot = get_catalog_snapshot()
    body = Group(
        Text(f"Provedor selecionado: {provider}", style="bold cyan"),
        Text(f"Modelos disponiveis: {len(models)}"),
        Text(f"Catalogo atualizado em {snapshot.last_updated_at}"),
    )
    CONSOLE.print(
        Panel(
            body,
            title="[bold white]Resumo do Provedor[/bold white]",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )


def _render_model_browser(provider: str, models: list[object]) -> None:
    list_table = _build_table("Modelos", ["#", "Nome", "Velocidade"])
    for index, item in enumerate(models, start=1):
        list_table.add_row(str(index), item.display_name, item.speed_estimate)
    recommended = sorted(
        models,
        key=lambda item: (item.output_cost_per_1k, -item.context_limit),
    )[0]
    spotlight = Panel(
        Group(
            Text(recommended.display_name, style="bold green"),
            Text(f"provedor: {provider}"),
            Text(f"contexto: {recommended.context_limit}"),
            Text(f"entrada: ${recommended.input_cost_per_1k}/1k"),
            Text(f"saida: ${recommended.output_cost_per_1k}/1k"),
            Text(f"velocidade: {_translate_speed(recommended.speed_estimate)}"),
            Text(recommended.source_url, style="cyan"),
        ),
        title="[bold white]Preview lateral do modelo[/bold white]",
        border_style="green",
        box=box.ROUNDED,
    )
    CONSOLE.print(Columns([list_table, spotlight], equal=True, expand=True))
    CONSOLE.print()


def _render_model_spotlight(provider: str, model: str) -> None:
    selected = next(
        item for item in list_models() if item.provider == provider and item.model == model
    )
    body = Group(
        Text(selected.display_name, style="bold bright_cyan"),
        Text(f"{selected.provider}/{selected.model}"),
        Text(f"contexto: {selected.context_limit}"),
        Text(f"entrada: ${selected.input_cost_per_1k}/1k"),
        Text(f"saida: ${selected.output_cost_per_1k}/1k"),
        Text(f"velocidade: {_translate_speed(selected.speed_estimate)}"),
        Text(selected.source_url, style="cyan"),
    )
    CONSOLE.print(
        Panel(
            body,
            title="[bold white]Modelo selecionado[/bold white]",
            border_style="bright_cyan",
            box=box.ROUNDED,
        )
    )


def _render_result_header(title: str, subtitle: str, color: str) -> None:
    CONSOLE.print(
        Panel(
            Text.from_markup(f"[bold]{subtitle}[/bold]"),
            title=f"[bold {color}]{title}[/bold {color}]",
            border_style=color,
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


def _render_info_strip(items: list[tuple[str, str]]) -> None:
    panels = [
        Panel(
            Group(Text(label, style="bold cyan"), Text(value, style="white")),
            box=box.ROUNDED,
            border_style="cyan",
        )
        for label, value in items
    ]
    CONSOLE.print(Columns(panels, equal=True, expand=True))


def _build_table(title: str, columns: list[str]) -> Table:
    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold cyan",
        expand=True,
    )
    for column in columns:
        table.add_column(column)
    return table


def _render_analysis_view(response) -> None:
    _render_result_header(
        "Analise do Prompt",
        f"{response.provider}/{response.model}",
        "bright_cyan",
    )
    _render_info_strip(
        [
            ("Tokens", str(response.estimated_total_tokens)),
            ("Custo estimado", f"${response.estimated_cost_usd:.6f}"),
            ("Uso de contexto", f"{response.context_usage_percent:.2f}%"),
            ("Risco", _translate_risk(response.risk_level)),
        ]
    )
    table = _build_table("Resumo", ["Campo", "Valor"])
    table.add_row("Tokens de entrada", str(response.input_tokens))
    table.add_row("Saida estimada", str(response.estimated_output_tokens))
    table.add_row("Limite de contexto", str(response.context_limit))
    table.add_row("Saude do contexto", str(response.context_health_score))
    table.add_row("Complexidade", _translate_complexity(response.complexity_score))
    table.add_row("Faixa de custo", response.cost_score)
    CONSOLE.print(table)
    suggestions = "\n".join(f"- {item}" for item in response.suggestions)
    CONSOLE.print(
        Panel(
            Markdown(f"### Recomendacoes\n{suggestions}"),
            title="[bold white]Orientacao do Prompt[/bold white]",
            border_style="green",
            box=box.ROUNDED,
        )
    )


def _render_compare_view(response) -> None:
    _render_result_header(
        "Comparacao de Modelos",
        f"Tamanho do prompt: {response.prompt_length}",
        "green",
    )
    table = _build_table(
        "Comparativo",
        ["Provedor/Modelo", "Tokens", "Custo", "Risco", "Velocidade"],
    )
    for item in response.comparisons:
        table.add_row(
            f"{item.provider}/{item.model}",
            str(item.estimated_total_tokens),
            f"${item.estimated_cost_usd:.6f}",
            _translate_risk(item.risk_level),
            _translate_speed(item.speed_estimate),
        )
    CONSOLE.print(table)


def _render_optimize_view(response) -> None:
    _render_result_header(
        "Prompt Otimizado",
        f"Reducao estimada: {response.estimated_reduction_percent}%",
        "magenta",
    )
    patterns = "\n".join(f"- {item}" for item in response.removed_patterns)
    CONSOLE.print(
        Columns(
            [
                Panel(
                    Markdown(f"### Padroes removidos\n{patterns}"),
                    border_style="magenta",
                    box=box.ROUNDED,
                ),
                Panel(
                    Text(response.optimized_prompt),
                    title="[bold white]Prompt final[/bold white]",
                    border_style="bright_cyan",
                    box=box.ROUNDED,
                ),
            ],
            equal=True,
            expand=True,
        )
    )


def _format_ranked(items: list[dict[str, int]]) -> str:
    if not items:
        return "nenhum dado ainda"
    return ", ".join(f"{name} ({count})" for item in items for name, count in item.items())


def _translate_risk(value: str) -> str:
    return RISK_LABELS.get(value, value)


def _translate_complexity(value: str) -> str:
    return COMPLEXITY_LABELS.get(value, value)


def _translate_speed(value: str) -> str:
    return SPEED_LABELS.get(value, value)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
