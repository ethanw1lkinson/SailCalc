import unittest

from boats import get_boat_definitions


class BoatDataTests(unittest.TestCase):
    def test_boat_definitions_include_handicap_values(self):
        boat_definitions = get_boat_definitions()
        self.assertIn("Laser", [entry["name"] for entry in boat_definitions])
        laser = next(entry for entry in boat_definitions if entry["name"] == "Laser")
        self.assertEqual(laser["handicap"], 100.0)


if __name__ == "__main__":
    unittest.main()
