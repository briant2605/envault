# Snapshots

Envault supports saving and restoring point-in-time snapshots of your encrypted `.env` vault. This is useful before rotating keys, sharing with teammates, or making bulk changes.

## Commands

### Save a snapshot

```bash
envault snapshot save .env --password yourpassword
```

Saves a timestamped copy of the current vault for `.env`. Snapshots are stored in `.envault/snapshots/`.

Optionally provide a label:

```bash
envault snapshot save .env --password yourpassword --label before-deploy
```

### List snapshots

```bash
envault snapshot list .env
```

Outputs a table of saved snapshots with their timestamp and optional label:

```
ID                        LABEL           CREATED
20240601T120000           before-deploy   2024-06-01 12:00:00
20240530T093000           (none)          2024-05-30 09:30:00
```

### Restore a snapshot

```bash
envault snapshot restore .env 20240601T120000 --password yourpassword
```

Restores the vault to the state captured in the given snapshot. The current vault is overwritten.

> **Tip:** Save a snapshot before restoring to avoid losing your current state.

### Delete a snapshot

```bash
envault snapshot delete .env 20240601T120000
```

Permanently removes the specified snapshot file.

## Storage

Snapshots are stored as encrypted vault files under:

```
.envault/snapshots/<env-file-stem>/<snapshot-id>.vault
```

They use the same encryption as the main vault, so the same password is required to restore.

## Notes

- Snapshots are **not** automatically created — you must save them explicitly.
- Snapshot IDs are UTC timestamps in `YYYYMMDDTHHMMSS` format, with an optional label appended.
- Restoring a snapshot does **not** affect the audit log — a restore event is recorded.
