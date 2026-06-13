from __future__ import annotations

import pytest

from app import cli
from app.services.metrics_service import record_analysis


def test_analyze_command_prints_report(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main(
        [
            "analyze",
            "--provider",
            "anthropic",
            "--model",
            "claude-sonnet-4",
            "--prompt",
            "Revise esta arquitetura.",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Analise do Prompt" in output
    assert "anthropic/claude-sonnet-4" in output


def test_main_without_args_prints_default_entrypoint_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main([])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Token Guardian CLI" in output
    assert "token-guardian analyze" in output


def test_main_without_args_opens_interactive_menu_when_tty(
    monkeypatch,
) -> None:
    monkeypatch.setattr(cli, "_supports_interactive_ui", lambda: True)
    monkeypatch.setattr(cli, "_interactive_menu", lambda: 7)

    assert cli.main([]) == 7


def test_compare_command_prints_models(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main(
        [
            "compare",
            "--prompt",
            "Compare custo e risco deste prompt.",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Comparacao de Modelos" in output
    assert "openai/gpt-4.1" in output


def test_optimize_command_prints_optimized_prompt(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(
        [
            "optimize",
            "--prompt",
            "Goal: summarize\nGoal: summarize",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Prompt Otimizado" in output
    assert "Goal: summarize" in output


def test_models_command_prints_catalog(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main(["models"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Catalogo atualizado em" in output
    assert "Modelos Suportados" in output
    assert "Claude Sonnet 4" in output


def test_sync_models_command_prints_summary(
    monkeypatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_snapshot = cli.get_catalog_snapshot()
    monkeypatch.setattr(cli, "sync_model_catalog", lambda _providers: fake_snapshot)

    exit_code = cli.main(["sync-models"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Catalogo Sincronizado" in output
    assert "Modelos sincronizados" in output


def test_metrics_command_prints_summary(capsys: pytest.CaptureFixture[str]) -> None:
    record_analysis("anthropic", "claude-sonnet-4", 1200, 0.021)

    exit_code = cli.main(["metrics"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Metricas Locais" in output
    assert "Total de requisicoes" in output
    assert "1" in output


def test_interactive_analyze_builds_flow(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_select_provider", lambda: "anthropic")
    monkeypatch.setattr(cli, "_select_model_for_provider", lambda provider: "claude-sonnet-4")
    monkeypatch.setattr(cli, "_prompt_text", lambda message: "Prompt interativo")

    captured: dict[str, object] = {}

    def fake_analyze(args):
        captured["provider"] = args.provider
        captured["model"] = args.model
        captured["prompt"] = args.prompt
        captured["estimated_output_tokens"] = args.estimated_output_tokens
        return 3

    monkeypatch.setattr(cli, "_analyze_command", fake_analyze)

    assert cli._interactive_analyze() == 3
    assert captured["provider"] == "anthropic"
    assert captured["model"] == "claude-sonnet-4"
    assert captured["estimated_output_tokens"] is None


def test_interactive_compare_and_optimize(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_prompt_text", lambda message: "Prompt interativo")
    monkeypatch.setattr(cli, "_compare_command", lambda args: 5)
    monkeypatch.setattr(cli, "_optimize_command", lambda args: 6)

    assert cli._interactive_compare() == 5
    assert cli._interactive_optimize() == 6


def test_interactive_sync_models_all_and_selected(monkeypatch) -> None:
    class FakePrompt:
        def __init__(self, result):
            self.result = result

        def execute(self):
            return self.result

    monkeypatch.setattr(
        cli,
        "list_models",
        lambda: [
            type("Model", (), {"provider": "anthropic"})(),
            type("Model", (), {"provider": "openai"})(),
        ],
    )
    monkeypatch.setattr(cli.inquirer, "checkbox", lambda **kwargs: FakePrompt(["__all__"]))
    monkeypatch.setattr(cli, "_sync_models_command", lambda args: 11 if args.provider == [] else 12)
    assert cli._interactive_sync_models() == 11

    monkeypatch.setattr(cli.inquirer, "checkbox", lambda **kwargs: FakePrompt(["openai"]))
    assert cli._interactive_sync_models() == 12


def test_selectors_and_text_prompts(monkeypatch) -> None:
    class FakePrompt:
        def __init__(self, result):
            self.result = result

        def execute(self):
            return self.result

    monkeypatch.setattr(
        cli,
        "list_models",
        lambda: [
            type(
                "Model",
                (),
                {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4",
                    "display_name": "Claude Sonnet 4",
                    "context_limit": 200000,
                    "input_cost_per_1k": 0.003,
                    "output_cost_per_1k": 0.015,
                    "speed_estimate": "fast",
                    "source_url": "https://example.com/model",
                },
            )(),
        ],
    )
    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("anthropic"))
    assert cli._select_provider() == "anthropic"

    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("claude-sonnet-4"))
    assert cli._select_model_for_provider("anthropic") == "claude-sonnet-4"

    monkeypatch.setattr(cli.inquirer, "text", lambda **kwargs: FakePrompt("texto"))
    assert cli._prompt_text("x") == "texto"


def test_interactive_menu_routes_choices(monkeypatch) -> None:
    class FakePrompt:
        def __init__(self, result):
            self.result = result

        def execute(self):
            return self.result

    monkeypatch.setattr(cli, "_render_cover", lambda: None)
    monkeypatch.setattr(cli, "_render_quick_actions", lambda: None)
    monkeypatch.setattr(cli, "_render_shortcuts_panel", lambda: None)
    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("models"))
    monkeypatch.setattr(cli, "_models_command", lambda args: 21)
    assert cli._interactive_menu() == 21

    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("sync-models"))
    monkeypatch.setattr(cli, "_interactive_sync_models", lambda: 22)
    assert cli._interactive_menu() == 22

    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("metrics"))
    monkeypatch.setattr(cli, "_metrics_command", lambda args: 23)
    assert cli._interactive_menu() == 23

    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("analyze"))
    monkeypatch.setattr(cli, "_interactive_analyze", lambda: 24)
    assert cli._interactive_menu() == 24


def test_supports_interactive_ui_and_render_cover(monkeypatch) -> None:
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: True)
    assert cli._supports_interactive_ui() is True

    monkeypatch.setattr(cli.CONSOLE, "print", lambda *args, **kwargs: None)
    cli._render_cover()
    cli._render_quick_actions()
    cli._render_shortcuts_panel()


def test_render_helpers_and_views(monkeypatch) -> None:
    monkeypatch.setattr(cli.CONSOLE, "print", lambda *args, **kwargs: None)
    cli._render_result_header("Titulo", "Subtitulo", "cyan")
    cli._render_info_strip([("A", "1"), ("B", "2")])
    table = cli._build_table("Tabela", ["A", "B"])
    table.add_row("1", "2")

    response = type(
        "AnalyzeResponse",
        (),
        {
            "provider": "anthropic",
            "model": "claude-sonnet-4",
            "input_tokens": 10,
            "estimated_output_tokens": 20,
            "estimated_total_tokens": 30,
            "context_limit": 200000,
            "context_usage_percent": 0.1,
            "estimated_cost_usd": 0.01,
            "risk_level": "low",
            "context_health_score": 99,
            "cost_score": "$",
            "complexity_score": "Simple",
            "suggestions": ["ok"],
        },
    )()
    cli._render_analysis_view(response)

    compare_response = type(
        "CompareResponse",
        (),
        {
            "prompt_length": 12,
            "comparisons": [
                type(
                    "Item",
                    (),
                    {
                        "provider": "openai",
                        "model": "gpt-4.1",
                        "estimated_total_tokens": 40,
                        "estimated_cost_usd": 0.02,
                        "risk_level": "low",
                        "speed_estimate": "medium",
                    },
                )()
            ],
        },
    )()
    cli._render_compare_view(compare_response)

    optimize_response = type(
        "OptimizeResponse",
        (),
        {
            "estimated_reduction_percent": 30,
            "removed_patterns": ["Linhas duplicadas"],
            "optimized_prompt": "Prompt final",
        },
    )()
    cli._render_optimize_view(optimize_response)


def test_render_model_focus_and_browser(monkeypatch) -> None:
    monkeypatch.setattr(cli.CONSOLE, "print", lambda *args, **kwargs: None)
    models = [
        type(
            "Model",
            (),
            {
                "provider": "anthropic",
                "model": "claude-sonnet-4",
                "display_name": "Claude Sonnet 4",
                "context_limit": 200000,
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015,
                "speed_estimate": "fast",
                "source_url": "https://example.com/sonnet",
            },
        )(),
        type(
            "Model",
            (),
            {
                "provider": "anthropic",
                "model": "claude-opus-4",
                "display_name": "Claude Opus 4",
                "context_limit": 200000,
                "input_cost_per_1k": 0.015,
                "output_cost_per_1k": 0.075,
                "speed_estimate": "slow",
                "source_url": "https://example.com/opus",
            },
        )(),
    ]
    monkeypatch.setattr(cli, "list_models", lambda: models)
    cli._render_provider_focus("anthropic")
    cli._render_model_browser("anthropic", models)
    cli._render_model_spotlight("anthropic", "claude-sonnet-4")
