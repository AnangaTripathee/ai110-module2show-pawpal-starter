"""PawPal+ pet care system — Phase 2 implementation.

Backend logic for Owner, Pet, Task, and Scheduler, plus the TaskType and
Recurrence enums. Built from diagrams/uml_draft.mmd.

Storage model: a Task is owned by a Pet (Pet.tasks). The Owner aggregates
tasks across all its pets, and the Scheduler reads tasks through the Owner
rather than keeping its own separate list — there is one source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum


class TaskType(Enum):
    FEEDING = "FEEDING"
    WALK = "WALK"
    MEDICATION = "MEDICATION"
    APPOINTMENT = "APPOINTMENT"


class Recurrence(Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


@dataclass
class Pet:
    pet_id: int
    name: str
    species: str
    breed: str
    birthdate: date
    medical_notes: str
    # Each pet owns its tasks; this is the canonical place tasks live.
    tasks: list[Task] = field(default_factory=list)

    def get_age(self) -> int:
        """Return the pet's age in whole years as of today."""
        today = date.today()
        # Subtract 1 if this year's birthday hasn't happened yet.
        had_birthday_this_year = (today.month, today.day) >= (
            self.birthdate.month,
            self.birthdate.day,
        )
        return today.year - self.birthdate.year - (0 if had_birthday_this_year else 1)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Task:
    task_id: int
    pet_id: int
    task_type: TaskType
    scheduled_time: datetime
    duration_minutes: int
    recurrence: Recurrence
    # priority convention: 1 = highest priority, higher numbers = lower priority
    priority: int
    completed: bool

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def end_time(self) -> datetime:
        """The moment this task finishes, based on its duration."""
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)

    def is_overdue(self, now: datetime | None = None) -> bool:
        """True if the task is unfinished and its scheduled end is in the past."""
        now = now or datetime.now()
        return not self.completed and self.end_time() < now

    def conflicts_with(self, other_task: "Task") -> bool:
        """True if this task's time interval overlaps the other's.

        Uses half-open intervals [start, end): two tasks that merely touch
        (one ends exactly when the other begins) do not conflict. A task is
        never considered in conflict with itself.
        """
        if self.task_id == other_task.task_id:
            return False
        return (
            self.scheduled_time < other_task.end_time()
            and other_task.scheduled_time < self.end_time()
        )


class Owner:
    def __init__(self, owner_id: int, name: str, email: str) -> None:
        """Create an owner with no pets yet."""
        self.owner_id: int = owner_id
        self.name: str = name
        self.email: str = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self) -> list[Task]:
        """Flatten and return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Create a scheduler that reads tasks through the given owner."""
        # The scheduler does not store tasks itself; it reads them through the
        # owner's pets so there is a single source of truth.
        self.owner: Owner = owner

    def add_task(self, task: Task) -> None:
        """Route a task to the pet it belongs to (matched by task.pet_id)."""
        for pet in self.owner.get_pets():
            if pet.pet_id == task.pet_id:
                pet.add_task(task)
                return
        raise ValueError(f"No pet with pet_id={task.pet_id} found for this owner.")

    def get_tasks_for_pet(self, pet_id: int) -> list[Task]:
        """Return the tasks belonging to a single pet."""
        for pet in self.owner.get_pets():
            if pet.pet_id == pet_id:
                return pet.tasks
        return []

    def get_todays_tasks(self, now: datetime | None = None) -> list[Task]:
        """Return all tasks (across pets) scheduled for today's date."""
        today = (now or datetime.now()).date()
        return [
            task
            for task in self.owner.get_all_tasks()
            if task.scheduled_time.date() == today
        ]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Find overlapping task pairs at the owner level.

        Conflicts are evaluated across all pets, not per-pet: a single owner
        can't be in two places at once. Completed tasks are ignored since they
        no longer compete for the owner's time.
        """
        tasks = [t for t in self.owner.get_all_tasks() if not t.completed]
        conflicts: list[tuple[Task, Task]] = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].conflicts_with(tasks[j]):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

    def sort_by_priority(self) -> list[Task]:
        """Return all tasks sorted by priority (1 = highest priority first)."""
        return sorted(self.owner.get_all_tasks(), key=lambda task: task.priority)
