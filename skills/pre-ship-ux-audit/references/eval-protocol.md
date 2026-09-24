# Eval protocol

This defines how an audit becomes a number. The point of scoring is to make Round 2
comparable to Round 1, so the team can tell whether the feature actually improved or
just moved its problems around.

Read this before running a scored audit, and hand it to every auditor agent so all six
return the same shape.

## The two outputs are independent

| Output | Derived from | Answers |
|---|---|---|
| **Verdict** | Critical count | Can we ship? |
| **Score** | Weighted pass rate | Did it get better since last round? |

Keep them separate and say so in the report. A feature can score 88 and still be 🛑 Do
not ship, because one Critical that loses user data outweighs twelve passes. If the score
is allowed to drive the verdict, people start optimising the number, and the number stops
meaning anything.

## Check results

Every rule an agent owns gets exactly one result:

| Result | Meaning | Counts as |
|---|---|---|
| `pass` | Verified against the design, spec, or build | Pass |
| `fail` | Verified, and it is wrong | Fail |
| `not_verifiable` | Cannot be checked because the artefact does not exist | **Fail** |
| `not_applicable` | Genuinely cannot occur in this feature | Excluded |
| `out_of_stage` | The artefact is too early for absence to mean anything | Excluded |

`not_verifiable` counts as a failure on purpose. "There is no error state frame, so I
could not check the error copy" is not a neutral result: an undesigned state ships as
whatever the engineer improvises. Reporting it as a gap rather than a blank is the whole
value of the audit. It is tracked separately so the report can distinguish "designed
wrong" from "not designed at all".

## The stage ladder

Before scoring anything, establish what the audit actually ran against:

| Stage | Artefact |
|---|---|
| `spec` | A written spec, tickets or a PRD |
| `static` | Figma frames or screenshots, not clickable |
| `prototype` | Clickable, staged data, no backend |
| `build` | A real build on staging or production |

Every rule declares `earliestStage` in its frontmatter. It is **the earliest stage at
which absence is trustworthy**: the point from which "the artefact does not do X" can be
read as "X was not designed" rather than "X was not built yet".

A check below that stage is `out_of_stage`. It is excluded from the score, not failed.
This matters for two reasons. Scoring it measures the artefact instead of the design, and
it makes a prototype round incomparable with a later build round, which is the one thing a
scored audit exists to prevent.

`stageNote` on each rule says what an earlier artefact can still answer. Read it: several
rules have a half you can judge early and a half you cannot. `edge-network-failure` is the
clearest case. There is no network to fail in a prototype, but whether the interface can
*represent* a failure at all is a real design question you can answer now.

The stage is a required argument to the scoring script. There is no default, on purpose.

**Checks with no rule file must carry their own stage.** The `ux-*` and `a11y-*` checks live
in their agent's table rather than in `rules/`, so they declare `earliestStage` inline
alongside `impact`, and the agent copies it into the check object. A check with neither a
rule file nor an inline stage is never deferred, which silently reintroduces the problem
stage gating exists to solve.

## Fidelity: is this a defect, or is it the artefact?

Stage gating works at the level of a whole check. It does not catch the case where a check
is answerable at this stage but one specific finding rests on how the demo was staged.
That case is common enough to have its own field.

Every finding carries `evidence_class`:

| Value | Meaning |
|---|---|
| `design` | The finding is about a decision someone made. It scores. |
| `fidelity-artifact` | The finding is real but rests on staging: seeded demo data, an unwired control, a hardcoded value, a stub. It is reported separately and does **not** score. |
| `unknown` | You could not tell. It scores, and it says so. |

The test is a counterfactual: **would this still be true if the same design were built
properly?** A sidebar link that goes nowhere because no page exists yet is
`fidelity-artifact`. A sidebar link that goes to the wrong page by design is `design`.

Two traps to avoid in both directions.

Do not use `fidelity-artifact` to make an awkward finding go away. If the artefact
contradicts itself, staging cannot explain it: when one long-running operation survives
being closed and an identical one next to it does not, that is a decision, not a stub.

Do not assume staged data is harmless either. A prototype seeded with a populated account
hides every empty state from the only audience that would see them. That is worth writing
down, in the fidelity section, so the next round re-tests it.

**`not_applicable` requires a written reason.** Without that rule, an agent can N/A its
way to 100. The reason has to name why the situation cannot arise, for example "this
screen has no network call". An N/A with no reason is scored as `not_verifiable`.

## Weights

Weight comes from the rule's declared `impact`, not from the auditor's mood:

| Impact | Weight |
|---|---|
| CRITICAL | 3 |
| MAJOR | 2 |
| NICE_TO_HAVE | 1 |

```
layer score = sum(weight of passed checks) / sum(weight of scored checks) × 100
```

where *scored* excludes `not_applicable`. The overall score is the same formula across
every check from every agent, not an average of layer scores: averaging would let a layer
with two checks outweigh one with six.

