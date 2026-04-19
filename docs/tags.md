# Tags

The **tags** feature lets you attach searchable labels to any `.env` file tracked by envault. Tags are stored in `~/.envault/tags.json` and are independent of encryption.

## CLI Usage

```bash
# Add a tag
envault tags add .env production

# List tags for a file
envault tags list .env

# Remove a tag
envault tags remove .env production

# Find all env files with a specific tag
envault tags find production

# Clear all tags from a file
envault tags clear .env
```

## Python API

```python
from envault.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags

add_tag(".env", "production")
print(get_tags(".env"))        # ['production']
print(find_by_tag("production"))  # ['.env']
remove_tag(".env", "production")
clear_tags(".env")
```

## Storage

Tags are persisted in `~/.envault/tags.json` as a mapping of file path → list of tags:

```json
{
  ".env": ["production", "team-a"],
  ".env.staging": ["staging"]
}
```

Tags are **not** encrypted and are intended for local organisational use only.
