"""Tkinter-based sailing race results application.

This is a beginner-friendly entry point that wires together the boat database,
race management, and storage modules.
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk

from boats import get_boat_classes
from race import Race
from storage import RaceStorage


class SailingRaceApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sailing Race Results")
        self.geometry("980x680")
        self.minsize(900, 620)

        self.storage = RaceStorage("races.json")
        self.race = Race("New Race")

        self.build_ui()
        self.load_saved_races()

    def build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Label(self, text="Sailing Race Results", font=("Segoe UI", 20, "bold"))
        header.grid(row=0, column=0, padx=18, pady=(16, 10), sticky="w")

        main = ttk.Frame(self, padding=16)
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)

        left = ttk.LabelFrame(main, text="Race Entry", padding=12)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        left.columnconfigure(1, weight=1)

        ttk.Label(left, text="Race name").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.race_name_entry = ttk.Entry(left)
        self.race_name_entry.grid(row=0, column=1, padx=6, pady=(0, 6), sticky="ew")
        self.race_name_entry.insert(0, "New Race")

        ttk.Label(left, text="Sailor name").grid(row=1, column=0, sticky="w", pady=6)
        self.sailor_name_entry = ttk.Entry(left)
        self.sailor_name_entry.grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(left, text="Boat class").grid(row=2, column=0, sticky="w", pady=6)
        self.boat_class_var = tk.StringVar(value=get_boat_classes()[0])
        self.boat_class_menu = ttk.Combobox(left, textvariable=self.boat_class_var, values=get_boat_classes(), state="readonly")
        self.boat_class_menu.grid(row=2, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(left, text="Sail number").grid(row=3, column=0, sticky="w", pady=6)
        self.sail_number_entry = ttk.Entry(left)
        self.sail_number_entry.grid(row=3, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(left, text="Elapsed time").grid(row=4, column=0, sticky="w", pady=6)
        self.elapsed_time_entry = ttk.Entry(left)
        self.elapsed_time_entry.grid(row=4, column=1, padx=6, pady=6, sticky="ew")
        self.elapsed_time_entry.insert(0, "35:00")

        buttons = ttk.Frame(left)
        buttons.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Button(buttons, text="Add competitor", command=self.add_competitor).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ttk.Button(buttons, text="Calculate results", command=self.calculate_results).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        ttk.Button(left, text="Save race", command=self.save_race).grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        ttk.Button(left, text="Clear / new race", command=self.clear_race).grid(row=7, column=0, columnspan=2, pady=(8, 0), sticky="ew")

        right = ttk.LabelFrame(main, text="Race Results", padding=12)
        right.grid(row=0, column=1, rowspan=2, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        columns = ("position", "sailor", "sail_number", "boat", "elapsed", "corrected", "difference")
        self.results_tree = ttk.Treeview(right, columns=columns, show="headings")
        self.results_tree.heading("position", text="Pos")
        self.results_tree.heading("sailor", text="Sailor")
        self.results_tree.heading("sail_number", text="Sail #")
        self.results_tree.heading("boat", text="Boat")
        self.results_tree.heading("elapsed", text="Elapsed")
        self.results_tree.heading("corrected", text="Corrected")
        self.results_tree.heading("difference", text="Diff")
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(right, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        saved_races_frame = ttk.LabelFrame(right, text="Saved races", padding=8)
        saved_races_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        saved_races_frame.columnconfigure(0, weight=1)

        self.saved_races_list = tk.Listbox(saved_races_frame, height=5)
        self.saved_races_list.grid(row=0, column=0, sticky="ew")

        saved_buttons = ttk.Frame(saved_races_frame)
        saved_buttons.grid(row=0, column=1, padx=(8, 0), sticky="n")
        ttk.Button(saved_buttons, text="Refresh", command=self.load_saved_races).grid(row=0, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready to enter a race")
        ttk.Label(self, textvariable=self.status_var, foreground="#1f5f3f").grid(row=2, column=0, padx=18, pady=(6, 16), sticky="w")

    def add_competitor(self) -> None:
        sailor_name = self.sailor_name_entry.get().strip()
        boat_class = self.boat_class_var.get().strip()
        sail_number = self.sail_number_entry.get().strip()
        elapsed_time = self.elapsed_time_entry.get().strip()

        if not sailor_name or not boat_class or not elapsed_time:
            messagebox.showwarning("Missing fields", "Please enter a sailor name, boat class, and elapsed time.")
            return

        self.race.add_competitor(sailor_name, boat_class, sail_number, elapsed_time)
        self.status_var.set(f"Added {sailor_name} for {boat_class}")
        self.sailor_name_entry.delete(0, tk.END)
        self.sail_number_entry.delete(0, tk.END)
        self.elapsed_time_entry.delete(0, tk.END)
        self.elapsed_time_entry.insert(0, "35:00")

    def calculate_results(self) -> None:
        if not self.race.competitors:
            messagebox.showinfo("No competitors", "Add at least one competitor before calculating results.")
            return

        results = self.race.calculate_results()
        self.populate_results(results)
        self.status_var.set(f"Calculated results for {self.race.race_name}")

    def populate_results(self, results: list[dict]) -> None:
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        for entry in results:
            self.results_tree.insert(
                "",
                "end",
                values=(
                    entry["position"],
                    entry["sailor_name"],
                    entry["sail_number"],
                    entry["boat_class"],
                    entry["elapsed_time"],
                    entry["corrected_time"],
                    entry["difference"],
                ),
            )

    def save_race(self) -> None:
        if not self.race.competitors:
            messagebox.showwarning("Nothing to save", "Add at least one competitor before saving.")
            return

        self.race.race_name = self.race_name_entry.get().strip() or "New Race"
        self.storage.save_race(self.race)
        self.status_var.set(f"Saved {self.race.race_name} to local JSON")
        messagebox.showinfo("Race saved", f"Saved {self.race.race_name} to races.json")

    def clear_race(self) -> None:
        self.race = Race("New Race")
        self.race_name_entry.delete(0, tk.END)
        self.race_name_entry.insert(0, "New Race")
        self.sailor_name_entry.delete(0, tk.END)
        self.sail_number_entry.delete(0, tk.END)
        self.elapsed_time_entry.delete(0, tk.END)
        self.elapsed_time_entry.insert(0, "35:00")
        self.populate_results([])
        self.status_var.set("Started a new race")

    def load_saved_races(self) -> None:
        races = self.storage.load_races()
        self.saved_races_list.delete(0, tk.END)
        for race in races:
            self.saved_races_list.insert(tk.END, race.get("race_name", "Untitled race"))
        if races:
            self.status_var.set(f"Loaded {len(races)} saved race(s)")
        else:
            self.status_var.set("No saved races yet")


if __name__ == "__main__":
    try:
        app = SailingRaceApp()
        app.mainloop()
    except tk.TclError as exc:
        print("Tkinter could not start because no desktop display is available.")
        print("Run this on a local machine with a GUI desktop, or use a remote desktop session.")
        print(f"Details: {exc}")
