# AI-First V1 Backlog

## Goal

Ship an AI-first assistant for Raid that:
- accepts natural-language goals,
- generates deterministic candidate builds/teams,
- uses AI to rerank and explain,
- validates final recommendations against core rules before returning output.

Core scoring remains authoritative. AI is advisory and explainability-focused.

---

## Execution Order

1. Build deterministic core primitives and scoring.
2. Add deterministic candidate generation services.
3. Add AI intent parsing, reranking, and explanations.
4. Add end-to-end orchestration and CLI entrypoints.
5. Add regression and performance checks.

---

## Epics

### Epic 1: Build Advisor (Deterministic Core + Candidate Pipeline)

Outcome:
- deterministic build scoring and candidate generation exist and are test-covered.

### Epic 2: Team Planner (Deterministic Synergy + Candidate Pipeline)

Outcome:
- deterministic team scoring and team candidate generation exist and are test-covered.

### Epic 3: AI Copilot Layer (Intent + Rerank + Explain + Orchestration)

Outcome:
- natural-language query -> structured intent -> deterministic candidates -> AI rerank + explain -> validated response.

---

## Ticket Backlog (First 10)

### AIV1-001 - Domain build objective and recommendation schema

Epic: Build Advisor  
Summary: Introduce typed domain models for build objectives, constraints, candidate stats, and recommendation explanations.

Target files:
- `src/raid_ops/domain/models.py`
- `src/raid_ops/domain/recommendation_models.py` (new)
- `tests/test_domain_recommendation_models.py` (new)

Acceptance criteria:
- New dataclasses or typed structures cover objective, constraints, score breakdown, and explanation metadata.
- Structures are immutable where practical (`frozen=True` for dataclasses).
- No connector or service imports inside domain models.

Tests:
- Unit tests validate defaults, immutability behavior, and serialization-safe field shapes.

### AIV1-002 - Deterministic build scoring engine

Epic: Build Advisor  
Summary: Implement deterministic build scoring function(s) with explicit weighted objective components.

Target files:
- `src/raid_ops/domain/build_scoring.py` (new)
- `tests/test_build_scoring.py` (new)

Acceptance criteria:
- `score_build(...)` exposes explicit component weights and total score.
- Same input produces byte-for-byte identical score payload.
- Optional tie-break strategy is explicit and deterministic.

Tests:
- Golden tests for fixed input/expected score.
- Tie-break determinism test.
- Constraint-fail scenarios return invalid/filtered result state.

### AIV1-003 - Deterministic team role and synergy scoring

Epic: Team Planner  
Summary: Implement team role coverage and synergy scoring primitives with deterministic outputs.

Target files:
- `src/raid_ops/domain/team_scoring.py` (new)
- `src/raid_ops/domain/team_roles.py` (new)
- `tests/test_team_scoring.py` (new)

Acceptance criteria:
- Role archetype coverage score and synergy score are explicit sub-components.
- No randomness; seeded behavior only if evolutionary mode is enabled later.
- Scoring payload includes reasons suitable for AI explanation grounding.

Tests:
- Fixed roster/team composition golden tests.
- Missing-role penalty tests.
- Repeated-run determinism test.

### AIV1-004 - Build candidate generation service

Epic: Build Advisor  
Summary: Add deterministic candidate generation with pre-filtering, pruning, and cached stat calculations.

Target files:
- `src/raid_ops/services/build_optimizer_service.py` (new)
- `src/raid_ops/services/cache.py` (new)
- `tests/test_build_optimizer_service.py` (new)

Acceptance criteria:
- Service consumes structured objective and inventory input.
- Candidate generation is deterministic when called with same seed/config.
- Output returns top N candidates with score breakdown and rejection reasons for filtered items.

Tests:
- Deterministic candidate order test.
- Constraint filter behavior tests.
- Cache hit/miss behavior tests.

### AIV1-005 - Team candidate generation service

Epic: Team Planner  
Summary: Add deterministic team candidate generation and filtering (faction, affinity, availability, role coverage).

Target files:
- `src/raid_ops/services/team_planner_service.py` (new)
- `tests/test_team_planner_service.py` (new)

Acceptance criteria:
- Service supports configurable constraints and max candidate limits.
- Service emits ranked candidates with role/synergy score breakdown.
- Deterministic output ordering across repeated runs.

