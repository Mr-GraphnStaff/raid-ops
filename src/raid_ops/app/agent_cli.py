from __future__ import annotations

import argparse
from pathlib import Path

from raid_ops.connectors.routine_recorder import JsonlRecorderGateway, RoutineRecorder
from raid_ops.services.routine_service import JsonlRoutineRepository, RoutineService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="raid-ops automation CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("record", help="Record state/action pairs")

    playback = subparsers.add_parser("playback", help="Play back a routine by screen")
    playback.add_argument("screen")

    run = subparsers.add_parser("run", help="Run the agent loop")
    run.add_argument("--max-iterations", type=int, default=1)

    subparsers.add_parser("list-routines", help="List available routines")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repository = JsonlRoutineRepository(Path("data/recordings"))
    routines = RoutineService(repository)

    if args.command == "list-routines":
        print("\n".join(routines.list_routines()))
        return

    if args.command == "record":
        recorder = RoutineRecorder(JsonlRecorderGateway())
        print(f"Recorder ready at: {recorder.output_path}")
        return

    if args.command in {"playback", "run"}:
        raise RuntimeError(
            "playback/run wiring requires concrete observer/input adapters; use app composition in runtime environment"
        )


if __name__ == "__main__":
    main()
