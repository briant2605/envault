"""cli_echo.py — CLI commands for echoing resolved env vars."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_echo import echo_env


@click.group("echo")
def echo_cli() -> None:
    """Echo resolved environment variables."""


@echo_cli.command("show")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--mask", is_flag=True, default=False, help="Redact sensitive values.")
@click.option("--prefix", default=None, help="Only show keys with this prefix.")
@click.option(
    "--export", "use_export", is_flag=True, default=False,
    help="Prepend 'export' to each line."
)
def echo_show(
    env_file: str,
    mask: bool,
    prefix: str | None,
    use_export: bool,
) -> None:
    """Print all (or filtered) env vars from ENV_FILE."""
    path = Path(env_file)
    try:
        lines = echo_env(path, mask=mask, prefix=prefix, export=use_export)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if not lines:
        click.echo("(no matching variables)")
        return

    for line in lines:
        click.echo(line)


@echo_cli.command("count")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--prefix", default=None, help="Only count keys with this prefix.")
def echo_count(env_file: str, prefix: str | None) -> None:
    """Print the number of env vars in ENV_FILE."""
    path = Path(env_file)
    try:
        lines = echo_env(path, prefix=prefix)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(str(len(lines)))
