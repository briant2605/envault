"""CLI commands for managing inline .env comments."""
from __future__ import annotations

from pathlib import Path

import click

from .env_comment import (
    set_comment_in_file,
    remove_comment_in_file,
    get_comment_from_file,
)


@click.group("comment")
def comment_cli() -> None:
    """Manage inline comments on .env keys."""


@comment_cli.command("set")
@click.argument("key")
@click.argument("comment")
@click.option("--env", "env_path", default=".env", show_default=True, help="Path to .env file")
def comment_set(key: str, comment: str, env_path: str) -> None:
    """Set or replace the inline comment for KEY."""
    path = Path(env_path)
    if not path.exists():
        raise click.ClickException(f"{env_path} not found")
    try:
        set_comment_in_file(path, key, comment)
        click.echo(f"Comment set on '{key}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@comment_cli.command("remove")
@click.argument("key")
@click.option("--env", "env_path", default=".env", show_default=True)
def comment_remove(key: str, env_path: str) -> None:
    """Remove the inline comment from KEY."""
    path = Path(env_path)
    if not path.exists():
        raise click.ClickException(f"{env_path} not found")
    try:
        remove_comment_in_file(path, key)
        click.echo(f"Comment removed from '{key}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@comment_cli.command("get")
@click.argument("key")
@click.option("--env", "env_path", default=".env", show_default=True)
def comment_get(key: str, env_path: str) -> None:
    """Show the inline comment for KEY."""
    path = Path(env_path)
    if not path.exists():
        raise click.ClickException(f"{env_path} not found")
    try:
        value = get_comment_from_file(path, key)
        if value is None:
            click.echo(f"No comment on '{key}'.")
        else:
            click.echo(value)
    except KeyError as exc:
        raise click.ClickException(str(exc))
