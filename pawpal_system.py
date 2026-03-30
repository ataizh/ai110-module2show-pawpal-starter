"""
PawPal+ System Logic
Core classes: Person, Patient, Appointment, Caretaker
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional

# Challenge 4: emoji map for task types based on title keywords
TASK_EMOJIS = {
    "walk":      "🦮",
    "feed":      "🍽️",
    "feeding":   "🍽️",
    "med":       "💊",
    "medication":"💊",
    "vet":       "🏥",
    "groom":     "✂️",
    "play":      "🎾",
    "bath":      "🛁",
    "supplement":"💊",
    "checkup":   "🏥",
}

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def task_emoji(title: str) -> str:
    """Return an emoji for a task based on its title keywords."""
    lower = title.lower()
    for keyword, emoji in TASK_EMOJIS.items():
        if keyword in lower:
            return emoji
    return "📋"


@dataclass
class Appointment:
    """A single care appointment for a patient (pet)."""

    title: str
    date: str                        # format: "YYYY-MM-DD"
    time: str                        # format: "HH:MM"
    duration_minutes: int
    priority: str                    # "low", "medium", "high"
    repeat: str = "none"             # "none", "daily", "weekly"
    attended: bool = False

    @property
    def emoji(self) -> str:
        """Return an emoji representing this appointment's type."""
        return task_emoji(self.title)

    @property
    def priority_emoji(self) -> str:
        """Return a color emoji for this appointment's priority."""
        return PRIORITY_EMOJI.get(self.priority, "⚪")

    def confirm(self):
        """Mark the appointment as attended."""
        self.attended = True

    def cancel(self):
        """Mark the appointment as not attended."""
        self.attended = False

    def reschedule(self, new_date: str, new_time: str):
        """Reschedule the appointment to a new date and time."""
        self.date = new_date
        self.time = new_time

    def next_occurrence(self) -> Optional["Appointment"]:
        """Return a new Appointment for the next occurrence if recurring."""
        if self.repeat == "none":
            return None
        current = datetime.strptime(self.date, "%Y-%m-%d").date()
        if self.repeat == "daily":
            next_date = current + timedelta(days=1)
        elif self.repeat == "weekly":
            next_date = current + timedelta(weeks=1)
        else:
            return None
        return Appointment(
            title=self.title,
            date=next_date.strftime("%Y-%m-%d"),
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            repeat=self.repeat,
        )

    def to_dict(self) -> dict:
        """Serialize this appointment to a plain dictionary."""
        return {
            "title":            self.title,
            "date":             self.date,
            "time":             self.time,
            "duration_minutes": self.duration_minutes,
            "priority":         self.priority,
            "repeat":           self.repeat,
            "attended":         self.attended,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Appointment":
        """Deserialize an Appointment from a plain dictionary."""
        return cls(
            title=data["title"],
            date=data["date"],
            time=data["time"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            repeat=data.get("repeat", "none"),
            attended=data.get("attended", False),
        )

    def __str__(self):
        status = "Attended" if self.attended else "Pending"
        return (
            f"{self.emoji} {self.priority_emoji} [{self.time}] {self.title} "
            f"({self.duration_minutes} min, {self.priority} priority) — {status}"
        )


@dataclass
class Patient:
    """A pet, treated as a care patient with a health record."""

    name: str
    species: str
    age: int
    medical_notes: str = ""
    appointments: list = field(default_factory=list)

    def book_appointment(self, appointment: Appointment):
        """Add an appointment to this patient's schedule."""
        self.appointments.append(appointment)

    def get_history(self) -> list:
        """Return all past (attended) appointments."""
        return [a for a in self.appointments if a.attended]

    def get_upcoming(self) -> list:
        """Return all pending (not yet attended) appointments."""
        return [a for a in self.appointments if not a.attended]

    def to_dict(self) -> dict:
        """Serialize this patient to a plain dictionary."""
        return {
            "name":          self.name,
            "species":       self.species,
            "age":           self.age,
            "medical_notes": self.medical_notes,
            "appointments":  [a.to_dict() for a in self.appointments],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Patient":
        """Deserialize a Patient from a plain dictionary."""
        p = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            medical_notes=data.get("medical_notes", ""),
        )
        p.appointments = [Appointment.from_dict(a) for a in data.get("appointments", [])]
        return p

    def __str__(self):
        return f"{self.name} ({self.species}, age {self.age})"


@dataclass
class Person:
    """The pet owner — a real human responsible for one or more patients."""

    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    patients: list = field(default_factory=list)

    def register_patient(self, patient: Patient):
        """Register a new patient (pet) under this person."""
        self.patients.append(patient)

    def get_appointments(self) -> list:
        """Return all appointments across all patients."""
        all_appointments = []
        for patient in self.patients:
            for appt in patient.appointments:
                all_appointments.append((patient.name, appt))
        return all_appointments

    @property
    def full_name(self) -> str:
        """Return the person's full name."""
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        """Serialize this person and all their data to a plain dictionary."""
        return {
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "phone":      self.phone,
            "email":      self.email,
            "patients":   [p.to_dict() for p in self.patients],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Person":
        """Deserialize a Person from a plain dictionary."""
        p = cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone", ""),
            email=data.get("email", ""),
        )
        p.patients = [Patient.from_dict(pt) for pt in data.get("patients", [])]
        return p

    def save_to_json(self, filepath: str = "data.json"):
        """Save all owner and pet data to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Person":
        """Load owner and pet data from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self):
        return f"{self.full_name} ({len(self.patients)} patient(s))"


class Caretaker:
    """Manages and plans appointments for a Person's patients."""

    def __init__(self, person: Person):
        """Initialize with the Person this caretaker serves."""
        self.person = person
        self.schedule = []

    def plan_day(self, target_date: str = None) -> list:
        """Build a sorted list of appointments for a given date (defaults to today)."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        day_appointments = []
        for patient in self.person.patients:
            for appt in patient.appointments:
                if appt.date == target_date:
                    day_appointments.append((patient.name, appt))
        self.schedule = sorted(day_appointments, key=lambda x: x[1].time)
        return self.schedule

    def sort_by_time(self) -> list:
        """Return all appointments sorted by time."""
        all_appts = self.person.get_appointments()
        return sorted(all_appts, key=lambda x: (x[1].date, x[1].time))

    def sort_by_priority(self) -> list:
        """Return all appointments sorted high → medium → low priority."""
        rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            self.person.get_appointments(),
            key=lambda x: (rank.get(x[1].priority, 99), x[1].date, x[1].time),
        )

    def find_conflicts(self) -> list:
        """Return pairs of appointments scheduled at the same date and time."""
        seen = {}
        conflicts = []
        for patient_name, appt in self.person.get_appointments():
            key = (appt.date, appt.time)
            if key in seen:
                conflicts.append((seen[key], (patient_name, appt)))
            else:
                seen[key] = (patient_name, appt)
        return conflicts

    def filter_by_priority(self, priority: str) -> list:
        """Return all appointments matching the given priority level."""
        return [
            (name, appt)
            for name, appt in self.person.get_appointments()
            if appt.priority == priority
        ]

    def what_fits(self, time_budget_minutes: int, target_date: str = None) -> list:
        """Return appointments that fit within a time budget, picking high priority first."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        rank = {"high": 0, "medium": 1, "low": 2}
        candidates = sorted(
            [(name, appt) for name, appt in self.person.get_appointments()
             if appt.date == target_date],
            key=lambda x: (rank.get(x[1].priority, 99), x[1].time),
        )
        chosen, total = [], 0
        for name, appt in candidates:
            if total + appt.duration_minutes <= time_budget_minutes:
                chosen.append((name, appt))
                total += appt.duration_minutes
        return chosen

    def find_next_slot(self, duration_minutes: int, target_date: str = None,
                       start_hour: int = 8) -> Optional[str]:
        """Challenge 1 — Find the next available time slot for a task of given duration.

        Scans the day in 15-minute increments from start_hour and returns the first
        time (HH:MM) where the requested duration fits without overlapping any
        existing appointment. Returns None if no slot is found before midnight.
        """
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")

        # Build list of (start_minutes, end_minutes) for existing appointments that day
        booked = []
        for _, appt in self.person.get_appointments():
            if appt.date == target_date:
                h, m = map(int, appt.time.split(":"))
                start = h * 60 + m
                booked.append((start, start + appt.duration_minutes))

        # Scan from start_hour to midnight in 15-min increments
        candidate = start_hour * 60
        end_of_day = 24 * 60

        while candidate + duration_minutes <= end_of_day:
            candidate_end = candidate + duration_minutes
            # Check overlap: two intervals [s1,e1] and [s2,e2] overlap if s1 < e2 and s2 < e1
            overlap = any(candidate < e and s < candidate_end for s, e in booked)
            if not overlap:
                return f"{candidate // 60:02d}:{candidate % 60:02d}"
            candidate += 15  # advance by 15-minute increments

        return None  # no slot found

    def explain_plan(self, time_budget_minutes: int, target_date: str = None) -> str:
        """Return a plain-English explanation of what was scheduled and why."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        rank = {"high": 0, "medium": 1, "low": 2}
        all_day = sorted(
            [(name, appt) for name, appt in self.person.get_appointments()
             if appt.date == target_date],
            key=lambda x: (rank.get(x[1].priority, 99), x[1].time),
        )
        lines = [f"Plan explanation for {target_date} (budget: {time_budget_minutes} min)\n"]
        total = 0
        for name, appt in all_day:
            if total + appt.duration_minutes <= time_budget_minutes:
                total += appt.duration_minutes
                lines.append(
                    f"  INCLUDED  {appt.emoji} '{appt.title}' for {name} at {appt.time} "
                    f"({appt.duration_minutes} min, {appt.priority} priority) "
                    f"— {total}/{time_budget_minutes} min used."
                )
            else:
                lines.append(
                    f"  SKIPPED   {appt.emoji} '{appt.title}' for {name} "
                    f"({appt.duration_minutes} min) — not enough time remaining "
                    f"({time_budget_minutes - total} min left)."
                )
        conflicts = self.find_conflicts()
        day_conflicts = [(a1, a2) for a1, a2 in conflicts if a1[1].date == target_date]
        if day_conflicts:
            lines.append("\n  Conflicts to resolve:")
            for (n1, a1), (n2, a2) in day_conflicts:
                lines.append(f"    '{a1.title}' ({n1}) and '{a2.title}' ({n2}) clash at {a1.time}.")
        return "\n".join(lines)

    def summarize_day(self, target_date: str = None) -> str:
        """Print a readable summary of the day's appointments."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        day = self.plan_day(target_date)
        if not day:
            return f"No appointments scheduled for {target_date}."
        lines = [f"\n--- Schedule for {target_date} ---"]
        for patient_name, appt in day:
            lines.append(f"  {patient_name}: {appt}")
        conflicts = self.find_conflicts()
        if conflicts:
            lines.append("\n  CONFLICTS DETECTED:")
            for (n1, a1), (n2, a2) in conflicts:
                lines.append(f"    {n1} '{a1.title}' and {n2} '{a2.title}' both at {a1.time} on {a1.date}")
        return "\n".join(lines)
