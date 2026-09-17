# Stakeholder report template

The audience is the PM, the CEO, and the engineers who will pick this up. They will read the
executive summary and the Critical list, and skim the rest. Write accordingly.

The whole report should fit on one printed page. If it does not, you have kept findings that
should have been dropped.

## Structure

```markdown
# UX audit: [feature name]
_[Date] · [Round N] · Audited against: [spec URL / Figma file]_

## Executive summary
[3 sentences max. Written for a teammate with no design background. Sentence 1: what was
audited and the headline verdict. Sentence 2: the single biggest risk. Sentence 3: what needs
to happen before ship.]

## 🔴 Critical (must fix before ship)
1. **[Issue title]**: [what's broken] → [why it matters] → [what to do]
2. ...

## 🟡 Major (fix in sprint 1 post-launch)
1. **[Issue title]**: [what's broken] → [why it matters] → [what to do]

## 🟢 Nice to have (polish backlog)
1. **[Issue title]**: [what's broken] → [what to do]

## Spec vs design mismatches
| Spec says | Design shows | Which is right? |
|---|---|---|

## Checklist scorecard
| Layer | Item | Result |
|---|---|---|
| Flow Integrity | Entry point is visible and clear | ✅ Pass |
| Flow Integrity | Prerequisites met before each step | ❌ Fail (see Critical #2) |
| Flow Integrity | Success / failure / loading / empty states designed | ⚠️ Not verifiable, no empty state in Figma |
| ... | ... | ... |
```

## Rules for the report

- Each issue is **one line**: what's broken, why it matters, what to do. The detail already
  lives in the findings above it. Repeating it doubles the length and halves the readership.
- Drop empty sections. A report with an empty "Nice to have" heading reads as unfinished.
- The scorecard is the proof of work. Include every checklist item, including the passes:
  it is what lets the PM trust the Criticals.
- Use ⚠️ Not verifiable for anything you could not check, and say why. That gap is information.
- No filler, no hedging, no "overall the design is solid but". Lead with the finding.

## Example executive summary

> The AI Interview Coach session setup flow (3 Figma frames) is functionally complete but has
> no designed response for a failed session start, which is the most likely failure in a
> real-time feature. A user whose session fails to launch currently sees nothing and will
> assume the product is broken. Two Critical items need designs before this can ship.
