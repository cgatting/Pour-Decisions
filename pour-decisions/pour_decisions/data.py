from __future__ import annotations

from typing import List

from .models import (
    GameState,
    Job,
    ShiftEvent,
    ShiftOutcome,
    StoryChoice,
    StoryEvent,
    Upgrade,
)


JOBS: List[Job] = [
    Job(
        id="glass-collector",
        title="Glass Collector",
        pay_range=(28, 46),
        xp_required=0,
        rent=220,
        flavor="Your night is a blur of clinking glasses and sticky floors.",
    ),
    Job(
        id="barback",
        title="Barback",
        pay_range=(45, 76),
        xp_required=120,
        rent=320,
        flavor="You are the invisible hands keeping the bar alive.",
    ),
    Job(
        id="bartender",
        title="Bartender",
        pay_range=(70, 118),
        xp_required=280,
        rent=480,
        flavor="Every order is a performance. Every eye is on you.",
    ),
    Job(
        id="mixologist",
        title="Mixologist",
        pay_range=(100, 160),
        xp_required=450,
        rent=650,
        entry_fee=250,
        requires="mixology-course",
        flavor="Signature cocktails, signature stress.",
    ),
    Job(
        id="shift-lead",
        title="Shift Lead",
        pay_range=(150, 220),
        xp_required=720,
        rent=880,
        flavor="You juggle staff drama and the night's chaos.",
    ),
    Job(
        id="bar-owner",
        title="Bar Owner",
        pay_range=(210, 290),
        xp_required=1100,
        rent=1200,
        entry_fee=900,
        flavor="You call the shots but the bills keep coming.",
    ),
]

UPGRADES: List[Upgrade] = [
    Upgrade(
        id="sneakers",
        name="Comfy Sneakers",
        cost=120,
        description="Reduce energy cost per shift.",
        effects={"energy_cost": -6},
    ),
    Upgrade(
        id="headphones",
        name="Noise-Canceling Headphones",
        cost=150,
        description="Reduce stress gain per shift and sleep deeper.",
        effects={"stress_gain": -6, "sleep_bonus": 5},
    ),
    Upgrade(
        id="bed",
        name="Memory Foam Mattress",
        cost=200,
        description="Sleeping restores more energy.",
        effects={"sleep_bonus": 15},
    ),
    Upgrade(
        id="car",
        name="Second-Hand Car",
        cost=320,
        description="Unlocks faster commute with its own risks.",
        effects={"commute_car": 1},
    ),
    Upgrade(
        id="mixology-course",
        name="Mixology Course",
        cost=200,
        description="Required for the Mixologist promotion.",
        effects={"qualification": 1},
    ),
    Upgrade(
        id="planner",
        name="Rent Planner",
        cost=140,
        description="Rent pressure fills slower.",
        effects={"rent_slow": -4},
    ),
    Upgrade(
        id="jigger",
        name="Pro Jigger",
        cost=110,
        description="Raises consistency and tips.",
        effects={"tip_bonus": 8},
    ),
    Upgrade(
        id="mentor",
        name="Mentor Sessions",
        cost=180,
        description="Weekly mentoring that boosts reputation and XP gain.",
        effects={"reputation_bonus": 8, "xp_bonus": 6},
    ),
]


def perfect_pour(outcome: ShiftOutcome) -> None:
    outcome.tips += 24
    outcome.xp_gain += 6
    outcome.stress_gain = max(0, outcome.stress_gain - 3)
    outcome.notes.append("Glowing reviews boost your reputation.")


def tray_spill(outcome: ShiftOutcome) -> None:
    outcome.tips = max(0, outcome.tips - 10)
    outcome.wage = max(0, outcome.wage - 8)
    outcome.stress_gain += 10
    outcome.energy_cost += 4
    outcome.notes.append("Clean-up duty eats time and patience.")


def vip_bottle(outcome: ShiftOutcome) -> None:
    outcome.tips += 45
    outcome.energy_cost += 6
    outcome.stress_gain += 8
    outcome.xp_gain += 10
    outcome.reputation_gain += 6
    outcome.notes.append("The VIP selfie with you goes viral.")


def rowdy_regulars(outcome: ShiftOutcome) -> None:
    outcome.tips += 12
    outcome.stress_gain += 8
    outcome.notes.append("They tip well but you earn every penny.")


