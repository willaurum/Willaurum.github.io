import json
import random
from pathlib import Path

class Tribute:
    def __init__(self, name):
        self.name = name
        self.alive = True
        self.kills = 0

    def to_dict(self):
        return {
            "name": self.name,
            "alive": self.alive,
            "kills": self.kills
        }


def run_simulation(names):
    tributes = [Tribute(n) for n in names]
    day = 0
    events = []

    while sum(t.alive for t in tributes) > 1:
        day += 1
        alive = [t for t in tributes if t.alive]

        # 60% chance of lethal event
        lethal = random.random() < 0.6

        if lethal and len(alive) > 1:
            killer = random.choice(alive)
            victim = random.choice([t for t in alive if t != killer])

            victim.alive = False
            killer.kills += 1

            events.append({
                "day": day,
                "text": f"{killer.name} eliminated {victim.name}."
            })
        else:
            person = random.choice(alive)
            non_lethal_events = [
                f"{person.name} finds water.",
                f"{person.name} builds a shelter.",
                f"{person.name} explores the arena.",
                f"{person.name} hides in the bushes.",
                f"{person.name} forages for food.",
            ]

            events.append({
                "day": day,
                "text": random.choice(non_lethal_events)
            })

    # Determine winner
    winner = [t for t in tributes if t.alive]
    if winner:
        events.append({
            "day": day,
            "text": f"🏆 {winner[0].name} wins with {winner[0].kills} kills!"
        })

    # Return a clean dictionary
    return {
        "tributes": [t.to_dict() for t in tributes],
        "events": events,
        "days": day,
        "winner": winner[0].name if winner else None
    }


if __name__ == "__main__":
    # Modify this list or load from a file if needed
    tribute_names = [
        "Alice", "Bob", "Charlie", "Diana", 
        "Evelyn", "Frank", "George", "Hannah"
    ]

    result = run_simulation(tribute_names)

    script_dir = Path(__file__).resolve().parent
    output_path = script_dir / "simulation.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print("Generated simulation.json!")
