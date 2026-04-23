"""CLI commands for chaining multiple .env files."""
from __future__ import annotations

from pathlib import Path
from typing import List

import click

from envault.env_chain import chain_env_files, chain_sources, _to_dotenv


@click.group("chain")
def chain_cli() -> None:
    """Chain multiple .env files together (later files override earlier ones)."""


@chain_cli.command("run")
@click.argument("files", nargs=-1, required=True, type=click.Path())
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write merged result to this file instead of stdout.")
def chain_run(files: List[str], output: str | None) -> None:
    """Merge FILES in order and print (or write) the result."""
    paths = [Path(f) for f in files]
    merged = chain_env_files(paths)
    result = _to_dotenv(merged)
    if output:
        Path(output).write_text(result)
        click.echo(f"Merged {len(paths)} file(s) → {output}")
    else:
        click.echo(result, nl=False)


@chain_cli.command("preview")
@click.argument("files", nargs=-1, required=True, type=click.Path())
def chain_preview(files: List[str]) -> None:
    """Show merged keys and which file each key originates from."""
    paths = [Path(f) for f in files]
    merged, provenance = chain_sources(paths)
    if not merged:
        click.echo("No keys found.")
        return
    max_key = max(len(k) for k in merged)
    for key in sorted(merged):
        src = provenance.get(key, "?")
        click.echo(f"{key:<{max_key}}  ← {src}")


@chain_cli.command("count")
@click.argument("files", nargs=-1, required=True, type=click.Path())
def chain_count(files: List[str]) -> None:
    """Print the number of unique keys after chaining FILES."""
    paths = [Path(f) for f in files]
    merged = chain_env_files(paths)
    click.echo(str(len(merged)))
