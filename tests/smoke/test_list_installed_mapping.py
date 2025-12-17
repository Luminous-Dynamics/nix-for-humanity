import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_list_installed_mapping_prints_user_packages():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:2] == ["nix-env", "-q"]:
                stdout = "vim\nneovim\n"
            elif isinstance(cmd, list) and cmd[:2] == ["ls", "/run/current-system/sw/bin"]:
                stdout = "bash\nvim\nls\n"
            else:
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(cli, ["ask", "list", "packages"])
        assert res.exit_code == 0, res.output
        assert "User packages" in res.output
        assert "vim" in res.output
