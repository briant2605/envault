"""CLI commands for managing envault profiles."""

import click
from envault.profile import set_profile, get_profile, delete_profile, list_profiles


@click.group("profile")
def profile_cli():
    """Manage named password profiles."""


@profile_cli.command("set")
@click.argument("name")
@click.password_option("--password", prompt=True, help="Password for the profile.")
def profile_set(name, password):
    """Create or update a named profile."""
    set_profile(name, password)
    click.echo(f"Profile '{name}' saved.")


@profile_cli.command("get")
@click.argument("name")
def profile_get(name):
    """Show the password stored in a profile."""
    try:
        p = get_profile(name)
        click.echo(f"Profile '{name}': password={p['password']}")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cli.command("delete")
@click.argument("name")
def profile_delete(name):
    """Delete a named profile."""
    try:
        delete_profile(name)
        click.echo(f"Profile '{name}' deleted.")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@profile_cli.command("list")
def profile_list():
    """List all saved profiles."""
    names = list_profiles()
    if not names:
        click.echo("No profiles found.")
    else:
        for name in names:
            click.echo(f"  - {name}")
