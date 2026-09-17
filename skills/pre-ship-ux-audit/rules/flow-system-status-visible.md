---
title: Users Don't Need to Guess What the System Is Doing
impact: MAJOR
impactDescription: silence during processing reads as failure and drives abandonment and duplicate submissions
order: 4
layer: Flow Integrity
tags: system status, feedback, latency, perceived performance
---

## Users Don't Need to Guess What the System Is Doing

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
