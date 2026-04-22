"""CLI commands for env key scope management."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_scope import (
    assign_scope,
    get_scopes,
    keys_in_scope,
    list_scopes,
    remove_scope,
)


@click.group("scope")
def scope_cli() -> None:
    """Manage scopes for .env keys (e.g. dev, prod, test)."""


@scope_cli.command("add")
@click.argument("key")
@click.argument("scope")
@click.option("--env", "env_file", default=".env", show_default=True)
def scope_add(key: str, scope: str, env_file: str) -> None:
    """Assign SCOPE to KEY."""
    assign_scope(Path(env_file), key, scope)
    click.echo(f"Assigned scope '{scope}' to '{key}'.")


@scope_cli.command("remove")
@click.argument("key")
@click.argument("scope")
@click.option("--env", "env_file", default=".env", show_default=True)
def scope_remove(key: str, scope: str, env_file: str) -> None:
    """Remove SCOPE from KEY."""
    try:
        remove_scope(Path(env_file), key, scope)
        click.echo(f"Removed scope '{scope}' from '{key}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@scope_cli.command("list")
@click.option("--env", "env_file", default=".env", show_default=True)
def scope_list(env_file: str) -> None:
    """List all key→scope assignments."""
    mapping = list_scopes(Path(env_file))
    if not mapping:
        click.echo("No scopes defined.")
        return
    for key, scopes in sorted(mapping.items()):
        click.echo(f"{key}: {', '.join(scopes)}")


@scope_cli.command("get")
@click.argument("key")
@click.option("--env", "env_file", default=".env", show_default=True)
def scope_get(key: str, env_file: str) -> None:
    """Show scopes assigned to KEY."""
    scopes = get_scopes(Path(env_file), key)
    if scopes:
        click.echo(", ".join(scopes))
    else:
        click.echo(f"No scopes assigned to '{key}'.")


@scope_cli.command("find")
@click.argument("scope")
@click.option("--env", "env_file", default=".env", show_default=True)
def scope_find(scope: str, env_file: str) -> None:
    """List all keys assigned to SCOPE."""
    keys = keys_in_scope(Path(env_file), scope)
    if keys:
        for k in sorted(keys):
            click.echo(k)
    else:
        click.echo(f"No keys assigned to scope '{scope}'.")
