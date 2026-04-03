"""
Automated tests for PawPal+ system logic.
Run with: python -m pytest
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def sample_task():
    return Task("Morning Feeding", "2026-03-29", "07:00", 10, "high", "daily")

@pytest.fixture
def sample_pet(sample_task):
    p = Pet(name="Mochi", species="Cat", age=3)
    p.add_task(sample_task)
    return p

@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(first_name="Jordan", last_name="Lee")
    owner.add_pet(sample_pet)
    return owner

@pytest.fixture
def scheduler(sample_owner):
    return Scheduler(sample_owner)


# --- Task Tests ---

def test_mark_complete(sample_task):
    """Marking a task complete sets completed to True."""
    sample_task.mark_complete()
    assert sample_task.completed is True

def test_unmark_task(sample_task):
    """Unmarking a completed task sets completed back to False."""
    sample_task.mark_complete()
    sample_task.unmark()
    assert sample_task.completed is False

def test_reschedule_task(sample_task):
    """Rescheduling updates the date and time."""
    sample_task.reschedule("2026-04-01", "09:00")
    assert sample_task.date == "2026-04-01"
    assert sample_task.time == "09:00"


# --- Recurrence Tests ---

def test_daily_recurrence(sample_task):
    """A daily task generates a next occurrence one day later."""
    next_task = sample_task.next_occurrence()
    assert next_task is not None
    assert next_task.date == "2026-03-30"

def test_weekly_recurrence():
    """A weekly task generates a next occurrence seven days later."""
    task = Task("Weekly Grooming", "2026-03-29", "10:00", 30, "medium", "weekly")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.date == "2026-04-05"

def test_no_recurrence():
    """A one-time task returns None for next occurrence."""
    task = Task("Vet Visit", "2026-03-29", "14:00", 60, "high", "none")
    assert task.next_occurrence() is None


# --- Pet Tests ---

def test_add_task_increases_count(sample_pet):
    """Adding a task increases the pet's task count."""
    initial = len(sample_pet.tasks)
    sample_pet.add_task(Task("Evening Feed", "2026-03-29", "18:00", 10, "high"))
    assert len(sample_pet.tasks) == initial + 1

def test_get_completed_returns_done(sample_pet):
    """get_completed returns only completed tasks."""
    sample_pet.tasks[0].mark_complete()
    completed = sample_pet.get_completed()
    assert len(completed) == 1
    assert completed[0].completed is True

def test_get_pending_returns_incomplete(sample_pet):
    """get_pending returns only unfinished tasks."""
    pending = sample_pet.get_pending()
    assert all(not t.completed for t in pending)


# --- Owner Tests ---

def test_add_pet_increases_count(sample_owner):
    """Adding a pet increases the owner's pet count."""
    initial = len(sample_owner.pets)
    sample_owner.add_pet(Pet(name="Rex", species="Dog", age=5))
    assert len(sample_owner.pets) == initial + 1

def test_get_all_tasks_returns_tuples(sample_owner):
    """get_all_tasks returns (pet_name, task) tuples."""
    all_tasks = sample_owner.get_all_tasks()
    assert len(all_tasks) > 0
    assert all(isinstance(n, str) and isinstance(t, Task) for n, t in all_tasks)


# --- Scheduler Tests ---

def test_sort_by_time(scheduler, sample_owner):
    """Tasks are returned in chronological order."""
    sample_owner.pets[0].add_task(Task("Late Feed",  "2026-03-29", "20:00", 10, "low"))
    sample_owner.pets[0].add_task(Task("Early Med",  "2026-03-29", "06:00", 5,  "high"))
    sorted_tasks = scheduler.sort_by_time()
    times = [t.time for _, t in sorted_tasks]
    assert times == sorted(times)

def test_sort_by_priority_order(scheduler, sample_owner):
    """Tasks are returned high → medium → low priority."""
    sample_owner.pets[0].add_task(Task("Low Task",    "2026-03-29", "09:00", 10, "low"))
    sample_owner.pets[0].add_task(Task("Medium Task", "2026-03-29", "10:00", 10, "medium"))
    sorted_tasks = scheduler.sort_by_priority()
    priorities = [t.priority for _, t in sorted_tasks]
    rank = {"high": 0, "medium": 1, "low": 2}
    assert priorities == sorted(priorities, key=lambda p: rank[p])

def test_detect_conflicts(scheduler, sample_owner):
    """Two tasks at the same date and time are flagged as a conflict."""
    sample_owner.pets[0].add_task(Task("Conflict Task", "2026-03-29", "07:00", 15, "medium"))
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) >= 1

def test_no_conflict_when_different_times(scheduler, sample_owner):
    """Tasks at different times produce no conflicts."""
    rex = Pet(name="Rex", species="Dog", age=5)
    rex.add_task(Task("Walk", "2026-03-29", "08:00", 30, "high"))
    sample_owner.add_pet(rex)
    conflicts = scheduler.detect_conflicts()
    assert all(a1[1].time != a2[1].time or a1[1].date != a2[1].date
               for a1, a2 in conflicts)

def test_filter_tasks_by_pet(scheduler, sample_owner):
    """filter_tasks returns only tasks for the specified pet."""
    rex = Pet(name="Rex", species="Dog", age=5)
    rex.add_task(Task("Walk", "2026-03-29", "08:00", 30, "high"))
    sample_owner.add_pet(rex)
    rex_tasks = scheduler.filter_tasks(pet_name="Rex")
    assert all(n == "Rex" for n, _ in rex_tasks)

def test_filter_tasks_by_status(scheduler):
    """filter_tasks returns only pending tasks when status='pending'."""
    pending = scheduler.filter_tasks(status="pending")
    assert all(not t.completed for _, t in pending)

def test_filter_by_priority(scheduler):
    """filter_by_priority returns only tasks matching the given level."""
    high = scheduler.filter_by_priority("high")
    assert all(t.priority == "high" for _, t in high)

def test_plan_day_returns_correct_date(scheduler):
    """plan_day returns only tasks for the specified date."""
    day = scheduler.plan_day("2026-03-29")
    assert all(t.date == "2026-03-29" for _, t in day)

def test_what_fits_respects_budget(scheduler, sample_owner):
    """what_fits never exceeds the given time budget."""
    sample_owner.pets[0].add_task(Task("Long Task", "2026-03-29", "12:00", 120, "low"))
    fits = scheduler.what_fits(30, "2026-03-29")
    total = sum(t.duration_minutes for _, t in fits)
    assert total <= 30

def test_what_fits_empty_when_no_budget(scheduler):
    """what_fits returns nothing when budget is 0."""
    fits = scheduler.what_fits(0, "2026-03-29")
    assert fits == []

def test_find_next_slot(scheduler):
    """find_next_slot returns a valid time string."""
    slot = scheduler.find_next_slot(15, "2026-03-29")
    assert slot is not None
    assert len(slot) == 5  # "HH:MM"

def test_explain_plan_includes_label(scheduler):
    """explain_plan contains INCLUDED for tasks that fit."""
    explanation = scheduler.explain_plan(60, "2026-03-29")
    assert "INCLUDED" in explanation

def test_explain_plan_skipped_label(scheduler, sample_owner):
    """explain_plan contains SKIPPED when a task exceeds budget."""
    sample_owner.pets[0].add_task(Task("Huge Task", "2026-03-29", "10:00", 999, "low"))
    explanation = scheduler.explain_plan(20, "2026-03-29")
    assert "SKIPPED" in explanation
