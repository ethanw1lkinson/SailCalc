"""Race management helpers.

This module keeps the race data model and the ranking logic separate from the
GUI and storage layers.
"""

from dataclasses import dataclass, field
from typing import List

from calculator import calculate_corrected_time, format_time


@dataclass
class Competitor:
    sailor_name: str
    boat_class: str
    sail_number: str = ""
    elapsed_time: str = ""
    corrected_time: int = 0
    position: int = 0
    difference: str = ""


@dataclass
class Race:
    race_name: str
    competitors: List[Competitor] = field(default_factory=list)

    def add_competitor(self, sailor_name: str, boat_class: str, sail_number: str, elapsed_time: str) -> None:
        corrected_time = calculate_corrected_time(elapsed_time, boat_class)
        self.competitors.append(
            Competitor(
                sailor_name=sailor_name,
                boat_class=boat_class,
                sail_number=sail_number,
                elapsed_time=elapsed_time,
                corrected_time=corrected_time,
            )
        )

    def calculate_results(self) -> list[dict]:
        sorted_competitors = sorted(self.competitors, key=lambda c: c.corrected_time)
        results = []
        winner_time = None

        for index, competitor in enumerate(sorted_competitors, start=1):
            if winner_time is None:
                winner_time = competitor.corrected_time
                difference = "00:00:00"
            else:
                difference_seconds = competitor.corrected_time - winner_time
                difference = format_time(difference_seconds)

            competitor.position = index
            competitor.difference = difference
            results.append(
                {
                    "position": index,
                    "sailor_name": competitor.sailor_name,
                    "boat_class": competitor.boat_class,
                    "sail_number": competitor.sail_number,
                    "elapsed_time": competitor.elapsed_time,
                    "corrected_time": format_time(competitor.corrected_time),
                    "difference": difference,
                }
            )

        return results


class RaceManager(Race):
    """Compatibility wrapper used by the tests and any older code paths."""

    pass
