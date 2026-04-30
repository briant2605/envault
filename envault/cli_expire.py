"""cli_expire.py — CLI commands for key expiry management."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from envault.env_expire import (
    check_expiry,
    get_expiry,
    remove_expiry,
    set_expiry,
)


@click.group("expire")
def expire_cli() -> None:
    """Manage expiry dates for .env keys."""


@expire_cli.command("set")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("key")
@click.argument("expiry")  # ISO date: YYYY-MM-DD
def expire_set(env_file: Path, key: str, expiry: str) -> None:
    """Set an expiry date for KEY in ENV_FILE."""
    try:
        d = date.fromisoformat(expiry)
    except ValueError:
        raise click.BadParameter(f"Invalid date '{expiry}'. Use YYYY-MM-DD.")
    set_expiry(env_file, key, d)
    click.echo(f"Set expiry for '{key}' to {d.isoformat()}.")


@expire_cli.command("remove")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("key")
def expire_remove(env_file: Path, key: str) -> None:
    """Remove the expiry date for KEY in ENV_FILE."""
    remove_expiry(env_file, key)
    click.echo(f"Removed expiry for '{key}'.")


@expire_cli.command("get")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.argument("key")
def expire_get(env_file: Path, key: str) -> None:
    """Show the expiry date for KEY."""
    d = get_expiry(env_file, key)
    if d is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        click.echo(d.isoformat())


@expire_cli.command("check")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option("--expired-only", is_flag=True, help="Show only expired keys.")
def expire_check(env_file: Path, expired_only: bool) -> None:
    """Check all key expiry dates in ENV_FILE."""
    reports = check_expiry(env_file)
    if not reports:
        click.echo("No expiry dates tracked.")
        return
    shown = [r for r in reports if r.expired] if expired_only else reports
    for r in shown:
        click.echo(str(r))
    expired = [r for r in reports if r.expired]
    if expired:
        raise SystemExit(1)
