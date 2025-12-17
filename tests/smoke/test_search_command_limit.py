import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_search_command_limit_applies_to_json():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli.search_command import search

    sample = {
        **{f"nixpkgs.pkg{i}": {"name": f"pkg{i}", "description": "desc"} for i in range(20)}
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
        res = runner.invoke(search, ["foo", "--json", "--limit", "5"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert len(data.get("results", [])) == 5
