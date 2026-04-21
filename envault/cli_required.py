"""CLI commands for managing required keys in a .env file."""
from __future__ import annotations

import click
from pathlib import Path

from .env_required import (
    check_required,
    load_required_keys,
    save_required_keys,
)


@click.group("required")
def required_cli() -> None:
    """Manage required keys for a .env file."""


@required_cli.command("add")
@click.argument("env_file", type=click.Path(dir_okay=False))
@click.argument("keys", nargs=-1, required=True)
def required_add(env_file: str, keys: tuple) -> None:
    """Add one or more keys to the required list."""
    path = Path(env_file)
    existing = load_required_keys(path)
    merged = sorted(set(existing) | set(keys))
    save_required_keys(path, merged)
    click.echo(f"Required keys updated: {', '.join(merged)}")


@required_cli.command("remove")
@click.argument("env_file", type=click.Path(dir_okay=False))
@click.argument("keys", nargs=-1, required=True)
def required_remove(env_file: str, keys: tuple) -> None:
    """Remove one or more keys from the required list."""
    path = Path(env_file)
    existing = set(load_required_keys(path))
    updated = sorted(existing - set(keys))
    save_required_keys(path, updated)
    click.echo(f"Required keys updated: {', '.join(updated) or '(none)'}")


@required_cli.command("list")
@click.argument("env_file", type=click.Path(dir_okay=False))
def required_list(env_file: str) -> None:
    """List all required keys for a .env file."""
    keys = load_required_keys(Path(env_file))
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo("No required keys defined.")


@required_cli.command("check")
@click.argument("env_file", type=click.Path(dir_okay=False))
@click.option("--strict", is_flag=True, help="Exit with non-zero code if any key is missing.")
def required_check(env_file: str, strict: bool) -> None:
    """Check which required keys are present or missing."""
    path = Path(env_file)
    report = check_required(path)
    click.echo(report.summary())
    if strict and not report.ok:
        raise SystemExit(1)
