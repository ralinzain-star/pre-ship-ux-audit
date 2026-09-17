---
title: System Behaviour Is Explained
impact: MAJOR
impactDescription: unexplained system behaviour reads as malfunction and generates support load
order: 3
layer: Control & Transparency
tags: transparency, mental model, automation, support cost
---

## System Behaviour Is Explained

Users build a mental model of what the product does whether or not you give them
one, and the model they invent unaided is usually wrong and usually
uncharitable. When the system takes an action, changes something, or declines to
do something, saying why costs one line of copy and saves the support
conversation. This is most acute where the system acts automatically: automation
the user cannot predict feels like a bug.

**Fails when:**

- An item disappears from a list with no explanation of what moved it
- A field is disabled with no indication of what would enable it
- The system silently changes something the user entered (trimming, reformatting, deduping)
- An action is rejected with no reason, so the user retries the same thing

**Passes when:**

- Every automatic change is attributed and briefly explained
- Disabled states say what unlocks them
- The user can predict what the system will do next before doing it

**How to check:** find every place the system acts without the user asking. Each
one needs an explanation the user can read at that moment.
