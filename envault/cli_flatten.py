"""CLI commands for flattening/expanding prefixed env keys."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envault.env_flatten import expand_from_dict, flatten_env_file, flatten_to_dict


@click.group("flatten")
def flatten_cli() -> None:
    """Flatten or expand prefixed .env keys."""


@flatten_cli.command("show")
@click.argument("env_file", default=".env")
@click.option("--sep", default="__", show_default=True, help="Key separator")
def flatten_show(env_file: str, sep: str) -> None:
    """Display env keys grouped by their prefix."""
    path = Path(env_file)
    try:
        groups = flatten_env_file(path, separator=sep)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not groups:
        click.echo("No keys found.")
        return

    for prefix, sub in sorted(groups.items()):
        header = prefix if prefix else "(no prefix)"
        click.echo(f"[{header}]")
        for key, value in sorted(sub.items()):
            click.echo(f"  {key} = {value}")


@flatten_cli.command("json")
@click.argument("env_file", default=".env")
@click.option("--sep", default="__", show_default=True, help="Key separator")
def flatten_json(env_file: str, sep: str) -> None:
    """Output grouped keys as JSON."""
    path = Path(env_file)
    try:
        groups = flatten_env_file(path, separator=sep)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(groups, indent=2))


@flatten_cli.command("expand")
@click.argument("json_file")
@click.option("--sep", default="__", show_default=True, help="Key separator")
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
def flatten_expand(json_file: str, sep: str, output: str | None) -> None:
    """Expand a JSON nested dict back into .env format."""
    try:
        nested = json.loads(Path(json_file).read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    text = expand_from_dict(nested, separator=sep)
    if output:
        Path(output).write_text(text + "\n")
        click.echo(f"Written to {output}")
    else:
        click.echo(text)
