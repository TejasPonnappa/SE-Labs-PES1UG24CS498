# Lab 5: Issues Found and Fixed

Line numbers refer to the original `parking_system.py` (see `before/`).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Mutable default argument (Pylint W0102) | Bug | 9 | `zone_records=[]` is shared across every call, so records leak between calls | Default to `None` and create a new list inside the function |
| Weak random for permit numbers (Bandit B311) | Security | 11 | `random.randint` is predictable, so permit numbers can be guessed | Use `secrets.randbelow` |
| Try/except/pass (Bandit B110) | Security / Bug | 22-23 | `revoke_permit` silently hides every error, including a missing permit | Use `permits.pop(plate, None)` and report when there is nothing to revoke |
| Bare `except:` (Pylint W0702, Flake8 E722) | Bug | 16, 22, 29, 43 | Catches everything, including `KeyboardInterrupt`, and hides real bugs | Catch only specific exceptions (`KeyError`, `ValueError`, `OSError`, `JSONDecodeError`) or remove the `try` |
| Global state (Pylint W0603) | Design | 6, 40 | `permits` is a module global modified with `global` | Pass `permits` explicitly; `load_permit_database` returns it |
| File opened without `with` / encoding (Pylint R1732, W1514) | Bug | 42, 47 | Files may not be closed on error; `open(file)` leaks a handle; encoding is platform dependent | `with open(..., encoding="utf-8")` |
| Naming (Pylint C0103) | Style | 51 | `setExpiry` is camelCase | Renamed to `set_expiry` |
| Missing docstrings (Pylint C0114, C0116) | Style | 1, 9-54 | No module or function docs | Added docstrings |
| Layout and line length (Flake8 E302, E305, E501) | Style | 9-68, 13, 27, 62 | Missing blank lines, lines over 79 chars | Reformatted to PEP 8 |
| Expired permits not flagged (found by running the program) | Logic bug | 27-30, 51-52 | `setExpiry` accepts `01/01/2020`, which `is_expired` cannot parse, so its bare `except` returns `False` and an expired permit is treated as valid | `set_expiry` validates `YYYY-MM-DD`; `is_expired` treats an unreadable date as expired |
| No input validation (found by running the program) | Logic bug | 9-15 | Empty plate, `None` plate and invalid zone `Z` were all registered | `register_permit` returns `None` for these |
| Enter-to-skip revokes the `""` permit (found by running the program) | Logic bug | 63-64 | Pressing Enter called `revoke_permit("")`, silently deleting the permit that had been wrongly registered for an empty plate | Skip revoke when the input is empty |
| `__main__` guard missing | Design | 68 | `main()` ran on import | Added `if __name__ == "__main__":` |

## Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 6.32/10 | 10.00/10 |
| Bandit | 2 Low | 0 |
| Flake8 | 16 | 0 |
