# philiprehberger-lock-run

Prevent duplicate script execution using file-based locking.

## Install

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

## API

| Name | Description |
|------|-------------|
| `lock(name, *, timeout=0, lock_dir=None)` | Context manager that acquires a file lock. Raises `LockError` on failure. |
| `locked(name, **kwargs)` | Decorator that wraps the function body in a file lock. |
| `LockError` | Raised when a lock cannot be acquired. Extends `RuntimeError`. |

## License

MIT
