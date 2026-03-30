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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The `what_fits()` and `explain_plan()` methods use a greedy algorithm — they pick appointments in priority order and include each one if it fits in the remaining time budget, never going back to reconsider earlier choices. This means a 60-minute budget might include three small high-priority tasks and skip a large medium-priority one, even if swapping one small task would allow the medium one to fit.

This tradeoff is reasonable for a daily pet care scenario because: (1) high-priority tasks like medications genuinely must come first, (2) the greedy approach is fast and easy to explain to a non-technical pet owner, and (3) the `explain_plan()` output tells the owner exactly what was skipped and why, so they can manually adjust if needed. A full knapsack optimization would be more "correct" but far harder to reason about.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
