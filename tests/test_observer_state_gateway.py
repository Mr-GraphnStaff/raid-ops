from __future__ import annotations

from datetime import datetime, timezone

from raid_ops.connectors.observer_state_gateway import ObserverStateGateway
from raid_ops.connectors.vision_observer import GameState, Screen


class FakeObserver:
    def __init__(self, latest: GameState | None = None) -> None:
        self.latest = latest


def _state() -> GameState:
    return GameState(
        timestamp=datetime.now(timezone.utc),
        screen=Screen.MAIN_MENU,
        energy=1,
        silver=2,
        gems=3,
        stage_info=None,
        battle_progress=None,
        actionable=(),
        recommended_action=None,
        raw_analysis="ok",
        screenshot_path=None,
    )


def test_latest_state_returns_none_when_no_state() -> None:
    gateway = ObserverStateGateway(FakeObserver())

    assert gateway.latest_state() is None


def test_latest_state_returns_observer_state() -> None:
    state = _state()
    gateway = ObserverStateGateway(FakeObserver(latest=state))

    assert gateway.latest_state() == state
