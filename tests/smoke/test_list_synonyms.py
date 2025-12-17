import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_list_synonyms_route_to_list_installed():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:2] == ["nix-env", "-q"]:
                stdout = ""
            elif isinstance(cmd, list) and cmd[:2] == ["ls", "/run/current-system/sw/bin"]:
                stdout = "bash\ncoreutils\n"
            else:
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        for phrase in (
            "what's installed?",
            "what packages do i have",
            "list installed packages",
            "list packages",
        ):
            res = runner.invoke(cli, ["ask", phrase])
            assert res.exit_code == 0, (phrase, res.output)
            assert "Installed packages" in res.output
