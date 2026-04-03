"""
PawPal+ System Logic
Core classes: Owner, Pet, Task, Scheduler
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Optional

# Emoji map for task types based on title keywords
TASK_EMOJIS = {
    "walk":       "🦮",
    "feed":       "🍽️",
    "feeding":    "🍽️",
    "med":        "💊",
    "medication": "💊",
    "vet":        "🏥",
    "groom":      "✂️",
    "play":       "🎾",
    "bath":       "🛁",
    "supplement": "💊",
    "checkup":    "🏥",
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
class Task:
    """A single pet care activity with scheduling and recurrence info."""

    title: str
    date: str                        # format: "YYYY-MM-DD"
    time: str                        # format: "HH:MM"
    duration_minutes: int
    priority: str                    # "low", "medium", "high"
    frequency: str = "none"          # "none", "daily", "weekly"
    completed: bool = False

    @property
    def emoji(self) -> str:
        """Return an emoji representing this task's type."""
        return task_emoji(self.title)

    @property
    def priority_emoji(self) -> str:
        """Return a color emoji for this task's priority."""
        return PRIORITY_EMOJI.get(self.priority, "⚪")

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True

    def unmark(self):
        """Mark the task as not completed."""
        self.completed = False

    def reschedule(self, new_date: str, new_time: str):
        """Reschedule the task to a new date and time."""
        self.date = new_date
        self.time = new_time

    def next_occurrence(self) -> Optional["Task"]:
        """Return a new Task for the next occurrence if recurring."""
        if self.frequency == "none":
            return None
        current = datetime.strptime(self.date, "%Y-%m-%d").date()
        if self.frequency == "daily":
            next_date = current + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = current + timedelta(weeks=1)
        else:
            return None
        return Task(
            title=self.title,
            date=next_date.strftime("%Y-%m-%d"),
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
        )

    def to_dict(self) -> dict:
        """Serialize this task to a plain dictionary."""
        return {
            "title":            self.title,
            "date":             self.date,
            "time":             self.time,
            "duration_minutes": self.duration_minutes,
            "priority":         self.priority,
            "frequency":        self.frequency,
            "completed":        self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Deserialize a Task from a plain dictionary."""
        return cls(
            title=data["title"],
            date=data["date"],
            time=data["time"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data.get("frequency", "none"),
            completed=data.get("completed", False),
        )

    def __str__(self):
        status = "Done" if self.completed else "Pending"
        return (
            f"{self.emoji} {self.priority_emoji} [{self.time}] {self.title} "
            f"({self.duration_minutes} min, {self.priority} priority) — {status}"
        )


@dataclass
class Pet:
    """A pet with identifying info and a list of care tasks."""

    name: str
    species: str
    age: int
    medical_notes: str = ""
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> list:
        """Return all tasks for this pet."""
        return self.tasks

    def get_completed(self) -> list:
        """Return all completed tasks."""
        return [t for t in self.tasks if t.completed]

    def get_pending(self) -> list:
        """Return all pending (not yet completed) tasks."""
        return [t for t in self.tasks if not t.completed]

    def to_dict(self) -> dict:
        """Serialize this pet to a plain dictionary."""
        return {
            "name":          self.name,
            "species":       self.species,
            "age":           self.age,
            "medical_notes": self.medical_notes,
            "tasks":         [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Deserialize a Pet from a plain dictionary."""
        p = cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            medical_notes=data.get("medical_notes", ""),
        )
        p.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return p

    def __str__(self):
        return f"{self.name} ({self.species}, age {self.age})"


