"""CLI commands for merging .env files."""
from __future__ import annotations

from pathlib import Path

import click

from .env_merge import MergeStrategy, merge_env_files


@click.group("merge")
def merge_cli() -> None:
    """Merge two .env files with conflict resolution."""


@merge_cli.command("run")
@click.argument("base", type=click.Path(exists=True, path_type=Path))
@click.argument("other", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output file (defaults to BASE).",
)
@click.option(
    "--strategy",
    "-s",
    type=click.Choice([s.value for s in MergeStrategy], case_sensitive=False),
    default=MergeStrategy.OURS.value,
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress conflict output.")
def merge_run(
    base: Path,
    other: Path,
    output: Path | None,
    strategy: str,
    quiet: bool,
) -> None:
    """Merge OTHER into BASE and write to OUTPUT."""
    dest = output or base
    conflicts = merge_env_files(base, other, dest, MergeStrategy(strategy))
    if conflicts and not quiet:
        click.echo(f"⚠  {len(conflicts)} conflict(s) resolved with strategy '{strategy}':")
        for key, base_val, other_val in conflicts:
            click.echo(f"   {key}: kept '{base_val}' (other was '{other_val}')")
    elif not conflicts:
        click.echo("✓ Merged with no conflicts.")
    click.echo(f"Written to {dest}")


@merge_cli.command("preview")
@click.argument("base", type=click.Path(exists=True, path_type=Path))
@click.argument("other", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--strategy",
    "-s",
    type=click.Choice([s.value for s in MergeStrategy], case_sensitive=False),
    default=MergeStrategy.OURS.value,
    show_default=True,
)
def merge_preview(base: Path, other: Path, strategy: str) -> None:
    """Preview the merged result without writing."""
    from .env_merge import merge_env_texts
    base_text = base.read_text()
    other_text = other.read_text()
    merged, conflicts = merge_env_texts(base_text, other_text, MergeStrategy(strategy))
    for key, val in sorted(merged.items()):
        click.echo(f"{key}={val}")
    if conflicts:
        click.echo(f"\n# {len(conflicts)} conflict(s) resolved with '{strategy}'")
