import os
from click.testing import CliRunner


def test_cli_help_imports():
    # Avoid onboarding prompts in tests
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    # Import lazily to avoid side effects
    from luminous_nix.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])  # top-level help
    assert result.exit_code == 0, result.output
    assert "Luminous Nix" in result.output


def test_subcommand_helps():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    for sub in ("settings", "generation", "config", "flake", "ask", "env", "doctor"):
        res = runner.invoke(cli, [sub, "--help"])  # each subcommand help
        assert res.exit_code == 0, f"{sub} help failed: {res.output}"


def test_ask_dry_run_noop():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    # Safe dry run that should not execute changes
    res = runner.invoke(cli, ["ask", "--dry-run", "install", "vim"])
    assert res.exit_code == 0, res.output
