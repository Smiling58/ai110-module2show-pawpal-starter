# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

---

## Features

### Mandatory-first scheduling
Tasks marked **Mandatory** (e.g., medications) are always placed in the daily plan before the time budget is applied. Optional tasks fill the remaining budget in priority order. Mandatory tasks can never be dropped, even if they push the plan over budget — the UI surfaces an over-budget warning instead.

### Priority-based sorting with time-of-day tiebreaker
`Scheduler.sort_by_priority()` orders optional tasks `high → medium → low`. When two tasks share the same priority, the one preferred earlier in the day (morning before afternoon, afternoon before evening) is scheduled first. This ensures the most important and most time-sensitive tasks are always attempted first.

### Chronological display (sort by time of day)
`Scheduler.sort_by_time()` reorders the task table and the final plan output so items read in natural daily sequence — morning tasks at the top, evening tasks at the bottom — regardless of the order they were added.

### Daily and weekly task recurrence
Each task has a **Frequency** setting (`daily`, `weekly`, or `as needed`). When `Task.mark_complete()` is called, it marks the task done and returns a new Task instance due on the next occurrence (tomorrow for daily, +7 days for weekly). `Scheduler.advance_recurring()` handles both the marking and the registration of the next occurrence on the pet.

### Time-slot conflict detection
`Scheduler.detect_conflicts()` scans each pet's tasks and flags any case where two or more tasks share the same non-`any` preferred time of day. Conflicts appear as yellow warning banners in the UI — both in the task list (Step 3) and at the top of the generated schedule (Step 4) — so owners can resolve them before the plan is finalized. Tasks with `preferred_time_of_day = "any"` never trigger conflicts because they have no fixed slot preference.

### Task filtering
`Scheduler.filter_tasks(pet_name=, completed=)` returns a flat list of tasks matching both criteria (AND logic). This powers queries like "show me all of Mochi's pending tasks" and is the foundation for future per-pet dashboards.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal.png" target="_blank"><img src='/course_images/ai110/pawpal.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## System Architecture

The final UML class diagram is in [uml_final.md](uml_final.md) as a Mermaid.js block. Open it at [https://mermaid.live](https://mermaid.live) and export as PNG to produce `uml_final.png`.

Key class relationships:
- `Owner` owns a list of `Pet` objects; `Pet` owns a list of `Task` objects
- `Scheduler` reads from `Owner` (and all nested pets/tasks) and produces a `DailyPlan`
- `Task.mark_complete()` returns a new `Task` instance — a self-referential dependency for recurrence

---

## Smarter Scheduling

Beyond the basic priority-and-time-budget scheduler, the system includes four additional algorithms:

- **Sort by time of day** — `Scheduler.sort_by_time()` orders any task list morning → afternoon → evening → any, so the plan reads in natural daily order.
- **Filter by pet / status** — `Scheduler.filter_tasks(pet_name=, completed=)` lets you query tasks for a specific pet or see only pending/completed items.
- **Recurring task advancement** — `Task.mark_complete()` returns a new `Task` instance due on the next occurrence (today + 1 day for daily, + 7 days for weekly). `Scheduler.advance_recurring()` marks the task and registers the next one on the pet automatically.
- **Conflict detection** — `Scheduler.detect_conflicts()` warns when two or more tasks for the same pet share the same time-of-day slot (e.g., two "morning" tasks). Returns warning strings rather than raising exceptions so the app can surface them without crashing.

## Testing PawPal+

Run the full test suite with:

```bash
python -m pytest
```

### What the tests cover

| Area | Tests |
|---|---|
| **Recurrence logic** | Daily tasks produce a next task due tomorrow; weekly tasks due in 7 days; `as needed` tasks return `None` and nothing is appended to the pet |
| **Sorting correctness** | `sort_by_priority` orders `high → medium → low`; `sort_by_time` orders `morning → afternoon → evening → any`; equal-priority tasks break ties by time-of-day |
| **Conflict detection** | Duplicate non-`any` slots on the same pet trigger a warning; `any`-time tasks never conflict; conflicts do not cross pets |
| **Scheduling — happy paths** | All tasks fit when budget is sufficient; mandatory tasks always appear even when they exceed budget; completed tasks are excluded |
| **Scheduling — edge cases** | Zero-budget schedules only mandatory tasks; pet with no tasks returns empty plan; owner with no pets returns empty plan; oversized optional tasks go to `skipped_tasks` |
| **Filter tasks** | `pet_name` filter returns only that pet's tasks; `completed=False` returns only pending tasks |

**23 tests — all passing.**

### Confidence Level

★★★★☆ (4/5)

The core scheduling logic — mandatory-first, priority sorting, recurrence, and conflict detection — is thoroughly covered and all tests pass. One star is held back because the greedy packing algorithm is order-dependent (task insertion order affects what gets scheduled when the budget is tight), and the UI layer has no automated tests.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
