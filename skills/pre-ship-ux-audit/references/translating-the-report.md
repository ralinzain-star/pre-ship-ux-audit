# Translating the report

The scorecard is written in English because the findings cite code, and the repo, the rules
and the agent files are English. When the reader works in another language, translate the
finished scorecard rather than making the agents write in it: an auditor writing a second
language while reading code writes worse findings in both.

Run this **after** `score_audit.py`, never before. Scoring stays the canonical artefact.

## The one rule that matters

**Anything the reader will search for in the build stays in the original.** A translated
product string cannot be found in the code, which makes the finding unusable at the exact
moment somebody tries to act on it.

## Do not translate

| Kind | Examples |
|---|---|
| Product strings, anything on screen | `"Keeps running in the background"`, `"Not for me"`, `"Welcome back, Emily!"` |
| Rule and check ids | `flow-all-states-designed`, `ux-no-dark-patterns`, `task-1b-skip-upload` |
| Code | `closeOptimize`, `resumeReadiness`, `Math.min(70, ...)`, file names, line numbers |
| Scoring vocabulary | Critical, Major, Nice to have, pass, fail, `out_of_stage`, `not_verifiable`, `evidence_class`, `design`, `fidelity-artifact`, `unknown` |
| Stage names | spec, static, prototype, build |
| Structure | Headings, tables, emoji, bold, pipes. The output must render as the same document |

The scoring vocabulary stays because it ties the translated report back to the script, the
rule files and every previous round. Translate `Critical` and a reader can no longer match a
row to `scorecard.md`, to `results/*.json`, or to what the audit said last round.

## Do translate

Every piece of explanatory prose: the verdict block, `problem`, `impact`, `recommendation`,
the Should be and Is columns, the Fix column, the `where` column when it is a description
rather than a quotation, section intros, and the notes under each table.

## How

Write as a working designer writes, not as a translator does. Restructure a sentence rather
than calque English word order. Keep the **Should be** and **Is** columns grammatically
parallel: the contrast is the whole point of that table, and it disappears if one side is a
noun phrase and the other a sentence.

Spend the most care on "What should be true, and what is". It is the table the reader starts
from, and for many readers it is the only one they finish.

**No em-dashes**, in any language. Use a colon, a comma, or restructure.

## Naming

`scorecard-zh.md` beside `scorecard.md`, same round directory. Do not overwrite the English.

## The thing to tell the reader

The translation is a snapshot. `scorecard.md` is regenerated every time the score is re-run,
and the translation is not. Say which round and which run it came from, and re-translate
after a re-score rather than patching the old one.
