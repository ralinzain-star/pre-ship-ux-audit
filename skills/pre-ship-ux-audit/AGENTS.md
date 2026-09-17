# A pre-ship UX audit framework

**Version 1.0.0**  
Jobscan Product Design  
September 2026

> **Note:**  
> This is the compiled, single-file version of the pre-ship-ux-audit skill.  
> Generated from `rules/` by `scripts/build_agents.py`. Edit the rule files,  
> not this document. `SKILL.md` is the index to read first when you only need  
> one or two layers.

---

## Abstract

A pre-ship UX audit framework. Every finding is evaluated against four layers (Flow Integrity, Control & Transparency, Trust & Copy, Edge Cases) and assigned a severity tied to user and business cost, so a PM can prioritise the result without re-litigating it.

---

## Table of Contents

1. [Flow Integrity](#1-flow-integrity) · **Critical**
   - 1.1 [Entry Point Is Visible and Clear](#11-entry-point-is-visible-and-clear)
   - 1.2 [Every Step's Prerequisite Is Met Before the User Enters It](#12-every-steps-prerequisite-is-met-before-the-user-enters-it)
   - 1.3 [Success, Failure, Loading, and Empty States All Have a Designed Response](#13-success-failure-loading-and-empty-states-all-have-a-designed-response)
   - 1.4 [Users Don't Need to Guess What the System Is Doing](#14-users-dont-need-to-guess-what-the-system-is-doing)
2. [Control & Transparency](#2-control-transparency) · **Critical**
   - 2.1 [Users Can Pause, Stop, or Undo, and the Exit Point Is Obvious](#21-users-can-pause-stop-or-undo-and-the-exit-point-is-obvious)
   - 2.2 [Irreversible Actions Have a Confirmation Step](#22-irreversible-actions-have-a-confirmation-step)
   - 2.3 [System Behaviour Is Explained](#23-system-behaviour-is-explained)
   - 2.4 [History or Log of System Actions Is Accessible to the User](#24-history-or-log-of-system-actions-is-accessible-to-the-user)
3. [Trust & Copy](#3-trust-copy) · **Major**
   - 3.1 [Error Messages Tell the User What Went Wrong and What to Do Next](#31-error-messages-tell-the-user-what-went-wrong-and-what-to-do-next)
   - 3.2 [UX Copy Is Clear, Jargon-Free, and Not Anxiety-Inducing](#32-ux-copy-is-clear-jargon-free-and-not-anxiety-inducing)
   - 3.3 [Recommendations and System Decisions Include a Brief Reason](#33-recommendations-and-system-decisions-include-a-brief-reason)
   - 3.4 [CTAs Are Specific](#34-ctas-are-specific)
4. [Edge Cases](#4-edge-cases) · **Major**
   - 4.1 [Incomplete Profile or Missing Data Is Handled Gracefully, Not Silently Ignored](#41-incomplete-profile-or-missing-data-is-handled-gracefully-not-silently-ignored)
   - 4.2 [Network Errors and Timeouts Have a User-Facing Fallback](#42-network-errors-and-timeouts-have-a-user-facing-fallback)
   - 4.3 [Duplicate or Conflicting Actions Are Prevented or Flagged](#43-duplicate-or-conflicting-actions-are-prevented-or-flagged)
   - 4.4 [Mid-Flow Interruptions Don't Cause Data Loss or Corruption](#44-mid-flow-interruptions-dont-cause-data-loss-or-corruption)
   - 4.5 [First-Time and Returning User Experiences Are Distinct, With No Dead Ends](#45-first-time-and-returning-user-experiences-are-distinct-with-no-dead-ends)

---

## 1. Flow Integrity

**Impact: Critical**

Broken steps or missing states. A user who cannot start, cannot continue, or hits an undesigned state is blocked, and no amount of polish elsewhere recovers that.

### 1.1 Entry Point Is Visible and Clear

**Impact: Critical (a feature users cannot find has zero activation regardless of quality)**

The user has to know the feature exists and know how to start it. This is the
cheapest thing to get wrong and the most expensive to discover after launch,
because the metric it moves is activation, and a flat activation curve looks
identical whether the feature is bad or simply invisible. Teams usually see the
entry point clearly because they have been staring at the frame for weeks.

**Fails when:**

- The only way in is a menu item three levels deep, or an icon with no label
- The entry point is a banner that a returning user dismissed once and never sees again
- Two entry points lead to the same flow but promise different things
- The spec says "users can access X from the dashboard" and no dashboard frame shows it

**Passes when:**

- A first-time user landing on the parent screen can name what the feature does and where to click
- The label describes the outcome, not the mechanism
- If the feature is promoted, there is still a permanent home for it after the promotion ends

**How to check:** open the parent screen frame and cover everything except what a
new user sees above the fold. If you cannot find the way in, neither can they.

_Rule file: `rules/flow-visible-entry-point.md`_

### 1.2 Every Step's Prerequisite Is Met Before the User Enters It

**Impact: Critical (users hit a wall mid-flow after investing effort, the worst place to drop out)**

A step that needs data the user has not provided yet is a dead end dressed as
progress. The cost is worse than blocking them at the start, because they have
already spent effort and now feel it was wasted. Check the order of the flow
against what each step actually consumes.

**Fails when:**

- Step 3 needs a resume on file, and nothing in steps 1 and 2 asked for one
- A paid-tier action sits inside a flow a free user can enter, with the paywall at the end
- The flow assumes a connected integration that the user may never have authorised
- A "Continue" button is enabled before the field it depends on is filled

**Passes when:**

- Each step can be completed with only what the user has supplied so far
- Where a prerequisite is genuinely required, it is collected earlier or the entry
  point states it up front
- Gating happens at the entry point, not at the finish line

**How to check:** walk the journey step by step and list what each screen reads
from. Any input that has no earlier source is a finding.

_Rule file: `rules/flow-prerequisites-met.md`_

### 1.3 Success, Failure, Loading, and Empty States All Have a Designed Response

**Impact: Critical (an undesigned state ships as whatever the engineer improvises, usually nothing)**

The happy path is almost always designed. The other three are where the feature
actually breaks, and an undesigned state does not disappear: it gets improvised
during implementation, usually as a blank screen or a spinner with no timeout.
Every screen in the flow needs all four accounted for, even if the answer is
"this state is impossible here" stated explicitly.

**Fails when:**

- A list screen has no empty state, so a new user sees a bare frame
- The only loading treatment is a spinner, with no indication of how long or what is happening
- There is a success screen but no failure screen for the same action
- The spec describes a failure case that has no corresponding frame

**Passes when:**

- Every screen has all four states designed, or a written note saying why one cannot occur
- The empty state tells the user what to do to fill it, not just that it is empty
- Long operations show progress or an estimate rather than an indefinite spinner

**How to check:** build the four-by-N grid (four states down, one column per
screen) and fill it in. Any blank cell is either a finding or a note.

_Rule file: `rules/flow-all-states-designed.md`_

### 1.4 Users Don't Need to Guess What the System Is Doing

**Impact: Major (silence during processing reads as failure and drives abandonment and duplicate submissions)**

When the interface goes quiet, users assume it is broken. They refresh, they
click again, they leave. This matters most in AI features, where a genuine
fifteen second wait is normal and indistinguishable from a hang. The fix is
rarely making it faster, it is making the wait legible.

**Fails when:**

- A multi-second action gives no acknowledgement that the click registered
- A background job finishes with no notification, so the user never learns it succeeded
- Progress is shown as a percentage that jumps from 10 to 100 with no meaning behind it
- The interface looks identical before and during processing

**Passes when:**

- Every action acknowledges the click immediately, even if the result takes time
- Waits longer than a few seconds say what is happening, in the user's terms
- Completion is surfaced whether or not the user is still on the screen

**How to check:** for each action, ask what the user sees at 0.5 seconds, at 3
seconds, and at 30 seconds. Three different answers usually means it is handled.

_Rule file: `rules/flow-system-status-visible.md`_

## 2. Control & Transparency

**Impact: Critical**

Whether the user feels in control of the system. Covers exits, undo, confirmation on irreversible actions, and whether the system explains what it is doing and what it has done.

### 2.1 Users Can Pause, Stop, or Undo, and the Exit Point Is Obvious

**Impact: Critical (a flow with no exit traps users, who then leave the product rather than the flow)**

People commit to a flow more readily when they can see the way out. Removing the
exit to improve completion is a false economy: the completion rate goes up and
trust goes down, and the users who felt trapped are the ones who do not come
back. This applies doubly to anything running on the user's behalf, where the
ability to stop it is the difference between a tool and a runaway process.

**Fails when:**

- A modal has no close affordance and the only buttons are "Continue" and "Upgrade"
- A long-running generation cannot be cancelled once started
- Leaving mid-flow silently discards everything with no way back
- Undo exists but only for three seconds in a toast the user did not look at

**Passes when:**

- Every screen in the flow has a visible way out, and the label says what leaving does
- Anything running on the user's behalf can be stopped, and stopping takes effect promptly
- Destructive-by-omission exits (closing loses work) either save a draft or warn first

**How to check:** on every frame, point at the exit. If you have to explain where
it is, it is not obvious.

_Rule file: `rules/control-pause-stop-undo.md`_

### 2.2 Irreversible Actions Have a Confirmation Step

**Impact: Critical (one mis-click causes permanent data loss and a support ticket you cannot resolve)**

Anything that cannot be undone needs a deliberate second action. The test for
"irreversible" is not whether the database row is deleted, it is whether the user
can get back to where they were: sending a message, publishing a profile, and
spending a credit all qualify. Note that a confirmation dialog on a reversible
action is its own problem, because dialogs people dismiss reflexively stop
working on the one that matters.

**Fails when:**

- Delete happens on a single click with a toast as the only notice
- The confirmation says "Are you sure?" without naming what will be lost
- Both buttons look the same, so the destructive one is as easy to hit as cancel
- Confirmations are used on routine, reversible actions, training users to click through

**Passes when:**

- The dialog names the specific thing being destroyed and what cannot be recovered
- The safe option is the default, and the destructive one is visually distinct
- For high-stakes actions, undo is offered instead of, or as well as, confirmation

**How to check:** list every action in the flow that cannot be undone from the
interface. Each one needs either a confirmation or an undo, and you should be
able to say which.

_Rule file: `rules/control-confirm-irreversible.md`_

### 2.3 System Behaviour Is Explained

**Impact: Major (unexplained system behaviour reads as malfunction and generates support load)**

Users build a mental model of what the product does whether or not you give them
one, and the model they invent unaided is usually wrong and usually
uncharitable. When the system takes an action, changes something, or declines to
do something, saying why costs one line of copy and saves the support
conversation. This is most acute where the system acts automatically: automation
the user cannot predict feels like a bug.

**Fails when:**

- An item disappears from a list with no explanation of what moved it
- A field is disabled with no indication of what would enable it
- The system silently changes something the user entered (trimming, reformatting, deduping)
- An action is rejected with no reason, so the user retries the same thing

**Passes when:**

- Every automatic change is attributed and briefly explained
- Disabled states say what unlocks them
- The user can predict what the system will do next before doing it

**How to check:** find every place the system acts without the user asking. Each
one needs an explanation the user can read at that moment.

_Rule file: `rules/control-explain-behaviour.md`_

### 2.4 History or Log of System Actions Is Accessible to the User

**Impact: Major (without a record, users cannot verify or dispute what happened, so they stop trusting the output)**

If the system does work on the user's behalf, the user needs to be able to look
back at what it did. This is what makes the difference between delegating and
gambling. The log does not have to be elaborate: a dated list of what ran and
what changed is enough for the user to verify, to notice something wrong, and to
explain the result to someone else.

**Fails when:**

- A one-off toast is the only record that an action occurred
- Results are overwritten by the next run with no version kept
- The user can see the current state but not how it got there
- Something the system did cannot be traced back to a trigger

**Passes when:**

- Past actions are listed with what happened, when, and what changed
- Previous results remain reachable after a new run
- The user can tell which changes were theirs and which were the system's

**How to check:** ask what a user would do if they suspected the system got
something wrong yesterday. If there is no screen that answers that, this fails.

_Rule file: `rules/control-action-history.md`_

## 3. Trust & Copy

**Impact: Major**

Whether the experience builds confidence rather than anxiety. Covers error messages, plain language, stated reasons behind system decisions, and specific calls to action.

### 3.1 Error Messages Tell the User What Went Wrong and What to Do Next

**Impact: Critical (a dead-end error converts a recoverable moment into a churned user)**

An error is a fork: the user either recovers or leaves. What decides it is
whether the message contains a next action. "Something went wrong" contains none,
so the user's only remaining move is to try again or give up. Every error needs
the cause in plain terms and the specific thing to do, and if there is genuinely
nothing the user can do, it needs to say that and say who is handling it.

**Fails when:**

- The message is a status code, a stack trace, or "An unexpected error occurred"
- The message states the problem but offers no action
- The error appears far from the field that caused it
- Validation fires only on submit, after the user has filled everything in

**Passes when:**

- The message names the cause in the user's vocabulary
- It gives one specific next step, and the control to do it is right there
- Where nothing can be done, it says so and sets an expectation
- Field-level problems are flagged at the field

**How to check:** read every error string aloud and ask what you would do next.
If the answer is "refresh and hope", it fails.

_Rule file: `rules/trust-actionable-errors.md`_

### 3.2 UX Copy Is Clear, Jargon-Free, and Not Anxiety-Inducing

**Impact: Major (copy that confuses or alarms suppresses the action it is attached to)**

Internal vocabulary leaks into interfaces constantly, because the team stopped
hearing it a year ago. So does defensive legal phrasing, which reads to a user
as a warning that something bad is about to happen. Both suppress the action they
sit next to. The bar is that a new user reads the line once, at speed, and knows
what will happen.

**Fails when:**

- Copy uses internal names for things: model names, feature codenames, table names
- Legal or safety phrasing is attached to a routine action, making it feel risky
- A sentence needs a second read to parse
- Copy implies blame: "You failed to...", "Invalid input"

**Passes when:**

- Every noun in the interface is something the user would say themselves
- The tone matches the stakes: calm for routine, direct for genuinely destructive
- Instructions lead with the action, not the caveat

**How to check:** read the screen as someone who started using the product this
morning. Circle every word you would have had to look up.

_Rule file: `rules/trust-plain-language.md`_

### 3.3 Recommendations and System Decisions Include a Brief Reason

**Impact: Major (unexplained recommendations are ignored or distrusted, wasting the feature entirely)**

When a product tells a user what to do, the reason is what converts the
suggestion into an action. Without it, a good recommendation and a bad one look
identical, so users apply their own judgement and the feature adds nothing. This
is the central design problem in AI features: the quality of the model matters
far less than whether the user can tell when to trust it.

**Fails when:**

- A score or rating is shown with no breakdown of what moved it
- The system ranks or filters results with no stated basis
- A suggestion is presented as fact with no source
- The reason exists but is buried behind a click most users will not make

**Passes when:**

- Each recommendation carries a short, specific reason visible at the same moment
- The reason references the user's own data where possible
- Confidence or uncertainty is expressed when the system is genuinely unsure

**How to check:** for each thing the system recommends, ask "why this one?" If the
interface cannot answer without you opening the code, the user cannot either.

_Rule file: `rules/trust-explain-recommendations.md`_

### 3.4 CTAs Are Specific

**Impact: Nice to have (vague buttons add hesitation at exactly the moment you want none)**

A button label is the last thing a user reads before committing, so it should
name the outcome rather than the mechanism. "Submit" describes what the form
does; "Start my audit" describes what the user gets. The gain per button is
small, which is why this is polish rather than a blocker, but it compounds
across a flow and it removes the pause where a user wonders what they just
agreed to.

**Fails when:**

- Labels are generic: "Submit", "Click here", "OK", "Continue" with no context
- Two buttons on the same screen are both called "Continue"
- The label describes the interaction rather than the result
- The primary and secondary actions are worded so similarly that the choice is unclear

**Passes when:**

- The label is a verb plus the object: "Save draft", "Send to my inbox"
- Reading only the buttons on a screen makes the choice clear
- Destructive and safe options are worded distinctly, not just coloured differently

**How to check:** cover everything on the frame except the buttons. If you cannot
tell what each one does, the label is doing no work.

_Rule file: `rules/trust-specific-ctas.md`_

## 4. Edge Cases

**Impact: Major**

What happens when things go wrong. Missing data, network failure, duplicate actions, interruptions, and the difference between a first-time and a returning user.

### 4.1 Incomplete Profile or Missing Data Is Handled Gracefully, Not Silently Ignored

**Impact: Critical (the users most likely to hit this are new users, so the failure lands on activation)**

Designs are drawn with a complete, realistic profile. Real users arrive with
three fields filled in. Silently degrading (a blank section, a zero score, a
result computed from nothing) is worse than refusing, because the user reads the
empty output as the product's verdict on them rather than as missing input.

**Fails when:**

- A section renders blank when its source data is absent, with no explanation
- A score is computed and displayed from partial data as if it were complete
- The feature runs and returns nothing, with no indication that input was missing
- Only the fully-populated version of the screen exists in Figma

**Passes when:**

- Missing input is named specifically, along with what to add and where
- The system either refuses clearly or proceeds with a stated caveat, never silently
- Partial results are labelled as partial

**How to check:** run the flow mentally with an account created two minutes ago.
Every screen that changes shape is a state that needs designing.

_Rule file: `rules/edge-missing-data.md`_

### 4.2 Network Errors and Timeouts Have a User-Facing Fallback

**Impact: Critical (the most common real-world failure, and usually the least designed)**

Every design is drawn on a fast connection against a healthy backend. In
production, requests time out, third-party APIs stall, and phones drop to one
bar. This is the highest-frequency failure in most products and the one most
likely to have no frame at all, which means it ships as an infinite spinner.

**Fails when:**

- There is no timeout: the spinner runs indefinitely
- A failed request leaves the interface in the pre-request state with no message
- Retry means starting the whole flow again
- An offline user gets the same generic error as a server-side failure

**Passes when:**

- Every request has a defined timeout and a designed state for exceeding it
- Failures offer retry in place, preserving what the user already entered
- Offline is distinguished from server error, because the user's next action differs
- For long operations, the result is recoverable after a disconnect

**How to check:** for each network call in the flow, name the frame the user sees
when it takes thirty seconds and when it never returns.

_Rule file: `rules/edge-network-failure.md`_

### 4.3 Duplicate or Conflicting Actions Are Prevented or Flagged

**Impact: Major (duplicates corrupt the user's data and burn credits or spend twice)**

When the system is slow, users click again. This is not user error, it is the
predictable response to an interface that gave no feedback. The result is
duplicate records, double charges, or two jobs racing each other. The same
applies to conflicts: two tabs open, or two people editing the same object.

**Fails when:**

- The primary button stays active while its request is in flight
- Submitting twice creates two records rather than being recognised as one intent
- Two tabs on the same object overwrite each other with no warning
- Starting a second run silently cancels or corrupts the first

**Passes when:**

- Actions disable while in flight and re-enable on a definite outcome
- Repeat submissions of the same intent are recognised, not duplicated
- Conflicts are surfaced to the user with a choice, rather than resolved silently
- Where a duplicate does occur, the user can see and remove it

**How to check:** for each action, ask what happens on a double click and what
happens with the same screen open in two tabs.

_Rule file: `rules/edge-duplicate-actions.md`_

### 4.4 Mid-Flow Interruptions Don't Cause Data Loss or Corruption

**Impact: Major (losing user input mid-flow is the single most reliable way to lose the user)**

Long flows get interrupted: a phone call, a closed tab, an expired session, a
battery. The question is not whether it happens but what the user finds when they
come back. Work lost to an interruption is felt as the product's fault, and
people rarely re-enter it a second time.

**Fails when:**

- Closing the tab discards everything entered, with no warning and no draft
- Session expiry logs the user out and drops their in-progress input
- Returning to the flow restarts it from step one
- A partially completed record is saved in a state that cannot be resumed or deleted

**Passes when:**

- Input is preserved across interruption, and the user is told it was saved
- Returning resumes at the step they left, with prior steps intact
- Session expiry re-authenticates and returns the user to their place
- Partial records are either resumable or cleanly discardable

**How to check:** at each step, ask what survives if the tab closes right now. If
the answer is "nothing", that is the finding.

_Rule file: `rules/edge-interruption-recovery.md`_

### 4.5 First-Time and Returning User Experiences Are Distinct, With No Dead Ends

**Impact: Nice to have (one screen serving both audiences under-serves both)**

These two users need opposite things. The first-timer needs orientation and a
single obvious next step. The returning user needs their work, fast, without
re-reading the introduction. A screen designed for one of them quietly penalises
the other, and the usual casualty is the returning user who sits through
onboarding every visit.

**Fails when:**

- The same screen serves both, so it is either too sparse or too noisy for one of them
- Onboarding cannot be skipped or repeats on every session
- The returning user lands on a generic home rather than their most recent work
- A user who completes the flow once has no obvious reason or route to return

**Passes when:**

- The first-time state teaches and offers exactly one next step
- The returning state leads with the user's own content and recent activity
- Guidance can be dismissed and recalled
- Finishing the flow leaves a clear next action rather than a dead end

**How to check:** draw the same screen twice, once for a user with no data and
once for a user with plenty. If they look the same, one of them is wrong.

_Rule file: `rules/edge-first-vs-returning.md`_

---

## References

- https://app.notion.com/p/Pre-ship-UX-checklist-361997983434804fb5d9c45c44e4c2f7
- https://app.notion.com/p/36d997983434802fb763dbd3179242aa
