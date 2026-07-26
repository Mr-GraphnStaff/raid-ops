# raid-ops v1 architecture draft

This document defines the v1 direction for `raid-ops`: a Windows-first AI-assisted Raid application whose core product, data model, and user experience are owned by this project.

`raid-ops` is not an RSL Helper wrapper and should not require RSL Helper to function.

## Product Decision

Build a real Windows app with an owned engine and owned connectors.

### Non-goals

- Do not build a dependency on RSL Helper.
- Do not require RTK as the foundation.
- Do not make automation the core product.
- Do not place game data extraction logic inside scoring or AI code.

Third-party tools may be useful for research or optional importers, but v1 must remain useful without them.

## Goals for v1

- Provide a Windows-first assistant experience for Raid account analysis.
- Own the account/champion/artifact data contracts used by the app.
- Support snapshot-based ingestion as the first reliable data path.
- Keep deterministic scoring and validation authoritative.
- Use AI only for intent parsing, reranking, planning, and explanations.
- Keep future live ingestion and automation behind replaceable connectors.

## Target Product Shape

```text
RaidOps.Desktop
  Windows-native app shell and UI

RaidOps.Core
  Deterministic domain models, rules, scoring, and optimization

RaidOps.Services
  Use-case orchestration and validation

RaidOps.Connectors
  Owned data ingestion adapters
  - snapshot imports
  - local capture/export formats
  - optional future live game observer
  - optional future RTK importer

RaidOps.AI
  Intent parsing, advisory reranking, and explanation generation

RaidOps.Tests
  Deterministic regression and connector contract tests
```

The current Python package can continue serving as a fast prototype for domain and service behavior. It must not constrain the final Windows app choice.

## Current Repository Mapping

```text
src/raid_ops/
  main.py
  app/
    CLI and composition root
  domain/
    Pure models and deterministic rules
  services/
    Use-case orchestration
  connectors/
    External adapters and data ingestion
  ai/
    Future isolated AI layer

tests/
  Unit and integration-lite tests
```

## Interface Boundaries

### Domain

Domain code owns:

- account, champion, artifact, and build models
- stat and rule primitives
- deterministic scoring payloads
- validation structures

Domain code must not import connector, UI, automation, or LLM code.

### Services

Services own:

- recommendation workflow orchestration
- mapping between connector DTOs and domain models
- validation of AI output against deterministic rules
- fallback behavior when a connector is unavailable

Services should depend on protocols/interfaces, not concrete tools.

### Connectors

Connectors own all external side effects:

- reading snapshot files
- calling local services
- reading export files
- observing game state
- future optional automation

Connectors must not contain scoring math or AI policy.

### AI

AI code owns:

- natural-language intent parsing
- reranking deterministic candidates
- explanation generation from grounded score metadata

AI must never invent game mechanics, bypass validation, or create candidates that deterministic services did not emit.

## Data Ingestion Strategy

V1 uses owned snapshot ingestion first.

Priority order:

1. Owned JSON snapshot format.
2. Owned local capture/export format.
3. Optional importers for external formats if they are easy and stable.
4. Optional live observer once the product core is useful.

RSL Helper is explicitly not a required data source.

RTK is optional research only until it is current and reliable.

## First Test Plan

### Unit tests

1. Snapshot gateway parses owned account payloads.
2. Account service maps connector payloads into stable domain objects.
3. Missing connector data produces clear, typed fallback behavior.
4. Deterministic scoring returns identical output for identical input.

### Integration-lite tests

5. CLI can list accounts from an owned snapshot.
6. Service tests run without RTK, RSL Helper, Raid, or network access.
7. Connector failures do not corrupt domain state.

## Lint and Test Commands

- Tests: `python -m pytest -q`

## Next Milestone

Define the owned account snapshot schema and add champion/artifact models.

After that, scaffold the Windows desktop app around the stable contracts rather than around any third-party helper.
