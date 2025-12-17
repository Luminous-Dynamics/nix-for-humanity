import json
import os
from click.testing import CliRunner


def test_preview_json_extracts_planned_actions():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import preview

    runner = CliRunner()
    res = runner.invoke(preview, ["install", "vim", "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data.get("query") == "install vim"
    assert isinstance(data.get("planned", []), list)
