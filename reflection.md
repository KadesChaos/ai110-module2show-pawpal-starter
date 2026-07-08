# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- A pet care app with the functions of adding a pet, event/vet scheduling, feeding schedules/reminders, and medication reminders
- What classes did you include, and what responsibilities did you assign to each?
- The classes I included are: User, Pet, FeedingSchedule, MedicationReminder, Event, VetAppointment. The responsabilities are self explanatory.

**b. Design changes**

- Did your design change during implementation?
No.
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- Really just time. Every task has one scheduled time, and everything (sorting, daily view, conflict checks) is built around that. It also cares about whether something's done or not, and whether it repeats (daily/weekly), since that decides if a new task gets created after you complete one. There's no priority or "owner preference" concept at all right now.
- How did you decide which constraints mattered most?
- Time was the obvious one to start with since it's the whole point of a schedule, and it's easy to reason about since it's just a timestamp. Priority and preferences felt like "nice to have later" features that would need more design work (how do you rank things? what if two priorities tie?) without actually fixing the main problem, which was "can I tell when I've double-booked myself for my pets." Catching two tasks scheduled at the same or nearly the same time solves that without needing anything fancier.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- My `Scheduler.get_exact_time_conflicts()` only flags tasks scheduled at the *exact* same timestamp, rather than checking for overlapping durations (e.g. a 30-minute vet visit at 3:00 PM overlapping a 3:15 PM feeding). Tasks in this app are modeled as single points in time (`scheduled_time`) with no duration field, so there's nothing to overlap — two tasks either share a timestamp or they don't. I also added a separate, buffer-based check (`get_conflicts`/`get_owner_conflicts`) that flags tasks within a configurable number of minutes of each other (default 15), which approximates "close enough to be impractical for one owner to do both," but it's still a proxy for real interval overlap, not a true duration-aware check.
- Why is that tradeoff reasonable for this scenario?
- For a pet owner's daily task list, most tasks (feeding, medication, walks) are quick and not meaningfully "in progress" for a modeled duration — what actually matters is whether two things are due around the same moment. Adding a `duration` field and full interval-overlap logic (checking `start_a < end_b and start_b < end_a`) would be more accurate but adds a field every existing task would need to populate, plus more edge cases (what's a sensible default duration for a vet visit vs. a feeding?) for a feature that mostly matters for the vet-appointment case anyway. The buffer-based check gets most of the practical benefit — warning the owner about back-to-back commitments — without that added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI for debugging, refactoring, and implementation of concepts that I didn't really understand in the first place.
- What kinds of prompts or questions were most helpful?
Reworded prompts from our project instructions were the most helpful, as were follow-ups.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
One thing I did not accept was the original remake of my mirmaid diagram, as it tried to add a lot of complicated things that I haven't discussed or implemented in my project.
- How did you evaluate or verify what the AI suggested?
By running Pytest and checking if all of the test cases went through.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- The main stuff: tasks come back sorted by time, filtering by pet/status/day works, completing a recurring task actually creates the next one on the right day, and the different conflict checks (exact same time, "too close together" with a buffer, across one pet vs. across all of an owner's pets) catch what they're supposed to and ignore what they shouldn't. Also some boundary/edge cases like an empty task list, an unknown task or pet id, and a gap that's exactly at the buffer cutoff.
- Why were these tests important?
- These are the behaviors the whole app is built around, so if any of them were subtly wrong the schedule you'd see on screen would just be wrong or misleading. The edge cases mattered because those are exactly the spots where off-by-one type bugs like to hide, e.g. is a gap of exactly 15 minutes a conflict or not.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- Pretty confident for what it currently does. All 25 tests pass and coverage is around 87%, and the parts that are tested are tested from a few angles, not just the happy path. I'm less sure about things I haven't tried yet, like a really large number of tasks, or tasks added in a weird order interacting with recurrence.
- What edge cases would you test next if you had more time?
- I'd want to test what happens with a huge cluster of overlapping tasks (more than three at once) to make sure conflicts don't get missed since the conflict check only compares neighboring tasks after sorting. I'd also want to check recurring tasks that get completed many times in a row to make sure they keep advancing correctly, what happens if you remove a pet that still has tasks tied to it, and mixing time zones if this app ever needs to support that.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
- Probably the conflict detection stuff. It ended up covering a bunch of real scenarios (same pet, across pets, exact time vs. just "too close") without the code getting messy, and the tests actually gave me confidence it works instead of just hoping it does.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
- I'd add priority and maybe task duration, since right now everything is just a single point in time and there's no way to say "this matters more" or "this actually takes 30 minutes." I'd also clean up the UI a bit more since it's functional but pretty bare-bones.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
- That my UML diagram and my actual code drifted apart pretty fast once I started implementing, and that's fine as long as you go back and update the diagram at the end instead of treating it as a one-and-done step. Also, AI is really useful for catching gaps (like missing edge case tests) that I wouldn't have thought to test myself, but I still needed to actually run things and check the output instead of just trusting a suggestion looked reasonable.
