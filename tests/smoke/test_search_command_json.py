import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_search_command_json_uses_nix_search_json():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli.search_command import search

    sample = {
        "nixpkgs.vim": {"name": "vim", "description": "Vim editor"},
        "nixpkgs.neovim": {"name": "neovim", "description": "Neovim"},
    }

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:3] == ["nix", "search", "nixpkgs"] and "--json" in cmd:
                import json as _json

                stdout = _json.dumps(sample)
            else:
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(search, ["vim", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert "results" in data and len(data["results"]) == 2
