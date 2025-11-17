"""
Arena Simulator backend.

This module produces ``simulation.json`` so the static viewer can play
through each day. The simulation supports inventories, per-day event
batches, and configurable flavor pulled from ``arena_events.json``.
"""

from __future__ import annotations

import json
import random
import re
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent
CONFIG_FILE = ROOT / "arena_events.json"
NAMES_FILE = ROOT / "tribute_names.txt"
MAX_INVENTORY_SIZE = 10
MAX_START_ITEMS = 0
PLACEHOLDER_PATTERN = re.compile(r"{(\w+)}")


def extract_placeholders(text: str) -> List[str]:
    """Return every ``{placeholder}`` token found inside ``text``."""

    if not text:
        return []
    return PLACEHOLDER_PATTERN.findall(text)


def infer_additional_roles(text: str, base_keys: Sequence[str]) -> List[str]:
    """Find placeholder names that should be filled with other tributes."""

    roles: List[str] = []
    reserved = set(base_keys)
    for key in extract_placeholders(text):
        if key in reserved:
            continue
        if key not in roles:
            roles.append(key)
    return roles


def infer_victim_roles(text: str) -> List[str]:
    """Return victim placeholder names ordered by appearance."""

    roles: List[str] = []
    for key in extract_placeholders(text):
        if key.startswith("victim") and key not in roles:
            roles.append(key)
    return roles


def ensure_victim_keys(base_keys: Sequence[str], count: int) -> List[str]:
    """Guarantee a list of victim placeholder names of ``count`` length."""

    keys = list(base_keys)
    candidates = ["victim"] + [f"victim{i}" for i in range(2, count + 5)]
    for candidate in candidates:
        if len(keys) >= count:
            break
        if candidate not in keys:
            keys.append(candidate)
    return keys[:count]


class _SafeFormatDict(dict):
    """Gracefully leave unknown placeholders untouched."""

    def __missing__(self, key: str) -> str:  # pragma: no cover - trivial
        return "{" + key + "}"


def format_template_text(template: str, replacements: Dict[str, str]) -> str:
    """Fill ``template`` without KeyErrors when placeholders are missing."""

    return template.format_map(_SafeFormatDict(replacements))


def normalize_special_event(
    event: object,
    default_consumes: bool,
) -> Optional[Dict[str, object]]:
    """Convert a raw special-event entry into a structured payload."""

    if isinstance(event, str):
        text = str(event)
        victim_roles = infer_victim_roles(text)
        victim_count = len(victim_roles)
        return {
            "text": text,
            "lethal": False,
            "victim_keys": ensure_victim_keys(victim_roles, victim_count),
            "victim_count": victim_count,
            "consumes": default_consumes,
        }

    if isinstance(event, dict) and "text" in event:
        text = str(event["text"])
        lethal = bool(event.get("lethal", False))

        explicit = event.get("victim_count", event.get("victims"))
        victim_roles = infer_victim_roles(text)
        victim_count: int
        if explicit is None:
            victim_count = len(victim_roles)
        else:
            try:
                victim_count = max(0, int(explicit))
            except (TypeError, ValueError):
                victim_count = len(victim_roles)
        if lethal and victim_count == 0:
            victim_count = max(1, len(victim_roles) or 1)

        consumes = event.get("consumes")
        consumes_flag = default_consumes if consumes is None else bool(consumes)

        return {
            "text": text,
            "lethal": lethal,
            "victim_keys": ensure_victim_keys(victim_roles, victim_count),
            "victim_count": victim_count,
            "consumes": consumes_flag,
        }

    return None


def normalize_non_lethal_entry(entry: object) -> Dict[str, object]:
    """Return text plus extra role placeholders for a non-lethal event."""

    base_keys = {"person"}
    if isinstance(entry, dict) and "text" in entry:
        text = str(entry["text"])
        raw_roles = entry.get("extra_roles") or entry.get("extraRoles")
        if isinstance(raw_roles, list):
            roles = [str(role) for role in raw_roles if role not in base_keys]
        else:
            roles = infer_additional_roles(text, base_keys)
    else:
        text = str(entry)
        roles = infer_additional_roles(text, base_keys)
    return {"text": text, "roles": roles}


