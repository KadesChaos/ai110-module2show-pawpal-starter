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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- My `Scheduler.get_exact_time_conflicts()` only flags tasks scheduled at the *exact* same timestamp, rather than checking for overlapping durations (e.g. a 30-minute vet visit at 3:00 PM overlapping a 3:15 PM feeding). Tasks in this app are modeled as single points in time (`scheduled_time`) with no duration field, so there's nothing to overlap — two tasks either share a timestamp or they don't. I also added a separate, buffer-based check (`get_conflicts`/`get_owner_conflicts`) that flags tasks within a configurable number of minutes of each other (default 15), which approximates "close enough to be impractical for one owner to do both," but it's still a proxy for real interval overlap, not a true duration-aware check.
- Why is that tradeoff reasonable for this scenario?
- For a pet owner's daily task list, most tasks (feeding, medication, walks) are quick and not meaningfully "in progress" for a modeled duration — what actually matters is whether two things are due around the same moment. Adding a `duration` field and full interval-overlap logic (checking `start_a < end_b and start_b < end_a`) would be more accurate but adds a field every existing task would need to populate, plus more edge cases (what's a sensible default duration for a vet visit vs. a feeding?) for a feature that mostly matters for the vet-appointment case anyway. The buffer-based check gets most of the practical benefit — warning the owner about back-to-back commitments — without that added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
