import sys
import textwrap

from .data import JOBS, UPGRADES
from .engine import GameEngine
from .storage import load_state, save_state


def _format_money(value: int) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value)}"


def _print_divider() -> None:
    print("-" * 72)


def _print_status(engine: GameEngine) -> None:
    state = engine.state
    job = engine.current_job
    upgrades = ", ".join(
        up.name for up in UPGRADES if up.id in state.owned_upgrades
    ) or "None"
    print(f"Day {state.day} | Age {state.age} | Role: {job.title}")
    print(
        f"Cash {_format_money(state.cash)} | XP {state.xp} | Reputation {state.reputation}"
    )
    print(
        f"Energy {state.energy}/100 | Stress {state.stress}/140 | Rent pressure {state.rent_progress}% (Rent {_format_money(job.rent)})"
    )
    print(f"Upgrades: {upgrades}")


def _print_report(report) -> None:
    for line in report.messages:
        print(f"• {line}")


def _prompt_commute(engine: GameEngine) -> str:
    if not engine.has_upgrade("car"):
        return "bus"
    choice = input("Commute (b=bus, c=car) [b]: ").strip().lower()
    if choice == "c":
        return "car"
    return "bus"


def _prompt_story(engine: GameEngine) -> None:
    event = engine.pick_story_event()
    if not event:
        return
    print()
    _print_divider()
    print(f"Story Event: {event.title}")
    print(textwrap.fill(event.text, width=68))
    for idx, choice in enumerate(event.choices, start=1):
        print(f"{idx}. {choice.label}")
    selection = input("Pick a choice (or Enter to skip): ").strip()
    if not selection:
        print("You let the moment pass.")
        return
    try:
        choice_idx = int(selection) - 1
        choice = event.choices[choice_idx]
    except (ValueError, IndexError):
        print("Invalid choice. Event slips by.")
        return

    report = engine.apply_story_choice(event, choice)
    _print_report(report)


def _shop(engine: GameEngine) -> None:
    print()
    _print_divider()
    print("Upgrades (buy once, permanent)")
    available = [up for up in UPGRADES if up.id not in engine.state.owned_upgrades]
    if not available:
        print("All upgrades owned.")
        return
    for idx, upgrade in enumerate(available, start=1):
        effects = ", ".join(f"{k}: {v}" for k, v in upgrade.effects.items())
        print(
            f"{idx}. {upgrade.name} - {_format_money(upgrade.cost)} | {upgrade.description} ({effects})"
        )
    selection = input("Pick an upgrade number to buy (or Enter to cancel): ").strip()
    if not selection:
        return
    try:
        choice_idx = int(selection) - 1
        upgrade = available[choice_idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    report = engine.purchase_upgrade(upgrade.id)
    _print_report(report)


def _promotion(engine: GameEngine) -> None:
    print()
    _print_divider()
    print("Career Ladder")
    current_idx = JOBS.index(engine.current_job)
    for idx, job in enumerate(JOBS, start=1):
        status = []
        if idx - 1 == current_idx:
            status.append("current")
        elif idx - 1 < current_idx:
            status.append("past")
        else:
            if engine.state.xp >= job.xp_required:
                status.append("xp ready")
            if job.requires and not engine.has_upgrade(job.requires):
                status.append("needs training")
            if job.entry_fee and engine.state.cash < job.entry_fee:
                status.append("needs cash")
        status_label = ", ".join(status) or "locked"
        entry = f"{idx}. {job.title} (Pay {job.pay_range[0]}-{job.pay_range[1]}, Rent {job.rent}, XP {job.xp_required}) [{status_label}]"
        if job.entry_fee:
            entry += f" Entry fee {_format_money(job.entry_fee)}"
        if job.requires:
            entry += " Requires mixology course"
        print(entry)

    selection = input("Enter job number to request promotion (or Enter to cancel): ").strip()
    if not selection:
        return
    try:
        choice_idx = int(selection) - 1
        job = JOBS[choice_idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    report = engine.request_promotion(job.id)
    _print_report(report)


def _show_log(engine: GameEngine) -> None:
    print()
    _print_divider()
    print("Recent feed:")
    for entry in engine.state.log:
        print(f"- {entry}")


def main() -> None:
    engine = GameEngine(load_state())
    print("Pour Decisions - BitLife-style Bartender Sim (Python Edition)")
    print("Type Ctrl+C to save and quit at any time.")

    try:
        while True:
            print()
            _print_divider()
            _print_status(engine)
            print()
            print("Actions:")
            print("1) Work a shift")
            print("2) Rest and reset")
            print("3) Practice recipes and speed")
            print("4) Shop for upgrades")
            print("5) Request promotion")
            print("6) Pay rent early")
            print("7) View recent log")
            print("8) Save and quit")

            action = input("Choose an action: ").strip()
            report = None

            if action == "1":
                commute = _prompt_commute(engine)
                report = engine.start_shift(commute)
            elif action == "2":
                report = engine.rest()
            elif action == "3":
                report = engine.practice()
            elif action == "4":
                _shop(engine)
            elif action == "5":
                _promotion(engine)
            elif action == "6":
                report = engine.pay_rent_now()
            elif action == "7":
                _show_log(engine)
            elif action == "8":
                save_state(engine.state)
                print("Saved. See you next shift.")
                sys.exit(0)
            else:
                print("Invalid choice.")

            if report:
                _print_report(report)
                _prompt_story(engine)

            save_state(engine.state)

    except KeyboardInterrupt:
        print("\nCaught exit. Saving progress...")
        save_state(engine.state)
        sys.exit(0)


if __name__ == "__main__":
    main()
