# envault backup

The `backup` command group lets you create and manage timestamped backups of your `.env` files, independent of the encrypted vault.

## Commands

### `envault backup create [ENV_FILE]`

Create a timestamped backup of the given env file (default: `.env`).
Backups are stored in a `.envault_backups/` directory next to the source file.

```bash
envault backup create .env
# Backup created: .envault_backups/.env.1700000000.bak
```

### `envault backup list [ENV_FILE]`

List all available backups for an env file, sorted oldest-first.

```bash
envault backup list .env
# .envault_backups/.env.1700000000.bak
# .envault_backups/.env.1700000060.bak
```

### `envault backup restore BACKUP_FILE [ENV_FILE]`

Restore an env file from a specific backup.

```bash
envault backup restore .envault_backups/.env.1700000000.bak .env
# Restored .env from .envault_backups/.env.1700000000.bak
```

### `envault backup delete BACKUP_FILE`

Delete a single backup file.

```bash
envault backup delete .envault_backups/.env.1700000000.bak
# Deleted backup: .envault_backups/.env.1700000000.bak
```

### `envault backup purge [ENV_FILE]`

Delete **all** backups for an env file. Prompts for confirmation.

```bash
envault backup purge .env
# Delete ALL backups for this file? [y/N]: y
# Purged 2 backup(s).
```

## Storage

Backups are plain copies of the env file stored under:

```
<env_file_dir>/.envault_backups/<env_filename>.<epoch_timestamp>.bak
```

Add `.envault_backups/` to your `.gitignore` to avoid committing backups:

```gitignore
.envault_backups/
```

## Tip

Combine `backup create` with the `watch` command in a shell script to auto-backup on every change.
