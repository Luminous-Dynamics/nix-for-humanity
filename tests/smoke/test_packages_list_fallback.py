import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_packages_list_json_falls_back_to_nix_env_q():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import packages

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            # Simulate nix profile list failing
            if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "list"]:
                returncode = 1
                stdout = ""
            elif isinstance(cmd, list) and cmd[:2] == ["nix-env", "-q"]:
                returncode = 0
                stdout = "vim\nneovim\n"
            else:
                returncode = 0
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(packages, ["list", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert data.get("packages") == ["vim", "neovim"]