def normalize_lethal_entry(entry: object) -> Dict[str, object]:
    """Return text plus victim metadata for a lethal template."""

    if isinstance(entry, dict) and "text" in entry:
        text = str(entry["text"])
        explicit = entry.get("victim_count", entry.get("victims"))
        victim_roles = infer_victim_roles(text)
        victim_count: int
        if explicit is None:
            victim_count = len(victim_roles) or 1
        else:
            try:
                victim_count = max(1, int(explicit))
            except (TypeError, ValueError):
                victim_count = len(victim_roles) or 1
    else:
        text = str(entry)
        victim_roles = infer_victim_roles(text)
        victim_count = len(victim_roles) or 1
    keys = ensure_victim_keys(victim_roles, victim_count)
    return {"text": text, "victim_count": victim_count, "victim_keys": keys}


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
    item_loot_text:
        Optional mapping of item name -> custom loot templates for that
        item. Falls back to ``loot_events`` when missing.
    special_item_events:
        Optional list of custom item hooks where a specific piece of
        gear unlocks custom flavor text (and can optionally be consumed)
        when chosen.
    special_item_event_chance:
        Probability (0-1) that a tribute with a qualifying item triggers
        one of those bespoke events before any other inventory logic.
    loot_event_chance:
        Chance that an event lets a tribute discover new gear.
    target_min_days / target_max_days:
        Desired duration bounds (in days) for a full simulation run.
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
    item_loot_text: Dict[str, Sequence[str]] = field(default_factory=dict)
    special_item_events: Sequence[Dict[str, object]] = field(default_factory=list)
    special_item_event_chance: float = 0.4
    target_min_days: int = 7
    target_max_days: int = 12
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
            item_loot_text=data.get("item_loot_text", dict(default.item_loot_text)),
            special_item_events=data.get(
                "special_item_events", list(default.special_item_events)
            ),
            special_item_event_chance=float(
                data.get("special_item_event_chance", default.special_item_event_chance)
            ),
            target_min_days=int(data.get("target_min_days", default.target_min_days)),
            target_max_days=int(data.get("target_max_days", default.target_max_days)),
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


def clamp(value: float, low: float, high: float) -> float:
    """Return ``value`` constrained between ``low`` and ``high``."""

    return max(low, min(high, value))


def determine_desired_total_days(total_tributes: int, config: SimulationConfig) -> int:
    """Scale the intended campaign length to remain within the configured window."""

    min_days = max(1, config.target_min_days)
    max_days = max(min_days, config.target_max_days)
    if total_tributes <= 1 or min_days == max_days:
        return min_days
    ratio = (total_tributes - 2) / 22 if total_tributes > 2 else 0.0
    ratio = clamp(ratio, 0.0, 1.0)
    span = max_days - min_days
    return int(round(min_days + span * ratio))


def required_events_for_progress(
    day_number: int,
    alive_count: int,
    desired_days: int,
    config: SimulationConfig,
) -> int:
    """Approximate how many events are needed to stay on pace for the target day count."""

    if alive_count <= 1:
        return 0
    remaining_days = max(1, desired_days - (day_number - 1))
    needed_eliminations = max(0, alive_count - 1)
    target_kills = max(1, math.ceil(needed_eliminations / remaining_days))
    base_chance = config.lethal_event_chance
    if day_number == 1:
        base_chance = min(1.0, base_chance + config.bloodbath_lethal_bonus)
    effective_chance = clamp(base_chance, 0.1, 0.95)
    return math.ceil(target_kills / effective_chance)


