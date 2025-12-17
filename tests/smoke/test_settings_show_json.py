import json
import os
from click.testing import CliRunner


def test_settings_show_json_raw_parses():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, ["settings", "show", "-f", "json", "--raw"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert isinstance(data, dict)
