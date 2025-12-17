import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_packages_list_json_uses_profile_when_available():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    from luminous_nix.cli import packages

    sample = [{"name": "vim"}, {"name": "neovim"}]

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "list"]:
                import json as _json

                stdout = _json.dumps(sample)
            else:
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(packages, ["list", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert "packages" in data and len(data["packages"]) == 2
