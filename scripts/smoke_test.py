from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from raid_ops.connectors.vision_observer import make_default_observer

__test__ = False


def main() -> int:
    observer = make_default_observer()
    state = observer.capture_once()
    if state is None:
        print("Plarium Play window not found")
        return 1

    print(f"screen: {state.screen.value}")
    print(f"energy: {state.energy}")
    print(f"recommended_action: {state.recommended_action}")
    print(f"actionable_count: {len(state.actionable)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
