---
title: Incomplete Profile or Missing Data Is Handled Gracefully, Not Silently Ignored
impact: CRITICAL
impactDescription: the users most likely to hit this are new users, so the failure lands on activation
order: 1
layer: Edge Cases
earliestStage: prototype
stageNote: Judging whether degradation is visible or silent needs something you can feed different data to. A design can still be checked for a drawn degraded state.
tags: missing data, empty profile, new user, activation
---

## Incomplete Profile or Missing Data Is Handled Gracefully, Not Silently Ignored

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
