# PawPal+ Project Reflection

## 1. System Design
- Add a pet to an owners profile
- Schedule a task
- View today's/upcoming tasks, sorted by priority across all of an owners pet

**a. Initial design**

- My design is built around four core classes, laid out in `diagrams/uml_draft.mmd`:

- **Owner** — represents the app's user. Holds owner_id, name, email, and a
  list of Pets. Responsible for managing that list (add_pet, get_pets). The
  relationship to Pet is composition (Owner "owns" its Pets outright), since
  a pet record doesn't meaningfully exist without an owner in this app.

- **Pet** — represents an individual animal. Holds descriptive attributes
  (pet_id, name, species, breed, birthdate, medical_notes) and is
  responsible for pet-specific derived info like calculating age from
  birthdate.

- **Task** — represents a single care event (feeding, walk, medication, or
  appointment). Holds scheduling info (scheduled_time, recurrence, priority,
  completed) and links to a pet via pet_id rather than holding a direct Pet
  object reference. This was a deliberate choice to avoid circular
  references between Pet and Task and to keep Task easy to serialize and
  test independently. Task is responsible for its own state changes
  (mark_complete) and for evaluating itself (is_overdue, conflicts_with).

- **Scheduler** — the orchestrator. Holds the full list of Tasks and is
  responsible for organizing them: filtering by pet, finding today's tasks,
  detecting conflicts, and sorting by priority. Scheduler has no direct
  relationship to Owner — it only needs pet_id to filter, which keeps
  scheduling logic decoupled from the ownership hierarchy.

Pet and Task are implemented as Python dataclasses, since they're primarily
data containers with a couple of small behaviors. Owner and Scheduler are
regular classes, since they're more about managing collections and
orchestrating behavior than holding fixed data. TaskType and Recurrence are
implemented as Enums to constrain their values to a fixed set.

**b. Design changes**

- fter AI review of the skeleton, I made two changes to `Task`:

1. Added `duration_minutes`, since conflict detection needs time *intervals*,
   not just a single `scheduled_time` instant.
2. Documented the `priority` convention (1 = highest) with a comment, since
   sort direction was ambiguous.

Two things came up in review that I'm deferring to implementation: conflicts
should be checked at the owner level (not per-pet, since one owner can't be
in two places at once), and the recurrence model (expand on demand vs.
generate instances ahead of time) is still undecided.

I kept `pet_id` instead of a direct `Pet` reference on `Task` — the review
confirmed it avoids stale references and keeps `Task` easy to serialize.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- My `detect_conflicts()` method compares every pair of tasks (O(n²)) rather
than sorting by time first and only comparing neighbors (O(n log n)). I
asked my AI assistant for a more efficient alternative, and while a
sort-then-sweep approach would scale better, I kept the simpler pairwise
version — for a personal pet-care app with realistically a few dozen tasks
at most, the performance difference is negligible, and the nested-loop
version is easier to read and reason about. I'd revisit this only if the
app needed to handle a much larger number of tasks (e.g. a multi-pet
boarding facility rather than a single household).

Another tradeoff: conflicts are detected as overlapping time *intervals*
(using `scheduled_time` + `duration_minutes`), not just exact time matches.
This is more correct — two tasks starting 10 minutes apart can still
genuinely conflict if one runs long — but it does mean `Task` needs an
explicit `duration_minutes` field to work, which wasn't in my original UML.

## 3. AI Collaboration

**a. How you used AI**

- I used AI throughout — brainstorming the UML design, generating class
skeletons, implementing logic, writing tests, and drafting docs. Keeping
separate chat sessions for implementation vs. algorithm brainstorming
helped: the brainstorm session gave fresh options instead of just building
on whatever we'd already decided.

**b. Judgment and verification**

- When refactoring `detect_conflicts()`, my AI assistant offered a readable
version (`itertools.combinations`) and a faster one (sort-then-sweep). I
picked the readable one — my task lists are small, so the performance gain
was theoretical, not real. I verified this by re-running my tests and CLI
demo to confirm behavior didn't change.

I also caught a case where a commit silently failed (I closed the commit
editor wrong) and a file got reverted without me noticing — a reminder that
I still need to check `git status`/`git log` myself instead of assuming
things "stuck."

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- Being the "lead architect" meant making the calls AI couldn't make for
me — which tradeoffs were worth it, and when to actually verify something
worked instead of assuming it did. AI was great at generating options and
explaining tradeoffs, but picking between them was always on me.
