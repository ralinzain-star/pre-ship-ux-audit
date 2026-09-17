---
title: Irreversible Actions Have a Confirmation Step
impact: CRITICAL
impactDescription: one mis-click causes permanent data loss and a support ticket you cannot resolve
order: 2
layer: Control & Transparency
tags: confirmation, destructive action, data loss, undo
---

## Irreversible Actions Have a Confirmation Step

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
