"""CLI commands for importing and exporting .env files in multiple formats."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.env_import import FORMATS, export_env, import_env, write_env


@click.group("convert")
def convert_cli() -> None:
    """Import/export .env files in dotenv, JSON, or YAML format."""


@convert_cli.command("export")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="json",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output", "-o", "output",
    type=click.Path(path_type=Path),
    default=None,
    help="Write output to this file instead of stdout.",
)
def export_cmd(env_file: Path, fmt: str, output: Path | None) -> None:
    """Export ENV_FILE to the chosen format."""
    try:
        text = export_env(env_file, fmt)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if output:
        output.write_text(text)
        click.echo(f"Exported to {output}")
    else:
        click.echo(text, nl=False)


@convert_cli.command("import")
@click.argument("source_file", type=click.Path(exists=True, path_type=Path))
@click.argument("dest_file", type=click.Path(path_type=Path))
@click.option(
    "--format", "-f", "fmt",
    type=click.Choice(FORMATS, case_sensitive=False),
    default="json",
    show_default=True,
    help="Format of SOURCE_FILE.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite DEST_FILE if it exists.")
def import_cmd(source_file: Path, dest_file: Path, fmt: str, overwrite: bool) -> None:
    """Import SOURCE_FILE (in FORMAT) and write it as a dotenv file to DEST_FILE."""
    if dest_file.exists() and not overwrite:
        click.echo(f"Error: {dest_file} already exists. Use --overwrite to replace it.", err=True)
        sys.exit(1)
    try:
        data = import_env(source_file.read_text(), fmt)
    except (ValueError, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    write_env(data, dest_file)
    click.echo(f"Imported {len(data)} key(s) into {dest_file}")
