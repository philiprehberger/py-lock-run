# Changelog

## 0.2.0 (2026-05-30)

- Add `is_locked()` non-blocking check for whether another process holds a lock
- Add `cleanup_locks()` for removing stale orphaned lock files

## 0.1.6 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.5 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.3

- Add Development section to README

## 0.1.0 (2026-03-13)

- Initial release
- `lock()` context manager for file-based locking
- `locked()` decorator for wrapping functions with a lock
- Cross-platform support (Unix and Windows)
- Configurable timeout and lock directory
