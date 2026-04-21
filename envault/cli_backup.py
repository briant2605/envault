"""CLI commands for env file backup/restore."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_backup import (
    create_backup,
    delete_backup,
    list_backups,
    purge_backups,
    restore_backup,
)


@click.group("backup")
def backup_cli() -> None:
    """Backup and restore .env files."""


@backup_cli.command("create")
@click.argument("env_file", default=".env")
def backup_create(env_file: str) -> None:
    """Create a timestamped backup of ENV_FILE."""
    path = Path(env_file)
    try:
        dest = create_backup(path)
        click.echo(f"Backup created: {dest}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@backup_cli.command("list")
@click.argument("env_file", default=".env")
def backup_list(env_file: str) -> None:
    """List all backups for ENV_FILE."""
    backups = list_backups(Path(env_file))
    if not backups:
        click.echo("No backups found.")
        return
    for b in backups:
        click.echo(str(b))


@backup_cli.command("restore")
@click.argument("backup_file")
@click.argument("env_file", default=".env")
def backup_restore(backup_file: str, env_file: str) -> None:
    """Restore ENV_FILE from BACKUP_FILE."""
    try:
        restore_backup(Path(env_file), Path(backup_file))
        click.echo(f"Restored {env_file} from {backup_file}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@backup_cli.command("delete")
@click.argument("backup_file")
def backup_delete(backup_file: str) -> None:
    """Delete a single BACKUP_FILE."""
    try:
        delete_backup(Path(backup_file))
        click.echo(f"Deleted backup: {backup_file}")
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@backup_cli.command("purge")
@click.argument("env_file", default=".env")
@click.confirmation_option(prompt="Delete ALL backups for this file?")
def backup_purge(env_file: str) -> None:
    """Delete all backups for ENV_FILE."""
    count = purge_backups(Path(env_file))
    click.echo(f"Purged {count} backup(s).")
