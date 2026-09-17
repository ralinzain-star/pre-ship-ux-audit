# Pre-ship UX audit

A structured audit to run on a feature before it ships. Four layers, severities tied to
business cost, and a go/no-go verdict rather than a list of opinions.

Based on Iris Hsieh's [Pre-ship UX checklist](https://app.notion.com/p/Pre-ship-UX-checklist-361997983434804fb5d9c45c44e4c2f7)
(Jobscan product team). Structured after the `vercel-labs/agent-skills` rule-file pattern,
with the verdict, quick diagnostic, and conditional reference pointers borrowed from
`wondelai/skills` ux-heuristics.

## Structure

- `SKILL.md` : the index. Verdict scale, layer priorities, quick reference of all 17 rule
  IDs, the six-step workflow. This is what the agent reads first.
- `rules/` : one file per checklist item
  - `_sections.md` : the four layers, their impact and description
  - `_template.md` : template for adding a rule
  - `<layer>-<slug>.md` : the rules themselves
- `references/`
  - `report-template.md` : the one-page stakeholder report format and scorecard
  - `notion-log.md` : how to read and write the Notion UX audit log database
- `assets/flow-template.md` : the completed flow, with every element tiered
- `assets/user-journey.md` : journey as designed, jobs, one task per goal
- `references/jtbd.md` : climbing from designed steps to real user goals
- `references/browser-audit.md` : auditing the live build; condition-simulation hooks and a verified contrast measurer
- `references/eval-protocol.md` : the scoring contract, JSON schema, and anti-gaming rules
- `AGENTS.md` : compiled output, every rule in one document (generated)
- `scripts/build_agents.py` : regenerates `AGENTS.md` from `rules/`
- `scripts/score_audit.py` : turns agent JSON into a scorecard, a verdict, and a round delta
- `scripts/check_consistency.py` : catches drift between the skill and its agents
- `metadata.json` : version, abstract, source links

## The 17 rules

### Flow Integrity (Critical)
- `flow-visible-entry-point` : users can find the feature and know how to start
- `flow-prerequisites-met` : each step's inputs were collected before the user arrives
- `flow-all-states-designed` : success, failure, loading, empty all have a response
- `flow-system-status-visible` : users never have to guess what the system is doing

### Control & Transparency (Critical)
- `control-pause-stop-undo` : pause, stop, undo exist and the exit is obvious
- `control-confirm-irreversible` : irreversible actions confirm or offer undo
- `control-explain-behaviour` : the system says why it did what it did
- `control-action-history` : a record of system actions is reachable

### Trust & Copy (Major)
- `trust-actionable-errors` : errors give the cause and the next step
- `trust-plain-language` : copy is clear, jargon-free, not anxiety-inducing
- `trust-explain-recommendations` : recommendations carry a short reason
- `trust-specific-ctas` : buttons name the outcome, not the mechanism

### Edge Cases (Major)
- `edge-missing-data` : incomplete profiles degrade visibly, never silently
- `edge-network-failure` : timeouts and offline have designed fallbacks
- `edge-duplicate-actions` : double submits and conflicts are prevented or flagged
- `edge-interruption-recovery` : interruptions do not lose work
- `edge-first-vs-returning` : new and returning users get different screens

## Core principles

1. **Audit the unhappy paths.** The happy path is always designed. Features break in the
   states nobody drew.
2. **Every finding names a business cost.** A PM cannot prioritise "this feels off".
3. **End with a verdict.** Ship, ship with fixes, or do not ship. A list without a call
   pushes the decision back onto the person who asked for the audit.
4. **Drop findings that cost nothing.** A padded report gets skimmed, and the real
   Criticals get lost with it.

## Adding a rule

1. Copy `rules/_template.md` to `rules/<layer>-<slug>.md`
2. Fill in the frontmatter, including `order` (its position in the user journey)
3. Add the line to the Quick reference in `SKILL.md` and to this README
4. Run `python3 scripts/build_agents.py`

## Scored audit: ten agents

Nine specialists plus the orchestrator that dispatches them.

Live in `~/.claude/agents/`. Dispatch `UX Audit Orchestrator` and it runs the rest.

| Agent | Dimension |
|---|---|
| `ux-flow-completion` | Rough flow to complete flow, tiered observed/inferred/invented. Runs first, alone |
| `ux-audit-jtbd` | Completed flow to validated JTBD; gaps and ceremony. Runs second, alone |
| `ux-audit-flow-integrity` | The four `flow-` rules |
| `ux-audit-control-transparency` | The four `control-` rules |
| `ux-audit-trust-copy` | The four `trust-` rules |
| `ux-audit-edge-cases` | The five `edge-` rules |
| `ux-audit-usability-heuristics` | Nielsen and Krug, restricted to what the four layers miss |
| `ux-audit-usability-test` | Live browser test against real user goals |
| `ux-audit-accessibility` | The WCAG 2.2 AA subset that should block a release |
| `ux-audit-orchestrator` | Dispatches, scores, deduplicates, writes the report |

Each auditor returns JSON. The orchestrator collects it and runs:

```bash
python3 scripts/score_audit.py <results-dir> --feature "Name" --round 2 --previous <round-1-dir>
```

### Why the arithmetic is in a script

Independent agents will not agree about what 100 means, and models are unreliable at consistent
weighted arithmetic. Doing it once, the same way every round, is the only thing that makes
Round 2 comparable to Round 1.

The script also enforces the two rules that keep a scorecard honest:

1. **`not_verifiable` counts as a failure.** An undesigned state ships as whatever the
   engineer improvises. Scoring it as neutral rewards not designing things.
2. **`not_applicable` needs a written reason**, or it is downgraded to `not_verifiable`.
   Without that, an agent can N/A its way to 100.

### Verdict and score are independent

The verdict comes from the Critical count. The score comes from the weighted pass rate. A
feature can score 88 and still be do-not-ship. Keeping them separate is what stops people
optimising the number instead of the product.

Coverage is reported next to the score, always. 90 at 40% coverage does not mean 90% good,
it means most of the feature could not be examined.

## The loop

```
rough flow  →  complete it  →  derive jobs  →  validity tests  →  map back: gaps + ceremony
                                              ↓
                              live test attempts each goal in the browser
                                              ↓
                           task results join the six inspectors' findings
                                              ↓
                                  script scores, orchestrator merges
                                              ↓
                        next round re-tests the SAME frozen JTBD set
```

Two rules keep this from collapsing:

1. **A derived goal must pass the other-path and competitor tests.** Goals read off a
   designed flow default to restating it, and a test built from a restatement cannot fail.
2. **Freeze the JTBD set after Round 1.** It is the fixed measuring stick. Rewrite it
   because the design changed and you are measuring the new design against itself.

The mapping step has its own payoff, separate from the test: a goal with no step serving it
is a **gap** (users leave without complaining, because nothing broke), and a step serving no
goal is **ceremony** (friction the user pays for and the team gets nothing from). Neither
shows up in a checklist audit.

## Keeping it consistent

This system grew in four increments, and the failure mode of that is silent drift: a count
that still says seven, a path that moved, a check id an agent invented that the scorer
cannot weight. None of it breaks loudly, it just produces a wrong report one day.

```bash
python3 scripts/check_consistency.py
```

Run it after editing any agent or rule. It checks that every rule has an `impact` and an
`order`, that every rule is owned by exactly one agent, that no two agents claim the same
check id (which would double-count findings), that every referenced path exists, that
agent counts in the prose match reality, that every auditor still carries an Output contract
with a real agent id, and that no em-dash has crept in. Exit code is the error count.
