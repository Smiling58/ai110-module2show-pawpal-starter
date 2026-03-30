from pawpal_system import Task, Pet


def make_task(**overrides):
    defaults = dict(
        title="Morning walk",
        category="walk",
        duration_minutes=30,
        priority="high",
    )
    return Task(**{**defaults, **overrides})


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
