"""CLI commands for setting/unsetting/getting individual .env keys."""

import click
from pathlib import Path
from envault.env_set import set_key, unset_key, get_key


@click.group("set")
def set_cli() -> None:
    """Set, unset, or get individual keys in a .env file."""


@set_cli.command("put")
@click.argument("key")
@click.argument("value")
@click.option(
    "--env-file",
    default=".env",
    show_default=True,
    help="Path to the .env file.",
)
def set_put(key: str, value: str, env_file: str) -> None:
    """Set KEY=VALUE in the .env file."""
    path = Path(env_file)
    set_key(path, key, value)
    click.echo(f"Set {key} in {env_file}")


@set_cli.command("unset")
@click.argument("key")
@click.option(
    "--env-file",
    default=".env",
    show_default=True,
    help="Path to the .env file.",
)
def set_unset(key: str, env_file: str) -> None:
    """Remove KEY from the .env file."""
    path = Path(env_file)
    try:
        unset_key(path, key)
        click.echo(f"Removed {key} from {env_file}")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@set_cli.command("get")
@click.argument("key")
@click.option(
    "--env-file",
    default=".env",
    show_default=True,
    help="Path to the .env file.",
)
def set_get(key: str, env_file: str) -> None:
    """Print the value of KEY from the .env file."""
    path = Path(env_file)
    value = get_key(path, key)
    if value is None:
        raise click.ClickException(f"Key '{key}' not found in {env_file}")
    click.echo(value)
