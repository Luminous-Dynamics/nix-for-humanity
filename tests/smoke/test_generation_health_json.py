import json
import os
from datetime import datetime
from unittest import mock

from click.testing import CliRunner


def test_generation_health_json_with_mocked_manager():
    os.environ["LUMINOUS_SKIP_ONBOARDING"] = "true"

    from luminous_nix.cli import generation
    from luminous_nix.core.generation_manager import SystemHealth

    sample = SystemHealth(
        disk_usage_percent=42.0,
        memory_usage_percent=55.5,
        failed_services=[],
        config_errors=[],
        last_successful_boot=datetime(2024, 1, 2, 3, 4, 5),
        warnings=["sample"],
    )

    with mock.patch(
        "luminous_nix.core.generation_manager.GenerationManager.check_system_health",
        return_value=sample,
    ):
        runner = CliRunner()
        res = runner.invoke(generation, ["health", "--json"])
        assert res.exit_code == 0, res.output
        data = json.loads(res.output)
        assert data["is_healthy"] is True
        assert data["disk_usage_percent"] == 42.0