Tests:
- Constraint inclusion/exclusion tests.
- Ranked order stability tests.
- Empty/low-roster edge case tests.

### AIV1-006 - AI intent parser with reproducibility metadata

Epic: AI Copilot Layer  
Summary: Parse natural-language user goals into structured objective/constraints plus metadata (`model`, `seed`, `prompt_version`).

Target files:
- `src/raid_ops/ai/intent_parser.py` (new)
- `src/raid_ops/ai/contracts.py` (new)
- `src/raid_ops/connectors/llm_gateway.py` (new)
- `tests/test_intent_parser.py` (new)

Acceptance criteria:
- AI parsing output schema is strict and validated before use.
- Parser returns normalized structured intent or explicit validation error.
- Metadata required for reproducibility is present in every successful parse.

Tests:
- Schema-valid parse test.
- Invalid/missing field rejection tests.
- Deterministic mocked gateway test for same seed/input.

### AIV1-007 - AI reranker and explanation generator

Epic: AI Copilot Layer  
Summary: Rerank deterministic candidates and generate explanation payloads without changing core-validity rules.

Target files:
- `src/raid_ops/ai/reranker.py` (new)
- `src/raid_ops/ai/explanations.py` (new)
- `tests/test_reranker.py` (new)

Acceptance criteria:
- Reranker never introduces candidates not emitted by deterministic core pipeline.
- Explanation payload references concrete scoring fields and tradeoffs.
- Output contains confidence/rationale metadata and source candidate ids.

Tests:
- Rerank stability test with fixed mocked LLM responses.
- Explanation grounding test (must reference existing score components).
- Validation test ensuring no fabricated mechanics fields.

### AIV1-008 - End-to-end recommendation orchestrator

Epic: AI Copilot Layer  
Summary: Implement service that composes intent parsing, deterministic generation, AI rerank, and final validation.

Target files:
- `src/raid_ops/services/recommendation_service.py` (new)
- `src/raid_ops/services/validation_service.py` (new)
- `tests/test_recommendation_service.py` (new)

Acceptance criteria:
- Pipeline order is enforced: parse -> generate -> rerank -> validate -> return.
- Validation blocks malformed/fabricated AI output and falls back safely.
- Response includes both deterministic score payload and AI explanation metadata.

Tests:
- Happy-path end-to-end service test with mocked gateways.
- AI output validation failure fallback test.
- Same input + seed -> same final response test.

### AIV1-009 - AI recommendation CLI commands

Epic: AI Copilot Layer  
Summary: Add CLI entry points for build/team recommendations with JSON output.

Target files:
- `src/raid_ops/main.py`
- `src/raid_ops/app/agent_cli.py`
- `tests/test_main.py`
- `tests/test_agent_cli.py` (new)

Acceptance criteria:
- New commands support objective text, optional constraints, and optional seed.
- CLI outputs machine-readable JSON that includes deterministic and AI metadata sections.
- Invalid input returns clear non-zero error path.

Tests:
- CLI parse tests for new commands/options.
- Success output structure test.
- Invalid JSON/args failure tests.

### AIV1-010 - Benchmarks and deterministic regression harness

Epic: Build Advisor + Team Planner + AI Copilot Layer  
Summary: Add baseline benchmark and deterministic regression checks for recommendation pipelines.

Target files:
- `tests/test_deterministic_regression.py` (new)
- `tests/test_performance_baseline.py` (new)
- `scripts/smoke_test.py`
- `docs/V1_ARCHITECTURE.md`

Acceptance criteria:
- Deterministic regression suite covers build and team recommendation flows.
- Benchmark captures candidate-generation throughput and end-to-end latency budget.
- Architecture doc updated with AI flow and validation gates.

Tests:
- Regression snapshot/golden tests.
- Performance budget assertions with configurable thresholds.

---

## Definition of Done (V1)

1. All tickets AIV1-001 through AIV1-010 completed.
2. `python -m pytest -q` passes.
3. Deterministic regression tests pass for fixed seeds.
4. Recommendation responses include:
- structured objective/constraints,
- deterministic score breakdown,
- AI rerank metadata,
- explanation payload,
- validation status.
5. `src/raid_ops/domain` coverage remains at or above 80%.

---

## Out of Scope for V1

- Full battle simulation engine.
- Evolutionary/genetic search in production path.
- GUI implementation.
- Live automation execution as part of recommendation path.
