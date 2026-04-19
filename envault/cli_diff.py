"""CLI sub-command: envault diff — show changes between vault and .env."""

from __future__ import annotations

from pathlib import Path

import click

from envault.diff import diff_env


@click.command("diff")
@click.argument("env_file", default=".env", type=click.Path(dir_okay=False))
@click.option(
    "--password",
    envvar="ENVAULT_PASSWORD",
    prompt=True,
    hide_input=True,
    help="Vault password (or set ENVAULT_PASSWORD).",
)
@click.option(
    "--context",
    default=3,
    show_default=True,
    help="Lines of context around each change.",
)
def diff_cmd(env_file: str, password: str, context: int) -> None:
    """Show a unified diff between the sealed vault and the current ENV_FILE."""
    path = Path(env_file)

    if not path.exists():
        raise click.ClickException(f"{env_file} does not exist.")

    try:
        result = diff_env(path, password, context_lines=context)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Could not decrypt vault: {exc}") from exc

    if result is None:
        click.secho("No differences — vault and .env are in sync.", fg="green")
    else:
        click.echo(result, nl=False)
        raise SystemExit(1)
