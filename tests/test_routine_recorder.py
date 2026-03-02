from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raid_ops.connectors.routine_recorder import RoutineRecorder, UserAction
from raid_ops.connectors.vision_observer import GameState, Screen


class FakeRecorderGateway:
    def __init__(self) -> None:
        self.rows: list[tuple[Path, dict[str, Any]]] = []

    def append_jsonl(self, path: Path, payload: dict[str, Any]) -> None:
        self.rows.append((path, payload))


def _state(screen: Screen = Screen.MAIN_MENU) -> GameState:
    return GameState(
        timestamp=datetime.now(timezone.utc),
        screen=screen,
        energy=100,
        silver=1000,
        gems=10,
        stage_info=None,
        battle_progress=None,
        actionable=(),
        recommended_action=None,
        raw_analysis="ok",
        screenshot_path=None,
    )


def test_record_action_writes_state_action_pair() -> None:
    gateway = FakeRecorderGateway()
    recorder = RoutineRecorder(
        gateway=gateway,
        filename_timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    recorder.on_state(_state())

    recorder.record_action(UserAction(type="click", x=10, y=20))

    assert len(gateway.rows) == 1
    row = gateway.rows[0][1]
    assert row["state"]["screen"] == "main_menu"
    assert row["action"] == {"type": "click", "x": 10, "y": 20}


def test_record_action_ignores_when_no_observed_state() -> None:
    gateway = FakeRecorderGateway()
    recorder = RoutineRecorder(gateway=gateway)

    recorder.record_action(UserAction(type="key", key="space"))

    assert gateway.rows == []
