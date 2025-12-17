import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_default_is_dry_run_no_system_calls():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    # Ensure env does not force execute
    os.environ.pop("LUMINOUS_EXECUTE", None)
    os.environ.pop("LUMINOUS_DRY_RUN", None)

    from luminous_nix.cli import cli

    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        # Record any subprocess invocations
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        # No --dry-run flag; should still be dry-run by default
        res = runner.invoke(cli, ["ask", "install", "vim"])
        assert res.exit_code == 0, res.output

    # Ensure no package manager calls were attempted
    forbidden = {"nix", "nix-env", "nixos-rebuild", "sudo"}
    assert not any(isinstance(c, list) and c and c[0] in forbidden for c in calls)
