"""
Automated tests for PawPal+ system logic.
Run with: python -m pytest
"""

import pytest
from pawpal_system import Person, Patient, Appointment, Caretaker


# --- Fixtures ---

@pytest.fixture
def sample_appointment():
    return Appointment("Morning Feeding", "2026-03-29", "07:00", 10, "high", "daily")

@pytest.fixture
def sample_patient(sample_appointment):
    p = Patient(name="Mochi", species="Cat", age=3)
    p.book_appointment(sample_appointment)
    return p

@pytest.fixture
def sample_owner(sample_patient):
    owner = Person(first_name="Jordan", last_name="Lee")
    owner.register_patient(sample_patient)
    return owner

@pytest.fixture
def caretaker(sample_owner):
    return Caretaker(sample_owner)


# --- Appointment Tests ---

def test_confirm_appointment(sample_appointment):
    """Marking an appointment confirmed sets attended to True."""
    sample_appointment.confirm()
    assert sample_appointment.attended is True

def test_cancel_appointment(sample_appointment):
    """Cancelling a confirmed appointment sets attended back to False."""
    sample_appointment.confirm()
    sample_appointment.cancel()
    assert sample_appointment.attended is False

def test_reschedule_appointment(sample_appointment):
    """Rescheduling updates the date and time."""
    sample_appointment.reschedule("2026-04-01", "09:00")
    assert sample_appointment.date == "2026-04-01"
    assert sample_appointment.time == "09:00"


# --- Recurrence Tests ---

def test_daily_recurrence(sample_appointment):
    """A daily appointment generates a next occurrence one day later."""
    next_appt = sample_appointment.next_occurrence()
    assert next_appt is not None
    assert next_appt.date == "2026-03-30"

def test_weekly_recurrence():
    """A weekly appointment generates a next occurrence seven days later."""
    appt = Appointment("Weekly Grooming", "2026-03-29", "10:00", 30, "medium", "weekly")
    next_appt = appt.next_occurrence()
    assert next_appt is not None
    assert next_appt.date == "2026-04-05"

def test_no_recurrence():
    """A one-time appointment returns None for next occurrence."""
    appt = Appointment("Vet Visit", "2026-03-29", "14:00", 60, "high", "none")
    assert appt.next_occurrence() is None


# --- Patient Tests ---

def test_add_appointment_increases_count(sample_patient):
    """Adding an appointment increases the patient's appointment count."""
    initial = len(sample_patient.appointments)
    sample_patient.book_appointment(Appointment("Evening Feed", "2026-03-29", "18:00", 10, "high"))
    assert len(sample_patient.appointments) == initial + 1

def test_get_history_returns_attended(sample_patient):
    """get_history returns only attended appointments."""
    sample_patient.appointments[0].confirm()
    history = sample_patient.get_history()
    assert len(history) == 1
    assert history[0].attended is True

def test_get_upcoming_returns_pending(sample_patient):
    """get_upcoming returns only unattended appointments."""
    upcoming = sample_patient.get_upcoming()
    assert all(not a.attended for a in upcoming)


# --- Caretaker Tests ---

def test_sort_by_time(caretaker, sample_owner):
    """Appointments are returned in chronological order."""
    sample_owner.patients[0].book_appointment(
        Appointment("Late Feed", "2026-03-29", "20:00", 10, "low")
    )
    sample_owner.patients[0].book_appointment(
        Appointment("Early Med", "2026-03-29", "06:00", 5, "high")
    )
    sorted_appts = caretaker.sort_by_time()
    times = [a.time for _, a in sorted_appts]
    assert times == sorted(times)

def test_conflict_detection(caretaker, sample_owner):
    """Two appointments at the same date and time are flagged as a conflict."""
    sample_owner.patients[0].book_appointment(
        Appointment("Conflict Task", "2026-03-29", "07:00", 15, "medium")
    )
    conflicts = caretaker.find_conflicts()
    assert len(conflicts) >= 1

