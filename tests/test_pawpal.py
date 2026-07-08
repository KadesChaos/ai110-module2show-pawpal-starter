from datetime import date, datetime

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("t1", "p1", "Walk the dog", datetime(2026, 7, 7, 8, 0))
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    assert len(pet.get_tasks()) == 0

    task = Task("t1", pet.id, "Walk the dog", datetime(2026, 7, 7, 8, 0))
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
