"""CLI commands for .env validation."""
from __future__ import annotations

import json
from pathlib import Path

import click

from .env_validate import ValidationRule, validate_env


@click.groupvalidate")
def validate_cli() -> None:
    """Validate .env files against a schema."""


def __schema(schema_path: Path) -> list[ValidationRule]:
    """Load validation rules from a JSON schema file."""
    data = json.loads(schema_n    rules = []
    for entry in data.get("rules", []):
        rules.append(
            ValidationRule(
                key=entry["key"],
                required=entry.get("required", True),
                pattern=entry.get("pattern"),
                min_length=entry.get("min_length"),
                max_length=entry.get("max_length"),
                allowed_values=entry.get("allowed_values", []),
            )
        )
    return rules


@validate_cli.command("check")
@click.argument("env_file", default=".env", type=click.Path())
@click.option(
    "--schema",
    "schema_path",
    default=".envschema.json",
    show_default=True,
    type=click.Path(),
    help="Path to JSON schema file.",
)
def validate_check(env_file: str, schema_path: str) -> None:
    """Check ENV_FILE against a validation schema."""
    schema = Path(schema_path)
    if not schema.exists():
        raise click.ClickException(f"Schema file not found: {schema_path}")

    rules = _load_schema(schema)
    errors = validate_env(Path(env_file), rules)

    if not errors:
        click.echo(click.style("All checks passed.", fg="green"))
        return

    click.echo(click.style(f"{len(errors)} validation error(s) found:", fg="red"))
    for err in errors:
        click.echo(f"  {err}")
    raise SystemExit(1)


@validate_cli.command("init-schema")
@click.argument("env_file", default=".env", type=click.Path())
@click.option("--output", default=".envschema.json", show_default=True)
def validate_init_schema(env_file: str, output: str) -> None:
    """Generate a starter schema from an existing .env file."""
    path = Path(env_file)
    if not path.exists():
        raise click.ClickException(f"{env_file} not found")

    keys = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k = line.split("=", 1)[0].strip()
            keys.append({"key": k, "required": True})

    schema = {"rules": keys}
    Path(output).write_text(json.dumps(schema, indent=2))
    click.echo(f"Schema written to {output} ({len(keys)} keys).")
