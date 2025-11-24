from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


@dataclass
class Job:
    id: str
    title: str
    pay_range: Tuple[int, int]
    xp_required: int
    rent: int
    entry_fee: int = 0
    requires: Optional[str] = None
    flavor: str = ""


@dataclass
class Upgrade:
    id: str
    name: str
    cost: int
    description: str
    effects: Dict[str, int]


@dataclass
class ShiftOutcome:
    wage: int
    tips: int
    energy_cost: int
    stress_gain: int
    xp_gain: int
    reputation_gain: int = 0
    cash_change: int = 0
    notes: List[str] = field(default_factory=list)


@dataclass
class ShiftEvent:
    id: str
    title: str
    text: str
    apply: Callable[[ShiftOutcome], None]
    weight: int = 1


@dataclass
class StoryChoice:
    id: str
    label: str
    effects: Dict[str, int]
    note: str


@dataclass
class StoryEvent:
    id: str
    title: str
    text: str
    choices: List[StoryChoice]
    weight: int = 1


@dataclass
class ActionReport:
    messages: List[str] = field(default_factory=list)
    day_advanced: bool = True


@dataclass
class GameState:
    day: int
    age: int
    energy: int
    stress: int
    cash: int
    xp: int
    reputation: int
    rent_progress: int
    job_id: str
    owned_upgrades: List[str] = field(default_factory=list)
    log: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "day": self.day,
            "age": self.age,
            "energy": self.energy,
            "stress": self.stress,
            "cash": self.cash,
            "xp": self.xp,
            "reputation": self.reputation,
            "rent_progress": self.rent_progress,
            "job_id": self.job_id,
            "owned_upgrades": list(self.owned_upgrades),
            "log": list(self.log),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object], fallback_job_id: str) -> "GameState":
        return cls(
            day=int(data.get("day", 1)),
            age=int(data.get("age", 21)),
            energy=int(data.get("energy", 80)),
            stress=int(data.get("stress", 12)),
            cash=int(data.get("cash", 120)),
            xp=int(data.get("xp", 0)),
            reputation=int(data.get("reputation", 10)),
            rent_progress=int(data.get("rent_progress", 0)),
            job_id=str(data.get("job_id", fallback_job_id)),
            owned_upgrades=list(data.get("owned_upgrades", [])),
            log=list(data.get("log", [])),
        )
