# philiprehberger-lock-run

[![Tests](https://github.com/philiprehberger/py-lock-run/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-lock-run/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-lock-run.svg)](https://pypi.org/project/philiprehberger-lock-run/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-lock-run)](https://github.com/philiprehberger/py-lock-run/commits/main)

Prevent duplicate script execution using file-based locking.

## Installation

```bash
pip install philiprehberger-lock-run
```

## Usage

### Context Manager

```python
from philiprehberger_lock_run import lock

with lock("my-job"):
    do_work()
```

### Decorator

```python
from philiprehberger_lock_run import locked

@locked("my-job")
def scheduled_task():
    ...
```

### Timeout

Wait up to 10 seconds for the lock to become available:

```python
with lock("my-job", timeout=10):
    do_work()
```

### Custom Lock Directory

```python
with lock("my-job", lock_dir="/var/lock"):
    do_work()
```

### Inspecting and cleaning up locks

Check whether another process currently holds a lock (non-blocking):

```python
from philiprehberger_lock_run import is_locked

if is_locked("my-job"):
    print("Another process is running my-job")
```

Remove orphaned lock files older than a threshold (defaults to 24 hours).
Only files that are not currently held are removed:

```python
from philiprehberger_lock_run import cleanup_locks

removed = cleanup_locks(max_age_seconds=3600)
print(f"Removed {len(removed)} stale lock files")
```

## API

| Name | Description |
|------|-------------|
| `lock(name, *, timeout=0, lock_dir=None)` | Context manager that acquires a file lock. Raises `LockError` on failure. |
| `locked(name, **kwargs)` | Decorator that wraps the function body in a file lock. |
| `is_locked(name, *, lock_dir=None)` | Return `True` if another process currently holds the named lock. Performs a non-blocking try-acquire. |
| `cleanup_locks(lock_dir=None, *, max_age_seconds=86400)` | Remove orphaned lock files older than `max_age_seconds` that are not currently held. Returns the list of removed file names. |
| `LockError` | Raised when a lock cannot be acquired. Extends `RuntimeError`. |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-lock-run)

🐛 [Report issues](https://github.com/philiprehberger/py-lock-run/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-lock-run/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
