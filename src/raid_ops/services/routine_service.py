from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

from raid_ops.connectors.vision_observer import Screen


class RoutineRepository(Protocol):
    """Data access port for stored routine recordings."""

    def list_recordings(self) -> list[str]:
        ...

    def load_recording(self, name: str) -> list[dict[str, Any]]:
        ...

    def delete_recording(self, name: str) -> None:
        ...


class JsonlRoutineRepository:
    """JSONL implementation of routine repository."""

    def __init__(self, recordings_dir: Path) -> None:
        self._recordings_dir = recordings_dir

    def list_recordings(self) -> list[str]:
        if not self._recordings_dir.exists():
            return []
        return sorted(path.name for path in self._recordings_dir.glob("*.jsonl"))

    def load_recording(self, name: str) -> list[dict[str, Any]]:
        import json

        path = self._recordings_dir / name
        entries: list[dict[str, Any]] = []
        if not path.exists():
            return entries
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))
        return entries

    def delete_recording(self, name: str) -> None:
        path = self._recordings_dir / name
        if path.exists():
            path.unlink()


@dataclass(frozen=True)
class Routine:
    name: str
    screen: Screen
    actions: tuple[dict[str, Any], ...]
    source_recording: str
    created_at: datetime


class RoutineService:
    """Service for discovering and materializing screen-scoped routines."""

    def __init__(self, repository: RoutineRepository) -> None:
        self._repository = repository

    def list_routines(self) -> list[str]:
        routines = self._load_routines()
        return sorted(routines)

    def get_routine(self, screen: Screen) -> Routine | None:
        return self._load_routines().get(screen.value)

    def delete_routine(self, name: str) -> None:
        self._repository.delete_recording(name)

    def _load_routines(self) -> dict[str, Routine]:
        routines: dict[str, Routine] = {}
        seen_sequences: set[tuple[str, tuple[tuple[str, Any], ...]]] = set()

        for recording in self._repository.list_recordings():
            entries = self._repository.load_recording(recording)
            for entry in entries:
                state_payload = entry.get("state", {})
                action_payload = entry.get("action", {})
                screen_raw = state_payload.get("screen")
                if screen_raw not in {item.value for item in Screen}:
                    continue
                screen = Screen(screen_raw)
                action_signature = (
                    screen.value,
                    tuple(sorted((str(key), value) for key, value in action_payload.items())),
                )
                if action_signature in seen_sequences:
                    continue
                seen_sequences.add(action_signature)

                existing = routines.get(screen.value)
                actions = list(existing.actions) if existing else []
                actions.append(dict(action_payload))
                routines[screen.value] = Routine(
                    name=f"{screen.value}_routine",
                    screen=screen,
                    actions=tuple(actions),
                    source_recording=recording,
                    created_at=datetime.utcnow(),
                )

        return routines
