---
title: Duplicate or Conflicting Actions Are Prevented or Flagged
impact: MAJOR
impactDescription: duplicates corrupt the user's data and burn credits or spend twice
order: 3
layer: Edge Cases
earliestStage: prototype
stageNote: Needs something clickable twice. A design can still be checked for a drawn conflict or already-submitted state.
tags: idempotency, double submit, race condition, conflict
---

## Duplicate or Conflicting Actions Are Prevented or Flagged

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
