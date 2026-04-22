# Scope Management

envault lets you assign named **scopes** to individual keys in your `.env` file.
Scopes are arbitrary labels (e.g. `dev`, `prod`, `test`, `ci`) that let you
document or filter which environments a key belongs to.

## Commands

### Assign a scope

```bash
envault scope add DB_URL prod
envault scope add DB_URL dev
```

### Remove a scope

```bash
envault scope remove DB_URL dev
```

Raises an error if the scope is not currently assigned to the key.

### Show scopes for a key

```bash
envault scope get DB_URL
# prod
```

### Find all keys in a scope

```bash
envault scope find prod
# DB_URL
# SECRET_KEY
```

### List all scope assignments

```bash
envault scope list
# DB_URL: dev, prod
# SECRET_KEY: prod
```

## Storage

Scope assignments are stored in a JSON sidecar file next to your `.env`:

```
.env.scopes.json
```

This file should be committed to version control alongside your `.env.vault`
so that team members share the same scope metadata.

## Use cases

- Mark keys that are only relevant in `prod` to avoid accidental exposure in `dev`.
- Generate scope-filtered exports for CI pipelines.
- Document which keys change between environments during code review.

## Custom env file

All commands accept `--env <path>` to target a file other than `.env`:

```bash
envault scope add API_KEY prod --env .env.production
```
