---
name: pre-ship-ux-audit
description: >
  Run a structured pre-ship UX audit and produce a scored eval with a ship verdict. Covers
  the 4-layer checklist (Flow Integrity, Control & Transparency, Trust & Copy, Edge Cases)
  plus usability heuristics, accessibility, and a live browser-driven usability test against
  real user goals. Completes a rough critical user flow, derives JTBD from it with measurable desired outcomes, dispatches
  nine specialist auditor agents, and scores them with a script so rounds are comparable. Use whenever a feature is about to ship, when
  reviewing a spec or Figma flow before engineering handoff, when someone wants to know if
  users can actually complete a task, or on "UX audit", "JTBD", "jobs to be done", "eval this feature", "pre-ship
  check", "UX review", "design QA", "usability test", "run the full check",
  "audit this flow", "is this ready to ship". Also use when asked what could go wrong with a
  feature, whether a flow is missing states, error handling, confirmations or edge cases,
  when findings need prioritising for engineering, when comparing this round against a
  previous audit, or when logging results to the Notion UX audit log. Prefer this over a
  generic design critique whenever the work is pre-launch and the output needs severities,
  a score, or a go/no-go call. For visual and frontend polish with no ship gate, use
  impeccable.
license: MIT
metadata:
  author: Iris Hsieh
  organization: Jobscan Product Design
  version: "1.0.0"
  argument-hint: <feature name or Figma/spec URL>
---

# Pre-ship UX audit

