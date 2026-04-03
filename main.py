"""
PawPal+ Demo Script
Run this to verify the backend logic works before connecting to the UI.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(first_name="Jordan", last_name="Lee", phone="555-1234", email="jordan@email.com")

mochi = Pet(name="Mochi", species="Cat", age=3, medical_notes="Allergic to grain-based food")
rex   = Pet(name="Rex",   species="Dog", age=5, medical_notes="Needs joint supplement daily")

owner.add_pet(mochi)
owner.add_pet(rex)

# --- Add Tasks ---
today = "2026-03-29"

mochi.add_task(Task("Morning Feeding",   today, "07:00", 10,  "high",   "daily"))
mochi.add_task(Task("Vet Checkup",       today, "14:00", 60,  "high",   "none"))
mochi.add_task(Task("Playtime",          today, "18:00", 20,  "low",    "daily"))

rex.add_task(Task("Morning Walk",        today, "07:30", 30,  "high",   "daily"))
rex.add_task(Task("Joint Supplement",    today, "08:00", 5,   "high",   "daily"))
rex.add_task(Task("Evening Walk",        today, "18:00", 30,  "medium", "daily"))
rex.add_task(Task("Early Feeding",       today, "07:00", 10,  "medium", "daily"))

scheduler = Scheduler(owner)

# --- Today's Schedule (tabulate) ---
print("\n=== Today's Schedule ===")
day = scheduler.plan_day(today)
table_data = [
    [t.emoji, t.time, pet, t.title, f"{t.duration_minutes} min",
     f"{t.priority_emoji} {t.priority}", t.frequency,
     "Done" if t.completed else "Pending"]
    for pet, t in day
]
print(tabulate(table_data,
               headers=["", "Time", "Pet", "Task", "Duration", "Priority", "Repeat", "Status"],
               tablefmt="rounded_outline"))

# --- Conflicts ---
print("\n=== Conflict Check ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for (n1, t1), (n2, t2) in conflicts:
        print(f"  ⚠️  '{t1.title}' ({n1}) and '{t2.title}' ({n2}) both at {t1.time} on {t1.date}")
else:
    print("  ✅ No conflicts.")

# --- Sort by priority ---
print("\n=== Sorted by Priority ===")
by_priority = scheduler.sort_by_priority()
priority_table = [
    [t.priority_emoji, t.priority, t.time, pet, t.title, f"{t.duration_minutes} min"]
    for pet, t in by_priority
]
print(tabulate(priority_table,
               headers=["", "Priority", "Time", "Pet", "Task", "Duration"],
               tablefmt="rounded_outline"))

# --- Filter tasks ---
print("\n=== Filter: Rex's Tasks Only ===")
rex_tasks = scheduler.filter_tasks(pet_name="Rex")
for pet_name, t in rex_tasks:
    print(f"  {pet_name}: {t}")

# --- What fits in 60 minutes ---
print("\n=== What Fits in 60 Minutes ===")
fits = scheduler.what_fits(60, today)
fits_table = [
    [t.emoji, t.time, pet, t.title, f"{t.duration_minutes} min", t.priority]
    for pet, t in fits
]
print(tabulate(fits_table,
               headers=["", "Time", "Pet", "Task", "Duration", "Priority"],
               tablefmt="rounded_outline"))

# --- Next Available Slot ---
print("\n=== Next Available Slot ===")
for duration in [15, 30, 60]:
    slot = scheduler.find_next_slot(duration, today)
    print(f"  Next available {duration}-min slot: {slot}")

# --- Explain plan ---
print("\n" + scheduler.explain_plan(60, today))

# --- Recurring task demo ---
print("\n=== Recurring Task Demo ===")
morning_feeding = mochi.tasks[0]
print(f"  Before: {morning_feeding}")
morning_feeding.mark_complete()
next_task = morning_feeding.next_occurrence()
if next_task:
    mochi.add_task(next_task)
    print(f"  Marked complete. Next occurrence booked: {next_task}")

# --- Data Persistence ---
print("\n=== Data Persistence Demo ===")
owner.save_to_json("data.json")
print("  Saved to data.json")
reloaded = Owner.load_from_json("data.json")
print(f"  Reloaded: {reloaded}")
print(f"  Pets: {[str(p) for p in reloaded.pets]}")
print(f"  Total tasks: {sum(len(p.tasks) for p in reloaded.pets)}")
