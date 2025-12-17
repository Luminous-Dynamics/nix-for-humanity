import json
import click


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("--json", "as_json", is_flag=True, help="Output JSON")
def preview(query: tuple[str, ...], as_json: bool):
    """Preview a planned action (core placeholder)."""
    q = " ".join(query)
    planned = [
        {
            "action": "plan",
            "detail": q,
        }
    ]
    if as_json:
        click.echo(json.dumps({"query": q, "planned": planned}))
    else:
        click.echo(f"DRY RUN: would handle '{q}'")
        for step in planned:
            click.echo(f"- {step['action']}: {step['detail']}")
