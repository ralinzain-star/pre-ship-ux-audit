---
title: Recommendations and System Decisions Include a Brief Reason
impact: MAJOR
impactDescription: unexplained recommendations are ignored or distrusted, wasting the feature entirely
order: 3
layer: Trust & Copy
tags: AI, recommendations, explainability, adoption
---

## Recommendations and System Decisions Include a Brief Reason

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
