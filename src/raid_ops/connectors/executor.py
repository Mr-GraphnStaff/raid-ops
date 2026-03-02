from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from raid_ops.connectors.vision_observer import GameState, Screen


class ExecutionError(RuntimeError):
    """Raised when execution conditions are not met."""


class InputGateway(Protocol):
    """Control adapter to interact with the game window."""

    def click(self, x: int, y: int) -> None:
        ...

    def key(self, key: str) -> None:
        ...

    def wait(self, seconds: float) -> None:
        ...


class StateGateway(Protocol):
    """Source of current game state for assertions."""

    def latest_state(self) -> GameState | None:
        ...


@dataclass(frozen=True)
class ExecutionStep:
    action: str
    params: dict[str, Any]
    expected_screen: Screen | None = None


@dataclass(frozen=True)
class ExecutionPlan:
    steps: tuple[ExecutionStep, ...]


class PlanExecutor:
    """Deterministic plan executor with strict state assertions."""

    def __init__(self, input_gateway: InputGateway, state_gateway: StateGateway) -> None:
        self._input_gateway = input_gateway
        self._state_gateway = state_gateway

    def execute(self, plan: ExecutionPlan) -> None:
        for step in plan.steps:
            if step.expected_screen is not None:
                self._assert_screen(step.expected_screen)

            if step.action == "click":
                self._input_gateway.click(int(step.params["x"]), int(step.params["y"]))
            elif step.action == "key":
                self._input_gateway.key(str(step.params["key"]))
            elif step.action == "wait":
                self._input_gateway.wait(float(step.params["seconds"]))
            elif step.action == "assert_screen":
                self._assert_screen(Screen(str(step.params["screen"])))
            else:
                raise ExecutionError(f"Unsupported action '{step.action}'")

    def _assert_screen(self, expected: Screen) -> None:
        state = self._state_gateway.latest_state()
        if state is None:
            raise ExecutionError("Cannot assert screen without an available state")
        if state.screen != expected:
            raise ExecutionError(
                f"State assertion failed. Expected '{expected.value}', got '{state.screen.value}'"
            )