def slow_monday(outcome: ShiftOutcome) -> None:
    outcome.wage = max(0, outcome.wage - 12)
    outcome.tips = max(0, outcome.tips - 14)
    outcome.energy_cost = max(8, outcome.energy_cost - 4)
    outcome.stress_gain = max(0, outcome.stress_gain - 6)
    outcome.notes.append("Quiet night lets you breathe.")


def tap_issue(outcome: ShiftOutcome) -> None:
    outcome.wage = max(0, outcome.wage - 6)
    outcome.stress_gain += 6
    outcome.energy_cost += 6
    outcome.notes.append("Sticky hands, sticky mood.")


def bar_fight(outcome: ShiftOutcome) -> None:
    outcome.tips = 0
    outcome.stress_gain += 18
    outcome.energy_cost += 10
    outcome.xp_gain += 6
    outcome.reputation_gain += 4
    outcome.notes.append("Security drags them out. Adrenaline lingers.")


def mystery_critic(outcome: ShiftOutcome) -> None:
    outcome.wage += 14
    outcome.xp_gain += 12
    outcome.stress_gain += 6
    outcome.reputation_gain += 10
    outcome.notes.append("Quiet critic writes about your composure.")


def cooler_break(outcome: ShiftOutcome) -> None:
    outcome.cash_change -= 28
    outcome.energy_cost += 6
    outcome.stress_gain += 7
    outcome.notes.append("Replacing ice comes out of your pocket.")


def karaoke(outcome: ShiftOutcome) -> None:
    outcome.tips += 16
    outcome.stress_gain += 4
    outcome.notes.append("Off-key singing, on-point tipping.")


def health_check(outcome: ShiftOutcome) -> None:
    outcome.wage = max(0, outcome.wage - 10)
    outcome.stress_gain += 9
    outcome.notes.append("You scramble to look spotless.")


SHIFT_EVENTS: List[ShiftEvent] = [
    ShiftEvent(id="perfect-pour", title="Perfect Pour Rush", text="Every drink lands flawlessly.", apply=perfect_pour, weight=3),
    ShiftEvent(id="tray-spill", title="Tray Spill", text="You slip and send a tray flying.", apply=tray_spill, weight=3),
    ShiftEvent(id="vip-bottle", title="VIP Bottle Service", text="A private table orders bottles all night.", apply=vip_bottle, weight=2),
    ShiftEvent(id="rowdy-regulars", title="Rowdy Regulars", text="Your favorite troublemakers show up loud.", apply=rowdy_regulars, weight=2),
    ShiftEvent(id="slow-monday", title="Slow Monday", text="The bar is half empty.", apply=slow_monday, weight=2),
    ShiftEvent(id="tap-issue", title="Busted Tap", text="You fight with the beer tap for an hour.", apply=tap_issue, weight=2),
    ShiftEvent(id="bar-fight", title="Bar Fight", text="Shouting turns into fists.", apply=bar_fight, weight=2),
    ShiftEvent(id="mystery-critic", title="Mystery Critic", text="Someone judges every pour.", apply=mystery_critic, weight=1),
    ShiftEvent(id="cooler-break", title="Cooler Breakdown", text="The cooler dies and melts the ice.", apply=cooler_break, weight=2),
    ShiftEvent(id="karaoke", title="Karaoke Night", text="A pop-up DJ invites singing.", apply=karaoke, weight=2),
    ShiftEvent(id="health-check", title="Surprise Health Inspection", text="Clipboards and flashlights mid-rush.", apply=health_check, weight=1),
]


