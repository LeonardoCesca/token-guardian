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
    assert '"provider": "anthropic"' in output


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
    assert "Total de requisicoes: 1" in output


def test_interactive_analyze_builds_flow(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_select_provider", lambda: "anthropic")
    monkeypatch.setattr(cli, "_select_model_for_provider", lambda provider: "claude-sonnet-4")
    monkeypatch.setattr(cli, "_prompt_text", lambda message, multiline: "Prompt interativo")
    monkeypatch.setattr(cli, "_prompt_optional_int", lambda message, default: 256)

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
    assert captured["estimated_output_tokens"] == 256


def test_interactive_compare_and_optimize(monkeypatch) -> None:
    monkeypatch.setattr(cli, "_prompt_text", lambda message, multiline: "Prompt interativo")
    monkeypatch.setattr(cli, "_prompt_optional_int", lambda message, default: None)
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
                },
            )(),
        ],
    )
    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("anthropic"))
    assert cli._select_provider() == "anthropic"

    monkeypatch.setattr(cli.inquirer, "select", lambda **kwargs: FakePrompt("claude-sonnet-4"))
    assert cli._select_model_for_provider("anthropic") == "claude-sonnet-4"

    monkeypatch.setattr(cli.inquirer, "text", lambda **kwargs: FakePrompt("texto"))
    assert cli._prompt_text("x", multiline=False) == "texto"

    monkeypatch.setattr(cli.inquirer, "text", lambda **kwargs: FakePrompt(""))
    assert cli._prompt_optional_int("x", default=None) is None

    monkeypatch.setattr(cli.inquirer, "text", lambda **kwargs: FakePrompt("123"))
    assert cli._prompt_optional_int("x", default=None) == 123


def test_interactive_menu_routes_choices(monkeypatch) -> None:
    class FakePrompt:
        def __init__(self, result):
            self.result = result

        def execute(self):
            return self.result

    monkeypatch.setattr(cli, "_render_cover", lambda: None)
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
