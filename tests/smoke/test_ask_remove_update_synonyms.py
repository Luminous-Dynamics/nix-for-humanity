import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_ask_remove_synonyms_are_dry_run_and_safe():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        for phrase in ("remove vim", "uninstall vim", "delete vim"):
            res = runner.invoke(cli, ["ask", phrase])
            assert res.exit_code == 0, (phrase, res.output)
            assert "DRY RUN" in res.output or "Would run" in res.output
        # No system calls in dry-run
        forbidden = {"nix", "nix-env", "nixos-rebuild", "sudo"}
        assert not any(isinstance(c, list) and c and c[0] in forbidden for c in calls)


def test_ask_update_system_dry_run_and_safe():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""
        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(cli, ["ask", "update system"])
        assert res.exit_code == 0, res.output
        assert "DRY RUN" in res.output or "Would run: sudo nixos-rebuild switch --upgrade" in res.output
        # No real system calls should be executed in dry-run
        forbidden = {"nix", "nix-env", "nixos-rebuild", "sudo"}
        assert not any(isinstance(c, list) and c and c[0] in forbidden for c in calls)

