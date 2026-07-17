import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from boats import get_boat_classes, get_boat_definitions
from calculator import calculate_corrected_time, parse_elapsed_time, format_time
from race import Race
from storage import RaceStorage


class RaceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/boats":
            self.send_json(get_boat_classes())
            return

        if parsed.path == "/api/boat-definitions":
            self.send_json(get_boat_definitions())
            return

        if parsed.path == "/api/races":
            path = os.path.join(os.getcwd(), "races.json")
            storage = RaceStorage(path)
            self.send_json(storage.load_races())
            return

        if parsed.path == "/":
            self.serve_file("home.html")
            return

        if parsed.path == "/app":
            self.serve_file("index.html")
            return

        if parsed.path.endswith(".css"):
            self.serve_file(parsed.path.lstrip("/"))
            return

        if parsed.path.endswith(".js"):
            self.serve_file(parsed.path.lstrip("/"))
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/races":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            race = Race(data.get("race_name", "New Race"))
            for competitor in data.get("competitors", []):
                race.add_competitor(
                    competitor.get("sailor_name", ""),
                    competitor.get("boat_class", "Laser"),
                    competitor.get("sail_number", ""),
                    competitor.get("elapsed_time", "35:00"),
                )

            storage = RaceStorage(os.path.join(os.getcwd(), "races.json"))
            storage.save_race(race)
            self.send_json({"status": "ok", "race_name": race.race_name})
            return

        self.send_error(404)

    def serve_file(self, filename: str):
        path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(path):
            self.send_error(404)
            return

        with open(path, "rb") as handle:
            content = handle.read()

        if filename.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        elif filename.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        else:
            content_type = "text/html; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), RaceHandler)
    print("Open http://127.0.0.1:8000 in your browser")
    server.serve_forever()
