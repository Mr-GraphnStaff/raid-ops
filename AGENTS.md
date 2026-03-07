# AGENTS.md

## Project Overview

`raid-ops` is a modular decision and automation engine for Raid: Shadow Legends.

Primary capabilities:
- Gear optimization
- Team composition generation
- Battle modeling and simulation
- Optional automation adapters
- AI-assisted ranking and recommendations

Core priorities:
- Determinism
- Transparency
- Reproducibility

AI is advisory. Core logic is authoritative.

---

## Canonical Layer Mapping

Use the existing repository structure as the source of truth.

| Conceptual Layer | Current Path(s) | Notes |
|---|---|---|
| Core Domain | `src/raid_ops/domain` | Pure data models and rule primitives. |
| Application Services | `src/raid_ops/services` | Orchestrates domain workflows; no UI or device I/O. |
| Integration/Adapters | `src/raid_ops/connectors` | RTK, automation, keyboard, vision, and external gateways. |
| App/Composition | `src/raid_ops/app`, `src/raid_ops/main.py` | CLI/composition root and wiring. |
| AI Layer (future or isolated additions) | `src/raid_ops/ai` | Keep all AI-specific logic isolated here. |

Do not create cross-layer shortcuts.

---

## Non-Negotiable Rules

1. Domain behavior must be deterministic and unit-testable.
2. No UI or connector code in `domain`.
3. No scoring or optimization math in `connectors`.
4. Side effects (network, filesystem, input automation, time, randomness) must be isolated behind interfaces.
5. No hidden global mutable state.
6. Prefer pure functions for scoring and optimization logic.
7. Seed all randomness explicitly when used.

---

## Layer Responsibilities

### `src/raid_ops/domain`

Contains:
- Game entities and typed models
- Stat and rule calculations
- Synergy/scoring primitives

Rules:
- Keep dependencies minimal.
- No direct RTK/game/tooling calls.
- No implicit wall-clock or unseeded randomness.

### `src/raid_ops/services`

Contains:
- Use-case orchestration
- Query/ranking workflow coordination
- Validation and mapping between layers

Rules:
- May call domain and connector interfaces.
- Must not embed device/game adapter specifics.
- Keep business decisions explicit and testable.

### `src/raid_ops/connectors`

Contains:
- External integrations (RTK, UI automation, keyboard/mouse, observers)
- Import/export and environment-facing adapters

Rules:
- No domain scoring logic.
- No silent mutation of domain objects outside defined contracts.
- Failures must surface clear error context.

### `src/raid_ops/app` and `src/raid_ops/main.py`

Contains:
- CLI entry points
- Dependency wiring
- Workflow startup/shutdown

Rules:
- No domain math implementation here.
- Keep orchestration thin; delegate logic to services/domain.

### `src/raid_ops/ai` (when present)

Contains:
- Recommendation ranking
- Strategy suggestion refinement
- Explanation generation

Rules:
- Consume structured data from domain/services only.
- Never invent game mechanics.
- Never bypass core validation.
- Return explainability metadata.
- Be reproducible for the same inputs and seed.

---

## Optimization Requirements

Gear optimization must:
- Use explicit objective functions.
- Expose configurable constraints.
- Support deterministic mode.
- Return full stat breakdowns for selected builds.

Team generation must:
- Use role archetypes and synergy scoring.
- Expose reasoning for selection and ranking.
- Support constraint filters (faction, affinity, availability, etc.).

Control combinatorial explosion with:
- Pre-filtering
- Heuristic pruning
- Caching/memoization
- Optional evolutionary methods

---

## Testing Standards

- Add unit tests for all new or changed stat/scoring logic.
- Deterministic paths must have deterministic tests.
- AI outputs must be verifiable against core scoring/validation logic.
- Performance-sensitive optimizers should include benchmark coverage when changed.

Coverage target:
- `src/raid_ops/domain` should remain at or above 80%.

Minimum local validation before handoff:
- `python -m pytest -q`

---

## Performance Constraints

- Gear evaluation must scale with inventory size.
- Repeated calculations should use caching where effective.
- Parallelism is allowed when deterministic behavior is preserved.
- AI or connector work must not block core processing unnecessarily.

---

## Agent Workflow Checklist

Before coding:
1. Identify the correct layer and boundary.
2. List assumptions and deterministic requirements.
3. Confirm where side effects are allowed.

During coding:
1. Keep interfaces explicit.
2. Avoid cross-layer contamination.
3. Keep behavior reproducible.

Before handoff:
1. Add/update tests for changed behavior.
2. Run `python -m pytest -q`.
3. Document tradeoffs, assumptions, and known gaps.

Refactors must not:
- Break determinism
- Introduce hidden side effects
- Reduce performance without justification

---

## Future Expansion Areas

- Battle simulation modeling
- Arena AI strategy modes
- Genetic algorithm optimizer
- Meta analysis module
- Data visualization layer

---

This document governs AI-assisted contributions. Core logic correctness overrides AI creativity.
