from dataclasses import dataclass
from typing import Literal


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""

    def get_required_tasks(self) -> list:
        pass


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    is_mandatory: bool = False
    preferred_time_of_day: Literal["morning", "afternoon", "evening", "any"] = "any"

    def is_high_priority(self) -> bool:
        pass

    def summary(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def set_available_time(self, minutes: int) -> None:
        pass


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.total_duration: int = 0

    def add_task(self, task: Task) -> None:
        pass

    def total_time(self) -> int:
        pass

    def explain(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self) -> DailyPlan:
        pass

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def explain_reasoning(self, plan: DailyPlan) -> str:
        pass
