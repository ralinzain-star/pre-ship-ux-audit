# What changed, and what each change taught

A log of the architecture changes made after the first two rounds of real use, on the
Jobscan Autopilot Job Dashboard. Each entry says what moved, why, and what it taught,
including where the obvious fix turned out not to be the effective one.

The trigger for all of it was one observation from Iris: the thing under audit was a
prototype, and the audit was scoring it as though it were a running build.

---

## 1. The artefact stage

**Before.** The skill had two dials: feature size, and whether a URL existed. A URL was
treated as "now we can verify everything".

**After.** Four stages: `spec`, `static`, `prototype`, `build`. Every rule declares
`earliestStage`, defined as **the earliest point at which absence is trustworthy**: the stage
from which "the build does not do X" can be read as "X was not designed" rather than "X was
not built yet". A check below its rule's stage is `out_of_stage`, excluded from the score
rather than failed. The stage is a required argument with no default, because a clickable
prototype has a URL and is not a build.

**What it taught.** *The obvious fix was not the effective one.* Gating at the check level
moved the score from 10 to 11. Two checks deferred, out of forty. The contamination was
almost entirely one level down, in individual findings, not in whole checks. Worth building,
and nowhere near sufficient on its own.

Second lesson: the ladder is cumulative and that surprises people. A prototype answers every
`spec` and `static` rule in full. It defers only `build` rules. Stage gating removes very
little, which is the point: it is a scalpel, not a discount.

---

## 2. Evidence class, the fidelity register

**Before.** A finding was a finding. Seeded demo data, an unwired stub and a real design
decision all scored the same.

**After.** Every finding carries `evidence_class`: `design`, `fidelity-artifact` or
`unknown`. Only `design` and `unknown` score. The test is a counterfactual: **would this still
be true if the same design were built properly?**

**What it taught.** This is where the real correction was. In the re-run, auditors filtered
staging at source and produced 3 fidelity artefacts where a retrofit pass over the previous
round's data had found 17. Judging at the point of observation beats judging afterwards,
because the auditor still has the evidence in front of it.

Two guard rails had to be written in, because both failure modes appeared in practice:

- **Laundering.** An auditor can make an awkward finding disappear by calling it staging. The
  counter-rule: when the artefact contradicts itself, staging cannot explain it. One
  long-running operation killed on close while an identical one beside it backgrounds
  correctly is a decision, and somebody wrote both.
- **Waving staging through.** A prototype seeded with a populated account hides every empty
  state from the only audience that would see them. Real, and worth writing down, in the
  fidelity list, so the next round re-tests it instead of forgetting.

`unknown` earns its place. Missing error copy in a prototype is genuinely undecidable:
unbuilt and undesigned look identical. One auditor called it `design` and another `unknown`,
both with reasons, and that disagreement is information rather than noise.

---

## 3. Counting root causes, not findings

**Before.** Nine auditors inspecting one build reported the same defect from nine angles, and
the headline counted all nine. The "Skip for now" defect was four Criticals. "No failure
state" was three. The count stopped meaning anything, and the defects only one auditor saw
were buried under the one everybody saw.

**After.** Findings naming the same root cause share a `cluster` slug. The report counts
distinct clusters and shows the raw count beside it. 19 Criticals became 10; in the re-run,
15 findings became 9. The test for sameness is **one fix closes both**: not the same screen,
not the same rule.

**What it taught.** *Where to draw the line between script and judgement.* The script does not
merge anything. It flags likely duplicates and leaves the decision alone, because folding two
real defects together loses one permanently and that is a judgement, not arithmetic. The
detector had to change metric to be useful: Jaccard similarity at 0.34 caught one of three
known clusters, because auditors write titles of very different lengths for the same defect
and the union inflates. Overlap coefficient at 0.5 caught all three.

Also: *building one thing surfaces another.* Writing the detector exposed that auditors had
been inventing an "out of scope" line, had nowhere to file it, and were filing it as
`nice_to_have`. Eight of them were being scored. That became its own change.

---

## 4. `out_of_scope`

**Before.** No field for "this is real and it belongs to somebody else".

**After.** A severity value that is listed under "Passed to another owner", never counted.
Nice-to-have findings dropped from 6 to 2 once the misfiled ones moved.

**What it taught.** When every agent independently invents the same workaround, the contract
is missing a field. Handing work to the right person should not cost the team a finding.

---

## 5. Length budgets, enforced by the script

**Before.** The skill said "max 2 sentences per field". Measured on real output: `problem` had
a median of 722 characters and a maximum of 1283. The rule was being exceeded roughly
fourfold, in every run, by every agent.

**After.** Budgets per field, checked by `score_audit.py`, which names every finding that
busts one. On the round that prompted this, 213 fields were over.

**What it taught.** *A rule written in prose does not bind.* This skill already knew that
about arithmetic, which is why scoring lives in a script. Style is the same: agents comply
with what is measured.

The design that makes short fields possible is `evidence`, which has **no** budget. Nothing
is being cut, it is being moved. The budgeted fields are the summary someone reads to decide
what to fix this sprint, and they stay short because the proof sits somewhere else.

