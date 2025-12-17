import json
import os
from click.testing import CliRunner


def test_env_show_json_parses():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, ["env", "show", "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert isinstance(data, dict)
    assert "python" in data and "features" in data and "extras" in data


def test_doctor_defaults_to_show():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, ["doctor"])  # should print env summary
    assert res.exit_code == 0, res.output
