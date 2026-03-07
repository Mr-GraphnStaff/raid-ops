from __future__ import annotations

from raid_ops.services.recommendation_service import (
    RecommendationCandidate,
    RecommendationRequest,
    RecommendationService,
)
from raid_ops.services.runtime_mode import RuntimeConfig, RuntimeMode


def test_recommendation_service_ranks_deterministically_in_read_only_mode() -> None:
    service = RecommendationService()
    request = RecommendationRequest(
        objective="maximize speed",
        candidates=(
            RecommendationCandidate(candidate_id="b", score=95.0),
            RecommendationCandidate(candidate_id="a", score=95.0),
            RecommendationCandidate(candidate_id="c", score=80.0),
        ),
        seed=42,
    )

    ranked = service.rank(request, RuntimeConfig(mode=RuntimeMode.READ_ONLY))

    assert [item.candidate_id for item in ranked] == ["a", "b", "c"]