def test_no_conflict_when_different_times(caretaker, sample_owner):
    """Appointments at different times produce no conflicts."""
    patient = Patient(name="Rex", species="Dog", age=5)
    patient.book_appointment(Appointment("Walk", "2026-03-29", "08:00", 30, "high"))
    sample_owner.register_patient(patient)
    conflicts = caretaker.find_conflicts()
    assert all(a1[1].time != a2[1].time or a1[1].date != a2[1].date
               for a1, a2 in conflicts)

def test_filter_by_priority(caretaker):
    """filter_by_priority returns only appointments matching the given level."""
    high = caretaker.filter_by_priority("high")
    assert all(a.priority == "high" for _, a in high)

def test_plan_day_returns_correct_date(caretaker):
    """plan_day returns only appointments for the specified date."""
    day = caretaker.plan_day("2026-03-29")
    assert all(a.date == "2026-03-29" for _, a in day)


# --- Sort by Priority Tests ---

def test_sort_by_priority_order(caretaker, sample_owner):
    """Appointments are returned high → medium → low priority."""
    sample_owner.patients[0].book_appointment(
        Appointment("Low Task",    "2026-03-29", "09:00", 10, "low")
    )
    sample_owner.patients[0].book_appointment(
        Appointment("Medium Task", "2026-03-29", "10:00", 10, "medium")
    )
    sorted_appts = caretaker.sort_by_priority()
    priorities = [a.priority for _, a in sorted_appts]
    rank = {"high": 0, "medium": 1, "low": 2}
    assert priorities == sorted(priorities, key=lambda p: rank[p])

def test_sort_by_priority_all_same(caretaker, sample_owner):
    """Appointments with the same priority are sorted by time."""
    sample_owner.patients[0].book_appointment(
        Appointment("Late High",  "2026-03-29", "20:00", 10, "high")
    )
    sample_owner.patients[0].book_appointment(
        Appointment("Early High", "2026-03-29", "05:00", 10, "high")
    )
    high_only = [(n, a) for n, a in caretaker.sort_by_priority() if a.priority == "high"]
    times = [a.time for _, a in high_only]
    assert times == sorted(times)


# --- what_fits Tests ---

def test_what_fits_respects_budget(caretaker, sample_owner):
    """what_fits never exceeds the given time budget."""
    sample_owner.patients[0].book_appointment(
        Appointment("Long Task", "2026-03-29", "12:00", 120, "low")
    )
    fits = caretaker.what_fits(30, "2026-03-29")
    total = sum(a.duration_minutes for _, a in fits)
    assert total <= 30

def test_what_fits_prefers_high_priority(caretaker, sample_owner):
    """what_fits includes high priority tasks before low priority ones."""
    sample_owner.patients[0].book_appointment(
        Appointment("Low Task",  "2026-03-29", "08:00", 25, "low")
    )
    sample_owner.patients[0].book_appointment(
        Appointment("High Task", "2026-03-29", "09:00", 25, "high")
    )
    fits = caretaker.what_fits(30, "2026-03-29")
    priorities = [a.priority for _, a in fits]
    assert "high" in priorities

def test_what_fits_empty_when_no_budget(caretaker):
    """what_fits returns nothing when budget is 0."""
    fits = caretaker.what_fits(0, "2026-03-29")
    assert fits == []


# --- explain_plan Tests ---

def test_explain_plan_includes_included_label(caretaker):
    """explain_plan output contains INCLUDED for tasks that fit."""
    explanation = caretaker.explain_plan(60, "2026-03-29")
    assert "INCLUDED" in explanation

def test_explain_plan_includes_skipped_label(caretaker, sample_owner):
    """explain_plan output contains SKIPPED when a task exceeds remaining budget."""
    sample_owner.patients[0].book_appointment(
        Appointment("Huge Task", "2026-03-29", "10:00", 999, "low")
    )
    explanation = caretaker.explain_plan(20, "2026-03-29")
    assert "SKIPPED" in explanation

def test_explain_plan_mentions_conflicts(caretaker, sample_owner):
    """explain_plan flags conflicts when two tasks share a date and time."""
    sample_owner.patients[0].book_appointment(
        Appointment("Clash Task", "2026-03-29", "07:00", 5, "medium")
    )
    explanation = caretaker.explain_plan(120, "2026-03-29")
    assert "clash" in explanation.lower() or "conflict" in explanation.lower()
