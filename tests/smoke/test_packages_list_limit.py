import json
import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_packages_list_limit_applies_to_json():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import packages

    sample = [{"name": f"pkg{i}"} for i in range(10)]

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:3] == ["nix", "profile", "list"]:
                import json as _json

                stdout = _json.dumps(sample)
            else:
                stdout = ""
            stderr = ""
        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(packages, ["list", "--json", "--limit", "3"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert len(data.get("packages", [])) == 3
