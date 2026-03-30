from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup Owner ---
jordan = Owner(name="Jordan", available_minutes=90, preferences="prefers morning tasks")

# --- Setup Pets ---
mochi = Pet(name="Mochi", species="dog", age=3, health_notes="on daily heartworm medication")
luna = Pet(name="Luna", species="cat", age=5, health_notes="")

# --- Add Tasks to Mochi (added out of order to test sorting) ---
mochi.add_task(Task(
    title="Brush coat",
    category="grooming",
    duration_minutes=15,
    priority="low",
    preferred_time_of_day="evening",
    frequency="weekly",
))
mochi.add_task(Task(
    title="Heartworm med",
    category="meds",
    duration_minutes=5,
    priority="high",
    is_mandatory=True,
    preferred_time_of_day="morning",
    frequency="daily",
))
mochi.add_task(Task(
    title="Morning walk",
    category="walk",
    duration_minutes=30,
    priority="high",
    preferred_time_of_day="morning",  # intentional conflict with Heartworm med
    frequency="daily",
))

# --- Add Tasks to Luna ---
luna.add_task(Task(
    title="Feeding",
    category="feeding",
    duration_minutes=10,
    priority="high",
    is_mandatory=True,
    preferred_time_of_day="morning",
    frequency="daily",
))
luna.add_task(Task(
    title="Puzzle feeder enrichment",
    category="enrichment",
    duration_minutes=20,
    priority="medium",
    preferred_time_of_day="afternoon",
    frequency="as needed",
))
luna.add_task(Task(
    title="Nail trim",
    category="grooming",
    duration_minutes=20,
    priority="low",
    preferred_time_of_day="any",
    frequency="weekly",
))

jordan.add_pet(mochi)
jordan.add_pet(luna)

scheduler = Scheduler(owner=jordan)
WIDTH = 52

# ---------------------------------------------------------------------------
# 1. Sort by time of day
# ---------------------------------------------------------------------------
print("=" * WIDTH)
print("  SORTED BY TIME OF DAY")
print("=" * WIDTH)
sorted_by_time = scheduler.sort_by_time(jordan.get_all_tasks())
for t in sorted_by_time:
    print(f"  [{t.preferred_time_of_day:10}] {t.title}")

# ---------------------------------------------------------------------------
# 2. Filter by pet and completion status
# ---------------------------------------------------------------------------
print()
print("=" * WIDTH)
print("  MOCHI'S TASKS (filter by pet)")
print("=" * WIDTH)
for t in scheduler.filter_tasks(pet_name="Mochi"):
    status = "done" if t.completed else "pending"
    print(f"  [{status}] {t.title}")

# ---------------------------------------------------------------------------
# 3. Conflict detection
# ---------------------------------------------------------------------------
print()
print("=" * WIDTH)
print("  CONFLICT DETECTION")
print("=" * WIDTH)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for w in conflicts:
        print(f"  WARNING: {w}")
else:
    print("  No conflicts detected.")

# ---------------------------------------------------------------------------
# 4. Recurring task advancement
# ---------------------------------------------------------------------------
print()
print("=" * WIDTH)
print("  RECURRING TASK — mark complete and advance")
print("=" * WIDTH)
heartworm = mochi.tasks[1]  # "Heartworm med"
print(f"  Before: '{heartworm.title}' completed={heartworm.completed}, due={heartworm.due_date or 'not set'}")
next_task = scheduler.advance_recurring(mochi, heartworm)
print(f"  After:  '{heartworm.title}' completed={heartworm.completed}")
if next_task:
    print(f"  Next occurrence created: '{next_task.title}' due {next_task.due_date}")

# ---------------------------------------------------------------------------
# 5. Generate plan (completed tasks are excluded automatically)
# ---------------------------------------------------------------------------
print()
plan = scheduler.generate_plan()
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
