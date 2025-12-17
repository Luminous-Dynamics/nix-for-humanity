import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_ask_add_package_routes_to_install_dry_run():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    # Ensure not executing
    os.environ.pop("LUMINOUS_EXECUTE", None)

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
        res = runner.invoke(cli, ["ask", "add", "vim"])
        assert res.exit_code == 0, res.output
        # Should indicate a dry-run install
        assert "DRY RUN" in res.output or "Would run: nix profile install" in res.output
        # No package manager calls should be made in dry-run
        forbidden = {"nix", "nix-env", "nixos-rebuild", "sudo"}
        assert not any(isinstance(c, list) and c and c[0] in forbidden for c in calls)
