from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(**overrides):
    defaults = dict(
        title="Morning walk",
        category="walk",
        duration_minutes=30,
        priority="high",
    )
    return Task(**{**defaults, **overrides})


def make_owner(minutes: int = 90) -> Owner:
    owner = Owner(name="Alex", available_minutes=minutes)
    pet = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(pet)
    return owner


# ---------------------------------------------------------------------------
# Existing tests (preserved)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(make_task(title="Feeding", category="feeding", duration_minutes=10, priority="medium"))
    assert len(pet.tasks) == 1
    pet.add_task(make_task(title="Nail trim", category="grooming", duration_minutes=15, priority="low"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_mark_complete_daily_creates_next_task_due_tomorrow():
    """Daily tasks should produce a new task due exactly one day from today."""
    task = make_task(frequency="daily")
    next_task = task.mark_complete()

    expected_due = str(date.today() + timedelta(days=1))
    assert next_task is not None
    assert next_task.due_date == expected_due
    assert next_task.completed is False
    assert next_task.title == task.title


def test_mark_complete_weekly_creates_next_task_due_in_7_days():
    """Weekly tasks should produce a new task due 7 days from today."""
    task = make_task(frequency="weekly")
    next_task = task.mark_complete()

    expected_due = str(date.today() + timedelta(weeks=1))
    assert next_task is not None
    assert next_task.due_date == expected_due


def test_mark_complete_as_needed_returns_none():
    """Non-recurring tasks return None — no next occurrence is created."""
    task = make_task(frequency="as needed")
    next_task = task.mark_complete()
    assert next_task is None


def test_advance_recurring_appends_new_task_to_pet():
    """advance_recurring should append the next occurrence to the pet's task list."""
    owner = make_owner()
    pet = owner.pets[0]
    task = make_task(frequency="daily")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.advance_recurring(pet, task)

    # Original stays (now completed), new one appended
    assert len(pet.tasks) == 2
    assert pet.tasks[0].completed is True
    assert pet.tasks[1].completed is False


def test_advance_recurring_non_recurring_does_not_append():
    """advance_recurring on an 'as needed' task must not grow the pet's task list."""
    owner = make_owner()
    pet = owner.pets[0]
    task = make_task(frequency="as needed")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    result = scheduler.advance_recurring(pet, task)

    assert result is None
    assert len(pet.tasks) == 1  # only the original, now completed


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_priority_orders_high_before_medium_before_low():
    """sort_by_priority must return tasks in descending priority order."""
    owner = make_owner()
    scheduler = Scheduler(owner)

    tasks = [
        make_task(title="Low task", priority="low"),
        make_task(title="High task", priority="high"),
        make_task(title="Med task", priority="medium"),
    ]
    result = scheduler.sort_by_priority(tasks)
    assert [t.priority for t in result] == ["high", "medium", "low"]


def test_sort_by_priority_tiebreaker_morning_before_afternoon_before_evening():
    """When priority is equal, morning slots must sort before afternoon, then evening."""
    owner = make_owner()
    scheduler = Scheduler(owner)

    tasks = [
        make_task(title="Evening task", priority="medium", preferred_time_of_day="evening"),
        make_task(title="Morning task", priority="medium", preferred_time_of_day="morning"),
        make_task(title="Afternoon task", priority="medium", preferred_time_of_day="afternoon"),
    ]
    result = scheduler.sort_by_priority(tasks)
    assert [t.preferred_time_of_day for t in result] == ["morning", "afternoon", "evening"]


def test_sort_by_time_chronological_order():
    """sort_by_time should return morning -> afternoon -> evening -> any."""
    owner = make_owner()
    scheduler = Scheduler(owner)

    tasks = [
        make_task(title="Any time", preferred_time_of_day="any"),
        make_task(title="Evening", preferred_time_of_day="evening"),
        make_task(title="Morning", preferred_time_of_day="morning"),
        make_task(title="Afternoon", preferred_time_of_day="afternoon"),
    ]
    result = scheduler.sort_by_time(tasks)
    assert [t.preferred_time_of_day for t in result] == ["morning", "afternoon", "evening", "any"]


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_duplicate_time_slot():
    """Two tasks for the same pet in the same non-'any' slot must produce a warning."""
    owner = make_owner()
    pet = owner.pets[0]
    pet.add_task(make_task(title="Walk", preferred_time_of_day="morning"))
    pet.add_task(make_task(title="Meds", preferred_time_of_day="morning"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "morning" in warnings[0]
    assert "Mochi" in warnings[0]


def test_detect_conflicts_no_warning_for_any_time():
    """Tasks with preferred_time_of_day='any' must never trigger a conflict warning."""
    owner = make_owner()
    pet = owner.pets[0]
    pet.add_task(make_task(title="Walk", preferred_time_of_day="any"))
    pet.add_task(make_task(title="Meds", preferred_time_of_day="any"))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_no_warning_for_distinct_slots():
    """Tasks in different time slots must not conflict."""
    owner = make_owner()
    pet = owner.pets[0]
    pet.add_task(make_task(title="Walk", preferred_time_of_day="morning"))
    pet.add_task(make_task(title="Meds", preferred_time_of_day="evening"))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_does_not_cross_pets():
    """Two pets each with a 'morning' task must NOT trigger a conflict with each other."""
    owner = Owner(name="Alex", available_minutes=90)
    pet1 = Pet(name="Mochi", species="dog", age=3)
    pet2 = Pet(name="Luna", species="cat", age=2)
    pet1.add_task(make_task(title="Walk", preferred_time_of_day="morning"))
    pet2.add_task(make_task(title="Play", preferred_time_of_day="morning"))
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Scheduling: happy paths
# ---------------------------------------------------------------------------

def test_generate_plan_all_tasks_fit_within_budget():
    """When total task duration <= budget, all tasks should be scheduled."""
    owner = make_owner(minutes=90)
    pet = owner.pets[0]
    pet.add_task(make_task(title="Walk", duration_minutes=30, priority="high"))
    pet.add_task(make_task(title="Feed", duration_minutes=10, priority="medium"))

    plan = Scheduler(owner).generate_plan()

    assert len(plan.scheduled_tasks) == 2
    assert len(plan.skipped_tasks) == 0


def test_generate_plan_mandatory_tasks_always_scheduled():
    """Mandatory tasks must appear in the plan even if they exhaust the entire budget."""
    owner = make_owner(minutes=20)
    pet = owner.pets[0]
    # Two mandatory tasks totalling 50 min — exceeds 20-min budget
    pet.add_task(make_task(title="Meds", duration_minutes=30, is_mandatory=True))
    pet.add_task(make_task(title="Feed", duration_minutes=20, is_mandatory=True))

    plan = Scheduler(owner).generate_plan()

    titles = [t.title for t in plan.scheduled_tasks]
    assert "Meds" in titles
    assert "Feed" in titles


def test_generate_plan_completed_tasks_excluded():
    """Already-completed tasks must not appear in the generated plan."""
    owner = make_owner(minutes=90)
    pet = owner.pets[0]
    done = make_task(title="Done task", completed=True)
    todo = make_task(title="Todo task", duration_minutes=20)
    pet.add_task(done)
    pet.add_task(todo)

    plan = Scheduler(owner).generate_plan()

    titles = [t.title for t in plan.scheduled_tasks]
    assert "Done task" not in titles
    assert "Todo task" in titles


def test_generate_plan_optional_task_skipped_when_over_budget():
    """Optional tasks that don't fit in the remaining budget go to skipped_tasks."""
    owner = make_owner(minutes=15)
    pet = owner.pets[0]
    pet.add_task(make_task(title="Big task", duration_minutes=30, priority="high"))

    plan = Scheduler(owner).generate_plan()

    assert len(plan.scheduled_tasks) == 0
    assert len(plan.skipped_tasks) == 1


# ---------------------------------------------------------------------------
# Scheduling: edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_pet_with_no_tasks_produces_empty_plan():
    """An owner whose pet has no tasks should get an empty but valid plan."""
    owner = make_owner(minutes=60)
    plan = Scheduler(owner).generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_time() == 0


def test_generate_plan_zero_budget_only_mandatory_scheduled():
    """With a 0-minute budget, mandatory tasks are still scheduled; optional tasks are skipped."""
    owner = make_owner(minutes=0)
    pet = owner.pets[0]
    pet.add_task(make_task(title="Meds", duration_minutes=10, is_mandatory=True))
    pet.add_task(make_task(title="Walk", duration_minutes=30, priority="high"))

    plan = Scheduler(owner).generate_plan()

    titles_scheduled = [t.title for t in plan.scheduled_tasks]
    titles_skipped = [t.title for t in plan.skipped_tasks]
    assert "Meds" in titles_scheduled
    assert "Walk" in titles_skipped


def test_generate_plan_owner_with_no_pets():
    """An owner with no pets at all should produce a valid, empty plan."""
    owner = Owner(name="Alex", available_minutes=60)
    plan = Scheduler(owner).generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []


# ---------------------------------------------------------------------------
# filter_tasks
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) must return only that pet's tasks."""
    owner = Owner(name="Alex", available_minutes=90)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=2)
    mochi.add_task(make_task(title="Mochi walk"))
    luna.add_task(make_task(title="Luna play"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(pet_name="Mochi")

    assert len(result) == 1
    assert result[0].title == "Mochi walk"


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=False) must return only incomplete tasks."""
    owner = make_owner()
    pet = owner.pets[0]
    pet.add_task(make_task(title="Done", completed=True))
    pet.add_task(make_task(title="Pending"))

    scheduler = Scheduler(owner)
    result = scheduler.filter_tasks(completed=False)

    assert len(result) == 1
    assert result[0].title == "Pending"
