from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Event, Lock, Thread
from typing import Any, Callable, Protocol


class Screen(str, Enum):
    """Known Raid UI screens."""

    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    CAMPAIGN = "campaign"
    CAMPAIGN_BATTLE = "campaign_battle"
    DUNGEON_SELECT = "dungeon_select"
    DUNGEON_BATTLE = "dungeon_battle"
    CLAN_BOSS = "clan_boss"
    ARENA_LOBBY = "arena_lobby"
    ARENA_BATTLE = "arena_battle"
    DAILY_QUESTS = "daily_quests"
    REWARD_SCREEN = "reward_screen"
    BATTLE_RESULT = "battle_result"
    LOADING = "loading"


@dataclass(frozen=True)
class ActionableElement:
    label: str
    confidence: float
    position_hint: str
    action_type: str


@dataclass(frozen=True)
class GameState:
    timestamp: datetime
    screen: Screen
    energy: int | None
    silver: int | None
    gems: int | None
    stage_info: str | None
    battle_progress: str | None
    actionable: tuple[ActionableElement, ...]
    recommended_action: str | None
    raw_analysis: str
    screenshot_path: Path | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "screen": self.screen.value,
            "energy": self.energy,
            "silver": self.silver,
            "gems": self.gems,
            "stage_info": self.stage_info,
            "battle_progress": self.battle_progress,
            "actionable": [
                {
                    "label": item.label,
                    "confidence": item.confidence,
                    "position_hint": item.position_hint,
                    "action_type": item.action_type,
                }
                for item in self.actionable
            ],
            "recommended_action": self.recommended_action,
            "raw_analysis": self.raw_analysis,
            "screenshot_path": str(self.screenshot_path) if self.screenshot_path else None,
        }


class VisionBackend(Protocol):
    def analyze(self, img: Any, timestamp: datetime) -> GameState:
        ...


class ScreenCapture(Protocol):
    def capture(self) -> Any | None:
        ...


class PlariumVisionObserver:
    """Polls a capture+analysis backend and publishes immutable game states."""

    def __init__(self, capture: ScreenCapture, backend: VisionBackend, interval_s: float = 1.0) -> None:
        self._capture = capture
        self._backend = backend
        self._interval_s = interval_s
        self._latest: GameState | None = None
        self._lock = Lock()
        self._thread: Thread | None = None
        self._stop_event = Event()

    def capture_once(self) -> GameState | None:
        image = self._capture.capture()
        if image is None:
            return None
        state = self._backend.analyze(image, datetime.now(timezone.utc))
        with self._lock:
            self._latest = state
        return state

    def start(self, callback: Callable[[GameState], None] | None = None) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()

        def _run() -> None:
            while not self._stop_event.wait(self._interval_s):
                state = self.capture_once()
                if state is not None and callback is not None:
                    callback(state)

        self._thread = Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)

    @property
    def latest(self) -> GameState | None:
        with self._lock:
            return self._latest
