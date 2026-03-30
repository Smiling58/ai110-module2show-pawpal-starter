# PawPal+ — Final Class Diagram (Mermaid.js)

Paste the block below into [https://mermaid.live](https://mermaid.live) and export as PNG to produce `uml_final.png`.

```mermaid
classDiagram
    direction TB

    class Task {
        +str title
        +str category
        +int duration_minutes
        +str priority
        +bool is_mandatory
        +str preferred_time_of_day
        +str frequency
        +bool completed
        +str due_date
        +mark_complete() Task|None
        +is_high_priority() bool
        +summary() str
    }

    class Pet {
        +str name
        +str species
        +int age
        +str health_notes
        +list~Task~ tasks
        +add_task(task: Task) None
        +get_required_tasks() list~Task~
    }

    class Owner {
        +str name
        +int available_minutes
        +str preferences
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +set_available_time(minutes: int) None
        +get_all_tasks() list~Task~
    }

    class DailyPlan {
        +str date
        +list~Task~ scheduled_tasks
        +list~Task~ skipped_tasks
        +add_task(task: Task) None
        +total_time() int
        +explain() str
    }

    class Scheduler {
        +Owner owner
        +generate_plan() DailyPlan
        +sort_by_priority(tasks) list~Task~
        +sort_by_time(tasks) list~Task~
        +filter_by_time(tasks, remaining_minutes) tuple
        +filter_tasks(pet_name, completed) list~Task~
        +detect_conflicts() list~str~
        +advance_recurring(pet, task) Task|None
        -_separate_mandatory(tasks) tuple
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : reads
    Scheduler ..> DailyPlan : produces
    Scheduler ..> Task : sorts / filters
    Task ..> Task : mark_complete() creates next occurrence
```

## Key relationships

| Relationship | Type | Description |
|---|---|---|
| Owner → Pet | Composition | Owner holds a list of pets; pets don't exist without an owner in this system |
| Pet → Task | Composition | Each pet owns its task list; tasks are added via `Pet.add_task()` |
| Scheduler → Owner | Association | Scheduler reads the owner and all nested pets/tasks at plan time |
| Scheduler → DailyPlan | Dependency | `generate_plan()` creates and returns a new DailyPlan each call |
| Task → Task | Self-reference | `mark_complete()` returns a new Task instance for the next recurrence |
