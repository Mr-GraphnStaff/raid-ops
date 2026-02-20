# raid-ops v1 architecture draft

This document defines an exact v1 starter architecture, interface boundaries, and an initial test plan for building an RSL Helper-style tool incrementally.

## Goals for v1
- Keep the current behavior working: connect to RTK, fetch accounts, print account data.
- Introduce clear module boundaries for future UI and automation work.
- Prioritize stable interfaces and testability.

## Proposed folder structure

```text
src/raid_ops/
  __init__.py
  main.py
  connectors/
    __init__.py
    rtk_client.py
  domain/
    __init__.py
    models.py
  services/
    __init__.py
    account_service.py

tests/
  test_account_service.py
```

## Interface boundaries

### `connectors/rtk_client.py`
- `AccountsGateway` protocol:
  - `connect() -> None`
  - `close() -> None`
  - `async get_accounts() -> list[dict]`
- `RaidToolkitAccountsGateway` implementation wraps `RaidToolkitClient`.

### `domain/models.py`
- `AccountSummary` dataclass:
  - `id: str`
  - `name: str`
  - `raw: dict`

### `services/account_service.py`
- `AccountService`:
  - constructor: accepts `AccountsGateway`
  - `async list_account_summaries() -> list[AccountSummary]`
  - Handles mapping from RTK account payloads into stable domain objects.

### `main.py`
- Composition root for dependency wiring.
- Keeps backward-compatible behavior: print `Accounts found:` followed by account data.

## First test plan

### Unit tests
1. `AccountService` maps account payloads correctly.
2. `AccountService` defaults missing fields safely (`id`/`name`).
3. Service returns empty list for empty gateway response.

### Integration-lite tests (mocked gateway)
4. Verify no direct RTK dependency needed in service tests.

## Lint and test commands
- Lint: `python -m ruff check src tests`
- Tests: `python -m pytest -q`

## Next milestone after this scaffold
- Add champion/gear domain models.
- Add persistence (SQLite snapshots).
- Add a UI adapter layer that consumes service outputs.
