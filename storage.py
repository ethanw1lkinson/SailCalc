"""Simple JSON-based persistence for race results.

The storage layer is intentionally simple so it can be upgraded later to a
proper database without changing the rest of the app.
"""

import json
import os
from typing import List

from race import Race


class RaceStorage:
    def __init__(self, path: str):
        self.path = path

    def save_race(self, race: Race) -> None:
        data = self.load_races()
        data.append(
            {
                "race_name": race.race_name,
                "competitors": [
                    {
                        "sailor_name": competitor.sailor_name,
                        "boat_class": competitor.boat_class,
                        "sail_number": competitor.sail_number,
                        "elapsed_time": competitor.elapsed_time,
                        "corrected_time": competitor.corrected_time,
                        "position": competitor.position,
                        "difference": competitor.difference,
                    }
                    for competitor in race.competitors
                ],
            }
        )
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def load_races(self) -> List[dict]:
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle)
