"""
PawPal+ Demo Script
Run this to verify the backend logic works before connecting to the UI.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

from tabulate import tabulate
from pawpal_system import Person, Patient, Appointment, Caretaker

# --- Setup ---
owner = Person(first_name="Jordan", last_name="Lee", phone="555-1234", email="jordan@email.com")

mochi = Patient(name="Mochi", species="Cat", age=3, medical_notes="Allergic to grain-based food")
rex   = Patient(name="Rex",   species="Dog", age=5, medical_notes="Needs joint supplement daily")

owner.register_patient(mochi)
owner.register_patient(rex)

# --- Add Appointments ---
today = "2026-03-29"

mochi.book_appointment(Appointment("Morning Feeding",    today, "07:00", 10,  "high",   "daily"))
mochi.book_appointment(Appointment("Vet Checkup",        today, "14:00", 60,  "high",   "none"))
mochi.book_appointment(Appointment("Playtime",           today, "18:00", 20,  "low",    "daily"))

rex.book_appointment(Appointment("Morning Walk",         today, "07:30", 30,  "high",   "daily"))
rex.book_appointment(Appointment("Joint Supplement",     today, "08:00", 5,   "high",   "daily"))
rex.book_appointment(Appointment("Evening Walk",         today, "18:00", 30,  "medium", "daily"))
rex.book_appointment(Appointment("Early Feeding",        today, "07:00", 10,  "medium", "daily"))

caretaker = Caretaker(owner)

# --- Challenge 4: tabulate formatted schedule ---
print("\n=== Today's Schedule ===")
day = caretaker.plan_day(today)
table_data = [
    [appt.emoji, appt.time, pet, appt.title,
     f"{appt.duration_minutes} min",
     f"{appt.priority_emoji} {appt.priority}",
     appt.repeat,
     "Done" if appt.attended else "Pending"]
    for pet, appt in day
]
print(tabulate(table_data,
               headers=["", "Time", "Pet", "Task", "Duration", "Priority", "Repeat", "Status"],
               tablefmt="rounded_outline"))

# --- Conflicts ---
print("\n=== Conflict Check ===")
conflicts = caretaker.find_conflicts()
if conflicts:
    for (n1, a1), (n2, a2) in conflicts:
        print(f"  ⚠️  '{a1.title}' ({n1}) and '{a2.title}' ({n2}) both at {a1.time} on {a1.date}")
else:
    print("  ✅ No conflicts.")

# --- Sort by priority (tabulate) ---
print("\n=== Sorted by Priority ===")
by_priority = caretaker.sort_by_priority()
priority_table = [
    [appt.priority_emoji, appt.priority, appt.time, pet, appt.title, f"{appt.duration_minutes} min"]
    for pet, appt in by_priority
]
print(tabulate(priority_table,
               headers=["", "Priority", "Time", "Pet", "Task", "Duration"],
               tablefmt="rounded_outline"))

# --- What fits in 60 minutes ---
print("\n=== What Fits in 60 Minutes ===")
fits = caretaker.what_fits(60, today)
fits_table = [
    [appt.emoji, appt.time, pet, appt.title, f"{appt.duration_minutes} min", appt.priority]
    for pet, appt in fits
]
print(tabulate(fits_table,
               headers=["", "Time", "Pet", "Task", "Duration", "Priority"],
               tablefmt="rounded_outline"))

# --- Challenge 1: Next Available Slot ---
print("\n=== Next Available Slot ===")
for duration in [15, 30, 60]:
    slot = caretaker.find_next_slot(duration, today)
    print(f"  Next available {duration}-min slot: {slot}")

# --- Explain plan ---
print("\n" + caretaker.explain_plan(60, today))

# --- Recurring task demo ---
print("\n=== Recurring Task Demo ===")
morning_feeding = mochi.appointments[0]
print(f"  Before: {morning_feeding}")
morning_feeding.confirm()
next_appt = morning_feeding.next_occurrence()
if next_appt:
    mochi.book_appointment(next_appt)
    print(f"  Marked complete. Next occurrence booked: {next_appt}")

# --- Challenge 2: Save and reload ---
print("\n=== Data Persistence Demo ===")
owner.save_to_json("data.json")
print("  Saved to data.json")
reloaded = Person.load_from_json("data.json")
print(f"  Reloaded: {reloaded}")
print(f"  Pets: {[str(p) for p in reloaded.patients]}")
print(f"  Total appointments: {sum(len(p.appointments) for p in reloaded.patients)}")
