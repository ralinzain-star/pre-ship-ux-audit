---
title: Mid-Flow Interruptions Don't Cause Data Loss or Corruption
impact: MAJOR
impactDescription: losing user input mid-flow is the single most reliable way to lose the user
order: 4
layer: Edge Cases
tags: draft, autosave, session, recovery, interruption
---

## Mid-Flow Interruptions Don't Cause Data Loss or Corruption

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
