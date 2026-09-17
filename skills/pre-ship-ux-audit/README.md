# pre-ship-ux-audit

The skill itself. `SKILL.md` is what an agent reads first; everything else is loaded only
when a job needs it.

The ten agents that run the scored pipeline live in `../../agents/`, and the repo README
covers how the whole thing is installed.

## Layout

```
SKILL.md          the index: verdict scale, layer priorities, rule ids, workflow
AGENTS.md         every rule expanded into one document (generated, do not hand edit)
metadata.json     version, abstract, source links

rules/            17 files, one per rule
  _sections.md      the four layers, their impact and description
  _template.md      copy this to add a rule
  flow-*.md   (4)   Flow Integrity
  control-*.md(4)   Control & Transparency
  trust-*.md  (4)   Trust & Copy
  edge-*.md   (5)   Edge Cases

references/       read when the job calls for it, not by default
  jtbd.md           climbing from steps to JTBD without restating the design
  browser-audit.md  auditing the live build, with hooks that force undesigned states
  eval-protocol.md  the JSON contract, the weights, the anti-gaming rules
  report-template.md the one-page report and its scorecard
  notion-log.md     reading and writing the Notion UX audit log

assets/           templates the agents fill in
  flow-template.md   the completed flow, every element tiered
  user-journey.md    JTBD, outcomes, and one test task each

scripts/
  build_agents.py       rules/ into AGENTS.md
  score_audit.py        agent JSON into a scorecard, a verdict and a round delta
  check_consistency.py  catches drift between this skill and its agents
```

## Anatomy of a rule

Four sections, the same in all 17. It is what lets an agent judge a case rather than tick a
box: why it matters in user and business terms, what failing looks like as an observable
symptom, what passing actually looks like, and how to check it on a design, a spec or a
build.

The frontmatter carries `impact` (the scoring weight) and `order` (position in the user
journey, which is the order the checklist is walked in, not impact order).

## Adding a rule

1. Copy `rules/_template.md` to `rules/<layer>-<slug>.md`
2. Fill in the frontmatter, including `order`
3. Add the id to the Quick reference in `SKILL.md`, and to the owning agent's check table
4. Run both scripts below

## After any edit

```bash
python3 scripts/build_agents.py       # rules/ into AGENTS.md
python3 scripts/check_consistency.py  # exit code is the error count
```

The checker exists because this grew in increments and the failure mode of that is silent:
a rule with no owner, two agents claiming one check id (which would double-count a finding),
an agent whose JSON identity no longer matches its filename, a path that moved. None of it
breaks loudly; it produces a wrong report one day.
