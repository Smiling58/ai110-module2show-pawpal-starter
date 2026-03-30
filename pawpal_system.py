from dataclasses import dataclass, field
from datetime import date
from typing import Literal

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}
TIME_OF_DAY_RANK = {"morning": 0, "afternoon": 1, "evening": 2, "any": 3}


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: Literal["low", "medium", "high"]
    is_mandatory: bool = False
    preferred_time_of_day: Literal["morning", "afternoon", "evening", "any"] = "any"
    frequency: str = "daily"  # e.g. "daily", "weekly", "as needed"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"

    def summary(self) -> str:
        """Return a single-line human-readable description of the task."""
        mandatory_tag = " [mandatory]" if self.is_mandatory else ""
        return (
            f"{self.title} ({self.category}) — "
            f"{self.duration_minutes} min, {self.priority} priority{mandatory_tag}"
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_required_tasks(self) -> list[Task]:
        """Return only the tasks marked as mandatory for this pet."""
        return [t for t in self.tasks if t.is_mandatory]


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: str = ""):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        """Update the owner's daily time budget in minutes."""
        self.available_minutes = minutes

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class DailyPlan:
    def __init__(self, date: str):
        self.date = date
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a task to the scheduled list."""
        self.scheduled_tasks.append(task)

    def total_time(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def explain(self) -> str:
        """Produce a readable summary of what was scheduled and why."""
        lines = [f"Daily plan for {self.date}", f"Total time: {self.total_time()} min\n"]

        if self.scheduled_tasks:
            lines.append("Scheduled:")
            for t in self.scheduled_tasks:
                reason = "mandatory" if t.is_mandatory else f"{t.priority} priority"
                lines.append(f"  + {t.title} ({t.duration_minutes} min) — included: {reason}")

        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for t in self.skipped_tasks:
                lines.append(f"  - {t.title} ({t.duration_minutes} min) — not enough time remaining")

        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> DailyPlan:
        """Build a DailyPlan by scheduling mandatory tasks first, then filling by priority."""
        today = str(date.today())
        plan = DailyPlan(date=today)
        budget = self.owner.available_minutes

        all_tasks = self.owner.get_all_tasks()
        mandatory, optional = self._separate_mandatory(all_tasks)

        # Always schedule mandatory tasks regardless of budget
        for task in mandatory:
            plan.add_task(task)
            budget -= task.duration_minutes

        # Sort optional tasks and fill remaining budget
        sorted_optional = self.sort_by_priority(optional)
        scheduled, skipped = self.filter_by_time(sorted_optional, budget)

        for task in scheduled:
            plan.add_task(task)
        plan.skipped_tasks = skipped

        return plan

    def _separate_mandatory(self, tasks: list[Task]) -> tuple[list[Task], list[Task]]:
        """Split tasks into (mandatory, optional) lists."""
        mandatory = [t for t in tasks if t.is_mandatory]
        optional = [t for t in tasks if not t.is_mandatory]
        return mandatory, optional

    def filter_by_time(
        self, tasks: list[Task], remaining_minutes: int
    ) -> tuple[list[Task], list[Task]]:
        """Greedily fit tasks into the time budget; return (scheduled, skipped)."""
        scheduled, skipped = [], []
        for task in tasks:
            if task.duration_minutes <= remaining_minutes:
                scheduled.append(task)
                remaining_minutes -= task.duration_minutes
            else:
                skipped.append(task)
        return scheduled, skipped

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks high-to-low priority, with preferred_time_of_day as tiebreaker."""
        return sorted(
            tasks,
            key=lambda t: (
                -PRIORITY_RANK[t.priority],
                TIME_OF_DAY_RANK[t.preferred_time_of_day],
            ),
        )
