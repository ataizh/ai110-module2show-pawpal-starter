# PawPal+ Project Reflection

## 1. System Design

### Core User Actions
1. **Add a pet** — enter your name and your pet's info to get started
2. **Schedule tasks** — add things like walks, feedings, or vet visits with a time and priority
3. **Generate a daily plan** — see everything sorted out for the day, with warnings if anything overlaps

**a. Initial design**

I went with four classes. I didn't want to just do the obvious "Owner, Pet, Task, Scheduler" thing because it felt too generic, so I modeled them after how a real care situation works — like a doctor's office. So I ended up with Person (the owner), Patient (the pet), Appointment (the task), and Caretaker (the one managing everything).

- **Person** — holds the owner's info and keeps track of all their pets
- **Patient** — the pet, but treated like someone with a health record — has medical notes, upcoming appointments, visit history
- **Appointment** — one care event, like a walk or medication. Has a time, date, how long it takes, priority, and whether it repeats
- **Caretaker** — the part that actually thinks. It figures out what fits in the day, what conflicts, and how to explain the plan

**b. Design changes**

The Caretaker ended up way bigger than I planned. I originally had like four methods on it but ended up with eight. The two I didn't expect to add were `what_fits()` and `explain_plan()`. I realized halfway through that just sorting tasks by time isn't that helpful — what a pet owner actually needs to know is "I only have an hour today, what should I actually do?" So I built those two methods around that idea. `explain_plan()` was specifically so the app could tell you *why* something got skipped, not just that it did.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The two things the scheduler cares about are priority (high/medium/low) and how much time you have. I made priority the main thing because not all pet tasks are equal — giving your dog his medication is not the same as taking him to the park. Time budget is secondary because you can't just pile everything in. Those two together actually let the system make real decisions instead of just listing stuff.

**b. Tradeoffs**

The way `what_fits()` works is greedy — it goes through tasks from high to low priority and just adds each one if it fits. It never goes back and rearranges. That means sometimes it'll grab three short high-priority tasks and then skip a medium one even though dropping one small task would've made room for it.

I kept it greedy on purpose though. For a pet care app, the person using it isn't a CS student — they just want to know what to do today. A greedy approach is easy to explain and easy to understand. And since `explain_plan()` shows exactly what got skipped and why, the user can just manually reschedule anything that got cut. A full knapsack solution would technically be more optimal but honestly it would've been overkill here.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI pretty much the whole way through. In the design phase I used it to bounce ideas for class names and structure. Once I had the UML I used it to generate the skeleton code. For the Streamlit part I asked it how session_state works because I hadn't used it before. For the algorithms it helped me think through the greedy vs. optimal tradeoff. For testing it drafted most of the test functions.

The prompts that actually worked were the specific ones. Like instead of "how do I connect my classes" I'd ask "given this Person and Patient structure, how should Caretaker get all appointments across all patients" — that kind of thing got useful answers way faster.

**b. Judgment and verification**

The biggest thing I changed was the class names. AI kept suggesting Owner, Pet, Task, Scheduler which works but it's boring and doesn't really say anything. I pushed back and asked for something more human and relatable, and we landed on Person/Patient/Appointment/Caretaker. That wasn't AI's idea — I had to keep rejecting the suggestions until it went in a different direction. Once I set that framing though, it built on it well.

I also didn't just paste in test code without reading it. A couple of the generated tests were testing the wrong thing or had fixtures set up in a way that would pass even if the logic was broken. I caught those by actually reading through what each assertion was checking.

---

## 4. Testing and Verification

**a. What you tested**

I ended up with 22 tests across all the main behaviors:
- **Appointment lifecycle** — confirming, cancelling, rescheduling
- **Recurrence** — daily and weekly both generate the right next date, and "none" returns nothing
- **Patient management** — adding an appointment actually increases the count, history only shows attended ones
- **Sorting** — by time comes back in order, by priority goes high to low
- **Conflicts** — same date and time gets flagged, different times don't
- **what_fits** — never goes over budget, picks high priority first, returns empty if budget is 0
- **explain_plan** — shows INCLUDED and SKIPPED labels, mentions conflicts when they exist

The reason I focused on those is because scheduling bugs don't throw errors — they just quietly give you the wrong answer. If a conflict doesn't get flagged or a task gets skipped silently, the app still runs fine but the user gets bad info.

**b. Confidence**

I'd say 4 out of 5. The core stuff works and I tested the main edge cases. What I didn't test is overlapping durations — like if one appointment is 30 minutes starting at 7am and another starts at 7:15, those overlap but my conflict detection won't catch it since it only checks exact start times. That's the next thing I'd fix.

---

## 5. Reflection

**a. What went well**

Writing all the logic in `main.py` first before touching the UI was probably the best decision I made. Every time I ran it in the terminal and it worked, I knew the class was actually doing what I thought it was. So when I wired it into Streamlit there were basically no surprises. The naming thing also helped a lot — calling it Patient instead of Pet made me think about it differently and the design got better because of it.

**b. What you would improve**

The conflict detection is too basic right now. It only catches exact time matches, so two appointments that overlap by 15 minutes slip through. I'd want to redo that with actual start/end interval math. I'd also add a way to delete or edit appointments in the UI — right now you can add and mark done but you can't change something you already booked.

**c. Key takeaway**

AI is really good at filling in the blanks once you know what you're building, but it can't figure out what you're building for you. Every time I gave it a vague prompt I got something generic back. Every time I came in with a clear idea of what I wanted — even if I couldn't code it yet — it actually helped. The class naming thing is a good example. I had to know I didn't want the generic version before I could push back and get something better. So the main thing I learned is that having a real opinion about your design before you start prompting makes everything go faster and the output way better.