## Coverage

```
coverage = 1 - (not_verifiable checks / scored checks)
```

Report it next to the score, always. A score of 90 at 40% coverage means most of the
feature could not be examined, and reading it as "90% good" is exactly the wrong
conclusion. Low coverage on a pre-ship audit is itself the headline finding: the feature
is not far enough along to audit.

## Finding schema

Each agent returns one JSON object. The orchestrator collects them and runs
`scripts/score_audit.py`, which does the arithmetic so six agents cannot disagree about
what 100 means.

```json
{
  "agent": "flow-integrity",
  "layer": "Flow Integrity",
  "feature": "AI Interview Coach: Session Setup",
  "round": 2,
  "checks": [
    { "rule": "flow-visible-entry-point", "result": "pass" },
    { "rule": "flow-all-states-designed", "result": "fail" },
    { "rule": "flow-system-status-visible", "result": "not_verifiable" },
    { "rule": "flow-prerequisites-met", "result": "not_applicable",
      "reason": "single-step flow, no downstream step to gate" }
  ],
  "findings": [
    {
      "title": "No designed state for a failed session start",
      "rule": "flow-all-states-designed",
      "severity": "critical",
      "screens": ["Step 2, Session Launch"],
      "problem": "A user whose session fails to start sees the launch screen unchanged.",
      "impact": "The most likely failure in a real-time feature reads as a dead product.",
      "recommendation": "Add a failure state with the cause and a retry that keeps the job selection.",
      "confidence": "verified",
      "evidence_class": "design",
      "step_order": 11, "step_name": "Optimize run",
      "where": "The drawer footer, during the run",
      "page": "Job Dashboard.dc.html",
      "expected": "A failed run says so and offers a retry",
      "actual": "Both runs always reach 100%. No error copy anywhere",
      "fix": "Add a failure state with a cause and a retry that keeps the selection",
      "decision_needed": "",
      "recurring_from_round": 1
    }
  ]
}
```

Field notes:

- `severity` is the auditor's judgement for **this** case, and may differ from the rule's
  default impact. A missing empty state on a screen nobody reaches is not Critical. The
  rule's impact sets the scoring weight; `severity` sets the report grouping and the verdict.
- `evidence_class` is `design`, `fidelity-artifact` or `unknown`, and it is required. See
  the fidelity section above. Omitting it is treated as `unknown`, which scores, so a
  fidelity artefact you forget to mark will inflate the count against the team.
- `confidence` is `verified` or `inferred`. Anything inferred from a spec without seeing
  the design must say so, because the team will otherwise go looking for a frame that is
  fine.
- `recurring_from_round` is set when the same finding was raised in an earlier round and
  not fixed. A finding that has been ignored once is a stronger finding than a fresh one,
  and the report should say which round first raised it.
- `screens` lists every affected frame. One finding with five screens, never five findings.
- `where`, `step_order` and `step_name` place the defect in the journey. The report's lead
  table is ordered by `step_order`, so a reader who does not know the feature can follow it
  top to bottom and watch the build break.
  - `step_order` is the position in the completed flow's step table. `step_name` is a short
    human label for that step, "Optimize run", not "S9".
  - `where` is how to get to it, 90 chars, in one of four forms, in this order of preference:
    a quoted on-screen string, a named control, an action to take, or **the empty place to
    look at** when the defect is that something is missing. That last form is the one the
    other three cannot do: "the drawer footer, during the run" proves an absence, where a
    quotation can only prove a presence, and most of what this audit finds is absence.
- `page` is the file or route the defect is on, exactly as the artefact names it, for example
  `Optimize Resume.dc.html`. The script turns it into a link with `--base-url`, so the report
  links to the screen instead of describing it. **Name the page, never paste a URL**: a URL
  in a finding rots the moment the project moves, and the whole report has to be re-edited.
- `expected` and `actual` are the report's lead table: **what should be true** next to **what
  is**. Both are required on every Critical and Major.
  - `expected` is the specific thing this build should do, 120 chars, written so the reader
    agrees with it before reading the right column: "A warning about a weak resume appears
    only when the resume is weak".
  - `actual` is what it does instead, 160 chars: "Fires on a 9.6 Top match. The headline is a
    hardcoded string".
  - **Do not restate the rule.** The script falls back to the rule's own title when `expected`
    is missing, and that fallback reads as a principle rather than a defect: "Users Can Pause,
    Stop, or Undo" tells the reader nothing about this build. The script names every finding
    that forces the fallback.
  - The pair should be readable with nothing else on screen. If the row needs the rest of the
    report to make sense, it is written wrong.
- `fix` is the change, in the imperative, 70 chars: "Wire Saved to the job title, not the list
  index". It is what the fix-scope table shows, because a scope table answers "what are we
  changing", not "what is broken". The full instruction stays in `recommendation`.
