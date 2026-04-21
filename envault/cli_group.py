"""CLI commands for key group management."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_group import (
    add_to_group,
    delete_group,
    get_group,
    list_groups,
    remove_from_group,
)


@click.group("group")
def group_cli() -> None:
    """Manage named groups of .env keys."""


@group_cli.command("add")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("group")
@click.argument("key")
def group_add(env_file: Path, group: str, key: str) -> None:
    """Add KEY to GROUP in ENV_FILE."""
    add_to_group(env_file, group, key)
    click.echo(f"Added '{key}' to group '{group}'.")


@group_cli.command("remove")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("group")
@click.argument("key")
def group_remove(env_file: Path, group: str, key: str) -> None:
    """Remove KEY from GROUP in ENV_FILE."""
    try:
        remove_from_group(env_file, group, key)
        click.echo(f"Removed '{key}' from group '{group}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@group_cli.command("list")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("group", required=False)
def group_list(env_file: Path, group: str | None) -> None:
    """List groups (or keys in a specific GROUP) for ENV_FILE."""
    if group:
        keys = get_group(env_file, group)
        if keys:
            click.echo("\n".join(keys))
        else:
            click.echo(f"Group '{group}' is empty or does not exist.")
    else:
        groups = list_groups(env_file)
        if groups:
            click.echo("\n".join(groups))
        else:
            click.echo("No groups defined.")


@group_cli.command("delete")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("group")
def group_delete(env_file: Path, group: str) -> None:
    """Delete an entire GROUP from ENV_FILE."""
    try:
        delete_group(env_file, group)
        click.echo(f"Deleted group '{group}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
