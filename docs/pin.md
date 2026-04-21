# Key Pinning

envault lets you **pin** specific keys in a `.env` file to protect them from
being silently overwritten during merge, import, or copy operations.

## Why pin a key?

Some keys (e.g. `DATABASE_URL`, `SECRET_KEY`) are environment-specific and
should never be overwritten by an automated workflow. Pinning makes this
intent explicit and machine-checkable.

## Commands

### Pin a key

```bash
envault pin add SECRET_KEY
envault pin add DATABASE_URL --env .env.production
```

### List pinned keys

```bash
envault pin list
envault pin list --env .env.production
```

### Check whether a key is pinned

```bash
envault pin check SECRET_KEY
```

Output:
```
'SECRET_KEY' is pinned.
```

### Remove a pin

```bash
envault pin remove SECRET_KEY
```

### Clear all pins

```bash
envault pin clear
envault pin clear --env .env.production
```

## Storage

Pins are stored in `.envault_pins.json` in the same directory as the `.env`
file. Add this file to version control so the whole team benefits from the
same protection rules.

```
# .gitignore — do NOT ignore this file
# .envault_pins.json
```

## Integration with merge

When `envault merge` encounters a conflict on a pinned key it will always keep
the **base** value, regardless of the chosen `--strategy`, and emit a warning:

```
Warning: SECRET_KEY is pinned — keeping base value.
```
