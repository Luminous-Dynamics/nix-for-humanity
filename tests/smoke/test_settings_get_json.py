import json
import os
from click.testing import CliRunner


def test_settings_get_json_outputs_object():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    # Query a known path; value may be None if not set, but JSON must parse
    res = runner.invoke(cli, ["settings", "get", "ui.default_personality", "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data.get("path") == "ui.default_personality"
    assert "value" in data
