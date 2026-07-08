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
    evening_walk = FeedingSchedule(
        "t4", rex.id, "Evening walk", datetime.combine(today, datetime.min.time().replace(hour=18)),
        frequency="daily", food_type="", portion_size=0.0,
    )
    grooming = VetAppointment(
        "t5", whiskers.id, "Grooming appointment", datetime.combine(today, datetime.min.time().replace(hour=15)),
        frequency="once", vet_name="Dr. Lopez", clinic_name="Sunny Vet Clinic", reason="Grooming",
    )

    # Added out of chronological order (15:00, 8:00, 18:00, 12:00, 15:00) to prove sorting works.
    # vet_visit and grooming share the same 3:00 PM slot for different pets, to trigger a conflict.
    rex.add_task(vet_visit)
    rex.add_task(breakfast)
    rex.add_task(evening_walk)
    whiskers.add_task(medication)
    whiskers.add_task(grooming)

    medication.mark_complete()

    scheduler = Scheduler(owner)

    def print_tasks(tasks) -> None:
        if not tasks:
            print("  (none)")
            return
        for task in tasks:
            pet = owner.get_pet(task.pet_id)
            pet_name = pet.name if pet else "Unknown"
            time_str = task.scheduled_time.strftime("%I:%M %p")
            status = "done" if task.completed else "pending"
            print(f"  {time_str}  {pet_name:<10} {task.description} ({status})")

    print("Today's Schedule (sort_by_time via get_daily_schedule)")
    print("=" * 55)
    print_tasks(scheduler.get_daily_schedule(today))

    print("\nAll tasks sorted by time (sort_by_time)")
    print("=" * 55)
    print_tasks(scheduler.sort_by_time())

    print("\nPending tasks only (filter_tasks completed=False)")
    print("=" * 55)
    print_tasks(scheduler.filter_tasks(completed=False))

    print("\nCompleted tasks only (filter_tasks completed=True)")
    print("=" * 55)
    print_tasks(scheduler.filter_tasks(completed=True))

    print("\nRex's tasks only (filter_tasks pet_name='Rex')")
    print("=" * 55)
    print_tasks(scheduler.filter_tasks(pet_name="Rex"))

    print("\nRex's pending tasks (filter_tasks pet_name='Rex', completed=False)")
    print("=" * 55)
    print_tasks(scheduler.filter_tasks(pet_name="Rex", completed=False))

    print("\nConflict check (get_exact_time_conflicts)")
    print("=" * 55)
    conflicts = scheduler.get_exact_time_conflicts()
    if conflicts:
        for message in scheduler.describe_conflicts(conflicts):
            print(message)
    else:
        print("  (no conflicts found)")


if __name__ == "__main__":
    main()
