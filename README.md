# raid-ops

A modular optimization and automation engine for Raid: Shadow Legends.

`raid-ops` is a structured, extensible system designed to analyze account data, optimize gear configurations, generate high-performance team compositions, and support automation workflows through a clean architecture.

Not a script.  
An engine.

Not an RSL Helper wrapper.  
The long-term product direction is an owned Windows-first AI assistant with owned data contracts and optional replaceable connectors.

---

## Purpose

`raid-ops` exists to solve combinatorial problems in Raid:

- Which gear combination maximizes a specific objective?
- Which team composition best satisfies defined constraints?
- How can builds be ranked, compared, and explained?
- How can deterministic logic and AI-assisted reasoning coexist?

The system prioritizes performance, determinism, and architectural clarity.

---

## Core Principles

### Deterministic First
All stat calculations and optimization logic must be reproducible.

### AI as Advisory
AI enhances ranking and strategy exploration.  
AI does not replace core math.

### Separation of Concerns
Game interaction, optimization logic, AI reasoning, and application control remain isolated.

### Explainability
Every recommendation must be traceable to measurable scoring logic.

---

## Architecture Overview

```text
/core
  Deterministic domain logic
  - Champion models
  - Gear models
  - Stat calculations
  - Synergy scoring
  - Optimization engines

/ai
  Advisory systems
  - Heuristic ranking
  - Strategy refinement
  - Recommendation explanations

/integration
  External adapters
  - Owned snapshot/capture ingestion
  - Optional third-party importers
  - Optional automation bridges

/app
  Orchestration layer
  - CLI
  - Workflows
  - Configuration
