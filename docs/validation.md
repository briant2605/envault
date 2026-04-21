# Env Validation

`envault validate` checks your `.env` file against a JSON schema of rules, ensuring required keys exist and values meet expected constraints.

## Quick Start

### 1. Generate a starter schema

```bash
envault validate init-schema .env --output .envschema.json
```

This reads all keys from your `.env` and writes a skeleton schema:

```json
{
  "rules": [
    { "key": "APP_ENV", "required": true },
    { "key": "SECRET_KEY", "required": true }
  ]
}
```

### 2. Enrich the schema

Edit `.envschema.json` to add constraints:

```json
{
  "rules": [
    {
      "key": "APP_ENV",
      "required": true,
      "allowed_values": ["development", "staging", "production"]
    },
    {
      "key": "PORT",
      "required": true,
      "pattern": "\\d+",
      "min_length": 2,
      "max_length": 5
    },
    {
      "key": "SECRET_KEY",
      "required": true,
      "min_length": 32
    },
    {
      "key": "DEBUG",
      "required": false,
      "allowed_values": ["true", "false"]
    }
  ]
}
```

### 3. Run validation

```bash
envault validate check .env --schema .envschema.json
```

Output on success:

```
All checks passed.
```

Output on failure:

```
3 validation error(s) found:
  [APP_ENV] value must be one of: development, staging, production
  [SECRET_KEY] value too short (min 32)
  [MISSING_KEY] required key is missing
```

The command exits with code `1` when errors are found, making it suitable for CI pipelines.

## Rule Fields

| Field | Type | Description |
|---|---|---|
| `key` | string | The env variable name |
| `required` | bool | Fail if key is absent (default: `true`) |
| `pattern` | string | Regex the value must fully match |
| `min_length` | int | Minimum character length of value |
| `max_length` | int | Maximum character length of value |
| `allowed_values` | list | Exact set of permitted values |

## CI Integration

Add to your pipeline before deploying:

```yaml
- name: Validate .env
  run: envault validate check .env
```

Commit `.envschema.json` to your repository so the whole team shares the same rules.
