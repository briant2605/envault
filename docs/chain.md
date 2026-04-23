# envault chain

The `chain` command merges multiple `.env` files together in order. Keys in later files override keys from earlier files — similar to how Docker Compose or `dotenv-flow` handles layered environments.

## Use cases

- Combine a shared `.env.base` with a local `.env.local` override
- Layer environment-specific files: `.env` → `.env.staging` → `.env.local`
- Build a single merged file for deployment

## Commands

### `envault chain run <file1> [file2 ...]`

Merge files left-to-right and print the result to stdout.

```bash
envault chain run .env.base .env.local
```

Write the result to a file instead:

```bash
envault chain run .env.base .env.local -o .env.merged
```

### `envault chain preview <file1> [file2 ...]`

Show each key and which file it originates from (last-wins).

```bash
envault chain preview .env.base .env.local
# A        ← .env.base
# B        ← .env.local
# C        ← .env.local
```

### `envault chain count <file1> [file2 ...]`

Print the total number of unique keys after merging.

```bash
envault chain count .env.base .env.local
# 3
```

## Behaviour

- Missing files are silently skipped (not an error).
- Comments and blank lines are ignored during parsing.
- Quoted values have their surrounding quotes stripped.
- Output is sorted alphabetically.

## Example

```
# .env.base
DB_HOST=localhost
DB_PORT=5432
APP_ENV=development

# .env.local
DB_HOST=mydevbox
SECRET_KEY=supersecret
```

```bash
envault chain run .env.base .env.local
# APP_ENV=development
# DB_HOST=mydevbox
# DB_PORT=5432
# SECRET_KEY=supersecret
```
