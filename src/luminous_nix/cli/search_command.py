import json
import subprocess
from typing import Any

import click


def _run_search(query: str, json_mode: bool) -> tuple[bool, str]:
    """Run nix search and return (ok, output)."""
    cmd = ["nix", "search", "nixpkgs", query]
    if json_mode:
        cmd.append("--json")
    else:
        cmd.append("--use-cache")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def search(query: tuple[str, ...], as_json: bool):
    """Search nixpkgs for packages (core placeholder)."""
    q = " ".join(query)

    if as_json:
        ok, out = _run_search(q, json_mode=True)
        if not ok or not out:
            # Fallback to raw text search
            ok_raw, raw_out = _run_search(q, json_mode=False)
            payload: dict[str, Any] = {"raw": raw_out if ok_raw else ""}
            click.echo(json.dumps(payload))
            return
        try:
            packages = json.loads(out)
        except json.JSONDecodeError:
            packages = {}
        results = []
        for name, info in packages.items():
            results.append(
                {
                    "name": info.get("name") or name.split(".")[-1],
                    "description": info.get("description", ""),
                }
            )
        click.echo(json.dumps({"results": results}))
        return

    # Text output path
    ok, out = _run_search(q, json_mode=False)
    if ok and out:
        click.echo(out)
    else:
        click.echo("No results or search failed")
