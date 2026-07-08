from datetime import date, datetime

from pawpal_system import (
    Owner,
    Pet,
    FeedingSchedule,
    MedicationReminder,
    VetAppointment,
    Scheduler,
)


def main() -> None:
    owner = Owner("o1", "Kate", "kate.tipograf@gmail.com")

    rex = Pet("p1", "Rex", "Dog", "Labrador", date(2020, 1, 1))
    whiskers = Pet("p2", "Whiskers", "Cat", "Tabby", date(2019, 6, 15))
    owner.add_pet(rex)
    owner.add_pet(whiskers)

    today = date.today()

    breakfast = FeedingSchedule(
        "t1", rex.id, "Breakfast", datetime.combine(today, datetime.min.time().replace(hour=8)),
        frequency="daily", food_type="kibble", portion_size=1.5,
    )
    medication = MedicationReminder(
        "t2", whiskers.id, "Give allergy pill", datetime.combine(today, datetime.min.time().replace(hour=12)),
        frequency="daily", medication_name="Cetirizine", dosage="5mg",
    )
    vet_visit = VetAppointment(
        "t3", rex.id, "Annual checkup", datetime.combine(today, datetime.min.time().replace(hour=15)),
        frequency="once", vet_name="Dr. Patel", clinic_name="Sunny Vet Clinic", reason="Annual checkup",
    )

    rex.add_task(breakfast)
    whiskers.add_task(medication)
    rex.add_task(vet_visit)

    scheduler = Scheduler(owner)

    print("Today's Schedule")
    print("=" * 40)
    for task in scheduler.get_daily_schedule(today):
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else "Unknown"
        time_str = task.scheduled_time.strftime("%I:%M %p")
        status = "done" if task.completed else "pending"
        print(f"{time_str}  {pet_name:<10} {task.description} ({status})")


if __name__ == "__main__":
    main()
