import { useEffect, useMemo, useState } from 'react';
import './App.css';

type CommuteMode = 'bus' | 'car';

type Job = {
  id: string;
  title: string;
  payRange: [number, number];
  xpReq: number;
  rent: number;
  entryFee?: number;
  requires?: string;
  flavor: string;
};

type Upgrade = {
  id: string;
  name: string;
  cost: number;
  description: string;
  type: 'energy' | 'stress' | 'sleep' | 'car' | 'qual' | 'rent';
  value: number;
};

type MutableOutcome = {
  wage: number;
  tips: number;
  energyCost: number;
  stressGain: number;
  xpGain: number;
  cashChange: number;
  notes: string[];
};

type ShiftEvent = {
  id: string;
  title: string;
  text: string;
  apply: (outcome: MutableOutcome) => void;
};

type GameState = {
  energy: number;
  stress: number;
  cash: number;
  xp: number;
  rentProgress: number;
  day: number;
  jobId: string;
  ownedUpgrades: string[];
  log: string[];
};

const JOBS: Job[] = [
  {
    id: 'glass-collector',
    title: 'Glass Collector',
    payRange: [28, 46],
    xpReq: 0,
    rent: 220,
    flavor: 'Your night is a blur of clinking glasses and sticky floors.',
  },
  {
    id: 'barback',
    title: 'Barback',
    payRange: [45, 76],
    xpReq: 100,
    rent: 320,
    flavor: 'You are the invisible hands keeping the bar alive.',
  },
  {
    id: 'bartender',
    title: 'Bartender',
    payRange: [70, 118],
    xpReq: 240,
    rent: 450,
    flavor: 'Every order is a performance. Every eye is on you.',
  },
  {
    id: 'mixologist',
    title: 'Mixologist',
    payRange: [96, 156],
    xpReq: 420,
    rent: 620,
    entryFee: 180,
    requires: 'course',
    flavor: 'Signature cocktails, signature stress.',
  },
  {
    id: 'shift-lead',
    title: 'Shift Lead',
    payRange: [140, 210],
    xpReq: 650,
    rent: 840,
    flavor: 'You juggle staff drama and the night’s chaos.',
  },
  {
    id: 'bar-owner',
    title: 'Bar Owner',
    payRange: [190, 260],
    xpReq: 1000,
    rent: 1150,
    flavor: 'You call the shots but the bills keep coming.',
  },
];

const UPGRADES: Upgrade[] = [
  {
    id: 'sneakers',
    name: 'Comfy Sneakers',
    cost: 120,
    description: 'Reduce energy cost per shift.',
    type: 'energy',
    value: 6,
  },
  {
    id: 'headphones',
    name: 'Noise-Canceling Headphones',
    cost: 150,
    description: 'Reduce stress gain per shift and rest better.',
    type: 'stress',
    value: 6,
  },
  {
    id: 'bed',
    name: 'Memory Foam Cot',
    cost: 200,
    description: 'Sleeping restores more energy.',
    type: 'sleep',
    value: 15,
  },
  {
    id: 'car',
    name: 'Second-Hand Car',
    cost: 320,
    description: 'Unlocks faster commute with its own risks.',
    type: 'car',
    value: 0,
  },
  {
    id: 'course',
    name: 'Mixology Course',
    cost: 180,
    description: 'Required for the Mixologist promotion.',
    type: 'qual',
    value: 0,
  },
  {
    id: 'planner',
    name: 'Rent Planner',
    cost: 110,
    description: 'Rent bar fills slower.',
    type: 'rent',
    value: 3,
  },
];

