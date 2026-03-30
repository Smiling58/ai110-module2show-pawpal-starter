# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- UML overview: a class diagram centered on a Scheduler that reads from Owner, Pet, and Task objects and produces a DailyPlan. Key relationships: Scheduler uses Owner and Pet as context, reads a list of Tasks, and outputs a DailyPlan containing ordered scheduled tasks and skipped tasks with reasoning.

- Classes and responsibilities:
    - Owner: holds the pet owner's name, daily time budget (available_minutes), and preferences (e.g., prefers morning tasks). Sets the time constraint the Scheduler must respect.
    - Pet: holds the pet's name, species, age, and health notes. Used by the Scheduler to determine which tasks are relevant or mandatory.
    - Task: represents a single care activity (walk, feeding, meds, grooming, enrichment). Stores title, category, duration_minutes, priority (low/medium/high), is_mandatory flag, and preferred_time_of_day. Mandatory tasks (e.g., medications) are always scheduled regardless of time budget.
    - DailyPlan: the output of the Scheduler. Holds an ordered list of scheduled tasks, a list of skipped tasks, and the total duration. Provides an explain() method that describes why each task was included or skipped.
    - Scheduler: the core logic layer. Takes an Owner, Pet, and list of Tasks; filters by time budget; always includes mandatory tasks; sorts remaining tasks by priority; and produces a DailyPlan with reasoning.

**b. Design changes**

Yes, several changes were made during skeleton review before implementation began:

1. **Removed `Owner.pets` and `add_pet()`** — the initial design gave `Owner` a list of pets and a method to add them, but `Scheduler` was already taking a single `Pet` directly. The two approaches conflicted and `Owner.pets` was never used by anything. Removing it keeps the data flow simple: one owner, one pet, one plan per run.

2. **Removed `Scheduler.explain_reasoning()`** — this duplicated the responsibility of `DailyPlan.explain()`. Since `DailyPlan` already holds both `scheduled_tasks` and `skipped_tasks`, it has everything needed to explain itself. Keeping both would have created ambiguity about which method to call and where reasoning logic lives.

3. **Removed `DailyPlan.total_duration` as a stored field** — storing a raw `int` that had to be kept in sync with `scheduled_tasks` was a bug waiting to happen. Replaced it with a single source of truth: `total_time()` computes the sum on demand from `scheduled_tasks`.

4. **Added `Scheduler._separate_mandatory()`** — the initial design had no explicit step for isolating mandatory tasks before time filtering. Without this, a greedy time filter could drop a medication task. The new stub enforces the correct order: always commit mandatory tasks first, then fill remaining budget with optional tasks sorted by priority.

5. **Added `remaining_minutes` parameter to `filter_by_time()`** — the original signature only took a task list, with no way to know the budget after mandatory tasks are already reserved. The updated signature makes the available time budget explicit so the method can be called correctly after mandatory tasks are committed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Mandatory flag** — tasks marked `is_mandatory=True` (e.g., medications) are always scheduled regardless of available time. This is a hard constraint: the scheduler commits to these tasks first and deducts their duration from the budget before evaluating anything else.

2. **Time budget** — the owner's `available_minutes` caps how much optional work can fit in the day. After mandatory tasks are reserved, the remaining budget is filled greedily: tasks are added in priority order until no more will fit.

3. **Priority** — optional tasks are sorted high → medium → low before the greedy fill. A secondary sort on `preferred_time_of_day` (morning → afternoon → evening → any) breaks ties so earlier-in-the-day tasks are preferred when priority is equal.

The mandatory flag was treated as most important because missing a pet's medication has real health consequences — no time pressure should ever drop it. Time budget was ranked second because it is the owner's primary real-world constraint. Priority came third because it is a soft preference: a low-priority task that fits should still be included rather than dropped for no reason.

**b. Tradeoffs**

The conflict detector flags tasks that share the same `preferred_time_of_day` slot (e.g., two "morning" tasks) as a conflict, even if the owner has enough total time to fit both. It does not check whether the tasks actually overlap in wall-clock time — it only compares the slot label.

This is a reasonable tradeoff for this scenario because tasks don't have fixed start times; they only have a preferred period. A true overlap check would require assigning start times first, which adds significant complexity (a scheduling sub-problem). For a daily care planner, a soft warning — "you have two morning tasks" — is more useful than a hard block, since the owner can simply do one after the other. The warning surfaces potential crowding without preventing valid schedules.

---

## 3. AI Collaboration

**a. How you used AI**

AI tools were used across every phase of the project, but in different roles at each stage:

- **Design brainstorming (Phase 1):** Used Claude to stress-test the UML before writing any code — asking "what edge cases would break this design?" surfaced the `_separate_mandatory()` gap and the `total_duration` stored-field problem before a single line was implemented. This was the highest-leverage use: catching design flaws early costs almost nothing; finding them after implementation is expensive.

- **Test planning (Phase 3):** Used `#codebase` context to generate a comprehensive test plan, asking specifically about happy paths and edge cases for a pet scheduler with sorting and recurring tasks. The most useful prompts were *specific and scenario-grounded* — "a pet with no tasks" and "two tasks at the exact same time" produced concrete, actionable test cases rather than generic advice.

