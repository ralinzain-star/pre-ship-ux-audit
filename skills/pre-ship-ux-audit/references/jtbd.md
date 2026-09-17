# Deriving JTBD from a flow

You usually have the flow before you have the job. The tickets were written, the frames
exist, and nobody recorded what the user was hiring this product to do. This is the method
for recovering that as a **job**, not as a goal.

## Job, not goal

A goal derivation that climbs until no product noun remains will overshoot. It lands on
aspirations: "walk into an interview and not freeze". That sentence is true, moving, and
useless here. It names no trigger, it cannot be measured, and a hundred other products are
hired for it too.

A JTBD stops lower, at the rung that still holds a **situation** and a **progress**:

| Too low | A job | Too high |
|---|---|---|
| "Open the Match Report tab" | "When I find a posting that looks plausible, I want to know how well I actually match before committing an evening, so I can spend my limited evenings on the ones that could work" | "Walk into an interview and not freeze" |
| Names your solution | Names a trigger and a change of state | Names a life outcome |
| Testable, but only of your design | Testable, and a different solution could do it | Not testable at all |

The reason this matters for an audit: only the middle column produces desired outcomes you
can score. The right column cannot fail a usability test, so it cannot inform a ship
decision.

## The climb, and where to stop

For each cluster of steps, ask "why is the user doing this?" and keep asking. Two stopping
conditions, both required:

1. The answer contains **no noun the product invented**.
2. The answer still names **a situation you could observe someone being in**.

The moment condition 2 breaks, you have gone one rung too far. Step back down.

| Level | Answer | Verdict |
|---|---|---|
| Steps | Spend a credit, approve sections, wait, download | Product nouns |
| Why? | Produce a resume tailored to this posting | Product nouns |
| Why? | Send something that is not the generic document they send everywhere | **Job. Stop.** |
| Why? | Get a reply | Aspiration, no situation |
| Why? | Get hired | A life outcome, not a job |

## Two statement formats, both required

### 1. The job statement, situational (Christensen / Moesta)

> **When** [situation], **I want to** [motivation], **so I can** [expected outcome].

This is the readable one. It goes in front of stakeholders, and it is what a usability test
task is written from. The situation clause is what makes it a job: it is the trigger that
makes someone reach for a solution today rather than someday.

### 2. Desired outcome statements, measurable (Ulwick)

> [direction] + [metric] + [object of control] + [contextual clarifier]

> "**Minimize the time it takes to** determine whether a posting is worth applying to."
> "**Minimize the likelihood that** a tailored resume contains a claim the applicant cannot defend."
> "**Increase the number of** applications a person can keep track of without losing one."

Direction is `minimize` or `increase`. Metric is time, likelihood, number, or effort.
No adjectives, no solutions, no product nouns.

Two to five outcomes per JTBD. **These are what the eval scores.** A JTBD with no outcome
statement cannot be tested, and a JTBD you cannot test does not belong in a pre-ship audit.

## Three validity tests

Every job passes all three, or you have not landed on a job.

1. **Situation test.** Does it name an observable trigger? If you cannot finish "When ___"
   with something you could watch happen, it is an aspiration.
2. **Solution-free test.** Could a different solution, including a person or a spreadsheet,
   be hired for this job? If only your design expresses it, it is a feature, not a job.
3. **Measurability test.** Can you write at least one desired outcome with a direction and
   a metric? If not, nothing downstream can score it.

## Forces, when you need to explain non-adoption

For a job the product serves but users do not switch to, the four forces say why:

| Force | Question |
|---|---|
| **Push** | What about their current situation is bad enough to make them look? |
| **Pull** | What about this solution attracts them? |
| **Anxiety** | What are they afraid of about the new thing? |
| **Habit** | What is comfortable about what they do today? |

Anxiety and habit are usually where a pre-ship feature dies, and they are usually
undesigned, because the team only modelled push and pull. When a job is served on paper but
you expect low adoption, name the anxiety and check whether anything in the flow addresses
it. That is a finding.

## Map back against the flow

Same two mismatches as before, now stated in job terms:

| | The flow serves it | The flow does not |
|---|---|---|
| **A real job** | Working as intended | **Gap:** a JTBD nobody is hired to do |
| **Not a JTBD** | **Ceremony:** a step no JTBD hires | Ignore |

- **Gaps** make users leave without complaining, because nothing broke. The thing they came
  for simply was not there. Report under `jtbd-coverage`, and add
  `"rule": "flow-visible-entry-point"` when there is no way in at all.
- **Ceremony** is work the user does on behalf of the architecture. Report under
  `journey-economy`. The strongest signal is a step whose output nothing downstream reads.

## Freeze the JTBD set after Round 1

Jobs and their desired outcomes are the fixed measuring stick. Do not rewrite them between
rounds: they are what makes Round 2's results comparable. Jobs are stable in a way solutions
are not, which is the practical argument for using them here at all. If the product gains a
genuinely new purpose, add a job and mark it new, never edit or drop an existing one. A job
whose outcomes got *worse* between rounds is the most valuable thing this system can report.
