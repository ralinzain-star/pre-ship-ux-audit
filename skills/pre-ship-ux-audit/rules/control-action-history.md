---
title: History or Log of System Actions Is Accessible to the User
impact: MAJOR
impactDescription: without a record, users cannot verify or dispute what happened, so they stop trusting the output
order: 4
layer: Control & Transparency
earliestStage: static
stageNote: Whether a history surface exists is a design question. Whether it is complete and accurate needs real data.
tags: history, audit trail, verification, trust
---

## History or Log of System Actions Is Accessible to the User

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