---

## 6. The report is a table: what should be true, and what is

**Before.** A severity-ordered list of findings in prose.

**After.** The report opens with a table: **where to look**, **should be**, **is**. Left is the
expectation, phrased so the reader agrees with it before reading the right column, with the
two kept grammatically parallel so the difference lands without being explained.

**What it taught.** Three things, in order of how much they mattered.

*The anchor is the biggest single win, and it came from copying the humans.* Every comment the
Jobscan team left on the build opens by quoting the words on screen. That is how a reader
locates the thing in one second. The audit had no equivalent, so every row made the reader
guess which screen was meant.

*Text is the best anchor, not the only one.* Most of what this audit finds is absence, and
absence has nothing to quote. So `where` takes four forms: a quoted string, a named control,
an action to take, or **the empty place to look at**. The last one is the strongest, because
"the drawer footer, during the run" proves something is missing, where a quotation can only
prove something is present.

*A visible fallback beats a silent default.* When `expected` is missing, the report falls back
to the rule's own title, which reads as a principle rather than a defect: "Users Can Pause,
Stop, or Undo" tells a reader nothing about this build. That fallback is deliberately ugly,
and the script names every finding that forces it. Three rows in the last run still read that
way, and they are visibly the worst rows in the table, which is exactly the intended pressure.

---

## 7. Journey order

**Before.** The findings table was ordered by severity.

**After.** The lead table is ordered by `step_order`, the position in the completed flow.
Someone who does not know the feature reads it top to bottom and watches the build break:
onboarding, feed, filters, card, apply gate, optimize run, resume, apply route, tracker.

**What it taught.** Two orderings answer two questions and cannot be the same table. Journey
order answers "what is this and where does it break". Severity order answers "what do I fix
first". So the fix-scope table stayed sorted by severity and by how many findings each fix
closes, and the two tables sit next to each other with different jobs.

---

## 8. The fix-scope table

**After.** One row per defect, not per finding: what to change, what it touches, how many
findings it closes, and whether a product decision is needed first.

**What it taught.** It cost almost nothing to build, because clustering had already produced
the rows. *A good structure pays twice.* The "closes 4 findings" column, which is what makes
a scope table useful for planning, is a by-product of merging duplicates.

`decision_needed` exists to separate blocked from small. Three rows in the last run were
blocked on a product question, including whether the credit quota ships at all, and without
the column they read as ordinary small fixes.

---

## 9. Screenshots: attempted, then dropped

**What was tried.** The extension takes screenshots but `save_to_disk` writes no file, verified
twice. A local server that accepts the page's own screenshots back over `POST /_shot/` works,
and html2canvas rendered the job feed exactly.

**Where it stopped.** It returns a blank canvas of the correct size for this build's overlays.
Ruled out, in order: entrance animation, ancestor opacity and transform, shadow DOM, and the
clone dropping the node. An `onclone` hook found the element present, visible, 489px tall,
with its text and three children. It paints nothing anyway. Most of the defects are in
overlays, so a mechanism that works only on the feed was not worth shipping into reports.

**What it taught.** *Check the capability before designing around it, and stop when the answer
is no.* The server and the recipe stay in `references/browser-audit.md` along with the
limitation and the instruction to check the first capture before taking fifty. A real
screenshot needs a visible window and an active tab, and agents drive background tabs.

---

## 10. The boundary, written down

Not a mechanism, but the change that explains the rest.

The audit does not design. **A reviewer's comment proposes what the product should be. This
audit's recommendations repair what has already been decided.** The difference is not how
specific each one is: "wire the Saved list to the job title rather than the list index" is as
concrete as anything in a comment thread. The difference is authority.

So a low score does not mean "this design is wrong". It means "these decisions do not hold up
on the unhappy paths". Different problems, different owners.

What the audit buys is the layer people cannot see by looking. Five reviewers left 29 comments
on this build. None of them said that auto-submit mode promises an approval step that never
comes, or that the readiness score is capped one point below the bar the copy tells you to
clear. Those are mechanisms, and you find them by reading the build, not by looking at it.

---

## The experiment that measured all of this

The re-run used the same artefact, the same frozen JTBD set, the same eight tasks and the same
excluded dimension. Only the contract changed, so the difference in output is attributable to
the architecture.

| | Round 2, as first run | Re-run under the new contract |
|---|---|---|
| Score | 10/100 | 7/100 |
| Critical | 19 raw | 9 root causes, 15 findings |
| Fidelity artefacts | 17, retrofitted | 3, judged at source |
| Passed to another owner | 0, misfiled as nice-to-have | 13 |
| Too early to judge | 0 | 2 |
| Tasks passed | 2 of 8 | 1 of 8 |

The score went **down**, and that is the correct direction. Auditors filtered staging at
source, which left the remaining failures cleaner, and two checks that had been judged
leniently were failed on the second look. The product did not change between the two runs.

One more result worth keeping: the second run was barred from reading the first until it had
finished. Four defects were found independently both times. That is the difference between a
finding and an artefact of one run.
