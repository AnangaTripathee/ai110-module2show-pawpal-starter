"""Manual CLI verification for pawpal_system.py.

Builds a small owner/pet/task setup and prints today's schedule so we can
eyeball that the backend logic behaves before wiring up any UI.
"""

import sys
from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Recurrence


def main() -> None:
    # Ensure emoji (e.g. the ⚠️ conflict warning) print on consoles whose
    # default encoding isn't UTF-8, such as the Windows cp1252 terminal.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    now = datetime.now()

    # One owner with two pets.
    owner = Owner(owner_id=1, name="Ana", email="ana@example.com")
    rex = Pet(
        pet_id=10,
        name="Rex",
        species="dog",
        breed="Labrador",
        birthdate=datetime(2020, 3, 15).date(),
        medical_notes="None",
    )
    milo = Pet(
        pet_id=20,
        name="Milo",
        species="cat",
        breed="Tabby",
        birthdate=datetime(2022, 6, 1).date(),
        medical_notes="Sensitive stomach",
    )
    owner.add_pet(rex)
    owner.add_pet(milo)

    scheduler = Scheduler(owner)

    # Anchor the two "today" tasks to fixed hours (9:00 AM, 2:00 PM) on today's
    # date so the output is identical no matter what time the script is run.
    today_9am = now.replace(hour=9, minute=0, second=0, microsecond=0)
    today_2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)

    # Three tasks: two today (fixed hours), one on a different day, so the
    # "today" filter has something to include and something to exclude.
    tasks = [
        Task(
            task_id=1,
            pet_id=rex.pet_id,
            task_type=TaskType.WALK,
            scheduled_time=today_9am,
            duration_minutes=30,
            recurrence=Recurrence.DAILY,
            priority=2,
            completed=False,
        ),
        Task(
            task_id=2,
            pet_id=milo.pet_id,
            task_type=TaskType.FEEDING,
            scheduled_time=today_2pm,
            duration_minutes=15,
            recurrence=Recurrence.DAILY,
            priority=1,
            completed=False,
        ),
        Task(
            task_id=3,
            pet_id=rex.pet_id,
            task_type=TaskType.APPOINTMENT,
            scheduled_time=now + timedelta(days=2),
            duration_minutes=60,
            recurrence=Recurrence.NONE,
            priority=1,
            completed=False,
        ),
    ]
    for task in tasks:
        scheduler.add_task(task)

    # Map pet_id -> name so we can show a friendly name next to each task.
    pet_names = {pet.pet_id: pet.name for pet in owner.get_pets()}

    # Today's tasks, sorted by scheduled time.
    todays_tasks = sorted(
        scheduler.get_todays_tasks(), key=lambda t: t.scheduled_time
    )

    print("=" * 48)
    print(f"Today's Schedule for {owner.name} ({now.strftime('%Y-%m-%d')})")
    print("=" * 48)
    if not todays_tasks:
        print("No tasks scheduled for today.")
    else:
        for task in todays_tasks:
            time_str = task.scheduled_time.strftime("%H:%M")
            pet_name = pet_names.get(task.pet_id, "Unknown")
            print(
                f"  {time_str}  {task.task_type.value:<12} "
                f"{pet_name:<6} (priority {task.priority})"
            )
    print("=" * 48)
    print(f"{len(todays_tasks)} task(s) today, "
          f"{len(owner.get_all_tasks())} total across all pets.")

    # ------------------------------------------------------------------
    # Demo: sort_by_time() and filter_tasks()
    # ------------------------------------------------------------------
    # Add a few more tasks in a deliberately out-of-order sequence (their
    # scheduled_times are NOT increasing) so sort_by_time() has real work to do.
    today_11am = now.replace(hour=11, minute=0, second=0, microsecond=0)
    today_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
    today_5pm = now.replace(hour=17, minute=0, second=0, microsecond=0)

    extra_tasks = [
        Task(
            task_id=4,
            pet_id=rex.pet_id,
            task_type=TaskType.MEDICATION,
            scheduled_time=today_5pm,   # latest, added first
            duration_minutes=5,
            recurrence=Recurrence.DAILY,
            priority=1,
            completed=True,             # already done, to show completed filter
        ),
        Task(
            task_id=5,
            pet_id=milo.pet_id,
            task_type=TaskType.WALK,
            scheduled_time=today_7am,   # earliest, added in the middle
            duration_minutes=20,
            recurrence=Recurrence.NONE,
            priority=3,
            completed=False,
        ),
        Task(
            task_id=6,
            pet_id=rex.pet_id,
            task_type=TaskType.FEEDING,
            scheduled_time=today_11am,  # middle
            duration_minutes=10,
            recurrence=Recurrence.DAILY,
            priority=2,
            completed=False,
        ),
    ]
    for task in extra_tasks:
        scheduler.add_task(task)

    def format_task(task: Task) -> str:
        """One-line description of a task for the demo output."""
        time_str = task.scheduled_time.strftime("%Y-%m-%d %H:%M")
        pet_name = pet_names.get(task.pet_id, "Unknown")
        status = "done" if task.completed else "pending"
        return (
            f"  {time_str}  {task.task_type.value:<12} "
            f"{pet_name:<6} (priority {task.priority}, {status})"
        )

    # sort_by_time(): every task, earliest scheduled_time first.
    print()
    print("=" * 48)
    print("Sorted by time:")
    print("=" * 48)
    for task in scheduler.sort_by_time():
        print(format_task(task))

    # filter_tasks(pet_id=...): only one pet's tasks.
    print()
    print("=" * 48)
    print(f"{rex.name}'s tasks:")
    print("=" * 48)
    rex_tasks = sorted(
        scheduler.filter_tasks(pet_id=rex.pet_id), key=lambda t: t.scheduled_time
    )
    for task in rex_tasks:
        print(format_task(task))

    # filter_tasks(completed=False): only tasks still to do.
    print()
    print("=" * 48)
    print("Incomplete tasks:")
    print("=" * 48)
    incomplete_tasks = sorted(
        scheduler.filter_tasks(completed=False), key=lambda t: t.scheduled_time
    )
    for task in incomplete_tasks:
        print(format_task(task))

    # ------------------------------------------------------------------
    # Demo: completing a recurring task spawns the next occurrence
    # ------------------------------------------------------------------
    # Rex's WALK (task_id=1) recurs DAILY. Completing it should leave the
    # original marked done and add a fresh WALK for tomorrow, same time of day.
    daily_walk = next(t for t in rex.tasks if t.task_id == 1)

    print()
    print("=" * 48)
    print(f"{rex.name}'s tasks BEFORE completing the daily WALK:")
    print("=" * 48)
    for task in sorted(rex.tasks, key=lambda t: t.scheduled_time):
        print(format_task(task))

    new_task = scheduler.complete_task(daily_walk)

    print()
    print("=" * 48)
    print(f"{rex.name}'s tasks AFTER completing the daily WALK:")
    print("=" * 48)
    for task in sorted(rex.tasks, key=lambda t: t.scheduled_time):
        print(format_task(task))
    print(
        f"\nOriginal WALK (task_id={daily_walk.task_id}) is now marked done; "
        f"new occurrence task_id={new_task.task_id} generated for "
        f"{new_task.scheduled_time.strftime('%Y-%m-%d %H:%M')}."
    )

    # ------------------------------------------------------------------
    # Demo: detecting and reporting schedule conflicts
    # ------------------------------------------------------------------
    def format_conflict(pair: tuple[Task, Task]) -> str:
        """Friendly one-line warning for a conflicting task pair."""
        first, second = pair
        first_pet = pet_names.get(first.pet_id, "Unknown")
        second_pet = pet_names.get(second.pet_id, "Unknown")
        return (
            f"⚠️  Conflict: "
            f"{first.task_type.value} ({first_pet}) at "
            f"{first.scheduled_time.strftime('%H:%M')} overlaps with "
            f"{second.task_type.value} ({second_pet}) at "
            f"{second.scheduled_time.strftime('%H:%M')}"
        )

    # Add two overlapping tasks at the same start time — one per pet — so the
    # single owner would have to be in two places at once.
    today_10am = now.replace(hour=10, minute=0, second=0, microsecond=0)
    scheduler.add_task(Task(
        task_id=100,
        pet_id=rex.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=today_10am,
        duration_minutes=30,
        recurrence=Recurrence.NONE,
        priority=2,
        completed=False,
    ))
    scheduler.add_task(Task(
        task_id=101,
        pet_id=milo.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=today_10am,
        duration_minutes=15,
        recurrence=Recurrence.NONE,
        priority=1,
        completed=False,
    ))

    print()
    print("=" * 48)
    print("Conflict check:")
    print("=" * 48)
    conflicts = scheduler.detect_conflicts()
    if not conflicts:
        print("No conflicts found.")
    else:
        for pair in conflicts:
            print(format_conflict(pair))


if __name__ == "__main__":
    main()
