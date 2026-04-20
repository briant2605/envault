"""CLI commands for envault lint."""

from __future__ import annotations

from pathlib import Path

import click

from envault.lint import format_issues, lint_env


@click.group(name="lint")
def lint_cli() -> None:
    """Lint .env files for common issues."""


@lint_cli.command(name="check")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too.")
def lint_check(env_file: str, strict: bool) -> None:
    """Check ENV_FILE for lint issues and report them."""
    path = Path(env_file)
    try:
        issues = lint_env(path)
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {env_file}")

    errors = [i for i in issues if i.code.startswith("E")]
    warnings = [i for i in issues if i.code.startswith("W")]

    if not issues:
        click.echo(click.style("✔ No issues found.", fg="green"))
        return

    for issue in issues:
        colour = "red" if issue.code.startswith("E") else "yellow"
        loc = f"line {issue.line}"
        key_part = f" [{issue.key}]" if issue.key else ""
        click.echo(click.style(f"{issue.code}{key_part} @ {loc}: {issue.message}", fg=colour))

    summary = f"{len(errors)} error(s), {len(warnings)} warning(s)."
    click.echo(summary)

    if errors or (strict and warnings):
        raise SystemExit(1)


@lint_cli.command(name="summary")
@click.argument("env_file", default=".env", type=click.Path())
def lint_summary(env_file: str) -> None:
    """Print a one-line summary of lint results for ENV_FILE."""
    path = Path(env_file)
    try:
        issues = lint_env(path)
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {env_file}")

    errors = sum(1 for i in issues if i.code.startswith("E"))
    warnings = sum(1 for i in issues if i.code.startswith("W"))
    colour = "green" if not issues else ("red" if errors else "yellow")
    click.echo(click.style(f"{env_file}: {errors} error(s), {warnings} warning(s).", fg=colour))
