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

`not_verifiable` counts as a failure on purpose. "There is no error state frame, so I
could not check the error copy" is not a neutral result: an undesigned state ships as
whatever the engineer improvises. Reporting it as a gap rather than a blank is the whole
value of the audit. It is tracked separately so the report can distinguish "designed
wrong" from "not designed at all".

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
      "recurring_from_round": 1
    }
  ]
}
```

Field notes:

- `severity` is the auditor's judgement for **this** case, and may differ from the rule's
  default impact. A missing empty state on a screen nobody reaches is not Critical. The
  rule's impact sets the scoring weight; `severity` sets the report grouping and the verdict.
- `confidence` is `verified` or `inferred`. Anything inferred from a spec without seeing
  the design must say so, because the team will otherwise go looking for a frame that is
  fine.
- `recurring_from_round` is set when the same finding was raised in an earlier round and
  not fixed. A finding that has been ignored once is a stronger finding than a fresh one,
  and the report should say which round first raised it.
- `screens` lists every affected frame. One finding with five screens, never five findings.

## Running the score

```bash
python3 scripts/score_audit.py <dir-of-agent-json> --feature "Name" --round 2
```

Add `--previous <dir>` to get the round-over-round delta per layer. The script prints the
scorecard markdown and the default verdict.

## Verdict rules

The script applies the conservative default:

- 0 Critical findings → ✅ **Ship**
- ≥1 Critical finding → 🛑 **Do not ship**

⚠️ **Ship with fixes** is a human override, not something the script infers, and it
requires a written justification for every Critical being waived (who owns it, what the
fix is, when it lands). Requiring the justification in writing is the point: it keeps the
decision with the PM and on the record, rather than letting an audit quietly soften itself.
