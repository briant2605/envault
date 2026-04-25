# envault flatten

The `flatten` feature lets you **group** prefixed `.env` keys into a structured
representation and **expand** a structured dict back to `.env` format.

## Motivation

Many projects use a naming convention like `DB__HOST`, `DB__PORT`, `APP__NAME`
to indicate logical groupings inside a flat `.env` file.  
`envault flatten` makes these groups explicit and lets you inspect or export
them as JSON.

## Commands

### `envault flatten show [ENV_FILE]`

Display keys grouped by their prefix.

```
$ envault flatten show .env
[APP]
  DEBUG = true
  NAME  = myapp
[DB]
  HOST = localhost
  PORT = 5432
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--sep` | `__` | Separator between prefix and key |

---

### `envault flatten json [ENV_FILE]`

Output the grouped keys as a JSON object.

```
$ envault flatten json .env
{
  "APP": {
    "DEBUG": "true",
    "NAME": "myapp"
  },
  "DB": {
    "HOST": "localhost",
    "PORT": "5432"
  }
}
```

---

### `envault flatten expand JSON_FILE`

Expand a JSON nested dict back into `.env` format.

```
$ envault flatten expand groups.json -o .env.expanded
Written to .env.expanded
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--sep` | `__` | Separator used when reconstructing keys |
| `-o / --output` | stdout | Write result to file instead of stdout |

---

## Python API

```python
from envault.env_flatten import flatten_to_dict, expand_from_dict, flatten_env_file

# Read from file
groups = flatten_env_file(Path(".env"))
# groups == {"DB": {"HOST": "localhost", "PORT": "5432"}, ...}

# Expand back
text = expand_from_dict(groups)
```

## Notes

- Keys without a separator are placed under the `""` (empty-string) group.
- Comments and blank lines are ignored during parsing.
- The separator can be any string (default `__`).
