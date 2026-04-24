"""CLI commands for truncating long .env values in display output."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_truncate import DEFAULT_MAX_LENGTH, truncate_env_file


@click.group("truncate")
def truncate_cli() -> None:
    """Display .env values truncated to a maximum length."""


@truncate_cli.command("show")
@click.argument("env_file", default=".env")
@click.option(
    "--max-length",
    "-n",
    default=DEFAULT_MAX_LENGTH,
    show_default=True,
    help="Maximum number of characters per value.",
)
@click.option("--only-truncated", is_flag=True, help="Show only truncated entries.")
def truncate_show(
    env_file: str, max_length: int, only_truncated: bool
) -> None:
    """Show .env values truncated to MAX_LENGTH characters."""
    path = Path(env_file)
    try:
        entries = truncate_env_file(path, max_length=max_length)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not entries:
        click.echo("No keys found.")
        return

    for entry in entries:
        if only_truncated and not entry.was_truncated:
            continue
        marker = click.style(" [truncated]", fg="yellow") if entry.was_truncated else ""
        click.echo(f"{entry.key}={entry.truncated_value}{marker}")


@truncate_cli.command("count")
@click.argument("env_file", default=".env")
@click.option(
    "--max-length",
    "-n",
    default=DEFAULT_MAX_LENGTH,
    show_default=True,
    help="Maximum number of characters per value.",
)
def truncate_count(env_file: str, max_length: int) -> None:
    """Count how many values exceed MAX_LENGTH characters."""
    path = Path(env_file)
    try:
        entries = truncate_env_file(path, max_length=max_length)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    count = sum(1 for e in entries if e.was_truncated)
    click.echo(str(count))
