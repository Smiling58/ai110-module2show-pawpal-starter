from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup Owner ---
jordan = Owner(name="Jordan", available_minutes=90, preferences="prefers morning tasks")

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="dog", age=3, health_notes="on daily heartworm medication")
luna = Pet(name="Luna", species="cat", age=5, health_notes="")

# --- Add Tasks to Mochi ---
mochi.add_task(Task(
    title="Heartworm med",
    category="meds",
    duration_minutes=5,
    priority="high",
    is_mandatory=True,
    preferred_time_of_day="morning",
))
mochi.add_task(Task(
    title="Morning walk",
    category="walk",
    duration_minutes=30,
    priority="high",
    preferred_time_of_day="morning",
))
mochi.add_task(Task(
    title="Brush coat",
    category="grooming",
    duration_minutes=15,
    priority="low",
    preferred_time_of_day="evening",
))

# --- Add Tasks to Luna ---
luna.add_task(Task(
    title="Feeding",
    category="feeding",
    duration_minutes=10,
    priority="high",
    is_mandatory=True,
    preferred_time_of_day="morning",
))
luna.add_task(Task(
    title="Puzzle feeder enrichment",
    category="enrichment",
    duration_minutes=20,
    priority="medium",
    preferred_time_of_day="afternoon",
))
luna.add_task(Task(
    title="Nail trim",
    category="grooming",
    duration_minutes=20,
    priority="low",
    preferred_time_of_day="any",
))

# --- Register pets with owner ---
jordan.add_pet(mochi)
jordan.add_pet(luna)

# --- Generate plan ---
scheduler = Scheduler(owner=jordan)
plan = scheduler.generate_plan()

# --- Print readable schedule ---
WIDTH = 52
print("=" * WIDTH)
print(f"  PAWPAL+ — TODAY'S SCHEDULE FOR {jordan.name.upper()}")
print(f"  Time budget: {jordan.available_minutes} min")
print("=" * WIDTH)

if plan.scheduled_tasks:
    print("\n  SCHEDULED TASKS")
    print("  " + "-" * (WIDTH - 2))
    for i, task in enumerate(plan.scheduled_tasks, 1):
        tag = " *" if task.is_mandatory else ""
        print(f"  {i}. {task.title}{tag}")
        print(f"     {task.category} | {task.duration_minutes} min | {task.priority} priority")
    print(f"\n  Total time: {plan.total_time()} min")

if plan.skipped_tasks:
    print(f"\n  SKIPPED (not enough time)")
    print("  " + "-" * (WIDTH - 2))
    for task in plan.skipped_tasks:
        print(f"  - {task.title} ({task.duration_minutes} min)")

print("\n  * = mandatory task (always scheduled)")
print("=" * WIDTH)
print()
print(plan.explain())
