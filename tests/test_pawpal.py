from datetime import date, datetime

from pawpal_system import Owner, Pet, Task, Scheduler


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


def test_next_occurrence_daily_advances_one_day():
    task = Task("t1", "p1", "Feed", datetime(2026, 7, 7, 8, 0), frequency="daily")

    next_task = task.next_occurrence()

    assert next_task is not None
    assert next_task.scheduled_time == datetime(2026, 7, 8, 8, 0)
    assert next_task.completed is False


def test_next_occurrence_once_returns_none():
    task = Task("t1", "p1", "Vet visit", datetime(2026, 7, 7, 8, 0), frequency="once")

    assert task.next_occurrence() is None


def test_complete_task_generates_next_recurrence():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Feed", datetime(2026, 7, 7, 8, 0), frequency="daily"))
    scheduler = Scheduler(owner)

    found = scheduler.complete_task("t1")

    assert found is True
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[0].completed is True
    assert pet.get_tasks()[1].scheduled_time == datetime(2026, 7, 8, 8, 0)
    assert pet.get_tasks()[1].id != pet.get_tasks()[0].id


def test_complete_task_once_does_not_duplicate():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Vet visit", datetime(2026, 7, 7, 8, 0), frequency="once"))
    scheduler = Scheduler(owner)

    scheduler.complete_task("t1")

    assert len(pet.get_tasks()) == 1


def test_get_filtered_tasks_by_status_and_pet():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    done_task = Task("t2", pet.id, "Feed", datetime(2026, 7, 7, 9, 0))
    done_task.mark_complete()
    pet.add_task(done_task)
    scheduler = Scheduler(owner)

    pending = scheduler.get_filtered_tasks(pet_id=pet.id, completed=False)

    assert [t.id for t in pending] == ["t1"]


def test_filter_tasks_by_pet_name_and_status():
    owner = Owner("o1", "Jordan", "")
    dog = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    cat = Pet("p2", "Mochi", "Cat", "Tabby", date(2021, 1, 1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("t1", dog.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    done_task = Task("t2", dog.id, "Feed", datetime(2026, 7, 7, 9, 0))
    done_task.mark_complete()
    dog.add_task(done_task)
    cat.add_task(Task("t3", cat.id, "Feed", datetime(2026, 7, 7, 8, 0)))
    scheduler = Scheduler(owner)

    assert [t.id for t in scheduler.filter_tasks(pet_name="Rex")] == ["t1", "t2"]
    assert [t.id for t in scheduler.filter_tasks(pet_name="Rex", completed=False)] == ["t1"]
    assert [t.id for t in scheduler.filter_tasks(completed=True)] == ["t2"]


def test_get_conflicts_detects_overlapping_tasks_for_pet():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    pet.add_task(Task("t2", pet.id, "Feed", datetime(2026, 7, 7, 8, 5)))
    scheduler = Scheduler(owner)

    conflicts = scheduler.get_conflicts(pet.id, buffer_minutes=15)

    assert len(conflicts) == 1
    assert conflicts[0][0].id == "t1"
    assert conflicts[0][1].id == "t2"


def test_get_conflicts_ignores_tasks_far_apart():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    pet.add_task(Task("t2", pet.id, "Feed", datetime(2026, 7, 7, 9, 0)))
    scheduler = Scheduler(owner)

    assert scheduler.get_conflicts(pet.id, buffer_minutes=15) == []


def test_get_exact_time_conflicts_same_pet():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    pet.add_task(Task("t2", pet.id, "Feed", datetime(2026, 7, 7, 8, 0)))
    pet.add_task(Task("t3", pet.id, "Groom", datetime(2026, 7, 7, 9, 0)))
    scheduler = Scheduler(owner)

    conflicts = scheduler.get_exact_time_conflicts(pet.id)

    assert len(conflicts) == 1
    assert {conflicts[0][0].id, conflicts[0][1].id} == {"t1", "t2"}


def test_get_exact_time_conflicts_across_pets():
    owner = Owner("o1", "Jordan", "")
    dog = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    cat = Pet("p2", "Mochi", "Cat", "Tabby", date(2021, 1, 1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("t1", dog.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    cat.add_task(Task("t2", cat.id, "Feed", datetime(2026, 7, 7, 8, 0)))
    scheduler = Scheduler(owner)

    conflicts = scheduler.get_exact_time_conflicts()

    assert len(conflicts) == 1


def test_get_exact_time_conflicts_close_but_not_exact_is_not_a_conflict():
    owner = Owner("o1", "Jordan", "")
    pet = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    owner.add_pet(pet)
    pet.add_task(Task("t1", pet.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    pet.add_task(Task("t2", pet.id, "Feed", datetime(2026, 7, 7, 8, 5)))
    scheduler = Scheduler(owner)

    assert scheduler.get_exact_time_conflicts(pet.id) == []


def test_get_owner_conflicts_across_pets():
    owner = Owner("o1", "Jordan", "")
    dog = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    cat = Pet("p2", "Mochi", "Cat", "Tabby", date(2021, 1, 1))
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("t1", dog.id, "Walk", datetime(2026, 7, 7, 8, 0)))
    cat.add_task(Task("t2", cat.id, "Feed", datetime(2026, 7, 7, 8, 5)))
    scheduler = Scheduler(owner)

    conflicts = scheduler.get_owner_conflicts(buffer_minutes=15)

    assert len(conflicts) == 1
