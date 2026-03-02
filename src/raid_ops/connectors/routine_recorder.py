from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Protocol

from raid_ops.connectors.vision_observer import GameState, PlariumVisionObserver


class RecorderGateway(Protocol):
    """Persistence adapter for routine recordings."""

    def append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        ...


class JsonlRecorderGateway:
    """File-backed JSONL writer."""

    def append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        import json

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str))
            handle.write("\n")


@dataclass(frozen=True)
class UserAction:
    type: str
    x: int | None = None
    y: int | None = None
    key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        if self.x is not None:
            payload["x"] = self.x
        if self.y is not None:
            payload["y"] = self.y
        if self.key is not None:
            payload["key"] = self.key
        return payload


class RoutineRecorder:
    """Records observed game states paired with explicit user actions."""

    def __init__(
        self,
        gateway: RecorderGateway,
        output_dir: Path = Path("data/recordings"),
        filename_timestamp: datetime | None = None,
    ) -> None:
        self._gateway = gateway
        self._output_dir = output_dir
        ts = filename_timestamp or datetime.now(timezone.utc)
        self._path = self._output_dir / f"{ts.strftime('%Y%m%d_%H%M%S')}.jsonl"
        self._latest_state: GameState | None = None
        self._lock = Lock()

    @property
    def output_path(self) -> Path:
        return self._path

    def on_state(self, state: GameState) -> None:
        with self._lock:
            self._latest_state = state

    def record_action(self, action: UserAction) -> None:
        with self._lock:
            state = self._latest_state
        if state is None:
            return
        self._gateway.append_jsonl(
            self._path,
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "state": state.to_dict(),
                "action": action.to_dict(),
            },
        )

    def start(self, observer: PlariumVisionObserver) -> None:
        observer.start(callback=self.on_state)

    def stop(self, observer: PlariumVisionObserver) -> None:
        observer.stop()
