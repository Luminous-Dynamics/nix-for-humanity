import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_search_command_fallback_raw_json_when_no_json_available():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli.search_command import search

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            # First attempt is --json path; simulate failure by returningcode != 0
            if isinstance(cmd, list) and cmd[:3] == ["nix", "search", "nixpkgs"] and "--json" in cmd:
                returncode = 1
                stdout = ""
            elif isinstance(cmd, list) and cmd[:3] == ["nix", "search", "nixpkgs"] and "--use-cache" in cmd:
                returncode = 0
                stdout = "* nixpkgs.vim (Vim)\n  editor\n"
            else:
                returncode = 0
                stdout = ""
            stderr = ""
        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(search, ["vim", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert "raw" in data and "nixpkgs.vim" in data["raw"]

