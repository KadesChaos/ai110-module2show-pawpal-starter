from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Data classes — plain data containers, no behaviour
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    id: str
    name: str
    species: str
    breed: str
    birth_date: date
    photo_url: str = ""

    def update_pet(self, **kwargs) -> None:
        pass

    def remove_pet(self) -> None:
        pass


@dataclass
class FeedingSchedule:
    id: str
    pet_id: str
    food_type: str
    portion_size: float
    scheduled_times: list[str] = field(default_factory=list)
    reminder_enabled: bool = True

    def add_schedule(self) -> None:
        pass

    def update_schedule(self, **kwargs) -> None:
        pass

    def send_reminder(self) -> None:
        pass


@dataclass
class MedicationReminder:
    id: str
    pet_id: str
    medication_name: str
    dosage: str
    frequency: str
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    reminder_enabled: bool = True

    def add_medication(self) -> None:
        pass

    def update_medication(self, **kwargs) -> None:
        pass

    def send_reminder(self) -> None:
        pass

    def mark_as_taken(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Event and its subclass
# ---------------------------------------------------------------------------

@dataclass
class Event:
    id: str
    pet_id: str
    title: str
    type: str
    date_time: datetime
    location: str = ""
    notes: str = ""
    reminder_enabled: bool = True

    def schedule_event(self) -> None:
        pass

    def cancel_event(self) -> None:
        pass

    def send_reminder(self) -> None:
        pass


@dataclass
class VetAppointment(Event):
    vet_name: str = ""
    clinic_name: str = ""
    clinic_phone: str = ""
    reason: str = ""

    def reschedule(self, new_date_time: datetime) -> None:
        pass


# ---------------------------------------------------------------------------
# User — owns pets and orchestrates everything
# ---------------------------------------------------------------------------

class User:
    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_id: str) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        return self.pets
