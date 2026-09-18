---
title: Users Can Pause, Stop, or Undo, and the Exit Point Is Obvious
impact: CRITICAL
impactDescription: a flow with no exit traps users, who then leave the product rather than the flow
order: 1
layer: Control & Transparency
earliestStage: static
stageNote: Whether an exit control was drawn is visible in the design. Whether it actually preserves work needs a build.
tags: exit, undo, cancel, escape hatch, agency
---

## Users Can Pause, Stop, or Undo, and the Exit Point Is Obvious

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
