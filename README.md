# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

PS C:\Users\anang\ai110-module2show-pawpal-starter> python main.py
================================================
Today's Schedule for Ana (2026-07-07)
================================================
  09:00  WALK         Rex    (priority 2)
  14:00  FEEDING      Milo   (priority 1)
================================================
2 task(s) today, 3 total across all pets.

## 🧪 Testing PawPal+

PS C:\Users\anang\ai110-module2show-pawpal-starter> python -m pytest -v
=========================================================== test session starts ===========================================================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\anang\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\anang\ai110-module2show-pawpal-starter
plugins: anyio-4.9.0
collected 5 items                                                                                                                          

tests/test_pawpal.py::test_task_completion PASSED                                                                                    [ 20%]
tests/test_pawpal.py::test_task_addition PASSED                                                                                      [ 40%]
tests/test_pawpal.py::test_sort_by_time PASSED                                                                                       [ 60%]
tests/test_pawpal.py::test_recurrence_generates_next_occurrence PASSED                                                               [ 80%]
tests/test_pawpal.py::test_detect_conflicts PASSED                                                                                   [100%]

============================================================ 5 passed in 0.09s ============================================================

Confidence Level:(4/5)

All five core behaviors — completion, addition, sorting, recurrence, and conflict detection — are covered and passing. I'd hold back from a full 5/5 since edge cases like same-timestamp ties beyond the basic conflict check, or a pet with zero tasks, aren't explicitly tested yet.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_time()`, `sort_by_priority()` | Sort by time or priority (1 = highest) |
| Filtering | `filter_tasks(pet_id, completed)` | Filter by pet and/or completion status |
| Conflict handling | `detect_conflicts()` | Flags overlapping task times, even across different pets |
| Recurring tasks | `complete_task(task)` | Completing a daily/weekly task auto-creates the next one |

## Features

- **Owner & Pet management** — track multiple pets per owner, each with their own care details (species, breed, birthdate, medical notes)
- **Task tracking** — feedings, walks, medications, and appointments, each with a scheduled time, duration, and priority
- **Sorting** — view tasks sorted by time (`sort_by_time()`) or by priority (`sort_by_priority()`, 1 = highest)
- **Filtering** — narrow the task list by pet and/or completion status (`filter_tasks()`)
- **Conflict detection** — automatically flags overlapping tasks, even across different pets, since one owner can't be in two places at once (`detect_conflicts()`)
- **Recurring tasks** — completing a daily or weekly task automatically generates the next occurrence (`complete_task()`), while keeping the original as history
- **Today's schedule** — a filtered, prioritized view of what's due today (`get_todays_tasks()`)

## 📸 Demo Walkthrough

PawPal+ can be used two ways: as a Streamlit web app (`app.py`) or verified directly in the terminal (`main.py`).

**Main UI features (Streamlit app):**
- Add an owner and a pet
- Add tasks (feeding, walk, medication, appointment) with a time, duration, priority, and optional recurrence
- Generate a schedule, viewable sorted by time or priority
- Filter the schedule by pet or to show only incomplete tasks
- See conflict warnings if two tasks overlap
- Mark a recurring task complete directly from the schedule, which automatically creates the next occurrence

**Example workflow:**
1. Enter an owner's name and add a pet (e.g. "Rex", a dog)
2. Add a task — e.g. a daily 9:00 AM walk
3. Add a second task that overlaps it — e.g. a 9:00 AM feeding for another pet
4. Click "Generate schedule" — the app shows both tasks and flags the overlap with a conflict warning
5. Mark the daily walk complete — a new walk task automatically appears for tomorrow

**Key Scheduler behaviors demonstrated:**
- Tasks added out of order are correctly sorted by time
- Filtering by pet or completion status narrows the list correctly
- Overlapping tasks across different pets are flagged with a clear warning
- Completing a recurring task generates its next occurrence while preserving the completed original

**Sample CLI output** (`python main.py`):

```
================================================
Today's Schedule for Ana (2026-07-07)
================================================
  09:00  WALK         Rex    (priority 2)
  14:00  FEEDING      Milo   (priority 1)
================================================
2 task(s) today, 3 total across all pets.

================================================
Conflict check:
================================================
⚠️  Conflict: WALK (Rex) at 10:00 overlaps with FEEDING (Milo) at 10:00
```
