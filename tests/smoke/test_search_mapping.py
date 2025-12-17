import os
import subprocess
from unittest import mock

from click.testing import CliRunner


def test_search_uses_nix_search_and_parses_basic_output():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"
    from luminous_nix.cli import cli

    sample_out = """* nixpkgs.vim (Vim)
  A highly configurable text editor
* nixpkgs.neovim (Neovim)
  Vim-fork focused on extensibility and agility
"""

    def fake_run(cmd, *args, **kwargs):  # noqa: ANN001
        class R:
            returncode = 0
            stdout = sample_out
            stderr = ""

        return R()

    with mock.patch.object(subprocess, "run", side_effect=fake_run):
        runner = CliRunner()
        res = runner.invoke(cli, ["ask", "search", "vim"])
        assert res.exit_code == 0, res.output
        assert "Found packages" in res.output
        assert "nixpkgs.vim" in res.output
