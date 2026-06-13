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