def compute_death_pressure(
    alive_count: int,
    day_number: int,
    daily_events: int,
    desired_days: int,
    config: SimulationConfig,
) -> float:
    """Return a multiplier applied to lethal odds to keep runs within 7-12 days."""

    if alive_count <= 1 or daily_events <= 0:
        return 1.0
    remaining_days = max(1, desired_days - (day_number - 1))
    needed_eliminations = max(0, alive_count - 1)
    target_kills = needed_eliminations / remaining_days
    base_chance = config.lethal_event_chance
    if day_number == 1:
        base_chance = min(1.0, base_chance + config.bloodbath_lethal_bonus)
    expected_kills = daily_events * clamp(base_chance, 0.05, 0.95)
    pressure = target_kills / max(expected_kills, 0.1)
    late_game_bonus = 1.0 + max(0, day_number - 10) * 0.5
    return clamp(pressure * late_game_bonus, 0.6, 4.0)


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
        default_consumes = bool(entry.get("consumes", False))
        parsed_events: List[Dict[str, object]] = []
        for event in events:
            normalized = normalize_special_event(event, default_consumes)
            if normalized:
                parsed_events.append(normalized)
        if not parsed_events:
            continue
        mapping[str(item)] = {
            "events": parsed_events,
            "consumes": default_consumes,
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
    count = rng.randint(0, MAX_START_ITEMS)
    return [rng.choice(items) for _ in range(count)]


def determine_event_count(
    day_number: int,
    alive_count: int,
    total_tributes: int,
    config: SimulationConfig,
    desired_days: int,
    rng: random.Random,
) -> int:
    """
    Decide how many events should run during the current day.

    Day 1 (the bloodbath) uses its own, higher range. Afterwards the
    count scales with how many tributes remain so the action tapers off
    organically instead of relying on a fixed min/max.
    """

    kill_pressure_events = required_events_for_progress(
        day_number,
        alive_count,
        desired_days,
        config,
    )

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
    target = max(target, kill_pressure_events)
    soft_cap = max(min(8, alive_count), kill_pressure_events)
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
    desired_days = determine_desired_total_days(total_tributes, config)

    days: List[Dict[str, object]] = []
    day_counter = 0

    def alive() -> List[Tribute]:
        return [t for t in tributes if t.alive]

    while len(alive()) > 1:
        day_counter += 1
        events_today: List[Dict[str, object]] = []
        fallen_today: List[str] = []
        current_alive = len(alive())
        daily_target = determine_event_count(
            day_counter,
            current_alive,
            total_tributes,
            config,
            desired_days,
            rng,
        )
        death_pressure = compute_death_pressure(
            current_alive,
            day_counter,
            daily_target,
            desired_days,
            config,
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
                death_pressure,
                rng,
            )
            if not event:
                continue
            events_today.append(event)
            if event["type"] in {"lethal", "item-special lethal"}:
                meta = event.get("meta", {}) or {}
                victims = meta.get("victims")
                if isinstance(victims, list):
                    for name in victims:
                        if name and name not in fallen_today:
                            fallen_today.append(name)
                else:
                    victim_name = meta.get("victim")
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
    death_pressure: float,
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
            consumes = template.get("consumes")
            consumes_flag = payload.get("consumes", False) if consumes is None else bool(consumes)
            victim_count = int(template.get("victim_count", 0))
            victim_keys = ensure_victim_keys(template.get("victim_keys", []), victim_count)
            victims: List[Tribute] = []
            if victim_count:
                candidates = [t for t in living if t is not actor]
                if len(candidates) < victim_count:
                    return None
                victims = rng.sample(candidates, victim_count)
            lethal_event = bool(template.get("lethal") and victim_count)
            if lethal_event:
                for target in victims:
                    target.alive = False
                actor.kills += len(victims)
            replacements = {"person": actor.name, "item": chosen}
            if victim_count:
                for idx, target in enumerate(victims):
                    replacements[victim_keys[idx]] = target.name
            text = format_template_text(template["text"], replacements)
            meta = {
                "person": actor.name,
                "item": chosen,
                "consumed": consumes_flag,
            }
            if victims:
                meta["victims"] = [t.name for t in victims]
                meta["victim"] = victims[0].name
            event_type = "item-special lethal" if lethal_event else "item-special"
            if consumes_flag:
                actor.inventory.remove(chosen)
            return {
                "type": event_type,
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
        item_templates = config.item_loot_text.get(item, [])
        template_pool = item_templates or config.loot_events
        if not template_pool:
            template_pool = ["{person} quietly pockets a {item}."]
        template = rng.choice(template_pool)
        return {
            "type": "loot",
            "text": format_template_text(template, {"person": actor.name, "item": item}),
            "meta": {"person": actor.name, "item": item},
        }

    if actor.inventory and config.inventory_events:
        if rng.random() < config.inventory_event_chance:
            item = rng.choice(actor.inventory)
            template = rng.choice(config.inventory_events)
            return {
                "type": "inventory",
                "text": format_template_text(template, {"person": actor.name, "item": item}),
                "meta": {"person": actor.name, "item": item},
            }

    lethal_chance = config.lethal_event_chance
    if day_number == 1:
        lethal_chance = min(1.0, lethal_chance + config.bloodbath_lethal_bonus)
    lethal_chance = clamp(lethal_chance * death_pressure, 0.05, 0.95)

    lethal_roll = can_attempt_lethal and rng.random() < lethal_chance
    if lethal_roll and len(living) > 1:
        template_info = normalize_lethal_entry(
            rng.choice(config.lethal_events or ["{killer} eliminates {victim}."])
        )
        candidates = [t for t in living if t is not actor]
        victim_count = min(template_info["victim_count"], len(candidates))
        if victim_count == 0:
            victim_count = 1
        victims = rng.sample(candidates, victim_count)
        for target in victims:
            target.alive = False
        actor.kills += len(victims)
        replacements = {"killer": actor.name}
        keys = template_info["victim_keys"]
        for idx, victim in enumerate(victims):
            replacements[keys[idx]] = victim.name
        template_text = format_template_text(template_info["text"], replacements)
        return {
            "type": "lethal",
            "text": template_text,
            "meta": {
                "killer": actor.name,
                "victim": victims[0].name if victims else None,
                "victims": [t.name for t in victims],
            },
        }

    non_lethal_pool = config.non_lethal_events or ["{person} passes the time in silence."]
    template_entry = normalize_non_lethal_entry(rng.choice(non_lethal_pool))
    replacements = {"person": actor.name}
    others: List[Tribute] = []
    if template_entry["roles"]:
        candidates = [t for t in living if t is not actor]
        if len(candidates) < len(template_entry["roles"]):
            return None
        others = rng.sample(candidates, len(template_entry["roles"]))
        for role, tribute in zip(template_entry["roles"], others):
            replacements[role] = tribute.name
    text = format_template_text(template_entry["text"], replacements)
    meta = {"person": actor.name}
    if others:
        meta["others"] = [t.name for t in others]
    return {
        "type": "non-lethal",
        "text": text,
        "meta": meta,
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
