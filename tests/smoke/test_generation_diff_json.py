import json
import os
from unittest import mock

from click.testing import CliRunner


def test_generation_diff_json_with_mocked_manager():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    from luminous_nix.cli import generation

    sample_diff = {
        "packages_added": ["foo-1.0"],
        "packages_removed": ["bar-2.0"],
        "config_changes": ["/etc/nixos/configuration.nix"],
        "kernel_changed": False,
        "nixos_version_changed": True,
    }

    with mock.patch(
        "luminous_nix.core.generation_manager.GenerationManager.get_generation_diff",
        return_value=sample_diff,
    ):
        runner = CliRunner()
        res = runner.invoke(generation, ["diff", "10", "11", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert data["gen1"] == 10 and data["gen2"] == 11
        assert data["nixos_version_changed"] is True
