# Pour Decisions (Python Edition)

A BitLife-style narrative sim about surviving and thriving behind the bar. Run your nights, manage stress and rent pressure, climb the career ladder from glass collector to bar owner, and respond to realistic nightlife events with meaningful choices.

## Quickstart

1. Install Python 3.11+.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Run the game from the project root:
   ```bash
   python main.py
   ```

Progress auto-saves to `savegame.json` in the project root. Press `Ctrl+C` to save and exit at any time.

## Game Loop

- **Work a shift**: Choose bus or car commute, then handle unpredictable shift events (spills, VIPs, inspections, fights). Earn wage and tips, gain XP/reputation, and watch rent pressure climb.
- **Rest and reset**: Recover energy and lower stress. Upgrades like better bedding or headphones improve recovery.
- **Practice**: Burn energy and a little cash to grow XP and reputation faster.
- **Shop**: Buy permanent upgrades (comfy sneakers, noise-canceling headphones, mixology course, car, rent planner, pro tools).
- **Promote**: Spend XP (and sometimes cash) plus qualifications to climb roles up to bar owner.
- **Story events**: BitLife-style prompts with choices that affect cash, stress, XP, and reputation.
- **Rent pressure**: Each day fills a rent bar. Pay when full or get demoted and wiped out.

## Controls

- Numbered menu for core actions.
- `b`/`c` to pick bus or car for commutes (car requires the upgrade).
- During story events, pick a numbered option or press Enter to let it pass.

## Files

- `main.py` – entry point.
- `pour_decisions/engine.py` – core simulation logic.
- `pour_decisions/data.py` – jobs, upgrades, and event definitions.
- `pour_decisions/cli.py` – terminal UI loop.
- `pour_decisions/storage.py` – JSON save/load helpers.
- `savegame.json` – auto-generated save file (ignored by git).

## Notes

- The game uses only the Python standard library; no extra installs required.
- Balancing aims for realism: stress caps work, rent punishes delays, and reputation meaningfully improves tips.
