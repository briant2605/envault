"""CLI commands for key pinning."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_pin import clear_pins, get_pinned, is_pinned, pin_key, unpin_key


@click.group("pin")
def pin_cli() -> None:
    """Pin or unpin .env keys to protect them from being overwritten."""


@pin_cli.command("add")
@click.argument("key")
@click.option("--env", "env_file", default=".env", show_default=True, help="Target .env file.")
def pin_add(key: str, env_file: str) -> None:
    """Pin KEY so it is protected from merge/import overwrites."""
    path = Path(env_file)
    pin_key(path, key)
    click.echo(f"Pinned {key!r} in {env_file}")


@pin_cli.command("remove")
@click.argument("key")
@click.option("--env", "env_file", default=".env", show_default=True)
def pin_remove(key: str, env_file: str) -> None:
    """Unpin KEY."""
    path = Path(env_file)
    try:
        unpin_key(path, key)
        click.echo(f"Unpinned {key!r} in {env_file}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@pin_cli.command("list")
@click.option("--env", "env_file", default=".env", show_default=True)
def pin_list(env_file: str) -> None:
    """List all pinned keys for the given .env file."""
    path = Path(env_file)
    pins = get_pinned(path)
    if not pins:
        click.echo("No pinned keys.")
    else:
        for key in pins:
            click.echo(key)


@pin_cli.command("check")
@click.argument("key")
@click.option("--env", "env_file", default=".env", show_default=True)
def pin_check(key: str, env_file: str) -> None:
    """Check whether KEY is pinned."""
    path = Path(env_file)
    if is_pinned(path, key):
        click.echo(f"{key!r} is pinned.")
    else:
        click.echo(f"{key!r} is NOT pinned.")


@pin_cli.command("clear")
@click.option("--env", "env_file", default=".env", show_default=True)
def pin_clear(env_file: str) -> None:
    """Remove all pins for the given .env file."""
    path = Path(env_file)
    clear_pins(path)
    click.echo(f"All pins cleared for {env_file}")
