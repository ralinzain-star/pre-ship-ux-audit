# User journey draft: [feature name]

Fill this in before a usability test. It is the difference between testing whether people
can achieve their goals and testing whether they can operate your interface, which are not
the same question and do not have the same answer.

Half-filled is fine. An honest draft with three goals and a note saying "not sure about the
returning-user case" is more useful than a complete-looking one built on guesses, because
the guesses are what the test is supposed to challenge.

---

## Context

- **Feature**: 
- **URL**: (the running build. Staging is fine. Note any state it needs)
- **Test account**: (a pre-authenticated session, or "none available")
- **Round**: 1
- **Out of scope**: (mobile, a half-built step, anything knowingly unfinished)

## Personas

| Persona | What they already have | What they have never seen |
|---|---|---|
| First-time | e.g. account created, no resume uploaded | this feature, the vocabulary |
| Returning | e.g. 3 past sessions, resume on file | the new step added this release |

The two need separate runs wherever the screens differ. A single averaged run hides the
failure that only one of them hits, and it is usually the new user.

---

## The journey as designed

List the steps the flow actually contains, in order, as built. This is the design talking,
not the user. Fill it in first: it is what you derive the goals from.

| # | Screen or step | What the user does here | What the system does |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

Anything you cannot fill in is worth noting. A step where you cannot say what the system
does with the input is usually ceremony, see below.

---

## Derived goals

Now climb out of the flow. For each cluster of steps, ask "why is the user doing this?"
until the answer stops containing nouns the product invented. The full method, the two
validity tests, and the gap analysis are in `references/jtbd.md`. Read it before
filling this in: deriving goals from a designed flow is circular unless you do it
deliberately, and a goal that is a restatement of the design produces a test that cannot
fail.

| Goal (user's words) | Steps it maps to | Other-path test | Competitor test |
|---|---|---|---|
|  |  | ✅ / ❌ |  ✅ / ❌ |
|  |  |  |  |

Both tests must pass. If either fails, you have not climbed far enough: the goal is still
describing your solution rather than the user's problem.

### Gaps and ceremony

The two mismatches are findings, and neither appears in a checklist audit:

- **Gaps**: a real goal with no step serving it. Users came for this and the product has no
  path. They leave without filing a complaint, because nothing broke.
- **Ceremony**: a step no JTBD hires. A field nothing reads downstream, a confirmation
  the backend needed, an onboarding question the product never uses. Friction the user pays
  for and the team gets nothing from.

| Type | What | Where |
|---|---|---|
| Gap |  |  |
| Ceremony |  |  |

---

## Tasks

One task per **derived goal** above, not one per screen. Write it the way the user would
say it to a friend, not the way the product names it. "Find out why my application was rejected" is a goal. "Open the Match
Report tab" is an instruction, and an instruction tests nothing: it hands over the answer.

### Task 1

- **Goal** (user's words): 
- **Persona**: first-time / returning
- **Starting point**: (URL and state, e.g. "logged-in dashboard, no resume uploaded")
- **Success condition** (observable on screen): 
- **Priority**: primary / secondary / tertiary
- **Shortest correct path**: (the steps you expect, for step-count comparison. The tester
  does not read this until after the attempt)

### Task 2

- **Goal**: 
- **Persona**: 
- **Starting point**: 
- **Success condition**: 
- **Priority**: 
- **Shortest correct path**: 

### Task 3

- **Goal**: 
- **Persona**: 
- **Starting point**: 
- **Success condition**: 
- **Priority**: 
- **Shortest correct path**: 

---

## Priority maps to severity

| Priority | Meaning | Weight if failed |
|---|---|---|
| **primary** | The reason the feature exists. Failing it means the feature does not work. | CRITICAL |
| **secondary** | A common supporting goal. Failing it hurts retention. | MAJOR |
| **tertiary** | An occasional or power-user goal. | NICE_TO_HAVE |

Be strict about primary. If everything is primary, the scorecard cannot tell the team what
to fix first, which is the only thing they wanted from it.

## Freeze this after Round 1

Once the JTBD set is agreed, do not rewrite it between rounds. These goals are the fixed
measuring stick: they are what makes Round 2's task success rate comparable to Round 1's.
Rewriting them because the design changed means measuring the new design against itself.

When the product genuinely gains a new purpose, add a goal and mark it new, so the report
can show the score on the original set and the full set separately. Never edit or quietly
drop one. A goal that got *harder* to reach between rounds is the single most valuable
thing this system can surface, and dropping it hides exactly that.

---

## Worked example

### Task 1

- **Goal**: "I want to practise for an interview at a specific company this week."
- **Persona**: first-time
- **Starting point**: `/dashboard`, logged in, resume on file, never opened Interview Coach
- **Success condition**: a practice session is running with questions tailored to a job the
  user chose
- **Priority**: primary
- **Shortest correct path**: dashboard → Interview Coach → pick saved job → Start session
  (4 steps)

### Task 2

- **Goal**: "I got interrupted. I want to pick up where I left off."
- **Persona**: returning
- **Starting point**: `/dashboard`, one session abandoned at question 3
- **Success condition**: the user is back at question 3 with earlier answers intact
- **Priority**: secondary
- **Shortest correct path**: dashboard → Resume session (2 steps)
