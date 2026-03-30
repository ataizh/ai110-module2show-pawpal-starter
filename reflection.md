# PawPal+ Project Reflection

## 1. System Design

### Core User Actions
1. **Add a pet** — the owner enters basic info (their name, pet name, species) to register a pet in the system.
2. **Schedule tasks** — the owner adds care tasks (walks, feedings, meds, grooming) with a duration and priority level.
3. **Generate a daily plan** — the system produces a sorted, prioritized schedule for the day and explains why each task was chosen and when it happens.

**a. Initial design**

The system uses four classes modeled after human healthcare and daily life roles:

- **Person** — the pet owner. Holds personal info (name, phone, email) and a list of patients. Responsible for registering new patients and retrieving all their appointments.
- **Patient** — the pet, treated like a care patient. Stores health info (species, age, medical notes) and owns a list of appointments. Can return upcoming or past appointments.
- **Appointment** — a single care event (walk, feeding, vet visit). Has a date, time, duration, priority, and repeat frequency. Can be confirmed, cancelled, rescheduled, or auto-generate its next occurrence.
- **Caretaker** — the scheduling brain. Wraps a Person and provides planning logic: sorting by time, filtering by priority, detecting time conflicts, and summarizing the day.

**b. Design changes**

Yes — the `Caretaker` class grew significantly during Phase 4. The original design had four methods; the final version has eight. The biggest addition was `what_fits()` and `explain_plan()`, which weren't in the initial UML. These emerged from realizing that sorting tasks is only half the problem — a pet owner also needs to know what to do when they don't have time for everything. The `explain_plan()` method was added specifically so the UI could show reasoning, not just results.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: **priority level** (high/medium/low) and **time budget** (total available minutes in the day). Priority was chosen as the primary constraint because pet care tasks are not equal — a medication dose is non-negotiable, while a play session can be skipped. Time budget is the secondary constraint because even a dedicated owner has a finite day. These two together let the system make meaningful tradeoffs rather than just listing everything blindly.

**b. Tradeoffs**

The `what_fits()` and `explain_plan()` methods use a greedy algorithm — they pick appointments in priority order and include each one if it fits in the remaining time budget, never going back to reconsider earlier choices. This means a 60-minute budget might include three small high-priority tasks and skip a large medium-priority one, even if swapping one small task would allow the medium one to fit.

This tradeoff is reasonable for a daily pet care scenario because: (1) high-priority tasks like medications genuinely must come first, (2) the greedy approach is fast and easy to explain to a non-technical pet owner, and (3) the `explain_plan()` output tells the owner exactly what was skipped and why, so they can manually adjust if needed. A full knapsack optimization would be more "correct" but far harder to reason about.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across every phase: brainstorming class names and responsibilities in Phase 1, generating class skeletons and method stubs in Phase 2, wiring Streamlit session state in Phase 3, suggesting algorithmic approaches (greedy vs knapsack) in Phase 4, and drafting test cases in Phase 5. The most effective prompts were specific and context-rich — for example, "given this class structure, how should `Caretaker` retrieve all tasks from `Person`'s patients?" worked much better than "how do I connect classes in Python?"

**b. Judgment and verification**

During the class naming phase, the AI initially suggested generic names like `Owner`, `Pet`, `Task`, and `Scheduler`. These were functional but unremarkable. The decision was made to reframe the design around human healthcare roles (`Person`, `Patient`, `Appointment`, `Caretaker`) to make the system more intuitive and relatable. This wasn't an AI suggestion — it came from pushing back and asking for something more human-centered. The AI then built on that direction once the framing was established.

---

## 4. Testing and Verification

**a. What you tested**

22 automated tests covering:
- **Appointment lifecycle** — confirm, cancel, reschedule
- **Recurrence** — daily (+1 day), weekly (+7 days), none (returns None)
- **Patient management** — booking increases count, history vs upcoming separation
- **Caretaker sorting** — by time (chronological), by priority (high → medium → low)
- **Conflict detection** — same date/time flagged, different times pass cleanly
- **what_fits** — never exceeds budget, prefers high priority, returns empty on 0-budget
- **explain_plan** — contains INCLUDED/SKIPPED labels and flags conflicts

These tests matter because scheduling bugs are silent — a task silently skipped or a conflict ignored won't crash the app but will confuse the user.

**b. Confidence**

★★★★☆ (4/5) — Core scheduling logic is thoroughly tested. Edge cases to explore next: overlapping duration windows (two 30-min tasks at 07:00 and 07:15), patients with zero appointments, and budget exactly equal to total duration.

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the right call. Building and verifying all logic in `main.py` before touching the UI meant that when `app.py` was wired up, everything just worked. There were no "it works in the UI but not in the logic" bugs because the logic was already proven. The human-centered class naming also made the code easier to read and reason about throughout the project.

**b. What you would improve**

The conflict detection only flags exact time matches — it doesn't catch overlapping durations (e.g., a 30-minute task at 07:00 and a 20-minute task at 07:15 overlap but aren't flagged). A proper overlap check using start/end time windows would make the system genuinely useful for dense schedules. I'd also add a `TimeSlot` concept to make duration-aware scheduling cleaner.

**c. Key takeaway**

The most important lesson was that AI is a powerful amplifier, but the design decisions that made this system interesting — the human-role class names, the `explain_plan()` feature, the greedy-with-explanation approach — all came from human judgment about what would be useful and meaningful. AI accelerated the implementation; the architecture came from thinking carefully about the problem first.
