"""CLI commands for detecting unresolved placeholders in .env files."""

from pathlib import Path

import click

from .env_placeholder import find_placeholders_in_file, has_placeholders, summary


@click.group("placeholder")
def placeholder_cli() -> None:
    """Detect unresolved placeholder values in .env files."""


@placeholder_cli.command("check")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--strict", is_flag=True, help="Exit with code 1 if placeholders found.")
def placeholder_check(env_file: str, strict: bool) -> None:
    """List any unresolved placeholders found in ENV_FILE."""
    path = Path(env_file)
    try:
        matches = find_placeholders_in_file(path)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(summary(matches))

    if strict and matches:
        raise SystemExit(1)


@placeholder_cli.command("has")
@click.argument("env_file", default=".env", type=click.Path())
def placeholder_has(env_file: str) -> None:
    """Exit 0 if no placeholders exist, 1 otherwise (useful in scripts)."""
    path = Path(env_file)
    try:
        text = path.read_text()
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc

    if has_placeholders(text):
        click.echo("Unresolved placeholders detected.")
        raise SystemExit(1)
    else:
        click.echo("No unresolved placeholders.")