STORY_EVENTS: List[StoryEvent] = [
    StoryEvent(
        id="influencer",
        title="Influencer Shoutout",
        text="A nightlife influencer tags the bar in their stories.",
        choices=[
            StoryChoice(
                id="lean-in",
                label="Lean into the buzz and comp a round.",
                effects={"cash": -25, "reputation": 14, "stress": 4},
                note="Crowd surges and your name trends locally.",
            ),
            StoryChoice(
                id="stay-cool",
                label="Acknowledge politely, keep the flow steady.",
                effects={"reputation": 8, "stress": 2},
                note="You keep control without losing pace.",
            ),
            StoryChoice(
                id="ignore",
                label="Ignore it and stick to regulars.",
                effects={"reputation": -6, "stress": -4},
                note="Some patrons call you cold, but night stays calm.",
            ),
        ],
        weight=3,
    ),
    StoryEvent(
        id="fake-id",
        title="Suspicious ID",
        text="A guest hands over an ID that looks barely legit.",
        choices=[
            StoryChoice(
                id="refuse",
                label="Refuse service and log it.",
                effects={"reputation": 6, "stress": 6, "xp": 12},
                note="Manager backs you; the guest complains online.",
            ),
            StoryChoice(
                id="serve",
                label="Serve anyway and hope it slides.",
                effects={"cash": 30, "reputation": -12, "xp": -6},
                note="You make quick cash but risk a report.",
            ),
            StoryChoice(
                id="call-manager",
                label="Escalate to the manager on duty.",
                effects={"reputation": 4, "stress": 2},
                note="Manager takes over; you dodge the fallout.",
            ),
        ],
        weight=2,
    ),
    StoryEvent(
        id="team-short",
        title="Short Staffed",
        text="Two teammates call out. The floor is thin.",
        choices=[
            StoryChoice(
                id="cover",
                label="Cover the extra tables yourself.",
                effects={"energy": -14, "stress": 10, "xp": 20, "reputation": 10},
                note="Exhausting night, but the GM notices.",
            ),
            StoryChoice(
                id="cut-menu",
                label="Cut the menu to essentials only.",
                effects={"stress": -4, "cash": -20, "reputation": -3},
                note="Guests grumble but you keep control.",
            ),
            StoryChoice(
                id="call-favors",
                label="Call in a favor from a friend.",
                effects={"cash": -10, "reputation": 6, "xp": 8},
                note="They bail you out after a Venmo bribe.",
            ),
        ],
        weight=3,
    ),
    StoryEvent(
        id="noise-complaint",
        title="Noise Complaint",
        text="Neighbors threaten to call the cops about noise spilling onto the street.",
        choices=[
            StoryChoice(
                id="calm-line",
                label="Step outside, calm the line, and offer water.",
                effects={"energy": -6, "stress": 4, "reputation": 8},
                note="The gesture diffuses tension and cops stay away.",
            ),
            StoryChoice(
                id="ignore-line",
                label="Ignore it and hope it blows over.",
                effects={"reputation": -10, "stress": 2},
                note="Police show up; nothing escalates but reviews dip.",
            ),
            StoryChoice(
                id="wrap-early",
                label="Shut down music early to keep the peace.",
                effects={"cash": -35, "reputation": 4, "stress": -6},
                note="Revenue dips but so does your heart rate.",
            ),
        ],
        weight=2,
    ),
    StoryEvent(
        id="training-offer",
        title="Training Offer",
        text="A distributor offers a free spirits workshop after hours.",
        choices=[
            StoryChoice(
                id="attend",
                label="Attend and take notes.",
                effects={"energy": -8, "xp": 30, "reputation": 6},
                note="New recipes boost your menu pitch.",
            ),
            StoryChoice(
                id="skip",
                label="Skip and rest instead.",
                effects={"energy": 12, "stress": -8},
                note="You are fresh for the next rush but miss insights.",
            ),
            StoryChoice(
                id="send-friend",
                label="Send a teammate and ask for their notes.",
                effects={"reputation": 4, "xp": 10, "cash": -10},
                note="You treat them for going and learn second-hand.",
            ),
        ],
        weight=2,
    ),
    StoryEvent(
        id="bar-fight-choice",
        title="Fight Brews",
        text="A shouting match between regulars is about to get physical.",
        choices=[
            StoryChoice(
                id="intervene",
                label="Step in before fists fly.",
                effects={"energy": -10, "stress": 10, "reputation": 12, "xp": 10},
                note="You earn respect but your hands shake after.",
            ),
            StoryChoice(
                id="call-security",
                label="Call security immediately.",
                effects={"reputation": 2, "stress": 4},
                note="Quick thinking prevents chaos.",
            ),
            StoryChoice(
                id="ignore",
                label="Ignore it and keep serving.",
                effects={"reputation": -14, "stress": 2},
                note="Patrons film the chaos; your name is tagged.",
            ),
        ],
        weight=2,
    ),
]


def initial_state() -> GameState:
    return GameState(
        day=1,
        age=21,
        energy=82,
        stress=12,
        cash=160,
        xp=0,
        reputation=10,
        rent_progress=12,
        job_id=JOBS[0].id,
        owned_upgrades=[],
        log=["You wake up in a neon-lit studio. Rent is looming."],
    )
