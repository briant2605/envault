"""CLI commands for tag management."""
import click
from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags


@click.group("tags")
def tags_cli():
    """Manage tags for vault entries."""


@tags_cli.command("add")
@click.argument("env_path")
@click.argument("tag")
def tag_add(env_path: str, tag: str):
    """Add TAG to ENV_PATH."""
    add_tag(env_path, tag)
    click.echo(f"Tag '{tag}' added to '{env_path}'.")


@tags_cli.command("remove")
@click.argument("env_path")
@click.argument("tag")
def tag_remove(env_path: str, tag: str):
    """Remove TAG from ENV_PATH."""
    try:
        remove_tag(env_path, tag)
        click.echo(f"Tag '{tag}' removed from '{env_path}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc))


@tags_cli.command("list")
@click.argument("env_path")
def tag_list(env_path: str):
    """List all tags for ENV_PATH."""
    tags = get_tags(env_path)
    if not tags:
        click.echo("No tags found.")
    else:
        for t in tags:
            click.echo(t)


@tags_cli.command("find")
@click.argument("tag")
def tag_find(tag: str):
    """Find all env paths with TAG."""
    paths = find_by_tag(tag)
    if not paths:
        click.echo("No entries found.")
    else:
        for p in paths:
            click.echo(p)


@tags_cli.command("clear")
@click.argument("env_path")
def tag_clear(env_path: str):
    """Remove all tags from ENV_PATH."""
    clear_tags(env_path)
    click.echo(f"All tags cleared for '{env_path}'.")
