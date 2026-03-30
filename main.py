"""
PawPal+ Demo Script
Run this to verify the backend logic works before connecting to the UI.
"""

from pawpal_system import Person, Patient, Appointment, Caretaker

# --- Setup ---
owner = Person(first_name="Jordan", last_name="Lee", phone="555-1234", email="jordan@email.com")

mochi = Patient(name="Mochi", species="Cat", age=3, medical_notes="Allergic to grain-based food")
rex   = Patient(name="Rex",   species="Dog", age=5, medical_notes="Needs joint supplement daily")

owner.register_patient(mochi)
owner.register_patient(rex)

# --- Add Appointments ---
today = "2026-03-29"

# Mochi's appointments
mochi.book_appointment(Appointment("Morning Feeding",    today, "07:00", 10,  "high",   "daily"))
mochi.book_appointment(Appointment("Vet Checkup",        today, "14:00", 60,  "high",   "none"))
mochi.book_appointment(Appointment("Playtime",           today, "18:00", 20,  "low",    "daily"))

# Rex's appointments
rex.book_appointment(Appointment("Morning Walk",         today, "07:30", 30,  "high",   "daily"))
rex.book_appointment(Appointment("Joint Supplement",     today, "08:00", 5,   "high",   "daily"))
rex.book_appointment(Appointment("Evening Walk",         today, "18:00", 30,  "medium", "daily"))

# Conflict test — same time as Mochi's Morning Feeding
rex.book_appointment(Appointment("Early Feeding",        today, "07:00", 10,  "medium", "daily"))

# --- Run the Caretaker ---
caretaker = Caretaker(owner)

# Today's schedule
print(caretaker.summarize_day(today))

# Filtering by priority
print("\n--- High Priority Appointments ---")
for patient_name, appt in caretaker.filter_by_priority("high"):
    print(f"  {patient_name}: {appt}")

# Sorting all appointments by time
print("\n--- All Appointments Sorted by Time ---")
for patient_name, appt in caretaker.sort_by_time():
    print(f"  {patient_name}: {appt}")

# Recurring task — mark complete and get next occurrence
print("\n--- Recurring Task Demo ---")
morning_feeding = mochi.appointments[0]
print(f"  Before: {morning_feeding}")
morning_feeding.confirm()
next_appt = morning_feeding.next_occurrence()
if next_appt:
    mochi.book_appointment(next_appt)
    print(f"  Marked complete. Next occurrence booked: {next_appt}")
