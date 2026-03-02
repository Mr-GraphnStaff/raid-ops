from __future__ import annotations

from typing import Any

from raid_ops.connectors.vision_observer import Screen
from raid_ops.services.routine_service import RoutineService


class FakeRoutineRepository:
    def __init__(self, recordings: dict[str, list[dict[str, Any]]]) -> None:
        self.recordings = recordings
        self.deleted: list[str] = []

    def list_recordings(self) -> list[str]:
        return list(self.recordings)

    def load_recording(self, name: str) -> list[dict[str, Any]]:
        return self.recordings[name]

    def delete_recording(self, name: str) -> None:
        self.deleted.append(name)


def test_get_routine_deduplicates_actions_per_screen() -> None:
    repo = FakeRoutineRepository(
        {
            "a.jsonl": [
                {"state": {"screen": "main_menu"}, "action": {"type": "click", "x": 1, "y": 2}},
                {"state": {"screen": "main_menu"}, "action": {"type": "click", "x": 1, "y": 2}},
                {"state": {"screen": "main_menu"}, "action": {"type": "key", "key": "r"}},
            ]
        }
    )
    service = RoutineService(repo)

    routine = service.get_routine(Screen.MAIN_MENU)

    assert routine is not None
    assert len(routine.actions) == 2


def test_delete_routine_delegates_to_repository() -> None:
    repo = FakeRoutineRepository({})
    service = RoutineService(repo)

    service.delete_routine("old.jsonl")

    assert repo.deleted == ["old.jsonl"]
