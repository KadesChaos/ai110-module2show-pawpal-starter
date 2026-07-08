from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


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

    def get_tasks(self) -> list[Task]:
        """Return this pet's list of tasks."""
        return self.tasks

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

    def get_upcoming_tasks(self, now: Optional[datetime] = None) -> list[Task]:
        """Return incomplete tasks scheduled at or after now, earliest first."""
        now = now or datetime.now()
        return sorted(
            (t for t in self.get_all_tasks() if not t.completed and t.scheduled_time >= now),
            key=lambda t: t.scheduled_time,
        )

    def get_overdue_tasks(self, now: Optional[datetime] = None) -> list[Task]:
        """Return incomplete tasks whose scheduled time has already passed."""
        now = now or datetime.now()
        return [t for t in self.get_all_tasks() if t.is_overdue(now)]

    def get_daily_schedule(self, day: date) -> list[Task]:
        """Return all tasks scheduled on the given day, earliest first."""
        return sorted(
            (t for t in self.get_all_tasks() if t.scheduled_time.date() == day),
            key=lambda t: t.scheduled_time,
        )

    def complete_task(self, task_id: str) -> bool:
        """Mark the task with the given id complete; return whether it was found."""
        for task in self.get_all_tasks():
            if task.id == task_id:
                task.mark_complete()
                return True
        return False

    def send_due_reminders(self, now: Optional[datetime] = None) -> None:
        """Send reminders for all incomplete tasks due at or before now."""
        now = now or datetime.now()
        for task in self.get_all_tasks():
            if task.reminder_enabled and not task.completed and task.scheduled_time <= now:
                task.send_reminder()
