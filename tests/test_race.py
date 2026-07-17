import json
import os
import tempfile
import unittest

from calculator import parse_elapsed_time, format_time
from race import RaceManager
from storage import RaceStorage


class RaceAppTests(unittest.TestCase):
    def test_parse_elapsed_time_supports_minutes_and_seconds(self):
        self.assertEqual(parse_elapsed_time("60:00"), 3600)
        self.assertEqual(parse_elapsed_time("1:02:03"), 3723)
        self.assertEqual(parse_elapsed_time("45"), 2700)

    def test_race_manager_calculates_positions_and_differences(self):
        race = RaceManager("Test Race")
        race.add_competitor("Alice", "Laser", "123", "35:00")
        race.add_competitor("Bob", "Laser", "456", "40:00")
        race.add_competitor("Cara", "Laser", "789", "30:00")

        results = race.calculate_results()

        self.assertEqual(results[0]["sailor_name"], "Cara")
        self.assertEqual(results[0]["position"], 1)
        self.assertEqual(results[1]["position"], 2)
        self.assertEqual(results[2]["position"], 3)
        self.assertEqual(results[1]["difference"], "00:05:00")
        self.assertEqual(results[2]["difference"], "00:10:00")

    def test_storage_saves_and_loads_races(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "races.json")
            storage = RaceStorage(path)
            race = RaceManager("Saved Race")
            race.add_competitor("Dana", "Laser", "100", "44:00")
            storage.save_race(race)

            loaded = storage.load_races()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["race_name"], "Saved Race")


if __name__ == "__main__":
    unittest.main()
