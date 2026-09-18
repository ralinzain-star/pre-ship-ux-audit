---
title: Entry Point Is Visible and Clear
impact: CRITICAL
impactDescription: a feature users cannot find has zero activation regardless of quality
order: 1
layer: Flow Integrity
earliestStage: static
stageNote: A design shows whether an entry affordance was drawn. A spec can describe one that nobody drew.
tags: entry point, discoverability, activation, first run
---

## Entry Point Is Visible and Clear

The user has to know the feature exists and know how to start it. This is the
cheapest thing to get wrong and the most expensive to discover after launch,
because the metric it moves is activation, and a flat activation curve looks
identical whether the feature is bad or simply invisible. Teams usually see the
entry point clearly because they have been staring at the frame for weeks.

**Fails when:**

- The only way in is a menu item three levels deep, or an icon with no label
- The entry point is a banner that a returning user dismissed once and never sees again
- Two entry points lead to the same flow but promise different things
- The spec says "users can access X from the dashboard" and no dashboard frame shows it

**Passes when:**

- A first-time user landing on the parent screen can name what the feature does and where to click
- The label describes the outcome, not the mechanism
- If the feature is promoted, there is still a permanent home for it after the promotion ends

**How to check:** open the parent screen frame and cover everything except what a
new user sees above the fold. If you cannot find the way in, neither can they.
