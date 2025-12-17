import json
import subprocess
from typing import Any

import click


def _list_profile() -> list[dict[str, Any]]:
    cmd = ["nix", "profile", "list"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return []
    return []


@click.group()
def packages():
    """Package utilities (core placeholder)."""
    pass


@packages.command()
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
@click.option("--limit", "-n", type=int, default=None, help="Limit results")
def list(as_json: bool, limit: int | None):
    """List packages in the current profile."""
    data = _list_profile()
    if limit is not None:
        data = data[:limit]

    if as_json:
        click.echo(json.dumps({"packages": data}))
    else:
        if not data:
            click.echo("No packages found in current profile")
            return
        click.echo("Packages in current profile:\n")
        for pkg in data:
            name = pkg.get("name") or ""
            click.echo(f"- {name}")
