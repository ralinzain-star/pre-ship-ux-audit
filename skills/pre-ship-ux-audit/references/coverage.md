# Coverage: who has this, the spec or the build

A prototype-stage reader is not asking which control is broken. They are asking **what still
has to be designed**. That question needs two sources compared, not one inspected.

So every element of the completed flow carries a `coverage` value, from comparing the spec
against the artefact. This is a different axis from the confidence tier in
`assets/flow-template.md`: **tier says how sure you are, coverage says who has it.** An
element can be `observed` in the build and still be `built-unspecified`.

## The four cells

|  | In the spec | Not in the spec |
|---|---|---|
| **In the build** | `agreed` | `built-unspecified` |
| **Not in the build** | `specified-unbuilt` | `absent` |

**`agreed`.** Somebody wrote it down and somebody built it. Audit it normally: this is the
only cell where a control-by-control finding makes sense.

**`specified-unbuilt`.** Promised, not built yet. At prototype stage this is usually **not a
finding**: it is the backlog. Report it as work outstanding, and only make it a finding when
something else in the build already depends on it. A pricing gate that the spec promises and
the build omits is a backlog item; a run the build spends a credit on, with no credit
anywhere, is a defect.

**`built-unspecified`.** Somebody made a decision and it is not written down anywhere. Nobody
reviewed it, nobody can maintain it, and the next person to touch it will not know it was
deliberate. This is the cell teams are most surprised by, and it is usually where a prototype
quietly became the spec.

**`absent`.** Neither source has it, and the flow needs it to be complete. **This is what the
audit is for.** A reviewer reads what is there; only a completed flow shows what nobody put
anywhere. Every `absent` element belongs in the report, and the Critical ones are the answer
to "what is missing".

## Write the element so a stranger can read it

The element is what the reader sees first and often all they read. A label is not enough:
"Session expiry mid-flow" tells someone who knows the product nothing they did not know, and
someone who does not know it nothing at all.

**Name the moment, from the user's side, as a clause that stands alone.**

| Not this | This |
|---|---|
| Refresh mid-run | Reloading the page while an optimization run is going |
| Optimize run failure screen | What the user sees when an optimization run fails |
| Zero-credit state and upgrade prompt | What the product shows once the free optimizations are used up |
| Base Resume present versus absent | Whether the user has a resume on file, and what the product does when they do not |
| "Not yet" and "Ask me later" | What each of the two deferral answers actually does after the user picks one |

Three habits carry most of it:

- **A branch is a question, not a pair of nouns.** "Whether X, and what happens when it is
  not" reads as something a person could answer. "X versus not-X" reads as a variable name.
- **A state is what somebody sees.** Start it with "What the user sees when", or with the
  thing itself described plainly, not with the internal name of the screen.
- **Do not use the product's shorthand as the whole label.** `?drawer=resume`, "Base Resume",
  "Match Rate" can appear inside the clause, never as the clause.

This costs a few extra words per row and it is the difference between a table a PM reads and
a table a PM skips. Say it in full.

## How to classify

Read the spec first and build an inventory from it, before you open the artefact. Reading
them together makes it too easy to see the spec in the build.

For each element of the completed flow:

1. Is it in the build? Verify in the source or by driving it, not from a screenshot.
2. Is it in the spec? Quote the line. "The spec implies it" means no: that is `absent`, and
   pretending otherwise hides the gap behind somebody's reasonable inference.
3. Where the two disagree about **behaviour**, that is not a coverage value, it is a finding.
   A spec that says a run cannot be cancelled, against a build where closing the drawer kills
   it, is `agreed` on coverage and a contradiction on behaviour. Say both.

## When there is no spec

Say so, and use two values only: `built` and `absent`. Do not fabricate a middle. A missing
spec is worth naming in the report on its own, because it means every decision in the build
is `built-unspecified` and nobody can tell design from accident.

## What it changes downstream

- The prototype report leads with the counts, then lists `absent` and `specified-unbuilt`.
- JTBD coverage gets sharper: a job served only by `specified-unbuilt` steps is not served,
  it is planned, and saying "works" of it would be wrong.
- `built-unspecified` is the one cell that does not fit a severity. Report it as a list with
  a question attached, not as findings with a Critical count.
