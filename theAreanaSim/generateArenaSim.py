"""
Arena Simulator backend.

This module produces ``simulation.json`` so the static viewer can play
through each day. The simulation supports inventories, per-day event
batches, and configurable flavor pulled from ``arena_events.json``.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "arena_events.json"
NAMES_FILE = ROOT / "tribute_names.txt"
MAX_INVENTORY_SIZE = 4


@dataclass
class Tribute:
    """Represents a single competitor inside the arena."""

    name: str
    alive: bool = True
    kills: int = 0
    inventory: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """JSON-friendly payload for the frontend."""
        return asdict(self)


@dataclass
class SimulationConfig:
    """
    Container for every tweakable setting.

    Attributes
    ----------
    lethal_event_chance:
        Probability (0-1) that a random event becomes lethal.
    inventory_event_chance:
        Probability (0-1) that a tribute with gear triggers an
        inventory-related event before the lethal roll is considered.
    min_events_per_day / max_events_per_day:
        Baseline range for how many events happen on a typical day.
    bloodbath_event_range:
        Range of events that fires on Day 1 before everyone scatters.
    bloodbath_lethal_bonus:
        Extra lethal chance added on Day 1 to emulate a Cornucopia rush.
    inventory_items:
        Pool of strings assigned to tributes at the start.
    lethal_events / non_lethal_events / inventory_events / loot_events:
        Template pools. ``{person}``, ``{killer}``, ``{victim}``, and
        ``{item}`` placeholders are supported.
    special_item_events:
        Optional list of custom item hooks where a specific piece of
        gear unlocks custom flavor text (and can optionally be consumed)
        when chosen.
    special_item_event_chance:
        Probability (0-1) that a tribute with a qualifying item triggers
        one of those bespoke events before any other inventory logic.
    loot_event_chance:
        Chance that an event lets a tribute discover new gear.
    victory_template:
        Message appended once a single tribute remains.
    seed:
        Optional deterministic seed.
    """

    lethal_event_chance: float = 0.55
    inventory_event_chance: float = 0.35
    loot_event_chance: float = 0.25
    min_events_per_day: int = 2
    max_events_per_day: int = 4
    bloodbath_event_range: Sequence[int] = (6, 9)
    bloodbath_lethal_bonus: float = 0.25
    inventory_items: Sequence[str] = field(
        default_factory=lambda: [
            "medkit",
            "snare trap",
            "flare",
            "camouflage cloak",
            "ration pack",
            "throwing knife",
        ]
    )
    lethal_events: Sequence[str] = field(
        default_factory=lambda: [
            "{killer} ambushes {victim} near the river.",
            "{killer} traps {victim} in a ravine.",
            "{killer} outmatches {victim} after a tense duel.",
            "{killer} sabotages {victim}'s shelter overnight.",
        ]
    )
    non_lethal_events: Sequence[str] = field(
        default_factory=lambda: [
            "{person} scouts the cornucopia from afar.",
            "{person} gathers herbs and hopes they are edible.",
            "{person} reinforces a hidden bunker.",
            "{person} shares stories with the breeze—silence answers back.",
            "{person} stalks distant footsteps but loses the trail.",
        ]
    )
    inventory_events: Sequence[str] = field(
        default_factory=lambda: [
            "{person} sets a {item} and waits patiently.",
            "{person} patches wounds with a trusty {item}.",
            "{person} flashes a {item} to ward off pursuers.",
            "{person} retools a {item} into something even more dangerous.",
        ]
    )
    loot_events: Sequence[str] = field(
        default_factory=lambda: [
            "{person} scavenges a {item} from the Cornucopia wreckage.",
            "{person} digs up a buried stash and pockets a {item}.",
            "{person} barters quietly for a {item}.",
            "{person} slips a {item} into their pack unnoticed.",
        ]
    )
    special_item_events: Sequence[Dict[str, object]] = field(default_factory=list)
    special_item_event_chance: float = 0.4
    victory_template: str = "{name} emerges victorious with {kills} elimination(s)!"
    seed: Optional[int] = None

    def rng(self) -> random.Random:
        """Return an RNG honoring the configured seed."""
        return random.Random(self.seed)

    @classmethod
    def from_mapping(cls, data: Dict[str, object]) -> "SimulationConfig":
        """Create a config from a JSON-compatible dictionary."""
        default = cls()
        return cls(
            lethal_event_chance=float(data.get("lethal_event_chance", default.lethal_event_chance)),
            inventory_event_chance=float(
                data.get("inventory_event_chance", default.inventory_event_chance)
            ),
            loot_event_chance=float(data.get("loot_event_chance", default.loot_event_chance)),
            min_events_per_day=int(data.get("min_events_per_day", default.min_events_per_day)),
            max_events_per_day=int(data.get("max_events_per_day", default.max_events_per_day)),
            bloodbath_event_range=tuple(
                data.get("bloodbath_event_range", list(default.bloodbath_event_range))
            ),
            bloodbath_lethal_bonus=float(
                data.get("bloodbath_lethal_bonus", default.bloodbath_lethal_bonus)
            ),
            inventory_items=data.get("inventory_items", list(default.inventory_items)),
            lethal_events=data.get("lethal_events", list(default.lethal_events)),
            non_lethal_events=data.get("non_lethal_events", list(default.non_lethal_events)),
            inventory_events=data.get("inventory_events", list(default.inventory_events)),
            loot_events=data.get("loot_events", list(default.loot_events)),
            special_item_events=data.get(
                "special_item_events", list(default.special_item_events)
            ),
            special_item_event_chance=float(
                data.get("special_item_event_chance", default.special_item_event_chance)
            ),
            victory_template=data.get("victory_template", default.victory_template),
            seed=data.get("seed"),
        )


DEFAULT_TRIBUTE_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Evelyn",
    "Frank",
    "George",
    "Hannah",
]


def build_special_item_map(config: SimulationConfig) -> Dict[str, Dict[str, object]]:
    """Normalize the configured special item events for quick lookups."""

    mapping: Dict[str, Dict[str, object]] = {}
    for entry in config.special_item_events:
        if not isinstance(entry, dict):
            continue
        item = entry.get("item")
        events = entry.get("events") or []
        if not item or not events:
            continue
        parsed_events: List[Dict[str, object]] = []
        for event in events:
            if isinstance(event, str):
                parsed_events.append({"text": event, "lethal": False})
            elif isinstance(event, dict) and "text" in event:
                parsed_events.append(
                    {
                        "text": str(event["text"]),
                        "lethal": bool(event.get("lethal", False)),
                    }
                )
        if not parsed_events:
            continue
        mapping[str(item)] = {
            "events": parsed_events,
            "consumes": bool(entry.get("consumes", False)),
        }
    return mapping


def load_names(source: Optional[Path] = None) -> List[str]:
    """Read names from ``tribute_names.txt`` if it exists."""

    path = source or NAMES_FILE
    if path.is_file():
        names = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if names:
            return names
    return DEFAULT_TRIBUTE_NAMES.copy()


def load_simulation_config(path: Optional[Path] = None) -> SimulationConfig:
    """
    Load ``arena_events.json`` if present.

    The file can override probabilities, templates, and inventory lists
    without touching this Python file.
    """

    target = path or CONFIG_FILE
    if target.is_file():
        data = json.loads(target.read_text(encoding="utf-8"))
        return SimulationConfig.from_mapping(data)
    return SimulationConfig()


def assign_inventory(rng: random.Random, items: Sequence[str]) -> List[str]:
    """
    Give each tribute a small grab bag of gear.

    Each tribute receives between 0 and 2 items (with replacement) so
    duplicates are possible. The UI never reveals inventory directly,
    but inventory-driven events will reference the chosen gear.
    """

    if not items:
        return []
    count = rng.randint(0, 2)
    return [rng.choice(items) for _ in range(count)]


def determine_event_count(
    day_number: int,
    alive_count: int,
    total_tributes: int,
    config: SimulationConfig,
    rng: random.Random,
) -> int:
    """
    Decide how many events should run during the current day.

    Day 1 (the bloodbath) uses its own, higher range. Afterwards the
    count scales with how many tributes remain so the action tapers off
    organically instead of relying on a fixed min/max.
    """

    if day_number == 1 and config.bloodbath_event_range:
        values = list(config.bloodbath_event_range)
        if len(values) == 1:
            values *= 2
        low, high = values[0], values[1]
        low = max(config.min_events_per_day, int(low))
        high = max(low, int(high))
        return rng.randint(low, high)

    span = max(0, config.max_events_per_day - config.min_events_per_day)
    density = alive_count / max(1, total_tributes)
    base = config.min_events_per_day + max(0, round(span * density))
    jitter = rng.choice([-1, 0, 0, 1]) if span else 0
    target = base + jitter
    soft_cap = min(8, alive_count)
    target = min(target, soft_cap)
    return max(config.min_events_per_day, min(target, alive_count))


def run_simulation(
    names: Sequence[str],
    config: Optional[SimulationConfig] = None,
) -> Dict[str, object]:
    """
    Execute the arena simulation and return a JSON-friendly payload.

    The result groups events by day so the UI can reveal them in two
    steps (events → fallen tributes) for added suspense.
    """

    config = config or SimulationConfig()
    rng = config.rng()

    tributes = [
        Tribute(name=n, inventory=assign_inventory(rng, config.inventory_items)) for n in names
    ]
    total_tributes = len(tributes)
    special_item_map = build_special_item_map(config)

    days: List[Dict[str, object]] = []
    day_counter = 0

    def alive() -> List[Tribute]:
        return [t for t in tributes if t.alive]

    while len(alive()) > 1:
        day_counter += 1
        events_today: List[Dict[str, object]] = []
        fallen_today: List[str] = []
        daily_target = determine_event_count(
            day_counter,
            len(alive()),
            total_tributes,
            config,
            rng,
        )

        for _ in range(daily_target):
            living = alive()
            if not living:
                break
            actor = rng.choice(living)
            event = generate_event(
                actor,
                tributes,
                config,
                day_counter,
                special_item_map,
                rng,
            )
            if not event:
                continue
            events_today.append(event)
            if event["type"] == "lethal":
                victim_name = event.get("meta", {}).get("victim")
                if victim_name and victim_name not in fallen_today:
                    fallen_today.append(victim_name)
            if len(alive()) <= 1:
                break

        days.append(
            {
                "number": day_counter,
                "bloodbath": day_counter == 1,
                "events": events_today,
                "fallen": fallen_today,
                "survivors": [t.name for t in alive()],
            }
        )

    winner = next((t for t in tributes if t.alive), None)
    if winner and days:
        days[-1]["events"].append(
            {
                "type": "victory",
                "text": config.victory_template.format(name=winner.name, kills=winner.kills),
                "meta": {"winner": winner.name, "kills": winner.kills},
            }
        )

    return {
        "tributes": [t.to_dict() for t in tributes],
        "days": days,
        "winner": winner.name if winner else None,
    }


def generate_event(
    actor: Tribute,
    tributes: Sequence[Tribute],
    config: SimulationConfig,
    day_number: int,
    special_item_map: Dict[str, Dict[str, object]],
    rng: random.Random,
) -> Optional[Dict[str, object]]:
    """Produce one event entry and mutate tribute state when needed."""

    living = [t for t in tributes if t.alive]
    can_attempt_lethal = len(living) > 1

    special_candidates = [item for item in actor.inventory if item in special_item_map]
    if special_candidates and rng.random() < config.special_item_event_chance:
        chosen = rng.choice(special_candidates)
        payload = special_item_map[chosen]
        templates = payload.get("events", [])
        if templates:
            template = rng.choice(templates)
            consumes = payload.get("consumes", False)
            if consumes:
                actor.inventory.remove(chosen)
            lethal_event = bool(template.get("lethal"))
            victim_name: Optional[str] = None
            if lethal_event:
                candidates = [t for t in living if t is not actor]
                if candidates:
                    victim = rng.choice(candidates)
                    victim.alive = False
                    actor.kills += 1
                    victim_name = victim.name
                else:
                    lethal_event = False
            replacements = {"person": actor.name, "item": chosen}
            if victim_name:
                replacements["victim"] = victim_name
            text = template["text"].format(**replacements)
            meta = {
                "person": actor.name,
                "item": chosen,
                "consumed": consumes,
            }
            if victim_name:
                meta["victim"] = victim_name
            return {
                "type": "item-special lethal" if victim_name else "item-special",
                "text": text,
                "meta": meta,
            }

    can_loot = (
        bool(config.loot_events)
        and bool(config.inventory_items)
        and len(actor.inventory) < MAX_INVENTORY_SIZE
    )
    if can_loot and rng.random() < config.loot_event_chance:
        item = rng.choice(config.inventory_items)
        actor.inventory.append(item)
        template = rng.choice(config.loot_events)
        return {
            "type": "loot",
            "text": template.format(person=actor.name, item=item),
            "meta": {"person": actor.name, "item": item},
        }

    if actor.inventory and config.inventory_events:
        if rng.random() < config.inventory_event_chance:
            item = rng.choice(actor.inventory)
            template = rng.choice(config.inventory_events)
            return {
                "type": "inventory",
                "text": template.format(person=actor.name, item=item),
                "meta": {"person": actor.name, "item": item},
            }

    lethal_chance = config.lethal_event_chance
    if day_number == 1:
        lethal_chance = min(1.0, lethal_chance + config.bloodbath_lethal_bonus)

    lethal_roll = can_attempt_lethal and rng.random() < lethal_chance
    if lethal_roll and len(living) > 1:
        victim = rng.choice([t for t in living if t is not actor])
        victim.alive = False
        actor.kills += 1
        template = rng.choice(config.lethal_events)
        return {
            "type": "lethal",
            "text": template.format(killer=actor.name, victim=victim.name),
            "meta": {"killer": actor.name, "victim": victim.name},
        }

    template = rng.choice(config.non_lethal_events or ["{person} passes the time in silence."])
    return {
        "type": "non-lethal",
        "text": template.format(person=actor.name),
        "meta": {"person": actor.name},
    }


def export_simulation(payload: Dict[str, object], target: Optional[Path] = None) -> Path:
    """Write ``simulation.json`` next to this file."""

    output_path = target or ROOT / "simulation.json"
    output_path.write_text(json.dumps(payload, indent=4), encoding="utf-8")
    return output_path


def main(names: Optional[Iterable[str]] = None) -> None:
    """
    CLI entry point.

    - Names default to ``tribute_names.txt`` or the built-in roster.
    - Event pools / odds default to ``arena_events.json`` when present.
    """

    roster = list(names) if names else load_names()
    config = load_simulation_config()
    results = run_simulation(roster, config)
    output = export_simulation(results)
    print(f"Generated {output.name} with {len(results['days'])} day(s).")


if __name__ == "__main__":
    main()
