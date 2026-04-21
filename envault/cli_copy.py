"""CLI commands for copying variables between .env files."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_copy import copy_keys


@click.group("copy")
def copy_cli() -> None:
    """Copy environment variables between .env files."""


@copy_cli.command("run")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(path_type=Path))
@click.option(
    "-k",
    "--key",
    "keys",
    multiple=True,
    help="Key to copy (repeat for multiple). Omit to copy all.",
)
@click.option(
    "--no-overwrite",
    is_flag=True,
    default=False,
    help="Skip keys already present in destination.",
)
def copy_run(
    src: Path,
    dst: Path,
    keys: tuple[str, ...],
    no_overwrite: bool,
) -> None:
    """Copy variables from SRC to DST."""
    try:
        written = copy_keys(
            src,
            dst,
            keys=list(keys) if keys else None,
            overwrite=not no_overwrite,
        )
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if written:
        click.echo(f"Copied {len(written)} key(s) to {dst}:")
        for k in sorted(written):
            click.echo(f"  {k}")
    else:
        click.echo("No keys were copied (all already present or none matched).")


@copy_cli.command("preview")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(path_type=Path))
@click.option("-k", "--key", "keys", multiple=True)
@click.option("--no-overwrite", is_flag=True, default=False)
def copy_preview(
    src: Path,
    dst: Path,
    keys: tuple[str, ...],
    no_overwrite: bool,
) -> None:
    """Preview which keys would be copied without writing anything."""
    from envault.env_copy import _parse_env  # noqa: PLC0415

    src_pairs = _parse_env(src.read_text())
    dst_pairs = _parse_env(dst.read_text()) if dst.exists() else {}

    candidates = {k: v for k, v in src_pairs.items() if not keys or k in keys}
    would_write = {
        k: v
        for k, v in candidates.items()
        if not (no_overwrite and k in dst_pairs)
    }

    if would_write:
        click.echo(f"Would copy {len(would_write)} key(s) to {dst}:")
        for k in sorted(would_write):
            click.echo(f"  {k}")
    else:
        click.echo("Nothing to copy.")
