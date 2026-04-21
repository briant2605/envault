# envault comment

Manage **inline comments** attached to individual keys in your `.env` file.

Inline comments appear on the same line as a key assignment, after a `#`:

```
DB_PORT=5432  # default port
```

They are useful for documenting what a variable does without adding a separate
comment block.

---

## Commands

### `envault comment set KEY COMMENT`

Set or replace the inline comment for `KEY`.

```bash
envault comment set DB_PORT "default port, change in prod"
# Result: DB_PORT=5432  # default port, change in prod
```

Options:

| Option | Default | Description |
|--------|---------|-------------|
| `--env` | `.env` | Path to the target `.env` file |

---

### `envault comment get KEY`

Print the current inline comment for `KEY`, or a notice if none is set.

```bash
envault comment get DB_PORT
# default port, change in prod
```

---

### `envault comment remove KEY`

Strip the inline comment from `KEY`, leaving the value intact.

```bash
envault comment remove DB_PORT
# Result: DB_PORT=5432
```

---

## Python API

```python
from envault.env_comment import (
    set_comment,
    remove_comment,
    get_comment,
    set_comment_in_file,
    remove_comment_in_file,
    get_comment_from_file,
)

# Work on raw text
updated = set_comment(text, "DB_PORT", "default port")
print(get_comment(updated, "DB_PORT"))  # "default port"
cleaned = remove_comment(updated, "DB_PORT")

# Work directly on a file
set_comment_in_file(Path(".env"), "DB_PORT", "default port")
get_comment_from_file(Path(".env"), "DB_PORT")
remove_comment_in_file(Path(".env"), "DB_PORT")
```

---

## Notes

- Only **inline** comments (same line as a key) are managed; standalone comment
  lines (lines beginning with `#`) are left untouched.
- If the key does not exist in the file a `KeyError` is raised.
- Leading `#` characters in the comment argument are stripped automatically.
