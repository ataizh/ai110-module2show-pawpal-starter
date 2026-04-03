# PawPal+ Project Reflection

## 1. System Design

### Core User Actions
1. Add a pet with their info like name, species and age
2. Schedule care tasks like walks, feedings, or vet visits
3. See today's schedule sorted out and get warned if anything overlaps

**a. Initial design**

I used the four classes Owner, Pet, Task, and Scheduler. Owner holds the persons info and their list of pets. Pet has the pets details and stores all its tasks. Task is like one care event, it has a title, time, date, how long it takes, priority and if it repeats. Scheduler is the one that does all the smart stuff like sorting and finding conflicts.

**b. Design changes**

Scheduler ended up way bigger than I thought. I started with like 4 methods and ended up needing more. I added what_fits() and explain_plan() because I realized just showing a sorted list wasnt that helpful. If you only have an hour you need to know what to actually do, not see everything. So those two methods handle that — one picks what fits in your time, the other explains why stuff got skipped.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at two things — priority level and how much time you have. I made priority the main one because some tasks genuinely cant be skipped like giving medication. Time is the second thing because you cant just schedule everything if you only have 30 minutes free.

**b. Tradeoffs**

The what_fits() method is greedy, it just picks tasks from high to low priority and adds them if they fit, it never goes back. So sometimes it takes a few small high priority tasks and skips a medium one even though swapping one small one wouldve made room. I kept it that way on purpose because its easier to understand and the explain_plan() output already tells you what got skipped and why so you can fix it yourself. A smarter algorithm wouldve been too complicated for what this needs.

---

## 3. AI Collaboration

**a. How you used AI**

I used Copilot through most of it. At the start I used it to help figure out what methods each class needed. When I got to Streamlit I asked how session_state works because I didnt know. For the algorithms I asked it to help write sort_by_time and detect_conflicts. For testing it helped me write most of the test functions.

The prompts that worked better were more specific. Like asking "how should Scheduler get all tasks from Owner's pets" got a way better answer than just asking how to connect classes.

**b. Judgment and verification**

When I asked it to write conflict detection the first version only checked if two tasks had the same start time exactly. That wouldnt catch cases where a task starts in the middle of another one. I told it that and it fixed it to use interval math instead. I also read through the test code it generated because a couple of them werent actually testing the right thing, they wouldve passed even with broken logic.

---

## 4. Testing and Verification

**a. What you tested**

I have 24 tests total covering:
- Task lifecycle — mark_complete, unmark, reschedule
- Recurrence — daily adds 1 day, weekly adds 7, none returns nothing
- Pet — adding a task increases count, completed and pending filter right
- Owner — add_pet works, get_all_tasks returns the right tuples
- Sorting — time order and priority order both work
- Filtering — by pet name and by status
- Conflicts — same time gets flagged, different times dont
- what_fits — stays under budget, prefers high priority
- explain_plan — shows INCLUDED and SKIPPED correctly

Scheduling bugs are tricky because they dont crash the app they just give wrong info, so I wanted tests that would actually catch that.

**b. Confidence**

4 out of 5. The main stuff all works. The thing I didnt test is when two tasks overlap in duration but not start time, like one starts at 7:00 for 30 min and another at 7:15. The conflict check misses that because it only compares start times. Thats what I'd fix next.

---

## 5. Reflection

**a. What went well**

Building everything in main.py first before touching the UI was really helpful. I could just run it in the terminal and see if the logic was right without dealing with Streamlit at the same time. When I finally connected it to the UI there were barely any issues.

**b. What you would improve**

The conflict detection like I said only catches exact time matches. Id redo it with proper interval math. Id also add a way to delete or edit tasks in the app, right now you can add and mark done but you cant change anything after booking it.

**c. Key takeaway**

AI is useful but it needs you to already have a direction. When I gave it vague questions I got generic answers. When I knew what I wanted and just needed help writing it, it actually worked well. The main thing I learned is you have to stay in charge of the design decisions, AI is good for the implementation parts but not for figuring out what you actually want to build.