Source of truth: [Pre-ship UX checklist](https://app.notion.com/p/Pre-ship-UX-checklist-361997983434804fb5d9c45c44e4c2f7).

This is not a design critique. It is the last honest read before real users see the
thing. The output has one job: give the PM a list they can act on this sprint, where
every item says what it costs if ignored.

## Terminology

**Critical user flow**, shortened to **flow** throughout these files, is the artefact the
team hands over: the ordered steps of the journey. **JTBD** is the job to be done, written
as a situation plus the progress the user is after, with measurable desired outcomes.

Note what a spec's critical user flow actually contains: the happy path. Completing it means
adding the arrivals, branches, states and exits nobody drew, so "the completed flow" is
deliberately more than the critical user flow you were given.

## Core principle

**Audit the unhappy paths.** The happy path is always designed, because that is the
frame everyone reviewed. Features break in the states nobody drew: the empty list, the
timed-out request, the half-filled profile, the user who closed the tab. Most of the
value of this audit is in finding states that do not exist yet.

## Verdict

Every audit ends with a call, not just a list:

| Verdict | Condition |
|---|---|
| ✅ **Ship** | No Critical findings. Majors are logged for sprint 1. |
| ⚠️ **Ship with fixes** | Criticals exist but are small and scoped. Name them and the owner. |
| 🛑 **Do not ship** | A Critical blocks task completion, loses data, or misleads the user. |

State the verdict first, then the count: "🛑 Do not ship. 2 Critical, 5 Major, 1 Nice to
have." A PM who reads only the first line should still know what to do. Do not soften a
verdict because the fix looks expensive: that trade is theirs to make, and they can only
make it if you report the problem honestly.

## Layers by priority

Every finding belongs to exactly one layer. If it fits none, it is a visual preference,
not an audit finding: drop it.

| Priority | Layer | Impact | Prefix |
|---|---|---|---|
| 1 | Flow Integrity | CRITICAL | `flow-` |
| 2 | Control & Transparency | CRITICAL | `control-` |
| 3 | Trust & Copy | MAJOR | `trust-` |
| 4 | Edge Cases | MAJOR | `edge-` |

## Quick reference

Each line is a rule file in `rules/`. Read the ones in play, not all seventeen.

### 1. Flow Integrity (CRITICAL)
- `flow-visible-entry-point` 🔴 Users can find the feature and know how to start
- `flow-prerequisites-met` 🔴 Each step's inputs were collected before the user arrives
- `flow-all-states-designed` 🔴 Success, failure, loading, empty all have a designed response
- `flow-system-status-visible` 🟡 Users never have to guess what the system is doing

### 2. Control & Transparency (CRITICAL)
- `control-pause-stop-undo` 🔴 Pause, stop, undo exist and the exit is obvious
- `control-confirm-irreversible` 🔴 Irreversible actions confirm or offer undo
- `control-explain-behaviour` 🟡 The system says why it did what it did
- `control-action-history` 🟡 A record of system actions is reachable

### 3. Trust & Copy (MAJOR)
- `trust-actionable-errors` 🔴 Errors give the cause and the next step
- `trust-plain-language` 🟡 Copy is clear, jargon-free, not anxiety-inducing
- `trust-explain-recommendations` 🟡 Recommendations carry a short reason
- `trust-specific-ctas` 🟢 Buttons name the outcome, not the mechanism

### 4. Edge Cases (MAJOR)
- `edge-missing-data` 🔴 Incomplete profiles degrade visibly, never silently
- `edge-network-failure` 🔴 Timeouts and offline have designed fallbacks
- `edge-duplicate-actions` 🟡 Double submits and conflicts are prevented or flagged
- `edge-interruption-recovery` 🟡 Interruptions do not lose work
- `edge-first-vs-returning` 🟢 New and returning users get different screens

The emoji is the *typical* severity, not a verdict. A missing empty state on a screen
nobody reaches is not Critical. Judge the actual case.

## Severity

- 🔴 **Critical**: must fix before shipping. A user gets stuck, loses data, or is misled.
- 🟡 **Major**: fix in sprint 1 after launch. Hurts activation or retention.
- 🟢 **Nice to have**: polish backlog.

Weigh three things: **frequency** (how many users hit it), **impact** (what it costs when
they do), **persistence** (once, or every session). A cosmetic issue every user hits on
every visit can outrank a rare one.

## Workflow

### Step 1: Gather context

An audit built on assumptions is worse than none, because it sends people to fix things
that are not broken. You need:

- **Feature and user journey**: entry point, the steps, where it ends
- **Intended behaviour**: spec, PRD, or the user's description. This is the source of truth
- **The design**: Figma frame names, screenshots, or the live build
- **Known constraints**: what is out of scope for v1, what has no backend yet
- **Target user**: first-time or returning changes which findings matter

If two of these are missing, ask. One question up front is cheaper than a report the team
discounts. For a Figma file, invoke `figma:figma-design-to-code` before calling
`get_design_context`, and read `get_metadata` first to find the frames.

### Step 2: Quick diagnostic

Before the full pass, run this. If several rows fail, the feature is not ready for a
detailed audit and the team should know that in the first five minutes.

| Question | If no | Rule |
|---|---|---|
| Can a new user find the way in? | Zero activation | `flow-visible-entry-point` |
| Does every screen have an empty and a failure state? | Ships as a blank screen | `flow-all-states-designed` |
| Can the user get out of the flow from every screen? | Users feel trapped | `control-pause-stop-undo` |
| Does anything irreversible confirm first? | Permanent data loss | `control-confirm-irreversible` |
| Does every error say what to do next? | Recoverable moment becomes churn | `trust-actionable-errors` |
| Does the flow work with a two-minute-old account? | Activation breaks | `edge-missing-data` |
| Is there a designed state for a request that never returns? | Infinite spinner | `edge-network-failure` |
| Does anything survive if the tab closes mid-flow? | Work lost, user gone | `edge-interruption-recovery` |

### Step 3: Calibrate depth

| Feature size | How to run it |
|---|---|
| **Small** (one screen, one state change) | Single pass. Findings plus a 2-sentence summary. Skip the report. |
| **Medium** (a multi-step flow) | Full checklist, spec vs design mismatches flagged separately, then the one-page report. |
| **Large** (a feature area, many frames) | Read the spec first and confirm you understood it. Audit frame by frame. Warn the user this is token-heavy before starting. |

### Step 4: Run the checklist

Read the rule files for the layers in play. Mark each item pass, fail, or not verifiable.
An item you cannot check because the state was never designed is itself a finding: say so
rather than skipping it silently.

### Step 5: Output findings

**[Issue title]**
- **Layer**: which of the 4
- **Severity**: 🔴 Critical / 🟡 Major / 🟢 Nice to have
- **Problem**: what the user experiences
- **Impact**: what this costs the business
- **Recommendation**: what to fix and how

Max 2 sentences per field. Reference the specific screen or step number. Where the design
contradicts the spec, group those separately: spec requirements with no design, and
designed states that contradict the spec.

### Step 6: Compile the report

For medium and large features, finish with a one-page report.
See `references/report-template.md` when you reach this step: it has the full structure,
the scorecard format, and an example executive summary.

## Scored audit

| Mode | What it is | When |
|---|---|---|
| **Inline** | You run the checklist yourself, here. Findings and a verdict, no score. | A small feature, a quick read, or a direct question. |
| **Scored** | Specialists inspect in parallel, a script scores them, one merged report. | A real ship gate, anything you will compare against a later round, or when a live URL exists. |

Scored mode is the one that answers "did Round 2 actually improve". Dispatch the
`UX Audit Orchestrator` agent: it takes stock of what exists, runs the two sequential steps,
sends the inspectors in one message so they run concurrently, scores the result, and merges
everything into one report.

| Agent | Dimension | Notes |
|---|---|---|
| `UX Flow Completion` | Flow Completion | **Runs first, alone.** Builds the flow: entry points, branches, four states per step, exits, loop-backs. Marks observed / inferred / invented |
| `UX Audit · JTBD` | JTBD | **Runs second, alone.** Turns the completed flow into a validated JTBD set, and reports gaps and ceremony |
| `UX Audit · Flow Integrity` | Flow Integrity | The four `flow-` rules |
| `UX Audit · Control & Transparency` | Control & Transparency | The four `control-` rules |
| `UX Audit · Trust & Copy` | Trust & Copy | The four `trust-` rules |
| `UX Audit · Edge Cases` | Edge Cases | The five `edge-` rules |
| `UX Audit · Usability Heuristics` | Usability Heuristics | Nielsen and Krug, restricted to what the four layers do not cover |
| `UX Audit · Usability Test` | Usability Test | **Live**: opens the browser and attempts real user goals. Needs a URL and a journey draft |
| `UX Audit · Accessibility` | Accessibility | The WCAG 2.2 AA subset that should block a release |

```
critical user flow  →  complete it  →  mark observed / inferred / invented
          ↓
    derive JTBD  →  validity tests  →  map back: gaps + ceremony
          ↓
 live test attempts each JTBD in the browser
          ↓
task results join the inspectors' findings
          ↓
    script scores, orchestrator merges
          ↓
next round re-tests the SAME frozen JTBD set
```

The first two steps run alone and in order; everything after fans out. JTBD are never
derived from invented steps: an invented step is a guess at a solution, so a JTBD climbed
out of it is a guess about a guess that looks authoritative by the time it reaches a test.

The JTBD set is frozen after Round 1 on purpose. It is the fixed measuring stick that makes
Round 2's task success rate mean something. Rewrite it because the design changed and you
are measuring the new design against itself, which is what scored mode exists to avoid.

Two supporting pieces:

- **`assets/flow-template.md`**: the flow the whole pipeline starts from. Entry points,
  mermaid diagram, preconditions and four states per step, exits, loop-backs, open
  questions, assumptions register. Every element marked observed, inferred or invented, so
  nothing invented gets built by accident.
- **`assets/user-journey.md`**: the journey draft the live test runs against. You fill in
  the flow as designed, derive the goals from it, then write one task per goal.
- **`references/jtbd.md`**: how to climb from designed steps to real user goals
  without ending up restating the design. Read it before deriving: a goal that is a
  restatement produces a test that cannot fail, and the run is wasted. It also covers the
  gap-and-ceremony mapping, which is usually the highest-value output of a round.
- **`references/browser-audit.md`**: how to audit the live build. The tool table, the
  JavaScript hooks that force loading, failure, offline, timeout and session-expiry states
  into existence, a contrast-measuring snippet, per-dimension recipes, and the safety rules.
  Every inspector reads it when a URL exists.
- **`references/eval-protocol.md`**: the scoring contract. Read this before running a scored
  audit. It defines the JSON schema, the weights, why `not_verifiable` counts as a failure,
  and the rule that stops agents claiming `not_applicable` to protect their score.

Scoring is done by a script, not by the model:

```bash
python3 scripts/score_audit.py <results-dir> --feature "Name" --round 2 --previous <round-1-dir>
```

Independent agents will not agree about what 100 means, and models are unreliable at consistent
weighted arithmetic. Doing it once, the same way every round, is what makes rounds
comparable. The script also prints the conservative verdict default.

**Verdict and score are independent.** The verdict comes from the Critical count, the score
from the weighted pass rate. A feature can score 88 and still be do-not-ship, because one
Critical that loses user data outweighs twelve passes. Let the score drive the verdict and
people start optimising the number.

**A URL changes everything.** Without one, the audit is inspection: the agents predict what
the build does and mark a large share of the checklist `not_verifiable`, which caps coverage
structurally. With one, they force the states into existence and verify. Ask for a URL
before running a scored audit, and say in the report which kind of round it was.

**Report coverage next to the score, always.** 90 at 40% coverage does not mean 90% good, it
means most of the feature could not be examined. On a pre-ship audit that is the headline.

## What is not a finding

The fastest way to get an audit ignored is padding. Drop these:

| Looks like a finding | Why it is not | Instead |
|---|---|---|
| "The spacing feels off" | Visual preference with no user cost | Send to a design review, not an audit |
| "I would have used a different pattern" | Preference, not defect | Drop, unless the pattern causes a real failure |
| A rule violation with no reachable path | Costs nothing if users never get there | Drop, or note as low-priority |
| A constraint the team already accepted | Already a decision, not a discovery | Drop, or confirm the decision still holds |
| The same issue restated per screen | Inflates the count, hides real Criticals | One finding, list the affected screens |

## When layers conflict

Rules pull against each other. When they do:

- **Control vs Flow**: an exit on every screen wins over a tighter funnel. Trapped users
  leave the product, not just the flow.
- **Error prevention vs Efficiency**: prefer undo over a confirmation dialog. People
  dismiss dialogs reflexively, which breaks the one that mattered.
- **Transparency vs Minimalism**: explain the system's own actions, hide its internals.
- **First-time vs Returning**: split the screen rather than averaging them. An averaged
  screen under-serves both.

## Logging the audit

Past audits live in a Notion database. Read `references/notion-log.md` when the user wants
this audit recorded, or asks what was found in a previous round: a finding that is still
open from Round 1 is a stronger finding than a fresh one, and should be labelled as such.

## Full compiled document

For the complete guide with all 17 rules expanded in one pass: `AGENTS.md`.
Regenerate it after editing any rule with `python3 scripts/build_agents.py`.

## Writing style

Write for a teammate with no design background. Never sugarcoat: if something is broken,
say it clearly. Frame every issue in user **and** business terms, because a PM cannot
prioritise "this feels off". Flag any finding you inferred rather than verified. Do not
use em-dashes in anything produced for Iris: use a colon, a comma, or restructure.
