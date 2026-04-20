"""CLI commands for viewing unlock/lock history."""

import click
from pathlib import Path
from envault.history import get_history, clear_history


@click.group("history")
def history_cli():
    """View and manage lock/unlock history for .env files."""


@history_cli.command("show")
@click.argument("env_file", default=".env")
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
def history_show(env_file: str, limit: int):
    """Show recent lock/unlock history for ENV_FILE."""
    path = Path(env_file)
    entries = get_history(path)
    if not entries:
        click.echo(f"No history found for {env_file}.")
        return
    recent = entries[-limit:]
    for entry in reversed(recent):
        note = f"  [{entry['note']}]" if entry.get("note") else ""
        click.echo(f"{entry['timestamp']}  {entry['action'].upper():6}  {entry['env_file']}{note}")


@history_cli.command("clear")
@click.argument("env_file", default=".env")
@click.confirmation_option(prompt="Clear all history for this file?")
def history_clear(env_file: str):
    """Clear history for ENV_FILE."""
    path = Path(env_file)
    clear_history(path)
    click.echo(f"History cleared for {env_file}.")


@history_cli.command("count")
@click.argument("env_file", default=".env")
def history_count(env_file: str):
    """Show total number of history entries for ENV_FILE."""
    path = Path(env_file)
    entries = get_history(path)
    click.echo(f"{len(entries)} history entries for {env_file}.")
