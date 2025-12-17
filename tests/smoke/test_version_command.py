import json
from click.testing import CliRunner


def test_version_command_json():
    from luminous_nix.cli.version_command import version

    runner = CliRunner()
    res = runner.invoke(version, ["--json"])
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert "luminous_nix" in data and "python" in data
