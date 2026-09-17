---
title: Network Errors and Timeouts Have a User-Facing Fallback
impact: CRITICAL
impactDescription: the most common real-world failure, and usually the least designed
order: 2
layer: Edge Cases
tags: network, timeout, offline, retry, resilience
---

## Network Errors and Timeouts Have a User-Facing Fallback

Every design is drawn on a fast connection against a healthy backend. In
production, requests time out, third-party APIs stall, and phones drop to one
bar. This is the highest-frequency failure in most products and the one most
likely to have no frame at all, which means it ships as an infinite spinner.

**Fails when:**

- There is no timeout: the spinner runs indefinitely
- A failed request leaves the interface in the pre-request state with no message
- Retry means starting the whole flow again
- An offline user gets the same generic error as a server-side failure

**Passes when:**

- Every request has a defined timeout and a designed state for exceeding it
- Failures offer retry in place, preserving what the user already entered
- Offline is distinguished from server error, because the user's next action differs
- For long operations, the result is recoverable after a disconnect

**How to check:** for each network call in the flow, name the frame the user sees
when it takes thirty seconds and when it never returns.