- **Test implementation:** Used the test plan as a spec and had AI draft the test functions. The factory helper (`make_task(**overrides)`) and `make_owner()` patterns came from this step and made the test suite significantly more readable.

- **UI upgrade (Phase 4):** Used AI to identify which Scheduler methods were not yet surfaced in the UI — `sort_by_time()`, `detect_conflicts()`, and the `frequency` field were all present in the backend but invisible to users until this pass.

The most effective prompting pattern throughout: **give the AI the current file as context, describe the constraint or invariant you care about, and ask it to find what's missing** — rather than asking it to generate code from scratch.

**b. Judgment and verification**

During test generation, AI initially suggested asserting on the *exact string output* of `DailyPlan.explain()` — for example, checking that the explanation contained the substring `"included: mandatory"`. This was rejected for two reasons:

1. **Brittleness:** String-matching tests break whenever wording changes, even if the logic is still correct. They test presentation, not behavior.
2. **Wrong layer:** The test suite's job is to verify scheduling decisions (what got scheduled and why), not to lock in the English wording of the explanation text.

The replacement approach was to assert on the *data* — check `plan.scheduled_tasks` and `plan.skipped_tasks` directly, verify task titles are in the right list, and trust `explain()` to format whatever is in those lists. This kept the tests focused on the invariants that actually matter for correctness.

---

## 4. Testing and Verification

**a. What you tested**

The 23-test suite covers five areas:

1. **Recurrence logic** — `daily` tasks produce a next occurrence due tomorrow, `weekly` due in 7 days, `as needed` returns `None`. `advance_recurring()` appends the new task to the pet and does not append for non-recurring tasks. These are critical because a bug here silently drops recurring care (e.g., daily medication) from future plans.

2. **Sorting correctness** — `sort_by_priority()` orders `high → medium → low` with time-of-day as tiebreaker; `sort_by_time()` orders `morning → afternoon → evening → any`. Incorrect sorting would cause low-priority tasks to crowd out high-priority ones.

3. **Conflict detection** — Duplicate time slots on the same pet trigger a warning; `any`-time tasks never conflict; conflicts do not cross pets. Conflict detection is user-facing — a false positive would alarm owners unnecessarily; a false negative would miss a real crowding problem.

4. **Scheduling happy paths** — All tasks fit when budget is sufficient; mandatory tasks appear even when they bust the budget; completed tasks are excluded from plans.

5. **Scheduling edge cases** — Zero-budget plans, pets with no tasks, owners with no pets, and oversized optional tasks all produce valid (empty or partial) plans rather than crashes.

**b. Confidence**

★★★★☆ (4 / 5). All 23 tests pass and cover the core invariants. The remaining uncertainty is in two areas:

- **Greedy packing is order-dependent.** If two tasks both fit individually but not together, which one gets scheduled depends on insertion order — not just priority. A future test could verify that the greedy algorithm's first-fit behavior is intentional and documented.
- **No UI-layer tests.** The Streamlit app is tested only by running it manually. Automated tests for the UI (e.g., with `streamlit-testing-library`) would close this gap.

---

## 5. Reflection

**a. What went well**

The clearest win was the **separation between data, logic, and presentation**. `Task`, `Pet`, and `Owner` hold state; `Scheduler` contains all the algorithms; `DailyPlan` holds results and explains them; `app.py` only calls into those layers without reimplementing any logic. This made it straightforward to upgrade the UI in Phase 4 — adding conflict warnings and chronological sorting required only two new method calls in `app.py` because the methods already existed and were tested in the backend. When the layers are clean, improvements are additive rather than surgical.

**b. What you would improve**

Two things stand out for a next iteration:

1. **Replace the greedy packer with a smarter algorithm.** The current first-fit greedy approach can leave gaps: if a 30-minute task comes before two 20-minute tasks and the budget is 45 minutes, the 30-minute task blocks both 20-minute tasks even though the two smaller ones would fit perfectly. A simple knapsack or best-fit algorithm would schedule more care within the same time budget.

2. **Expose recurring task advancement in the UI.** The backend has `Scheduler.advance_recurring()` fully implemented and tested, but there is no button in `app.py` to mark a task complete and trigger the next recurrence. This is the most useful daily interaction for a pet owner — it should be the first UI feature added in the next sprint.

**c. Key takeaway**

The most important lesson from this project is that **AI works best when the architect has already made the hard decisions.** When the class boundaries were fuzzy (early Phase 1), AI suggestions were inconsistent — sometimes putting logic in `Owner`, sometimes in `Scheduler`, sometimes proposing new classes. Once the invariants were explicit ("mandatory tasks are never dropped," "conflict detection is a warning not a block," "`DailyPlan` is read-only output"), AI could fill in implementations reliably because it had a clear spec to target.

The lead architect's job when working with AI is not to write every line — it is to define the constraints that every line must satisfy. AI is a very fast implementation engine; the human supplies the requirements, the invariants, and the judgment about when a suggestion violates them. Keeping those two roles distinct — and not letting AI make architectural decisions by default — is what makes the collaboration produce clean, maintainable code rather than a patchwork of plausible-looking suggestions.
