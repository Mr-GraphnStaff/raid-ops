from __future__ import annotations

from dataclasses import dataclass

from raid_ops.services.runtime_mode import RuntimeConfig


@dataclass(frozen=True)
class RecommendationCandidate:
    candidate_id: str
    score: float


@dataclass(frozen=True)
class RecommendationRequest:
    objective: str
    candidates: tuple[RecommendationCandidate, ...]
    seed: int = 0


class RecommendationService:
    """Deterministic placeholder recommendation service for read-only flows."""

    def rank(self, request: RecommendationRequest, runtime: RuntimeConfig) -> list[RecommendationCandidate]:
        # Read-only mode is supported by default; ranking is deterministic.
        _ = runtime
        return sorted(
            request.candidates,
            key=lambda item: (-item.score, item.candidate_id),
        )
