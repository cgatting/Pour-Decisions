import random
from typing import List, Optional, Tuple

from . import data
from .data import JOBS, SHIFT_EVENTS, STORY_EVENTS, UPGRADES, initial_state
from .models import (
    ActionReport,
    GameState,
    Job,
    ShiftEvent,
    ShiftOutcome,
    StoryChoice,
    StoryEvent,
    Upgrade,
)


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


def rand_range(min_value: int, max_value: int) -> int:
    return random.randint(min_value, max_value)


class GameEngine:
    def __init__(self, state: Optional[GameState] = None) -> None:
        self.state = state or initial_state()

    @property
    def current_job(self) -> Job:
        job = next((job for job in JOBS if job.id == self.state.job_id), JOBS[0])
        return job

    def has_upgrade(self, upgrade_id: str) -> bool:
        return upgrade_id in self.state.owned_upgrades

    def _upgrade_effect(self, key: str) -> int:
        total = 0
        for upgrade in UPGRADES:
            if upgrade.id in self.state.owned_upgrades:
                total += upgrade.effects.get(key, 0)
        return total

    def _push_log(self, message: str) -> None:
        self.state.log.insert(0, message)
        self.state.log = self.state.log[:20]

    def _weighted_choice(self, events: List[ShiftEvent] | List[StoryEvent]) -> ShiftEvent | StoryEvent:
        total_weight = sum(event.weight for event in events)
        pick = random.uniform(0, total_weight)
        current = 0.0
        for event in events:
            current += event.weight
            if pick <= current:
                return event
        return events[-1]

    def _resolve_commute(self, mode: str) -> Tuple[bool, int, int, str]:
        if mode == "car" and not self.has_upgrade("car"):
            return False, 0, 0, "No car yet. Back on the bus."

        if mode == "bus":
            late = random.random() < 0.35
            stress_delta = 3 + (4 if random.random() < 0.25 else 0)
            note = "Bus crawls through traffic. You arrive late." if late else "Bus ride: cheap and cramped."
            return late, stress_delta, 0, note

        breakdown = random.random() < 0.18
        traffic = (not breakdown) and random.random() < 0.3
        late = False
        stress_delta = 2
        cash_change = 0
        note = "You glide through neon streets in your beater car."

        if breakdown:
            cash_change = -rand_range(35, 60)
            stress_delta += 14
            late = random.random() < 0.4
            note = "Car coughs to a stop. Repair eats cash and time."
        elif traffic:
            stress_delta += 8
            late = random.random() < 0.22
            note = "Gridlock. Horns blare. Pulse rises."

        return late, stress_delta, cash_change, note

    def _advance_day(self, rent_increment: int, messages: List[str]) -> None:
        rent_increment = max(0, rent_increment)
        self.state.day += 1
        self.state.rent_progress += rent_increment
        self._apply_rent_pressure(messages)
        if self.state.day % 365 == 0:
            self.state.age += 1
            birthday = f"You turned {self.state.age}. Service life does not slow down."
            messages.append(birthday)
            self._push_log(birthday)

    def _apply_rent_pressure(self, messages: List[str]) -> None:
        rent_due = self.current_job.rent
        while self.state.rent_progress >= 100:
            if self.state.cash >= rent_due:
                self.state.cash -= rent_due
                self.state.rent_progress -= 100
                note = f"Paid rent: ${rent_due}."
                messages.append(note)
                self._push_log(note)
            else:
                demotion = JOBS[0]
                self.state.cash = 0
                self.state.rent_progress = 0
                self.state.job_id = demotion.id
                note = f"Evicted. Cash wiped and demoted to {demotion.title}."
                messages.append(note)
                self._push_log(note)
                break

    def start_shift(self, commute_mode: str = "bus") -> ActionReport:
        messages: List[str] = []

        if self.state.energy < 15:
            msg = "Too exhausted to work. Crash at home first."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        if self.state.stress > 95:
            msg = "You freeze at the door. Stress is maxed."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        job = self.current_job
        job_index = JOBS.index(job)

        energy_cost = 22 + job_index * 2
        stress_gain = 14 + job_index * 2
        wage = rand_range(job.pay_range[0], job.pay_range[1])
        tips = rand_range(14, 38) + self._upgrade_effect("tip_bonus")
        xp_gain = 22 + job_index * 6 + self._upgrade_effect("xp_bonus")
        reputation_gain = self._upgrade_effect("reputation_bonus")
        cash_change = 0

        energy_cost += self._upgrade_effect("energy_cost")
        stress_gain += self._upgrade_effect("stress_gain")

        late, commute_stress, commute_cash, commute_note = self._resolve_commute(commute_mode)
        stress_gain += commute_stress
        cash_change += commute_cash
        messages.append(commute_note)
        self._push_log(commute_note)

        if late:
            tips = max(0, int(tips * 0.25))
            wage = max(0, int(wage * 0.85))
            xp_gain = max(6, xp_gain - 4)
            messages.append("Late to the shift. Tips are crushed.")
            self._push_log("Late to the shift. Tips are crushed.")

        notes: List[str] = []

        if random.random() < 0.55:
            event = self._weighted_choice(SHIFT_EVENTS)
            outcome = ShiftOutcome(
                wage=wage,
                tips=tips,
                energy_cost=energy_cost,
                stress_gain=stress_gain,
                xp_gain=xp_gain,
                reputation_gain=reputation_gain,
                cash_change=cash_change,
            )
            event.apply(outcome)
            wage = max(0, outcome.wage)
            tips = max(0, outcome.tips)
            energy_cost = max(8, outcome.energy_cost)
            stress_gain = max(0, outcome.stress_gain)
            xp_gain = max(8, outcome.xp_gain)
            reputation_gain += outcome.reputation_gain
            cash_change = outcome.cash_change
            notes = outcome.notes
            event_line = f"{event.title}: {event.text}"
            messages.append(event_line)
            self._push_log(event_line)

        earnings = wage + tips + cash_change
        self.state.cash += earnings
        self.state.energy = clamp(self.state.energy - energy_cost, 0, 120)
        self.state.stress = clamp(self.state.stress + stress_gain, 0, 140)
        self.state.xp = max(0, self.state.xp + xp_gain)
        if reputation_gain:
            self.state.reputation = clamp(self.state.reputation + reputation_gain, 0, 150)

        summary = f"Shift finished as {job.title}: +${earnings} (${wage} wage, ${tips} tips)"
        messages.append(summary)
        self._push_log(summary)

        for note in notes:
            messages.append(note)
            self._push_log(note)

        rent_increment = max(6, 14 + self._upgrade_effect("rent_slow"))
        self._advance_day(rent_increment, messages)

        return ActionReport(messages=messages, day_advanced=True)

    def rest(self) -> ActionReport:
        messages: List[str] = []
        energy_gain = 42 + self._upgrade_effect("sleep_bonus")
        stress_relief = 20 + max(0, self._upgrade_effect("sleep_bonus") // 3)

        self.state.energy = clamp(self.state.energy + energy_gain, 0, 120)
        self.state.stress = clamp(self.state.stress - stress_relief, 0, 140)

        summary = f"You crash at home and sleep. +{energy_gain} energy, -{stress_relief} stress."
        messages.append(summary)
        self._push_log(summary)

        rent_increment = max(4, 6 + self._upgrade_effect("rent_slow"))
        self._advance_day(rent_increment, messages)

        return ActionReport(messages=messages, day_advanced=True)

    def practice(self) -> ActionReport:
        messages: List[str] = []
        energy_cost = max(10, 20 + self._upgrade_effect("energy_cost"))
        stress_gain = max(0, 6 + self._upgrade_effect("stress_gain"))
        xp_gain = 48 + self._upgrade_effect("xp_bonus")
        reputation_gain = 6 + self._upgrade_effect("reputation_bonus")
        cash_cost = 12

        if self.state.energy < energy_cost:
            msg = "Not enough energy to practice. Rest first."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        self.state.energy = clamp(self.state.energy - energy_cost, 0, 120)
        self.state.stress = clamp(self.state.stress + stress_gain, 0, 140)
        self.state.cash -= cash_cost
        self.state.xp += xp_gain
        self.state.reputation = clamp(self.state.reputation + reputation_gain, 0, 150)

        summary = f"Practiced pours and recipes. -{energy_cost} energy, +{xp_gain} XP, +{reputation_gain} reputation."
        messages.append(summary)
        self._push_log(summary)

        rent_increment = max(6, 10 + self._upgrade_effect("rent_slow"))
        self._advance_day(rent_increment, messages)

        return ActionReport(messages=messages, day_advanced=True)

    def pay_rent_now(self) -> ActionReport:
        messages: List[str] = []
        rent_due = self.current_job.rent
        if self.state.cash >= rent_due:
            self.state.cash -= rent_due
            self.state.rent_progress = 0
            note = f"Paid rent early: ${rent_due}. Pressure resets."
            messages.append(note)
            self._push_log(note)
        else:
            note = f"Need ${rent_due} to cover rent. Cash on hand: ${self.state.cash}."
            messages.append(note)
            self._push_log(note)
        return ActionReport(messages=messages, day_advanced=False)

    def available_promotions(self) -> List[Job]:
        current_index = JOBS.index(self.current_job)
        return JOBS[current_index + 1 :]

    def request_promotion(self, job_id: str) -> ActionReport:
        messages: List[str] = []
        target = next((job for job in JOBS if job.id == job_id), None)
        if not target:
            messages.append("That role does not exist.")
            return ActionReport(messages=messages, day_advanced=False)

        current_index = JOBS.index(self.current_job)
        target_index = JOBS.index(target)
        if target_index <= current_index:
            msg = "You already wear that name tag."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        if target.requires and not self.has_upgrade(target.requires):
            msg = "Need the required training first."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        if self.state.xp < target.xp_required:
            msg = "Not enough XP to impress management yet."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        if target.entry_fee and self.state.cash < target.entry_fee:
            msg = f"Need ${target.entry_fee} to onboard."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        self.state.cash -= target.entry_fee
        self.state.job_id = target.id
        note = f"Promoted to {target.title}!"
        messages.append(note)
        self._push_log(note)

        return ActionReport(messages=messages, day_advanced=False)

    def purchase_upgrade(self, upgrade_id: str) -> ActionReport:
        messages: List[str] = []
        upgrade = next((up for up in UPGRADES if up.id == upgrade_id), None)
        if not upgrade:
            messages.append("That upgrade does not exist.")
            return ActionReport(messages=messages, day_advanced=False)

        if self.has_upgrade(upgrade.id):
            msg = f"{upgrade.name} already owned."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        if self.state.cash < upgrade.cost:
            msg = f"Need ${upgrade.cost} for {upgrade.name}."
            messages.append(msg)
            self._push_log(msg)
            return ActionReport(messages=messages, day_advanced=False)

        self.state.cash -= upgrade.cost
        self.state.owned_upgrades.append(upgrade.id)
        note = f"Bought {upgrade.name}. {upgrade.description}"
        messages.append(note)
        self._push_log(note)

        return ActionReport(messages=messages, day_advanced=False)

    def pick_story_event(self) -> Optional[StoryEvent]:
        if random.random() < 0.3:
            return self._weighted_choice(STORY_EVENTS)
        return None

    def apply_story_choice(self, event: StoryEvent, choice: StoryChoice) -> ActionReport:
        messages: List[str] = []
        effects = choice.effects

        self.state.energy = clamp(self.state.energy + effects.get("energy", 0), 0, 120)
        self.state.stress = clamp(self.state.stress + effects.get("stress", 0), 0, 140)
        self.state.cash += effects.get("cash", 0)
        self.state.xp = max(0, self.state.xp + effects.get("xp", 0))
        self.state.reputation = clamp(self.state.reputation + effects.get("reputation", 0), 0, 150)

        summary = f"{event.title} -> {choice.label}: {choice.note}"
        messages.append(summary)
        self._push_log(summary)

        return ActionReport(messages=messages, day_advanced=False)
