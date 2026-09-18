---
title: Every Step's Prerequisite Is Met Before the User Enters It
impact: CRITICAL
impactDescription: users hit a wall mid-flow after investing effort, the worst place to drop out
order: 2
layer: Flow Integrity
earliestStage: spec
stageNote: The order of steps and what each one needs is a property of the flow itself, so a written spec can answer this in full.
tags: sequencing, gating, drop-off, dead end
---

## Every Step's Prerequisite Is Met Before the User Enters It

A step that needs data the user has not provided yet is a dead end dressed as
progress. The cost is worse than blocking them at the start, because they have
already spent effort and now feel it was wasted. Check the order of the flow
against what each step actually consumes.

**Fails when:**

- Step 3 needs a resume on file, and nothing in steps 1 and 2 asked for one
- A paid-tier action sits inside a flow a free user can enter, with the paywall at the end
- The flow assumes a connected integration that the user may never have authorised
- A "Continue" button is enabled before the field it depends on is filled

**Passes when:**

- Each step can be completed with only what the user has supplied so far
- Where a prerequisite is genuinely required, it is collected earlier or the entry
  point states it up front
- Gating happens at the entry point, not at the finish line

**How to check:** walk the journey step by step and list what each screen reads
from. Any input that has no earlier source is a finding.
