"""CLI commands for the doctor feature."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_doctor import run_doctor


@click.group("doctor")
def doctor_cli() -> None:
    """Diagnose issues with a .env file and its vault."""


@doctor_cli.command("check")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--strict", is_flag=True, help="Exit non-zero on warnings too.")
def doctor_check(env_file: str, strict: bool) -> None:
    """Run all health checks on ENV_FILE."""
    path = Path(env_file)
    report = run_doctor(path)

    click.echo(f"envault doctor — {path}")
    click.echo("")

    for msg in report.checks:
        click.echo(click.style(f"  ✓ {msg}", fg="green"))

    for msg in report.warnings:
        click.echo(click.style(f"  ⚠ {msg}", fg="yellow"))

    for msg in report.errors:
        click.echo(click.style(f"  ✗ {msg}", fg="red"))

    click.echo("")
    if report.errors:
        click.echo(click.style("Result: FAIL", fg="red", bold=True))
        raise SystemExit(1)
    if strict and report.warnings:
        click.echo(click.style("Result: FAIL (strict mode — warnings treated as errors)", fg="yellow", bold=True))
        raise SystemExit(1)
    click.echo(click.style("Result: OK", fg="green", bold=True))


@doctor_cli.command("summary")
@click.argument("env_file", default=".env", type=click.Path())
def doctor_summary(env_file: str) -> None:
    """Print a one-line summary of the health status."""
    path = Path(env_file)
    report = run_doctor(path)
    status = "OK" if report.ok else "FAIL"
    w = len(report.warnings)
    e = len(report.errors)
    c = len(report.checks)
    click.echo(f"{path}: {status} | checks={c} warnings={w} errors={e}")
