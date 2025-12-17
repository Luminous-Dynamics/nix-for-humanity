import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_ask_search_synonyms_use_search_flow():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            if isinstance(cmd, list) and cmd[:3] == ["nix", "search", "nixpkgs"]:
                stdout = "* nixpkgs.vim (Vim)\n  editor\n"
            else:
                stdout = ""
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        for phrase in ("find vim", "look for vim", "search vim"):
            res = runner.invoke(cli, ["ask", phrase])
            assert res.exit_code == 0, (phrase, res.output)
            assert "Found" in res.output or "nixpkgs.vim" in res.output
