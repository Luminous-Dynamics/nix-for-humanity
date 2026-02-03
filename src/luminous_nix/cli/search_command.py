import json
import subprocess
from typing import Any

import click

from luminous_nix.core.search_cache import SearchCache

_cache = SearchCache()


def _run_search(query: str, json_mode: bool) -> tuple[bool, str]:
    """Run nix search and return (ok, output)."""
    cmd = ["nix", "search", "nixpkgs", query]
    if json_mode:
        cmd.append("--json")
    else:
        cmd.append("--use-cache")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout


def _search_json(q: str) -> list[dict[str, str]]:
    """Search with cache, returning structured results."""
    cached = _cache.get_cached_search(q)
    if cached is not None:
        return cached

    ok, out = _run_search(q, json_mode=True)
    if ok and out:
        try:
            packages = json.loads(out)
        except json.JSONDecodeError:
            packages = {}
        results = [
            {
                "name": info.get("name") or name.split(".")[-1],
                "description": info.get("description", ""),
            }
            for name, info in packages.items()
        ]
        if results:
            _cache.cache_search_results(q, results)
        return results
    return []


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def search(query: tuple[str, ...], as_json: bool):
    """Search nixpkgs for packages."""
    q = " ".join(query)

    if as_json:
        results = _search_json(q)
        if results:
            click.echo(json.dumps({"results": results}))
        else:
            # Fallback to raw text search
            ok_raw, raw_out = _run_search(q, json_mode=False)
            payload: dict[str, Any] = {"raw": raw_out if ok_raw else ""}
            click.echo(json.dumps(payload))
        return

    # Text output path: check cache first
    cached = _cache.get_cached_search(q)
    if cached:
        for pkg in cached:
            click.echo(f"  {pkg.get('name', '?')} - {pkg.get('description', '')}")
        return

    ok, out = _run_search(q, json_mode=False)
    if ok and out:
        click.echo(out)
        # Parse and cache the text output for next time
        results = _search_json(q)  # noqa: F841 - side effect caches
    else:
        click.echo("No results or search failed")
