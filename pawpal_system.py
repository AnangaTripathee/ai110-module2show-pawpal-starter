"""PawPal+ pet care system — class skeleton generated from diagrams/uml_draft.mmd.

Stubs only: attributes, method signatures, and type hints. No logic yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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

    def get_age(self) -> int:
        ...


@dataclass
class Task:
    task_id: int
    pet_id: int
    task_type: TaskType
    scheduled_time: datetime
    recurrence: Recurrence
    priority: int
    completed: bool

    def mark_complete(self) -> None:
        ...

    def is_overdue(self) -> bool:
        ...

    def conflicts_with(self, other_task: "Task") -> bool:
        ...


class Owner:
    def __init__(self, owner_id: int, name: str, email: str) -> None:
        self.owner_id: int = owner_id
        self.name: str = name
        self.email: str = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        ...

    def get_pets(self) -> list[Pet]:
        ...


class Scheduler:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        ...

    def get_tasks_for_pet(self, pet_id: int) -> list[Task]:
        ...

    def get_todays_tasks(self) -> list[Task]:
        ...

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        ...

    def sort_by_priority(self) -> list[Task]:
        ...
