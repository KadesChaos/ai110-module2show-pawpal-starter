from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+, a pet care planning assistant.

Add an owner's pets, schedule tasks for them, then generate today's schedule.
"""
)

st.divider()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("owner-1", owner_name, "")

owner: Owner = st.session_state.owner
owner.name = owner_name

st.subheader("Add a Pet")
col1, col2 = st.columns(2)
with col1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    pet_id = f"pet-{len(owner.get_pets()) + 1}"
    owner.add_pet(Pet(pet_id, new_pet_name, new_pet_species, "", date(2020, 1, 1)))
    st.rerun()

if not owner.get_pets():
    st.info("No pets yet. Add one above.")
    st.stop()

st.write("Current pets:")
st.table([{"name": p.name, "species": p.species} for p in owner.get_pets()])

st.divider()

st.subheader("Schedule a Task")

pet_names = [p.name for p in owner.get_pets()]
selected_pet_name = st.selectbox("Pet", pet_names)
selected_pet = next(p for p in owner.get_pets() if p.name == selected_pet_name)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.time_input("Time", value=time(8, 0))
with col3:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Add task"):
    task_id = f"task-{len(selected_pet.get_tasks()) + 1}"
    scheduled_time = datetime.combine(date.today(), task_time)
    selected_pet.add_task(
        Task(
            id=task_id,
            pet_id=selected_pet.id,
            description=task_title,
            scheduled_time=scheduled_time,
            frequency=frequency,
        )
    )
    st.rerun()

if selected_pet.get_tasks():
    st.write(f"Tasks for {selected_pet.name}:")
    st.table(
        [
            {"description": t.description, "time": t.scheduled_time.strftime("%I:%M %p"), "frequency": t.frequency}
            for t in selected_pet.get_tasks()
        ]
    )
else:
    st.info(f"No tasks yet for {selected_pet.name}. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    todays_tasks = scheduler.get_daily_schedule(date.today())

    if not todays_tasks:
        st.info("No tasks scheduled for today. Add some tasks above.")
    else:
        conflicts = scheduler.get_owner_conflicts()
        if conflicts:
            for earlier, later in conflicts:
                earlier_pet = owner.get_pet(earlier.pet_id)
                later_pet = owner.get_pet(later.pet_id)
                st.warning(
                    f"Conflict: '{earlier.description}' ({earlier_pet.name if earlier_pet else 'Unknown'}) "
                    f"at {earlier.scheduled_time.strftime('%I:%M %p')} is close to "
                    f"'{later.description}' ({later_pet.name if later_pet else 'Unknown'}) "
                    f"at {later.scheduled_time.strftime('%I:%M %p')}"
                )

        st.write("Today's schedule:")
        for task in todays_tasks:
            pet = owner.get_pet(task.pet_id)
            pet_label = pet.name if pet else "Unknown"
            time_str = task.scheduled_time.strftime("%I:%M %p")
            status = "done" if task.completed else "pending"
            st.markdown(f"- **{time_str}** — {pet_label}: {task.description} ({task.frequency}, {status})")
