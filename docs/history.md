# History

envault records every `lock` and `unlock` operation per `.env` file, giving you a lightweight audit trail of when secrets were accessed or sealed.

## Commands

### Show history

```bash
envault history show [ENV_FILE] [--limit N]
```

Displays the most recent lock/unlock events for the given `.env` file (default: `.env`).
Entries are shown newest-first.

**Options:**
- `--limit N` — maximum number of entries to display (default: 20)

**Example output:**
```
2024-06-01T12:34:56+00:00  UNLOCK  /project/.env  [pre-deploy]
2024-06-01T11:00:00+00:00  LOCK    /project/.env
```

---

### Count entries

```bash
envault history count [ENV_FILE]
```

Prints the total number of recorded events for the file.

---

### Clear history

```bash
envault history clear [ENV_FILE]
```

Permanently removes all history entries for the specified file. You will be prompted to confirm.

---

## Storage

History files are stored in:
```
~/.envault/history/<encoded_path>.json
```

Each entry contains:
- `action` — `"lock"` or `"unlock"`
- `timestamp` — ISO 8601 UTC timestamp
- `env_file` — absolute path to the `.env` file
- `note` — optional free-text annotation

## Notes

- History is stored locally and is **not** included in vault exports or share files.
- To annotate an event, use the `--note` option on `lock`/`unlock` commands (if supported by your CLI version).
- History is append-only; entries are never modified after recording.
