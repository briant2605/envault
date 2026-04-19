"""CLI commands for searching vault keys."""

from __future__ import annotations

import click

from envault.search import search_keys, list_keys


@click.group("search")
def search_cli() -> None:
    """Search and inspect vault keys."""


@search_cli.command("keys")
@click.argument("env_file")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--pattern", default="*", show_default=True, help="Glob pattern for key names.")
@click.option("--value-contains", default=None, help="Filter by substring in value.")
def search_keys_cmd(
    env_file: str,
    password: str,
    pattern: str,
    value_contains: str | None,
) -> None:
    """Search vault keys matching PATTERN."""
    try:
        matches = search_keys(env_file, password, pattern, value_contains)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(f"Decryption failed: {exc}")

    if not matches:
        click.echo("No matching keys found.")
        return

    for key, value in matches.items():
        click.echo(f"{key}={value}")


@search_cli.command("list")
@click.argument("env_file")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def list_keys_cmd(env_file: str, password: str) -> None:
    """List all key names stored in the vault."""
    try:
        keys = list_keys(env_file, password)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    except ValueError as exc:
        raise click.ClickException(f"Decryption failed: {exc}")

    if not keys:
        click.echo("Vault is empty.")
        return

    for key in keys:
        click.echo(key)