const SHIFT_EVENTS: ShiftEvent[] = [
  {
    id: 'perfect-pour',
    title: 'Perfect Pour Rush',
    text: 'Every drink lands flawlessly. Customers notice.',
    apply: (o) => {
      o.tips += 24;
      o.xpGain += 6;
      o.stressGain -= 2;
      o.notes.push('Glowing reviews boost your reputation.');
    },
  },
  {
    id: 'tray-spill',
    title: 'Tray Spill',
    text: 'You slip and send a tray flying.',
    apply: (o) => {
      o.tips = Math.max(0, o.tips - 10);
      o.wage -= 8;
      o.stressGain += 10;
      o.energyCost += 4;
      o.notes.push('Clean-up duty eats time and patience.');
    },
  },
  {
    id: 'vip-bottle',
    title: 'VIP Bottle Service',
    text: 'A private table orders bottles all night.',
    apply: (o) => {
      o.tips += 40;
      o.energyCost += 8;
      o.stressGain += 6;
      o.xpGain += 10;
      o.notes.push('The VIP selfie with you goes viral.');
    },
  },
  {
    id: 'rowdy-regulars',
    title: 'Rowdy Regulars',
    text: 'Your favorite troublemakers show up loud.',
    apply: (o) => {
      o.tips += 12;
      o.stressGain += 8;
      o.notes.push('They tip well but you earn every penny.');
    },
  },
  {
    id: 'slow-monday',
    title: 'Slow Monday',
    text: 'The bar is half empty.',
    apply: (o) => {
      o.wage -= 10;
      o.tips = Math.max(0, o.tips - 12);
      o.energyCost -= 4;
      o.stressGain -= 4;
      o.notes.push('Quiet night lets you breathe.');
    },
  },
  {
    id: 'tap-issue',
    title: 'Busted Tap',
    text: 'You fight with the beer tap for an hour.',
    apply: (o) => {
      o.wage -= 6;
      o.stressGain += 6;
      o.energyCost += 6;
      o.notes.push('Sticky hands, sticky mood.');
    },
  },
  {
    id: 'bar-fight',
    title: 'Bar Fight',
    text: 'Shouting turns into fists. Security drags them out.',
    apply: (o) => {
      o.tips = 0;
      o.stressGain += 18;
      o.energyCost += 10;
      o.xpGain += 4;
      o.notes.push('Adrenaline shakes you for the rest of the night.');
    },
  },
  {
    id: 'social-shout',
    title: 'Social Media Shoutout',
    text: 'An influencer tags the bar.',
    apply: (o) => {
      o.tips += 26;
      o.xpGain += 8;
      o.stressGain += 3;
      o.notes.push('New followers flood your feed.');
    },
  },
  {
    id: 'health-check',
    title: 'Surprise Health Inspection',
    text: 'Clipboards and flashlights appear mid-rush.',
    apply: (o) => {
      o.wage -= 12;
      o.stressGain += 9;
      o.notes.push('You scramble to look spotless.');
    },
  },
  {
    id: 'cooler-break',
    title: 'Cooler Breakdown',
    text: 'The cooler dies and melts the ice.',
    apply: (o) => {
      o.cashChange -= 20;
      o.energyCost += 6;
      o.stressGain += 7;
      o.notes.push('Replacing ice costs you out of pocket.');
    },
  },
  {
    id: 'karaoke',
    title: 'Karaoke Night',
    text: 'Off-key singing, on-point tipping.',
    apply: (o) => {
      o.tips += 14;
      o.stressGain += 4;
      o.notes.push('You mouth along and earn extra.');
    },
  },
  {
    id: 'mystery-critic',
    title: 'Mystery Critic',
    text: 'Someone is quietly judging every pour.',
    apply: (o) => {
      o.wage += 10;
      o.xpGain += 12;
      o.stressGain += 8;
      o.notes.push('You keep your form tight all night.');
    },
  },
  {
    id: 'free-round',
    title: 'Free Drinks Mistake',
    text: 'A comped round goes wrong.',
    apply: (o) => {
      o.cashChange -= 25;
      o.tips -= 8;
      o.stressGain += 6;
      o.notes.push('Manager docks you for the slip.');
    },
  },
  {
    id: 'popup-dj',
    title: 'Pop-Up DJ',
    text: 'A local DJ spins a surprise set.',
    apply: (o) => {
      o.tips += 20;
      o.energyCost += 6;
      o.stressGain += 5;
      o.notes.push('Dance floor erupts, orders spike.');
    },
  },
];

