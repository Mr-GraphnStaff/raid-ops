# AGENTS.md

## Project Overview

RSL Toolkit is a modular decision engine for Raid: Shadow Legends.

Primary capabilities: - Gear optimization - Team composition
generation - Battle modeling and simulation - Optional automation
adapters - AI-assisted ranking and recommendation layers

This project prioritizes determinism, transparency, and reproducibility.

AI enhances decision-making but does not replace core logic.

------------------------------------------------------------------------

## Architectural Principles

1.  Core domain logic must be deterministic and testable.
2.  AI modules must be isolated in `/ai`.
3.  No UI logic in the domain layer.
4.  No direct game interaction inside core logic.
5.  All side effects must occur in integration or application layers.
6.  No global mutable state.
7.  Pure functions preferred in optimization and scoring logic.

------------------------------------------------------------------------

## Layered Architecture

### 1. Core Domain (`/core`)

Contains: - Champion models - Gear models - Stat calculations - Synergy
logic - Scoring functions - Optimization engines

Rules: - No external dependencies beyond standard libraries. - Must be
fully unit-testable. - No randomness unless explicitly seeded.

------------------------------------------------------------------------

### 2. AI Layer (`/ai`)

Contains: - Recommendation ranking - Heuristic refinement - Strategy
suggestion engines - Explanation generators

Rules: - Must operate only on structured inputs from `/core`. - Must not
invent game mechanics. - Must not bypass validation logic. - All outputs
must include explainability metadata. - AI results must be reproducible
when given same seed and inputs.

AI is advisory, not authoritative.

------------------------------------------------------------------------

### 3. Integration Layer (`/integration`)

Contains: - Game interaction adapters (if implemented) - Import/export
handlers - External data ingestion

Rules: - Must not contain scoring logic. - Must not modify core data
directly. - All integration must go through defined interfaces.

------------------------------------------------------------------------

### 4. Application Layer (`/app`)

Contains: - CLI - GUI - Configuration management - Workflow
orchestration

Rules: - No business logic here. - Only calls into core or AI modules.

------------------------------------------------------------------------

## Optimization Engine Requirements

Gear Optimization: - Objective functions must be explicit. - Constraints
must be configurable. - Must support deterministic mode. - Must provide
full stat breakdown of chosen builds.

Team Generation: - Must use defined role archetypes. - Must use synergy
scoring. - Must expose reasoning behind team selection. - Must support
constraint filtering (faction, affinity, availability).

Combinatorial explosion must be mitigated through: - Heuristic pruning -
Pre-filtering - Caching - Optional evolutionary algorithms

------------------------------------------------------------------------

## AI Behavior Constraints

AI modules: - Must not fabricate champion abilities. - Must not override
stat rules. - Must validate all outputs before acceptance. - Must
provide explanation data structures. - Must not degrade performance
beyond defined thresholds.

AI suggestions must be ranked, not absolute.

------------------------------------------------------------------------

## Testing Standards

-   All stat calculations must have unit tests.
-   Optimization routines must support deterministic test mode.
-   Performance benchmarks required for optimization engine.
-   AI outputs must be verifiable against core scoring logic.

Test coverage target: ≥ 80% for `/core`.

------------------------------------------------------------------------

## Performance Constraints

-   Gear evaluation must scale efficiently with inventory size.
-   Optimization must support parallel execution if applicable.
-   Caching strategy must be implemented for repeated stat calculations.
-   AI modules must not block core processing.

------------------------------------------------------------------------

## Contribution Guidelines for Agents

Before generating code: 1. Identify correct layer. 2. Avoid cross-layer
contamination. 3. Ensure deterministic behavior where required. 4. Add
tests for new scoring logic. 5. Document assumptions clearly.

Refactors must not: - Break deterministic behavior. - Introduce hidden
side effects. - Reduce performance without justification.

------------------------------------------------------------------------

## Future Expansion Areas

-   Battle simulation modeling
-   Arena AI strategy modes
-   Genetic algorithm optimizer
-   Meta analysis module
-   Data visualization layer

------------------------------------------------------------------------

This document governs AI-assisted contributions. Core logic correctness
always overrides AI creativity.
