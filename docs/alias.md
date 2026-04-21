# Key Aliases

The `alias` feature lets you register short, memorable names for long `.env` keys.
This is useful in teams where canonical key names are verbose but you want a quick
shorthand in scripts or documentation.

## Storage

Aliases are stored in `.envault_aliases.json` next to your `.env` file.
Add this file to version control so the whole team shares the same aliases.

## Commands

### Add an alias

```bash
envault alias add host DB_HOST
envault alias add port DB_PORT --env-file .env.production
```

### Resolve an alias to its canonical key

```bash
envault alias resolve host
# DB_HOST
```

### List all aliases

```bash
envault alias list
# host                 -> DB_HOST
# port                 -> DB_PORT
```

### Remove an alias

```bash
envault alias remove host
```

## Python API

```python
from pathlib import Path
from envault.env_alias import add_alias, resolve_alias, list_aliases, remove_alias

env = Path(".env")

add_alias(env, "host", "DB_HOST")
print(resolve_alias(env, "host"))   # "DB_HOST"
print(list_aliases(env))            # [{"alias": "host", "key": "DB_HOST"}]
remove_alias(env, "host")
```

## Notes

- Aliases are **not** keys themselves; they are purely a lookup table.
- Duplicate alias names are rejected with an error.
- Each `.env` file has its own independent alias store.
