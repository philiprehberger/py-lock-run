"""Prevent duplicate script execution using file-based locking."""

from __future__ import annotations

import os
import sys
import tempfile
import time
from contextlib import contextmanager
from collections.abc import Callable, Generator
from functools import wraps
from pathlib import Path
from typing import Any

__all__ = ["LockError", "cleanup_locks", "is_locked", "lock", "locked"]


class LockError(RuntimeError):
    """Raised when a lock cannot be acquired."""


@contextmanager
def lock(
    name: str,
    *,
    timeout: float = 0,
    lock_dir: str | Path | None = None,
) -> Generator[Path, None, None]:
    """Acquire a file lock for the given name.

    Args:
        name: Lock identifier (used in the lock filename).
        timeout: Seconds to wait for the lock. 0 means fail immediately.
        lock_dir: Directory for lock files. Defaults to system temp dir.
    """
    directory = Path(lock_dir) if lock_dir else Path(tempfile.gettempdir())
    lock_path = directory / f".philiprehberger-lock-{name}.lock"

    fd = _acquire(lock_path, timeout)
    try:
        yield lock_path
    finally:
        _release(fd, lock_path)


def locked(
    name: str, **kwargs: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that wraps the function body in a file lock."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kw: Any) -> Any:
            with lock(name, **kwargs):
                return func(*args, **kw)

        return wrapper

    return decorator


def is_locked(name: str, *, lock_dir: str | Path | None = None) -> bool:
    """Return True if another process currently holds the *name* lock.

    Performs a non-blocking try-acquire; if acquisition succeeds, the
    lock is immediately released (without deleting the file) and the
    function returns False. If acquisition fails (would block), returns True.
    """
    directory = Path(lock_dir) if lock_dir else Path(tempfile.gettempdir())
    lock_path = directory / f".philiprehberger-lock-{name}.lock"

    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    except OSError:
        return False
    try:
        _lock_fd(fd)
    except OSError:
        os.close(fd)
        return True
    try:
        _unlock_fd(fd)
    finally:
        os.close(fd)
    return False


def cleanup_locks(
    lock_dir: str | Path | None = None,
    *,
    max_age_seconds: float = 86400,
) -> list[str]:
    """Remove orphaned lock files older than *max_age_seconds*.

    Only files that are NOT currently held (verified via non-blocking
    try-acquire) and whose mtime is older than the threshold are removed.

    Returns:
        List of file names that were removed.
    """
    directory = Path(lock_dir) if lock_dir else Path(tempfile.gettempdir())
    if not directory.exists():
        return []

    removed: list[str] = []
    cutoff = time.time() - max_age_seconds

    for lock_path in directory.glob(".philiprehberger-lock-*.lock"):
        try:
            mtime = lock_path.stat().st_mtime
        except OSError:
            continue
        if mtime >= cutoff:
            continue
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
        except OSError:
            continue
        try:
            try:
                _lock_fd(fd)
            except OSError:
                continue
            try:
                _unlock_fd(fd)
            finally:
                pass
            try:
                lock_path.unlink()
                removed.append(lock_path.name)
            except OSError:
                pass
        finally:
            os.close(fd)

    return removed


def _acquire(lock_path: Path, timeout: float) -> int:
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    try:
        os.write(fd, str(os.getpid()).encode())
    except OSError:
        pass

    deadline = time.monotonic() + timeout
    while True:
        try:
            _lock_fd(fd)
            return fd
        except OSError:
            if timeout <= 0 or time.monotonic() >= deadline:
                os.close(fd)
                raise LockError(f"Could not acquire lock {lock_path.name!r}") from None
            time.sleep(0.1)


def _release(fd: int, lock_path: Path) -> None:
    try:
        _unlock_fd(fd)
    finally:
        os.close(fd)
        try:
            lock_path.unlink()
        except OSError:
            pass


if sys.platform == "win32":
    import msvcrt

    def _lock_fd(fd: int) -> None:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _unlock_fd(fd: int) -> None:
        try:
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
else:
    import fcntl

    def _lock_fd(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_fd(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)
