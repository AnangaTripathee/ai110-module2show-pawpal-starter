"""Basic pytest coverage for pawpal_system backend logic."""

from datetime import date, datetime

from pawpal_system import Pet, Task, TaskType, Recurrence


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