@dataclass
class Owner:
    """The pet owner — stores identifying info and manages a list of pets."""

    first_name: str
    last_name: str
    phone: str = ""
    email: str = ""
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's list."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Return all tasks across all pets as (pet_name, task) tuples."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))
        return all_tasks

    @property
    def full_name(self) -> str:
        """Return the owner's full name."""
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        """Serialize this owner and all their data to a plain dictionary."""
        return {
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "phone":      self.phone,
            "email":      self.email,
            "pets":       [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Deserialize an Owner from a plain dictionary."""
        o = cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone", ""),
            email=data.get("email", ""),
        )
        o.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return o

    def save_to_json(self, filepath: str = "data.json"):
        """Save all owner and pet data to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load owner and pet data from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self):
        return f"{self.full_name} ({len(self.pets)} pet(s))"


class Scheduler:
    """The brain — retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        """Initialize with the Owner this scheduler manages."""
        self.owner = owner
        self.schedule = []

    def plan_day(self, target_date: str = None) -> list:
        """Return all tasks for a given date sorted by time (defaults to today)."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        day_tasks = [
            (pet_name, task)
            for pet_name, task in self.owner.get_all_tasks()
            if task.date == target_date
        ]
        self.schedule = sorted(day_tasks, key=lambda x: x[1].time)
        return self.schedule

    def sort_by_time(self) -> list:
        """Return all tasks sorted chronologically."""
        return sorted(self.owner.get_all_tasks(), key=lambda x: (x[1].date, x[1].time))

    def sort_by_priority(self) -> list:
        """Return all tasks sorted high → medium → low priority."""
        rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda x: (rank.get(x[1].priority, 99), x[1].date, x[1].time),
        )

    def filter_tasks(self, pet_name: str = None, status: str = None) -> list:
        """Filter tasks by pet name and/or completion status ('done' or 'pending')."""
        results = self.owner.get_all_tasks()
        if pet_name:
            results = [(n, t) for n, t in results if n == pet_name]
        if status == "done":
            results = [(n, t) for n, t in results if t.completed]
        elif status == "pending":
            results = [(n, t) for n, t in results if not t.completed]
        return results

    def filter_by_priority(self, priority: str) -> list:
        """Return all tasks matching the given priority level."""
        return [(n, t) for n, t in self.owner.get_all_tasks() if t.priority == priority]

    def detect_conflicts(self) -> list:
        """Return pairs of tasks scheduled at the same date and time."""
        seen = {}
        conflicts = []
        for pet_name, task in self.owner.get_all_tasks():
            key = (task.date, task.time)
            if key in seen:
                conflicts.append((seen[key], (pet_name, task)))
            else:
                seen[key] = (pet_name, task)
        return conflicts

    def what_fits(self, time_budget_minutes: int, target_date: str = None) -> list:
        """Return tasks that fit within a time budget, picking high priority first."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        rank = {"high": 0, "medium": 1, "low": 2}
        candidates = sorted(
            [(n, t) for n, t in self.owner.get_all_tasks() if t.date == target_date],
            key=lambda x: (rank.get(x[1].priority, 99), x[1].time),
        )
        chosen, total = [], 0
        for name, task in candidates:
            if total + task.duration_minutes <= time_budget_minutes:
                chosen.append((name, task))
                total += task.duration_minutes
        return chosen

    def find_next_slot(self, duration_minutes: int, target_date: str = None,
                       start_hour: int = 8) -> Optional[str]:
        """Find the next available time slot for a task of given duration.

        Scans the day in 15-minute increments from start_hour and returns the
        first time (HH:MM) where the duration fits without overlapping any
        existing task. Returns None if no slot is found before midnight.
        """
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        booked = []
        for _, task in self.owner.get_all_tasks():
            if task.date == target_date:
                h, m = map(int, task.time.split(":"))
                start = h * 60 + m
                booked.append((start, start + task.duration_minutes))
        candidate = start_hour * 60
        while candidate + duration_minutes <= 24 * 60:
            end = candidate + duration_minutes
            if not any(candidate < e and s < end for s, e in booked):
                return f"{candidate // 60:02d}:{candidate % 60:02d}"
            candidate += 15
        return None

    def explain_plan(self, time_budget_minutes: int, target_date: str = None) -> str:
        """Return a plain-English explanation of what was scheduled and why."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        rank = {"high": 0, "medium": 1, "low": 2}
        all_day = sorted(
            [(n, t) for n, t in self.owner.get_all_tasks() if t.date == target_date],
            key=lambda x: (rank.get(x[1].priority, 99), x[1].time),
        )
        lines = [f"Plan explanation for {target_date} (budget: {time_budget_minutes} min)\n"]
        total = 0
        for name, task in all_day:
            if total + task.duration_minutes <= time_budget_minutes:
                total += task.duration_minutes
                lines.append(
                    f"  INCLUDED  {task.emoji} '{task.title}' for {name} at {task.time} "
                    f"({task.duration_minutes} min, {task.priority} priority) "
                    f"— {total}/{time_budget_minutes} min used."
                )
            else:
                lines.append(
                    f"  SKIPPED   {task.emoji} '{task.title}' for {name} "
                    f"({task.duration_minutes} min) — not enough time remaining "
                    f"({time_budget_minutes - total} min left)."
                )
        conflicts = self.detect_conflicts()
        day_conflicts = [(a1, a2) for a1, a2 in conflicts if a1[1].date == target_date]
        if day_conflicts:
            lines.append("\n  Conflicts to resolve:")
            for (n1, t1), (n2, t2) in day_conflicts:
                lines.append(f"    '{t1.title}' ({n1}) and '{t2.title}' ({n2}) clash at {t1.time}.")
        return "\n".join(lines)

    def summarize_day(self, target_date: str = None) -> str:
        """Return a readable summary of the day's tasks."""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
        day = self.plan_day(target_date)
        if not day:
            return f"No tasks scheduled for {target_date}."
        lines = [f"\n--- Schedule for {target_date} ---"]
        for pet_name, task in day:
            lines.append(f"  {pet_name}: {task}")
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\n  CONFLICTS DETECTED:")
            for (n1, t1), (n2, t2) in conflicts:
                lines.append(f"    {n1} '{t1.title}' and {n2} '{t2.title}' both at {t1.time} on {t1.date}")
        return "\n".join(lines)
