from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable, Optional


# ---------------------------------------------------------------------------
# Task — base class for any schedulable activity tied to a pet
# ---------------------------------------------------------------------------

@dataclass
class Task:
    id: str
    pet_id: str
    description: str
    scheduled_time: datetime
    frequency: str = "once"  # e.g. "once", "daily", "weekly"
    completed: bool = False
    reminder_enabled: bool = True

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def reschedule(self, new_time: datetime) -> None:
        """Change the scheduled time and reset completion status."""
        self.scheduled_time = new_time
        self.completed = False

    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """Return True if the task is incomplete and its time has passed."""
        now = now or datetime.now()
        return not self.completed and self.scheduled_time < now

    def send_reminder(self) -> None:
        """Print a reminder for this task if reminders are enabled."""
        if self.reminder_enabled:
            print(f"Reminder: '{self.description}' for pet {self.pet_id} at {self.scheduled_time}")

    def next_occurrence(self, new_id: Optional[str] = None) -> Optional["Task"]:
        """Return a new, incomplete copy of this task advanced to its next occurrence, or None if it doesn't recur.

        For "daily" tasks, scheduled_time advances by one day; for "weekly", by one week,
        both computed relative to this task's own scheduled_time (not "now"), so the
        time-of-day is preserved. Any other frequency (e.g. "once") returns None. The
        copy gets a fresh id (new_id if provided, otherwise a generated suffix) so it
        never collides with the original task's id.
        """
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        import copy
        import uuid

        next_task = copy.copy(self)
        next_task.id = new_id or f"{self.id}-{uuid.uuid4().hex[:8]}"
        next_task.scheduled_time = self.scheduled_time + delta
        next_task.completed = False
        return next_task


@dataclass
class FeedingSchedule(Task):
    food_type: str = ""
    portion_size: float = 0.0


@dataclass
class MedicationReminder(Task):
    medication_name: str = ""
    dosage: str = ""
    end_date: Optional[date] = None

    def mark_as_taken(self) -> None:
        """Mark this medication dose as taken."""
        self.mark_complete()


@dataclass
class Event(Task):
    title: str = ""
    location: str = ""
    notes: str = ""

    def cancel_event(self) -> None:
        """Cancel this event and disable its reminder."""
        self.completed = True
        self.reminder_enabled = False


@dataclass
class VetAppointment(Event):
    vet_name: str = ""
    clinic_name: str = ""
    clinic_phone: str = ""
    reason: str = ""


