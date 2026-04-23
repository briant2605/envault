"""CLI commands for env-key namespace management."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_namespace import (
    assign_namespace,
    delete_namespace,
    find_namespaces_for_key,
    get_namespace_keys,
    list_namespaces,
    remove_from_namespace,
)


@click.group("namespace")
def namespace_cli() -> None:
    """Manage logical namespaces for .env keys."""


@namespace_cli.command("add")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("namespace")
@click.argument("key")
def namespace_add(env_file: str, namespace: str, key: str) -> None:
    """Add KEY to NAMESPACE."""
    assign_namespace(Path(env_file), key, namespace)
    click.echo(f"Key '{key}' added to namespace '{namespace}'.")


@namespace_cli.command("remove")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("namespace")
@click.argument("key")
def namespace_remove(env_file: str, namespace: str, key: str) -> None:
    """Remove KEY from NAMESPACE."""
    try:
        remove_from_namespace(Path(env_file), key, namespace)
        click.echo(f"Key '{key}' removed from namespace '{namespace}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@namespace_cli.command("list")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--namespace", "-n", default=None, help="Show keys in this namespace.")
def namespace_list(env_file: str, namespace: str | None) -> None:
    """List namespaces (or keys within a specific namespace)."""
    path = Path(env_file)
    if namespace:
        keys = get_namespace_keys(path, namespace)
        if not keys:
            click.echo(f"Namespace '{namespace}' is empty.")
        else:
            for k in keys:
                click.echo(k)
    else:
        namespaces = list_namespaces(path)
        if not namespaces:
            click.echo("No namespaces defined.")
        else:
            for ns in namespaces:
                click.echo(ns)


@namespace_cli.command("find")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("key")
def namespace_find(env_file: str, key: str) -> None:
    """Find all namespaces that contain KEY."""
    namespaces = find_namespaces_for_key(Path(env_file), key)
    if not namespaces:
        click.echo(f"Key '{key}' is not in any namespace.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_cli.command("delete")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("namespace")
def namespace_delete(env_file: str, namespace: str) -> None:
    """Delete an entire NAMESPACE."""
    try:
        delete_namespace(Path(env_file), namespace)
        click.echo(f"Namespace '{namespace}' deleted.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