- `decision_needed` is set only when the fix **cannot be specified** until someone answers a
  product question, for example whether a quota ships at all. It marks the row blocked. Do not
  use it for a fix you simply think is expensive: that is engineering's call, not a blocker.
- **Length budgets, enforced.** `title` 100 chars, `problem` 300, `impact` 200,
  `recommendation` 250. `score_audit.py` lists every finding that busts one. Put the proof in
  `evidence`, which has no budget: line numbers, what you clicked, what happened. The four
  budgeted fields are the summary a PM reads, and they stay short because the evidence sits
  somewhere else. If the reader would act the same after reading half a field, cut that half.
- `severity` may also be `out_of_scope` for something real that belongs to another owner.
  It is listed under "Passed to another owner", never scored and never counted. Auditors
  invent this line anyway; without a home for it, handing work to the right person costs
  the team a Nice to have.
- `cluster` is a short slug shared by every finding that names the **same root cause**.
  The headline counts distinct clusters, not raw findings.

## Clustering: one defect is one thing to fix

Seven auditors inspecting the same build will find the same defect from seven angles. Left
alone, one root cause becomes seven Criticals, the count stops meaning anything, and the
defects that only one auditor saw are buried under the one everybody saw.

So the report counts **distinct root causes**, and shows the raw finding count beside it.

Clustering is the orchestrator's job, not an auditor's: an auditor cannot see the others'
findings, so it cannot know it is duplicating one. After collecting the JSON and before
scoring, read across the dimensions and set a shared `cluster` slug on every finding that
names the same underlying cause. A cluster takes the highest severity among its members,
and the report shows the fullest member with the other auditors listed underneath.

**The script never merges anything by itself.** It flags likely duplicates it noticed,
under "Possible duplicates, not merged", and leaves the decision alone. Folding two real
defects together loses one of them permanently, and that is a judgement, not arithmetic.

Two findings are the same root cause when **one fix closes both**. They are not the same
just because they sit on the same screen, or cite the same rule: "the drawer has no exit"
and "the drawer's copy is wrong" are two fixes and two findings.

## The report changes shape with the stage

Below `build`, the deliverable is not the scorecard. An early artefact cannot answer a
control-by-control question, and its reader is not choosing which button to fix: they are
deciding what still has to be designed. So the script writes two files, and at `spec`,
`static` and `prototype` **the short one is the report**.

| File | Who reads it |
|---|---|
| `report.md` | The short, stage-shaped report. Jobs, then what is not designed yet |
| `scorecard.md` | Every finding with line numbers. For whoever fixes it, at `build` |

The short report needs two arrays that the findings cannot supply:

**`jobs`, from the JTBD agent only.** It owns the job set, so it reports it:

```json
"jobs": [
  { "id": 1, "name": "Start a search from nothing", "priority": "primary",
    "served": false, "blocked_by": "No state for a user who has no resume yet" }
]
```

`blocked_by` is one clause, the thing standing in the way, not a summary of the findings.
A job with `served: true` needs no `blocked_by`.

**`closed`, from any agent**, listing what the previous round raised and this build fixed:

```json
"closed": [ { "title": "Save meant two different things one screen apart", "round": 2 } ]
```

Report closures as carefully as defects. A team that only hears what is still broken
concludes the round did not count, and the next round gets less honest. The script puts
them in the report with that instruction attached.

## Linking to the screen

Pass `--base-url` with `{page}` where the page name goes:

```bash
--base-url 'https://claude.ai/design/p/<id>?file={page}&via=share'
```

Each finding's `page` then becomes a link on its `where` text. The reader clicks through to
the screen rather than hunting for it.

**Only as deep as the product allows.** A link reaches a page; it reaches a *state* only if
the product gives that state an address. Most do not, and when a build has no URL state at
all, say so in the report: the reason a finding cannot be linked precisely is usually itself
a finding, and one a spec often promised. Do not fake depth by linking to the page and
implying it shows the state: the `where` text carries the steps, and that is what gets the
reader there.

## Running the score

```bash
python3 scripts/score_audit.py <dir-of-agent-json> --stage prototype --feature "Name" --round 2
```

`--stage` is required. Add `--previous <dir>` to get the round-over-round delta per layer,
and `--previous-stage` when the earlier round ran against a different artefact: the script
will warn that the deltas are only indicative, because the two rounds answered different
sets of checks. The script prints the
scorecard markdown and the default verdict.

## Verdict rules

The script applies the conservative default:

- 0 Critical findings → ✅ **Ship**
- ≥1 Critical finding → 🛑 **Do not ship**

⚠️ **Ship with fixes** is a human override, not something the script infers, and it
requires a written justification for every Critical being waived (who owns it, what the
fix is, when it lands). Requiring the justification in writing is the point: it keeps the
decision with the PM and on the record, rather than letting an audit quietly soften itself.
