"""CLI commands for env file statistics."""
from __future__ import annotations

from pathlib import Path

import click

from .env_stats import compute_stats_file


@click.group("stats")
def stats_cli() -> None:
    """Show statistics about a .env file."""


@stats_cli.command("show")
@click.argument("env_file", default=".env")
def stats_show(env_file: str) -> None:
    """Print a full statistics summary for ENV_FILE."""
    path = Path(env_file)
    try:
        stats = compute_stats_file(path)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"Statistics for: {path}")
    click.echo("-" * 36)
    click.echo(stats.summary())


@stats_cli.command("count")
@click.argument("env_file", default=".env")
def stats_count(env_file: str) -> None:
    """Print only the total number of keys in ENV_FILE."""
    path = Path(env_file)
    try:
        stats = compute_stats_file(path)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(stats.total_keys)


@stats_cli.command("sensitive")
@click.argument("env_file", default=".env")
def stats_sensitive(env_file: str) -> None:
    """Print the number of sensitive-looking keys in ENV_FILE."""
    path = Path(env_file)
    try:
        stats = compute_stats_file(path)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(stats.sensitive_keys)
