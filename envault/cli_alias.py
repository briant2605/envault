"""CLI commands for managing key aliases."""
from __future__ import annotations

from pathlib import Path

import click

from .env_alias import add_alias, remove_alias, resolve_alias, list_aliases


@click.group("alias")
def alias_cli() -> None:
    """Manage short aliases for .env keys."""


@alias_cli.command("add")
@click.argument("alias")
@click.argument("key")
@click.option("--env-file", default=".env", show_default=True, help="Target .env file.")
def alias_add(alias: str, key: str, env_file: str) -> None:
    """Add ALIAS as a shorthand for KEY."""
    try:
        add_alias(Path(env_file), alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' added.")
    except ValueError as exc:
        raise click.ClickException(str(exc))


@alias_cli.command("remove")
@click.argument("alias")
@click.option("--env-file", default=".env", show_default=True)
def alias_remove(alias: str, env_file: str) -> None:
    """Remove an existing ALIAS."""
    try:
        remove_alias(Path(env_file), alias)
        click.echo(f"Alias '{alias}' removed.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@alias_cli.command("resolve")
@click.argument("alias")
@click.option("--env-file", default=".env", show_default=True)
def alias_resolve(alias: str, env_file: str) -> None:
    """Print the canonical key that ALIAS points to."""
    key = resolve_alias(Path(env_file), alias)
    if key is None:
        raise click.ClickException(f"Alias '{alias}' not found.")
    click.echo(key)


@alias_cli.command("list")
@click.option("--env-file", default=".env", show_default=True)
def alias_list(env_file: str) -> None:
    """List all registered aliases."""
    entries = list_aliases(Path(env_file))
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"{entry['alias']:20s} -> {entry['key']}")
