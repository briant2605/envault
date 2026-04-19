"""Command-line interface for envault."""

import click
from envault.vault import seal, unseal


@click.group()
@click.version_option(package_name="envault")
def cli():
    """envault — encrypt and manage your .env files."""


@cli.command()
@click.argument("env_file", default=".env")
@click.option("--output", "-o", default=None, help="Output vault file path.")
@click.password_option("--password", "-p", help="Encryption password.")
def lock(env_file, output, password):
    """Encrypt ENV_FILE into a vault file."""
    try:
        out = seal(env_file, password, output)
        click.secho(f"Sealed → {out}", fg="green")
    except FileNotFoundError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@cli.command()
@click.argument("vault_file", default=".env.vault")
@click.option("--output", "-o", default=None, help="Output .env file path.")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Decryption password.")
def unlock(vault_file, output, password):
    """Decrypt VAULT_FILE back into a .env file."""
    try:
        out = unseal(vault_file, password, output)
        click.secho(f"Unsealed → {out}", fg="green")
    except FileNotFoundError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)
    except ValueError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
