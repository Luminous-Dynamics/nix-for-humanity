import json
import os
from datetime import datetime
from unittest import mock

from click.testing import CliRunner


def test_generation_list_json_with_mocked_manager():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    from luminous_nix.cli import generation
    from luminous_nix.core.generation_manager import Generation

    sample = [
        Generation(
            number=123,
            date=datetime(2024, 1, 1, 12, 0, 0),
            kernel="linux-6.8",
            nixos_version="24.05",
            is_current=True,
        )
    ]

    with mock.patch(
        "luminous_nix.core.generation_manager.GenerationManager.list_generations",
        return_value=sample,
    ):
        runner = CliRunner()
        res = runner.invoke(generation, ["list", "--json", "-n", "1"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert "generations" in data
        assert data["generations"][0]["number"] == 123
        assert data["generations"][0]["current"] is True
