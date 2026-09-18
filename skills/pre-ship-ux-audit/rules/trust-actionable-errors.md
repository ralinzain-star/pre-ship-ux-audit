---
title: Error Messages Tell the User What Went Wrong and What to Do Next
impact: CRITICAL
impactDescription: a dead-end error converts a recoverable moment into a churned user
order: 1
layer: Trust & Copy
earliestStage: static
stageNote: Error copy belongs to the design deliverable. In a prototype, missing error copy is ambiguous: it may be unbuilt rather than undesigned, so check the design before scoring it.
tags: error message, recovery, copy, support cost
---

## Error Messages Tell the User What Went Wrong and What to Do Next

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
