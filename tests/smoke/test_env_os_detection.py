import json
import os
from click.testing import CliRunner


def test_env_show_json_includes_os_fields():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    runner = CliRunner()
    res = runner.invoke(cli, ["env", "show", "--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert "os" in data and isinstance(data["os"], dict)
    # Keys 'id' and 'pretty' may be None on non-Linux CI, but must exist
    assert "id" in data["os"] and "pretty" in data["os"]
