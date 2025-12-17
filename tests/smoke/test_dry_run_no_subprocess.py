import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_dry_run_does_not_call_nix_commands():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    from luminous_nix.cli import cli

    calls = []

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        calls.append(cmd)
        # Simulate a harmless command returning success
        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(cli, ["ask", "--dry-run", "install", "vim"])
        assert res.exit_code == 0, res.output

    # Ensure no 'nix' or 'nix-env' or 'nixos-rebuild' calls were attempted in dry-run
    forbidden = {"nix", "nix-env", "nixos-rebuild"}
    assert not any(isinstance(c, list) and c and c[0] in forbidden for c in calls)
