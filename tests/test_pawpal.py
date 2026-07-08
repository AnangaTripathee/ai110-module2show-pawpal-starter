"""Basic pytest coverage for pawpal_system backend logic."""

from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task, TaskType, Recurrence


def make_task(completed: bool = False) -> Task:
    """Build a Task with minimal valid fixture data."""
    return Task(
        task_id=1,
        pet_id=10,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 7, 9, 0),
        duration_minutes=30,
        recurrence=Recurrence.NONE,
        priority=1,
        completed=completed,
    )


def make_pet() -> Pet:
    """Build a Pet with minimal valid fixture data."""
    return Pet(
        pet_id=10,
        name="Rex",
        species="dog",
        breed="Labrador",
        birthdate=date(2020, 3, 15),
        medical_notes="None",
    )


def test_task_completion():
    task = make_task(completed=False)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_task_addition():
    pet = make_pet()
    assert len(pet.tasks) == 0

    pet.add_task(make_task())

    assert len(pet.tasks) == 1


def make_scheduler_with_pet(pet: Pet | None = None) -> Scheduler:
    """Build an Owner with one registered pet and a Scheduler over it."""
    owner = Owner(owner_id=1, name="Sam", email="sam@example.com")
    owner.add_pet(pet or make_pet())
    return Scheduler(owner)


def test_sort_by_time():
    pet = make_pet()
    scheduler = make_scheduler_with_pet(pet)

    # Add tasks out of chronological order (noon, then 9am, then 3pm).
    scheduler.add_task(
        Task(
            task_id=1,
            pet_id=pet.pet_id,
            task_type=TaskType.WALK,
            scheduled_time=datetime(2026, 7, 7, 12, 0),
            duration_minutes=30,
            recurrence=Recurrence.NONE,
            priority=1,
            completed=False,
        )
    )
    scheduler.add_task(
        Task(
            task_id=2,
            pet_id=pet.pet_id,
            task_type=TaskType.FEEDING,
            scheduled_time=datetime(2026, 7, 7, 9, 0),
            duration_minutes=15,
            recurrence=Recurrence.NONE,
            priority=1,
            completed=False,
        )
    )
    scheduler.add_task(
        Task(
            task_id=3,
            pet_id=pet.pet_id,
            task_type=TaskType.MEDICATION,
            scheduled_time=datetime(2026, 7, 7, 15, 0),
            duration_minutes=5,
            recurrence=Recurrence.NONE,
            priority=1,
            completed=False,
        )
    )

    ordered = scheduler.sort_by_time()

    times = [task.scheduled_time for task in ordered]
    assert times == sorted(times)
    assert times == [
        datetime(2026, 7, 7, 9, 0),
        datetime(2026, 7, 7, 12, 0),
        datetime(2026, 7, 7, 15, 0),
    ]


def test_recurrence_generates_next_occurrence():
    pet = make_pet()
    scheduler = make_scheduler_with_pet(pet)

    original = Task(
        task_id=1,
        pet_id=pet.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 7, 8, 0),
        duration_minutes=20,
        recurrence=Recurrence.DAILY,
        priority=2,
        completed=False,
    )
    scheduler.add_task(original)

    # Pin `now` to the original's time so the next occurrence is deterministic.
    new_task = scheduler.complete_task(original, now=original.scheduled_time)

    # (a) the original task is now completed.
    assert original.completed is True

    # (b) a fresh, uncompleted task exists exactly one day later, same details.
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.scheduled_time == original.scheduled_time + timedelta(days=1)
    assert new_task.pet_id == original.pet_id
    assert new_task.task_type == original.task_type
    assert new_task.priority == original.priority
    assert new_task in scheduler.get_tasks_for_pet(pet.pet_id)


def test_detect_conflicts():
    # Two pets under the same owner, whose tasks overlap in time.
    dog = make_pet()  # pet_id=10
    cat = Pet(
        pet_id=20,
        name="Whiskers",
        species="cat",
        breed="Tabby",
        birthdate=date(2021, 6, 1),
        medical_notes="None",
    )
    owner = Owner(owner_id=1, name="Sam", email="sam@example.com")
    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)

    dog_task = Task(
        task_id=1,
        pet_id=dog.pet_id,
        task_type=TaskType.WALK,
        scheduled_time=datetime(2026, 7, 7, 9, 0),
        duration_minutes=60,
        recurrence=Recurrence.NONE,
        priority=1,
        completed=False,
    )
    cat_task = Task(
        task_id=2,
        pet_id=cat.pet_id,
        task_type=TaskType.FEEDING,
        scheduled_time=datetime(2026, 7, 7, 9, 30),  # overlaps the walk
        duration_minutes=30,
        recurrence=Recurrence.NONE,
        priority=1,
        completed=False,
    )
    scheduler.add_task(dog_task)
    scheduler.add_task(cat_task)

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    flagged = {task.task_id for task in conflicts[0]}
    assert flagged == {dog_task.task_id, cat_task.task_id}

    # Non-overlapping tasks must NOT be flagged: move the cat's task to start
    # after the dog's walk ends (10:00), leaving no overlap.
    cat_task.scheduled_time = datetime(2026, 7, 7, 10, 30)
    assert scheduler.detect_conflicts() == []
