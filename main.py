"""Manual CLI verification for pawpal_system.py.

Builds a small owner/pet/task setup and prints today's schedule so we can
eyeball that the backend logic behaves before wiring up any UI.
"""

from datetime import datetime, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, TaskType, Recurrence


def main() -> None:
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


if __name__ == "__main__":
    main()
