---
title: Success, Failure, Loading, and Empty States All Have a Designed Response
impact: CRITICAL
impactDescription: an undesigned state ships as whatever the engineer improvises, usually nothing
order: 3
layer: Flow Integrity
tags: states, empty state, loading, error state, handoff
---

## Success, Failure, Loading, and Empty States All Have a Designed Response

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
