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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
