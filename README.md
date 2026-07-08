# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
========================================
08:00 AM  Rex        Breakfast (pending)
12:00 PM  Whiskers   Give allergy pill (pending)
03:00 PM  Rex        Annual checkup (pending)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
================================================= test session starts =================================================
platform win32 -- Python 3.14.5, pytest-9.0.3, pluggy-1.6.0
rootdir: E:\school\codepath\.git\codepathAI110\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 25 items

tests\test_pawpal.py .........................                                                                   [100%]

================================================= 25 passed in 0.07s ==================================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts any iterable of tasks (or all of the owner's tasks) by `scheduled_time`, earliest first. Reused internally by `get_upcoming_tasks()`, `get_daily_schedule()`, `get_filtered_tasks()`, and `filter_tasks()` so there's one sort implementation instead of four. |
| Filtering | `Scheduler.get_filtered_tasks()`, `Scheduler.filter_tasks()` | `get_filtered_tasks(pet_id, completed, day)` filters by pet id, completion status, and/or calendar day. `filter_tasks(completed, pet_name)` filters the same way but by pet **name** instead of id, for callers that only have the pet's display name. Both combine filters with AND and return results sorted by time. |
| Conflict handling | `Scheduler.get_conflicts()`, `Scheduler.get_owner_conflicts()`, `Scheduler.get_exact_time_conflicts()`, `Scheduler.describe_conflicts()` | `get_conflicts(pet_id, buffer_minutes=15)` flags a single pet's incomplete tasks scheduled within a time buffer of each other; `get_owner_conflicts(buffer_minutes=15)` does the same across all of the owner's pets (e.g. two different pets needing attention at once). `get_exact_time_conflicts(pet_id=None)` is a stricter check for tasks at the *exact* same timestamp. All three sort once and compare only adjacent tasks (O(n log n)) and return conflicts as data, not exceptions. `describe_conflicts()` turns those pairs into printable warning strings so a scheduling clash surfaces as a warning instead of crashing the app. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | `Task.next_occurrence()` advances `scheduled_time` by one day (`frequency="daily"`) or one week (`frequency="weekly"`) using `timedelta`, preserving the original time-of-day; a `"once"` task returns `None`. `Scheduler.complete_task(task_id)` marks the task complete and, if it recurs, automatically appends the next occurrence (with a freshly generated id) to the same pet's task list. |
| UI presentation | `app.py` | Sorted/filtered task lists render via `st.table()` with a ✅/⏳ status column instead of raw text. Conflict warnings from `describe_conflicts()` are shown with `st.warning()` next to the schedule they refer to, each ending in an actionable suggestion (e.g. "consider rescheduling one of these"). When no conflicts are found, `st.success()` confirms the schedule is clear instead of showing nothing. |

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`) is organized into three sections:

- **Owner** — enter/edit the owner's name, stored in session state.
- **Pets** — add a pet (name + species) and see all current pets in a table.
- **Schedule a Task** — pick a pet, enter a task title, time, and frequency (`once`, `daily`, `weekly`), and add it to that pet's task list. Each pet's task table shows time, description, frequency, and a ✅/⏳ status, and immediately flags any same-pet time conflicts with `st.warning`/`st.success`.
- **Build Schedule** — generates today's full schedule across every pet, sorted chronologically, with owner-wide conflict warnings shown above the table.

### Example workflow

1. Enter the owner's name ("Kate") and click **Add pet** to add "Rex" (Dog).
2. Add a second pet, "Whiskers" (Cat).
3. Select Rex, add a task "Breakfast" at 8:00 AM with frequency `daily`.
4. Select Whiskers, add a task "Grooming appointment" at 3:00 PM with frequency `once`.
5. Select Rex again, add "Annual checkup" also at 3:00 PM — the per-pet view stays clear since these are different pets, but click **Generate schedule** and the owner-wide conflict check flags that Rex and Whiskers both need attention at 3:00 PM.
6. View **Today's schedule**, sorted earliest to latest, with the conflict warning displayed above it.

### Key Scheduler behaviors demonstrated

- **Sorting** — `Scheduler.sort_by_time()` (via `get_daily_schedule()`) always returns tasks earliest-first regardless of the order they were added.
- **Conflict warnings** — `Scheduler.get_conflicts()` / `get_owner_conflicts()` / `get_exact_time_conflicts()` catch tasks scheduled too close together (or at the exact same time) for one pet or across all of an owner's pets, and `describe_conflicts()` turns them into human-readable warnings instead of crashing the app.
- **Recurring tasks** — completing a `daily`/`weekly` task via `Scheduler.complete_task()` automatically generates and schedules its next occurrence.

### Sample CLI output (`python main.py`)

```
Today's Schedule (sort_by_time via get_daily_schedule)
=======================================================
  08:00 AM  Rex        Breakfast (pending)
  12:00 PM  Whiskers   Give allergy pill (done)
  03:00 PM  Rex        Annual checkup (pending)
  03:00 PM  Whiskers   Grooming appointment (pending)
  06:00 PM  Rex        Evening walk (pending)

All tasks sorted by time (sort_by_time)
=======================================================
  08:00 AM  Rex        Breakfast (pending)
  12:00 PM  Whiskers   Give allergy pill (done)
  03:00 PM  Rex        Annual checkup (pending)
  03:00 PM  Whiskers   Grooming appointment (pending)
  06:00 PM  Rex        Evening walk (pending)

Pending tasks only (filter_tasks completed=False)
=======================================================
  08:00 AM  Rex        Breakfast (pending)
  03:00 PM  Rex        Annual checkup (pending)
  03:00 PM  Whiskers   Grooming appointment (pending)
  06:00 PM  Rex        Evening walk (pending)

Completed tasks only (filter_tasks completed=True)
=======================================================
  12:00 PM  Whiskers   Give allergy pill (done)

Rex's tasks only (filter_tasks pet_name='Rex')
=======================================================
  08:00 AM  Rex        Breakfast (pending)
  03:00 PM  Rex        Annual checkup (pending)
  06:00 PM  Rex        Evening walk (pending)

Rex's pending tasks (filter_tasks pet_name='Rex', completed=False)
=======================================================
  08:00 AM  Rex        Breakfast (pending)
  03:00 PM  Rex        Annual checkup (pending)
  06:00 PM  Rex        Evening walk (pending)

Conflict check (get_exact_time_conflicts)
=======================================================
Warning: 'Annual checkup' (Rex) at 03:00 PM conflicts with 'Grooming appointment' (Whiskers) at 03:00 PM
```