const STORAGE_KEY = 'pour-decisions-v1';

const clamp = (value: number, min: number, max: number) =>
  Math.min(max, Math.max(min, value));

const randRange = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1)) + min;

const BASE_STATE: GameState = {
  energy: 80,
  stress: 12,
  cash: 120,
  xp: 0,
  rentProgress: 20,
  day: 1,
  jobId: JOBS[0].id,
  ownedUpgrades: [],
  log: ['You wake up in a neon-lit studio. Rent is looming.'],
};

const loadInitial = (): GameState => {
  if (typeof window === 'undefined') return BASE_STATE;
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return BASE_STATE;

  try {
    const parsed = JSON.parse(saved) as GameState;
    return { ...BASE_STATE, ...parsed, log: parsed.log ?? BASE_STATE.log };
  } catch (error) {
    console.error('Failed to load save, using defaults.', error);
    return BASE_STATE;
  }
};

function App() {
  const [state, setState] = useState<GameState>(() => loadInitial());
  const [commute, setCommute] = useState<CommuteMode>('bus');

  const currentJob = useMemo(
    () => JOBS.find((j) => j.id === state.jobId) ?? JOBS[0],
    [state.jobId]
  );

  const hasUpgrade = (id: string) => state.ownedUpgrades.includes(id);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
  }, [state]);

  const pushLog = (message: string, prevLog?: string[]) => {
    const newLog = [message, ...(prevLog ?? state.log)];
    return newLog.slice(0, 14);
  };

  const applyRentPressure = (
    cash: number,
    rentProgress: number,
    jobId: string,
    log: string[]
  ) => {
    let nextJobId = jobId;
    let rentBar = rentProgress;
    let updatedCash = cash;
    let updatedLog = log;
    const rentDue = (JOBS.find((j) => j.id === jobId) ?? JOBS[0]).rent;

    while (rentBar >= 100) {
      if (updatedCash >= rentDue) {
        updatedCash -= rentDue;
        rentBar -= 100;
        updatedLog = pushLog(`Paid rent: $${rentDue}.`, updatedLog);
      } else {
        nextJobId = JOBS[0].id;
        updatedCash = 0;
        rentBar = 0;
        updatedLog = pushLog(
          `Evicted. Cash wiped and demoted to ${JOBS[0].title}.`,
          updatedLog
        );
        break;
      }
    }

    return { cash: updatedCash, rentProgress: rentBar, jobId: nextJobId, log: updatedLog };
  };

  const handleRest = () => {
    setState((prev) => {
      const owned = prev.ownedUpgrades;
      let log = pushLog('You crash at home and sleep through the city hum.', prev.log);
      const energyGain = 40 + (owned.includes('bed') ? 15 : 0);
      const stressRelief = 22 + (owned.includes('headphones') ? 6 : 0);

      const energy = clamp(prev.energy + energyGain, 0, 100);
      const stress = clamp(prev.stress - stressRelief, 0, 100);
      const rentProgress = prev.rentProgress + 6 - (owned.includes('planner') ? 3 : 0);

      const rentResult = applyRentPressure(prev.cash, rentProgress, prev.jobId, log);

      return {
        ...prev,
        energy,
        stress,
        cash: rentResult.cash,
        rentProgress: rentResult.rentProgress,
        jobId: rentResult.jobId,
        day: prev.day + 1,
        log: rentResult.log,
      };
    });
  };

  const resolveCommute = (mode: CommuteMode, owned: string[]) => {
    if (mode === 'car' && !owned.includes('car')) {
      return { late: false, stressDelta: 0, cashChange: 0, note: 'No car yet. Back on the bus.' };
    }

    if (mode === 'bus') {
      const late = Math.random() < 0.35;
      const stressDelta = 3 + (Math.random() < 0.25 ? 4 : 0);
      const note = late
        ? 'Bus crawls through traffic. You arrive late.'
        : 'Bus ride: cheap and cramped.';
      return { late, stressDelta, cashChange: 0, note };
    }

    const breakdown = Math.random() < 0.2;
    const traffic = !breakdown && Math.random() < 0.3;
    let late = false;
    let stressDelta = 2;
    let cashChange = 0;
    let note = 'You glide through neon streets in your beater car.';

    if (breakdown) {
      cashChange = -randRange(35, 65);
      stressDelta += 14;
      late = Math.random() < 0.4;
      note = 'Car coughs to a stop. Repair eats cash and time.';
    } else if (traffic) {
      stressDelta += 8;
      late = Math.random() < 0.25;
      note = 'Gridlock. Horns blare. Pulse rises.';
    }

    return { late, stressDelta, cashChange, note };
  };

  const handleShift = () => {
    setState((prev) => {
      if (prev.energy < 15) {
        return { ...prev, log: pushLog('Too exhausted to work. Crash at home first.', prev.log) };
      }

      if (prev.stress > 90) {
        return { ...prev, log: pushLog('You freeze at the door. Stress is maxed.', prev.log) };
      }

      const job = JOBS.find((j) => j.id === prev.jobId) ?? JOBS[0];
      const jobIndex = JOBS.findIndex((j) => j.id === job.id);

      const owned = prev.ownedUpgrades;
      let energyCost = 22 + jobIndex * 2;
      let stressGain = 14 + jobIndex * 2;
      let wage = randRange(job.payRange[0], job.payRange[1]);
      let tips = randRange(12, 38);
      let xpGain = 22 + jobIndex * 6;
      let cashChange = 0;
      let log = prev.log;

      if (owned.includes('sneakers')) energyCost -= 6;
      if (owned.includes('headphones')) stressGain -= 6;

    const commuteResult = resolveCommute(commute, owned);
      stressGain += commuteResult.stressDelta;
      cashChange += commuteResult.cashChange;
      log = pushLog(commuteResult.note, log);

      if (commuteResult.late) {
        tips = 0;
        wage = Math.floor(wage * 0.85);
        xpGain = Math.max(8, xpGain - 4);
        log = pushLog('Late to the shift. No tips this time.', log);
      }

      let notes: string[] = [];

      if (Math.random() < 0.4) {
        const event = SHIFT_EVENTS[randRange(0, SHIFT_EVENTS.length - 1)];
        const outcome: MutableOutcome = {
          wage,
          tips,
          energyCost,
          stressGain,
          xpGain,
          cashChange,
          notes: [],
        };
        event.apply(outcome);
        wage = Math.max(0, outcome.wage);
        tips = Math.max(0, outcome.tips);
        energyCost = Math.max(8, outcome.energyCost);
        stressGain = Math.max(0, outcome.stressGain);
        xpGain = Math.max(10, outcome.xpGain);
        cashChange = outcome.cashChange;
        notes = outcome.notes;
        log = pushLog(`${event.title}: ${event.text}`, log);
      }

      const earnings = wage + tips + cashChange;
      const energy = clamp(prev.energy - energyCost, 0, 100);
      const stress = clamp(prev.stress + stressGain, 0, 120);
      const xp = prev.xp + xpGain;
      const rentProgress = prev.rentProgress + 14 - (owned.includes('planner') ? 3 : 0);

      let updatedLog = pushLog(
        `Shift finished as ${job.title}: +$${earnings} ($${wage} wage, $${Math.max(
          tips,
          0
        )} tips)`,
        log
      );

      notes.forEach((note) => {
        updatedLog = pushLog(note, updatedLog);
      });

      const rentResult = applyRentPressure(
        prev.cash + earnings,
        rentProgress,
        prev.jobId,
        updatedLog
      );

      return {
        ...prev,
        cash: rentResult.cash,
        energy,
        stress,
        xp,
        rentProgress: rentResult.rentProgress,
        jobId: rentResult.jobId,
        day: prev.day + 1,
        log: rentResult.log,
      };
    });
  };

  const handlePurchase = (upgrade: Upgrade) => {
    setState((prev) => {
      if (prev.ownedUpgrades.includes(upgrade.id)) {
        return { ...prev, log: pushLog(`${upgrade.name} already installed.`, prev.log) };
      }

      if (prev.cash < upgrade.cost) {
        return { ...prev, log: pushLog(`Need $${upgrade.cost} for ${upgrade.name}.`, prev.log) };
      }

      return {
        ...prev,
        cash: prev.cash - upgrade.cost,
        ownedUpgrades: [...prev.ownedUpgrades, upgrade.id],
        log: pushLog(`Bought ${upgrade.name}. ${upgrade.description}`, prev.log),
      };
    });
  };

  const handlePromotion = (jobId: string) => {
    setState((prev) => {
      const target = JOBS.find((j) => j.id === jobId);
      if (!target) return prev;

      const currentIndex = JOBS.findIndex((j) => j.id === prev.jobId);
      const targetIndex = JOBS.findIndex((j) => j.id === jobId);

      if (targetIndex <= currentIndex) {
        return { ...prev, log: pushLog('You already wear that name tag.', prev.log) };
      }

      if (target.requires && !prev.ownedUpgrades.includes(target.requires)) {
        return { ...prev, log: pushLog('Need the required training first.', prev.log) };
      }

      if (prev.xp < target.xpReq) {
        return { ...prev, log: pushLog('Not enough XP to impress management yet.', prev.log) };
      }

      if (target.entryFee && prev.cash < target.entryFee) {
        return { ...prev, log: pushLog(`Need $${target.entryFee} to onboard.`, prev.log) };
      }

      const cash = prev.cash - (target.entryFee ?? 0);
      return {
        ...prev,
        jobId: target.id,
        cash,
        log: pushLog(`Promoted to ${target.title}!`, prev.log),
      };
    });
  };

  const resetProgress = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY);
    }
    setState({ ...BASE_STATE });
    setCommute('bus');
  };

  const rentPercent = Math.min(100, Math.max(0, state.rentProgress));

  return (
    <div className="app-shell relative min-h-screen pb-16 text-slate-100">
      <div className="bg-grid-overlay" />
      <div className="orb orb-pink" />
      <div className="orb orb-blue" />
      <div className="orb orb-amber" />

      <header className="glass-panel hero-panel relative mb-8 p-6 md:p-8">
        <div className="hero-radial" />
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <span className="hud-pill">Neon Noir Campaign</span>
              <span className="hud-pill alt">Night Shift</span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="font-display text-4xl font-semibold text-white sm:text-5xl">
                Pour Decisions
              </h1>
              <span className="badge-live">Build 2.0</span>
              <span className="badge-soft">Autosave Ready</span>
            </div>
            <p className="max-w-2xl text-sm text-slate-300">
              Grind through neon nights, balance energy and stress, and climb from glass collector to bar
              legend.
            </p>
            <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
              <span className="stat-pill">Current role: {currentJob.title}</span>
              <span className="stat-pill">Rent: ${currentJob.rent}</span>
              <span className={`stat-pill ${commute === 'car' ? 'stat-pill-strong' : ''}`}>
                Commute: {commute === 'car' ? 'Car' : 'Bus'}
              </span>
            </div>
          </div>
          <div className="w-full md:w-auto">
            <div className="hero-hud grid min-w-[280px] grid-cols-2 gap-3">
              <div className="hud-card">
                <p className="hud-label">Cash</p>
                <p className="hud-value">${state.cash}</p>
                <span className="hud-sub">Wallet</span>
              </div>
              <div className="hud-card">
                <p className="hud-label">XP</p>
                <p className="hud-value">{state.xp}</p>
                <span className="hud-sub">Career</span>
              </div>
              <div className="hud-card">
                <p className="hud-label">Day</p>
                <p className="hud-value">{state.day}</p>
                <span className="hud-sub">Campaign</span>
              </div>
              <div className="hud-card">
                <p className="hud-label">Rent Meter</p>
                <div className="hud-gauge">
                  <span>{rentPercent.toFixed(0)}%</span>
                  <div className="hud-gauge-track">
                    <div className="hud-gauge-fill" style={{ width: `${rentPercent}%` }} />
                  </div>
                </div>
                <span className="hud-sub">${currentJob.rent} due on fill</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel holo-card p-6 md:p-7">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Vitals</p>
                <h3 className="panel-title">Status & Actions</h3>
              </div>
              <div
                className={`panel-chip ${
                  state.energy < 15 || state.stress > 90 ? 'chip-warning' : 'chip-ready'
                }`}
              >
                {state.energy < 15
                  ? 'Rest to regain energy'
                  : state.stress > 90
                    ? 'Stress too high'
                    : 'Shift ready'}
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div className="stat-meter">
                <div className="flex items-center justify-between text-sm text-slate-200">
                  <span>Energy</span>
                  <span>{state.energy}%</span>
                </div>
                <div className="meter-track">
                  <div className="meter-fill energy" style={{ width: `${state.energy}%` }} />
                </div>
                <p className="meter-caption">Fuel for the grind. Sneakers and rest make it last.</p>
              </div>
              <div className="stat-meter">
                <div className="flex items-center justify-between text-sm text-slate-200">
                  <span>Stress</span>
                  <span>{Math.round(state.stress)}%</span>
                </div>
                <div className="meter-track">
                  <div
                    className="meter-fill stress"
                    style={{ width: `${Math.min(100, Math.round(state.stress))}%` }}
                  />
                </div>
                <p className="meter-caption">
                  Hit 90% and you cannot start a shift. Headphones help.
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
              <div className="holo-subcard">
                <div className="flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Commute Loadout</p>
                  <span className="text-[11px] text-slate-400">Choose your risk profile</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {(['bus', 'car'] as CommuteMode[]).map((mode) => {
                    const locked = mode === 'car' && !hasUpgrade('car');
                    return (
                      <button
                        key={mode}
                        onClick={() => setCommute(mode)}
                        disabled={locked}
                        className={`commute-btn ${commute === mode ? 'active' : ''} ${
                          locked ? 'locked' : ''
                        }`}
                      >
                        {mode === 'bus' ? 'Bus // Cheap' : 'Car // Fast'}
                      </button>
                    );
                  })}
                </div>
                <p className="mt-2 text-xs text-slate-400">
                  Bus: free but often late. Car: faster with repair risks. Lateness wipes tips.
                </p>
              </div>
              <div className="holo-subcard flex flex-wrap items-center justify-end gap-3">
                <button
                  onClick={handleShift}
                  className="action-btn primary"
                  disabled={state.energy < 15 || state.stress > 90}
                >
                  Start Shift
                </button>
                <button onClick={handleRest} className="action-btn ghost">
                  Crash at Home
                </button>
                <button onClick={resetProgress} className="action-btn secondary">
                  Reset Save
                </button>
              </div>
            </div>
          </div>

          <div className="glass-panel holo-card p-6 md:p-7">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Pressure</p>
                <h3 className="panel-title">Rent Threat</h3>
              </div>
              <div className="panel-chip subtle">${currentJob.rent} due on fill</div>
            </div>
            <p className="text-sm text-slate-300">
              Rent climbs as your title improves. Keep the bar below 100% to avoid eviction.
            </p>
            <div className="mt-4 progress-block">
              <div className="progress-track glow">
                <div className="progress-fill" style={{ width: `${rentPercent}%` }} />
              </div>
              <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                <span>Rent Meter</span>
                <span>{rentPercent.toFixed(0)}%</span>
              </div>
            </div>
          </div>

          <div className="glass-panel holo-card p-6 md:p-7">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Career</p>
                <h3 className="panel-title">Climb the Night</h3>
              </div>
              <p className="text-xs text-slate-400">XP unlocks roles</p>
            </div>
            <div className="mt-4 space-y-3">
              {JOBS.map((job) => {
                const isCurrent = job.id === state.jobId;
                const reachable = state.xp >= job.xpReq;
                const lockedQualification = job.requires && !hasUpgrade(job.requires);
                const affordEntry = job.entryFee ? state.cash >= job.entryFee : true;
                const xpPercent =
                  job.xpReq === 0 ? 100 : clamp(Math.round((state.xp / job.xpReq) * 100), 0, 140);
                return (
                  <div
                    key={job.id}
                    className={`career-card ${isCurrent ? 'current' : ''} ${
                      !reachable ? 'dimmed' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="space-y-1">
                        <p className="text-sm font-semibold text-white">{job.title}</p>
                        <p className="text-[11px] text-slate-400">{job.flavor}</p>
                        <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
                          <span className="chip">Pay ${job.payRange[0]}-${job.payRange[1]}</span>
                          <span className="chip">Rent ${job.rent}</span>
                          <span className="chip">XP {job.xpReq}</span>
                          {job.entryFee ? <span className="chip">Entry ${job.entryFee}</span> : null}
                          {job.requires ? <span className="chip warn">Needs Course</span> : null}
                        </div>
                        <div className="xp-track">
                          <div className="xp-fill" style={{ width: `${xpPercent}%` }} />
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <button
                          onClick={() => handlePromotion(job.id)}
                          disabled={
                            isCurrent ||
                            !reachable ||
                            lockedQualification ||
                            !affordEntry ||
                            JOBS.findIndex((j) => j.id === job.id) <=
                              JOBS.findIndex((j) => j.id === state.jobId)
                          }
                          className={`promote-btn ${isCurrent ? 'active' : ''}`}
                        >
                          {isCurrent ? 'Current' : 'Promote'}
                        </button>
                        {lockedQualification && (
                          <p className="text-[10px] text-amber-300">Requires Mixology Course</p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-panel holo-card p-6 md:p-7">
            <div className="panel-heading">
              <div>
                <p className="panel-kicker">Upgrades</p>
                <h3 className="panel-title">Dark Web Shop</h3>
              </div>
              <p className="text-xs text-slate-400">Permanent boosts</p>
            </div>
            <div className="mt-4 space-y-3">
              {UPGRADES.map((upgrade) => {
                const owned = state.ownedUpgrades.includes(upgrade.id);
                const affordable = state.cash >= upgrade.cost;
                return (
                  <div key={upgrade.id} className="upgrade-card">
                    <div>
                      <p className="text-sm font-semibold text-white">{upgrade.name}</p>
                      <p className="text-[11px] text-slate-400">{upgrade.description}</p>
                      <p className="text-[11px] text-slate-500">${upgrade.cost}</p>
                    </div>
                    <button
                      onClick={() => handlePurchase(upgrade)}
                      disabled={owned || !affordable}
                      className={`buy-btn ${owned ? 'owned' : ''}`}
                    >
                      {owned ? 'Owned' : 'Buy'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="glass-panel holo-card p-6 md:p-7">
            <div className="panel-heading">
              <h3 className="panel-title">Shift Feed</h3>
              <p className="text-xs text-slate-400">Latest events</p>
            </div>
            <div className="mt-4 space-y-2">
              {state.log.map((entry, idx) => (
                <div key={`${entry}-${idx}`} className="log-entry">
                  <span className="log-bullet" />
                  <p className="text-sm text-slate-200">{entry}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
