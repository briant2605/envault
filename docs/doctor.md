# envault doctor

The `doctor` command diagnoses common issues with your `.env` file and its associated vault.

## Usage

```bash
envault doctor check [ENV_FILE] [--strict]
envault doctor summary [ENV_FILE]
```

`ENV_FILE` defaults to `.env` in the current directory.

---

## Checks performed

| Check | Severity |
|---|---|
| `.env` file exists | error |
| `.env` file is readable | error |
| Vault file exists (created by `envault lock`) | warning |
| `.env` listed in `.gitignore` | warning |
| No lint errors in the file | error |
| No lint warnings in the file | warning |

---

## Examples

### Basic check

```bash
$ envault doctor check
envault doctor — .env

  ✓ .env file exists
  ✓ .env file is readable
  ✓ Vault file exists
  ✓ .env appears in .gitignore
  ✓ No lint errors

Result: OK
```

### Strict mode

In strict mode warnings are treated as errors and the command exits with code 1:

```bash
envault doctor check --strict
```

### One-line summary

Useful in scripts or CI pipelines:

```bash
$ envault doctor summary
.env: OK | checks=5 warnings=0 errors=0
```

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed (or only warnings in non-strict mode) |
| `1` | One or more errors (or warnings in strict mode) |

---

## Tips

- Run `envault lock` to create a vault file and silence the vault warning.
- Add `.env` to your `.gitignore` to prevent secrets from being committed.
- Use `envault lint check` for detailed lint output.
