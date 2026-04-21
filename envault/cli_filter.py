"""CLI commands for filtering .env keys."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from .env_filter import filter_env_file


@click.group("filter")
def filter_cli() -> None:
    """Filter .env keys by prefix, suffix, glob, or regex."""


def _print_result(result: dict, show_values: bool) -> None:
    if not result:
        click.echo("(no matching keys)")
        return
    for key, value in sorted(result.items()):
        if show_values:
            click.echo(f"{key}={value}")
        else:
            click.echo(key)


@filter_cli.command("run")
@click.argument("env_file", default=".env")
@click.option("--prefix", default=None, help="Keep keys starting with this prefix.")
@click.option("--suffix", default=None, help="Keep keys ending with this suffix.")
@click.option("--glob", default=None, help="Keep keys matching a glob pattern.")
@click.option("--regex", default=None, help="Keep keys matching a regex pattern.")
@click.option("--values/--no-values", default=True, show_default=True,
              help="Include values in output.")
def filter_run(
    env_file: str,
    prefix: Optional[str],
    suffix: Optional[str],
    glob: Optional[str],
    regex: Optional[str],
    values: bool,
) -> None:
    """Filter keys in ENV_FILE and print matches."""
    path = Path(env_file)
    if not path.exists():
        raise click.ClickException(f"File not found: {env_file}")
    if not any([prefix, suffix, glob, regex]):
        raise click.ClickException(
            "Provide at least one of --prefix, --suffix, --glob, --regex."
        )
    result = filter_env_file(
        path, prefix=prefix, suffix=suffix, glob=glob, regex=regex
    )
    _print_result(result, show_values=values)


@filter_cli.command("count")
@click.argument("env_file", default=".env")
@click.option("--prefix", default=None)
@click.option("--suffix", default=None)
@click.option("--glob", default=None)
@click.option("--regex", default=None)
def filter_count(
    env_file: str,
    prefix: Optional[str],
    suffix: Optional[str],
    glob: Optional[str],
    regex: Optional[str],
) -> None:
    """Print the number of keys that match the given filters."""
    path = Path(env_file)
    result = filter_env_file(
        path, prefix=prefix, suffix=suffix, glob=glob, regex=regex
    )
    click.echo(len(result))
