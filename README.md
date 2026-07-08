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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts any iterable of tasks (or all of the owner's tasks) by `scheduled_time`, earliest first. Reused internally by `get_upcoming_tasks()`, `get_daily_schedule()`, `get_filtered_tasks()`, and `filter_tasks()` so there's one sort implementation instead of four. |
| Filtering | `Scheduler.get_filtered_tasks()`, `Scheduler.filter_tasks()` | `get_filtered_tasks(pet_id, completed, day)` filters by pet id, completion status, and/or calendar day. `filter_tasks(completed, pet_name)` filters the same way but by pet **name** instead of id, for callers that only have the pet's display name. Both combine filters with AND and return results sorted by time. |
| Conflict handling | `Scheduler.get_conflicts()`, `Scheduler.get_owner_conflicts()`, `Scheduler.get_exact_time_conflicts()`, `Scheduler.describe_conflicts()` | `get_conflicts(pet_id, buffer_minutes=15)` flags a single pet's incomplete tasks scheduled within a time buffer of each other; `get_owner_conflicts(buffer_minutes=15)` does the same across all of the owner's pets (e.g. two different pets needing attention at once). `get_exact_time_conflicts(pet_id=None)` is a stricter check for tasks at the *exact* same timestamp. All three sort once and compare only adjacent tasks (O(n log n)) and return conflicts as data, not exceptions. `describe_conflicts()` turns those pairs into printable warning strings so a scheduling clash surfaces as a warning instead of crashing the app. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | `Task.next_occurrence()` advances `scheduled_time` by one day (`frequency="daily"`) or one week (`frequency="weekly"`) using `timedelta`, preserving the original time-of-day; a `"once"` task returns `None`. `Scheduler.complete_task(task_id)` marks the task complete and, if it recurs, automatically appends the next occurrence (with a freshly generated id) to the same pet's task list. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
