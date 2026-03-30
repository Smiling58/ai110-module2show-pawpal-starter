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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
