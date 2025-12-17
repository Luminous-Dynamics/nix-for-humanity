import json
import sys
from importlib import metadata

import click


def _get_version() -> str:
    try:
        return metadata.version("luminous-nix")
    except metadata.PackageNotFoundError:
        return "0.0.0"


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def version(as_json: bool):
    """Show version information (core placeholder)."""
    info = {
        "luminous_nix": _get_version(),
        "python": sys.version.split()[0],
    }
    if as_json:
        click.echo(json.dumps(info))
    else:
        click.echo(f"Luminous Nix version: {info['luminous_nix']}")
        click.echo(f"Python: {info['python']}")