# ---------------------------------------------------------------------------
# Pet — stores pet details and its own list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    id: str
    name: str
    species: str
    breed: str
    birth_date: date
    photo_url: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        """Return this pet's list of tasks, optionally excluding completed ones."""
        if include_completed:
            return self.tasks
        return [t for t in self.tasks if not t.completed]

    def update_pet(self, **kwargs) -> None:
        """Update this pet's attributes from keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and gives access to all their tasks
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove the pet with the given id from this owner's list of pets."""
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_pets(self) -> list[Pet]:
        """Return this owner's list of pets."""
        return self.pets

    def get_pet(self, pet_id: str) -> Optional[Pet]:
        """Return the pet with the given id, or None if not found."""
        return next((p for p in self.pets if p.id == pet_id), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler — retrieves, organizes, and manages tasks across pets
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return self.owner.get_all_tasks()

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Return the tasks belonging to the pet with the given id."""
        pet = self.owner.get_pet(pet_id)
        return pet.get_tasks() if pet else []

    def sort_by_time(self, tasks: Optional[Iterable[Task]] = None) -> list[Task]:
        """Return the given tasks (or all of the owner's tasks) sorted earliest first.

        Accepts any iterable of Task (list, generator, etc.) and sorts by
        scheduled_time using Python's stable sort, so tasks with equal times
        keep their relative input order. This is the single sort
        implementation reused by get_upcoming_tasks, get_daily_schedule,
        get_filtered_tasks, and filter_tasks.
        """
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.scheduled_time)

    def get_upcoming_tasks(self, now: Optional[datetime] = None) -> list[Task]:
        """Return incomplete tasks scheduled at or after now, earliest first."""
        now = now or datetime.now()
        return self.sort_by_time(
            t for t in self.get_all_tasks() if not t.completed and t.scheduled_time >= now
        )

    def get_overdue_tasks(self, now: Optional[datetime] = None) -> list[Task]:
        """Return incomplete tasks whose scheduled time has already passed."""
        now = now or datetime.now()
        return [t for t in self.get_all_tasks() if t.is_overdue(now)]

    def get_daily_schedule(self, day: date) -> list[Task]:
        """Return all tasks scheduled on the given day, earliest first."""
        return self.sort_by_time(t for t in self.get_all_tasks() if t.scheduled_time.date() == day)

    def get_filtered_tasks(
        self,
        pet_id: Optional[str] = None,
        completed: Optional[bool] = None,
        day: Optional[date] = None,
    ) -> list[Task]:
        """Return tasks matching the given pet, completion status, and/or day, earliest first.

        Each filter (pet_id, completed, day) is applied only if provided, and
        filters combine with AND. Passing no filters returns every task,
        sorted by time.
        """
        tasks = self.get_all_tasks()
        if pet_id is not None:
            tasks = [t for t in tasks if t.pet_id == pet_id]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if day is not None:
            tasks = [t for t in tasks if t.scheduled_time.date() == day]
        return self.sort_by_time(tasks)

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks matching the given completion status and/or pet name, earliest first.

        Unlike get_filtered_tasks (which filters by pet_id), this filters by
        the pet's name, resolving each task's pet_id via owner.get_pet on the
        fly. Filters combine with AND; passing neither returns every task,
        sorted by time.
        """
        tasks = self.get_all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [
                t for t in tasks
                if (pet := self.owner.get_pet(t.pet_id)) is not None and pet.name == pet_name
            ]
        return self.sort_by_time(tasks)

    def complete_task(self, task_id: str) -> bool:
        """Mark the task with the given id complete, generate its next recurrence if any, and return whether it was found.

        If the completed task's frequency is "daily" or "weekly",
        Task.next_occurrence() produces a new, incomplete task advanced to
        the next due date, which is appended to the same pet's task list.
        A "once" task is completed with no follow-up. Returns False without
        raising if no task with task_id exists.
        """
        for pet in self.owner.get_pets():
            for task in pet.get_tasks():
                if task.id == task_id:
                    task.mark_complete()
                    next_task = task.next_occurrence()
                    if next_task is not None:
                        pet.add_task(next_task)
                    return True
        return False

    def get_conflicts(self, pet_id: str, buffer_minutes: int = 15) -> list[tuple[Task, Task]]:
        """Return pairs of this pet's incomplete tasks scheduled within buffer_minutes of each other.

        Sorts the pet's incomplete tasks by time once, then compares each
        task only to its immediate neighbor in that sorted order (O(n log n)
        overall, rather than comparing every pair). buffer_minutes controls
        how close two tasks must be to count as a conflict; completed tasks
        are excluded since they no longer need attention.
        """
        tasks = sorted(
            (t for t in self.get_tasks_for_pet(pet_id) if not t.completed),
            key=lambda t: t.scheduled_time,
        )
        buffer = timedelta(minutes=buffer_minutes)
        conflicts = []
        for earlier, later in zip(tasks, tasks[1:]):
            if later.scheduled_time - earlier.scheduled_time < buffer:
                conflicts.append((earlier, later))
        return conflicts

    def get_exact_time_conflicts(self, pet_id: Optional[str] = None) -> list[tuple[Task, Task]]:
        """Return pairs of incomplete tasks scheduled at the exact same time, for one pet or across all pets.

        Unlike get_conflicts/get_owner_conflicts, this only matches an exact
        timestamp equality rather than a proximity buffer. Pass pet_id to
        scope the check to one pet's tasks; omit it to check across every
        pet the owner has. Uses the same sort-then-compare-neighbors
        approach for O(n log n) performance.
        """
        tasks = self.get_tasks_for_pet(pet_id) if pet_id is not None else self.get_all_tasks()
        tasks = sorted((t for t in tasks if not t.completed), key=lambda t: t.scheduled_time)
        conflicts = []
        for earlier, later in zip(tasks, tasks[1:]):
            if later.scheduled_time == earlier.scheduled_time:
                conflicts.append((earlier, later))
        return conflicts

    def get_owner_conflicts(self, buffer_minutes: int = 15) -> list[tuple[Task, Task]]:
        """Return pairs of the owner's incomplete tasks (across all pets) scheduled within buffer_minutes of each other.

        Same buffer-based logic as get_conflicts, but scoped to the whole
        owner instead of a single pet - this is what catches the case where
        one owner can't physically be in two places for two different pets
        at (nearly) the same time.
        """
        tasks = sorted(
            (t for t in self.get_all_tasks() if not t.completed),
            key=lambda t: t.scheduled_time,
        )
        buffer = timedelta(minutes=buffer_minutes)
        conflicts = []
        for earlier, later in zip(tasks, tasks[1:]):
            if later.scheduled_time - earlier.scheduled_time < buffer:
                conflicts.append((earlier, later))
        return conflicts

    def describe_conflicts(self, conflicts: list[tuple[Task, Task]]) -> list[str]:
        """Turn conflict pairs into human-readable warning messages, without raising or halting the program.

        Accepts the output of get_conflicts, get_exact_time_conflicts, or
        get_owner_conflicts and formats each (earlier, later) pair into one
        warning string naming both tasks, their pets, and times. Conflicts
        are reported as data for the caller to print or display, never as
        an exception, so a scheduling clash never crashes the program.
        """
        messages = []
        for earlier, later in conflicts:
            earlier_pet = self.owner.get_pet(earlier.pet_id)
            later_pet = self.owner.get_pet(later.pet_id)
            messages.append(
                f"Warning: '{earlier.description}' ({earlier_pet.name if earlier_pet else 'Unknown'}) "
                f"at {earlier.scheduled_time.strftime('%I:%M %p')} conflicts with "
                f"'{later.description}' ({later_pet.name if later_pet else 'Unknown'}) "
                f"at {later.scheduled_time.strftime('%I:%M %p')}"
            )
        return messages

    def send_due_reminders(self, now: Optional[datetime] = None) -> None:
        """Send reminders for all incomplete tasks due at or before now."""
        now = now or datetime.now()
        for task in self.get_all_tasks():
            if task.reminder_enabled and not task.completed and task.scheduled_time <= now:
                task.send_reminder()
