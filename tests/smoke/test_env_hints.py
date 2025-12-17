import json
import os
from click.testing import CliRunner


def test_env_show_hints_when_flags_enabled_but_missing():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    # Enable all flags (modules likely not installed in test env)
    os.environ["LUMINOUS_AI_ENABLED"] = "true"
    os.environ["LUMINOUS_VOICE_ENABLED"] = "true"
    os.environ["LUMINOUS_WEB_ENABLED"] = "true"

    from luminous_nix.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, ["env", "show", "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert isinstance(data.get("hints", []), list)
    # We expect at least one hint if extras are not installed
    assert len(data["hints"]) >= 1
