import json
from pathlib import Path
from typing import Optional

from .data import JOBS, initial_state
from .models import GameState

SAVE_PATH = Path(__file__).resolve().parent.parent / "savegame.json"


def load_state(path: Optional[Path] = None) -> GameState:
    target = path or SAVE_PATH
    if target.exists():
        with target.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        return GameState.from_dict(raw, fallback_job_id=JOBS[0].id)
    return initial_state()


def save_state(state: GameState, path: Optional[Path] = None) -> None:
    target = path or SAVE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(state.to_dict(), handle, indent=2)
