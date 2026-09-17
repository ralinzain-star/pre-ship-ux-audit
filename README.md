# Pre-ship UX audit

A skill and ten agents that audit a feature before it ships: complete the critical user
flow, derive the JTBD, run seven auditors in parallel, score the result with a script so
rounds are comparable, and return one report with a ship or no-ship verdict.

Built from Iris Hsieh's [Pre-ship UX checklist](https://app.notion.com/p/Pre-ship-UX-checklist-361997983434804fb5d9c45c44e4c2f7),
Jobscan product team.

## What is here

```
skills/pre-ship-ux-audit/  SKILL.md, 17 rules, references, assets, scripts
agents/                    ten agent definitions, one orchestrator plus nine specialists
docs/                      the architecture diagram, Chinese and English
.claude-plugin/            plugin and marketplace manifests
install.sh                 links this repo into ~/.claude so Claude Code can load it
```

Two ways to install: run `./install.sh` for symlinks, or add it as a plugin using the
`.claude-plugin` manifest. The symlink route is the one to use while you are still editing,
because changes are live with no reinstall.

## How it is wired

Claude Code only loads skills from `~/.claude/skills` and agents from `~/.claude/agents`.
This bundle is the source of truth; those two locations hold symlinks back to it. So you
edit files here, and the change is live immediately with nothing to copy.

Run `./install.sh` on a new machine, or after moving this folder. It is safe to re-run and
it refuses to overwrite a real file that is sitting where a link should go.

Moving the bundle somewhere else is one command plus a re-link:

```bash
mv ~/Documents/GitHub/pre-ship-ux-audit /somewhere/else
/somewhere/else/install.sh
```

## Using it

Say what you have, in one message. The orchestrator asks for anything missing and decides
which specialists are worth dispatching.

> Run a full pre-ship audit on Interview Coach session setup. Spec is at [link], Figma
> frames "Step 1 to Step 3", staging at [url], I have a test account. Round 1.

Each specialist is independently useful: ask for `UX Flow Completion` to fill in a rough
flow, `UX Audit · JTBD` to derive testable jobs, `UX Audit · Usability Test` to attempt
real goals on the live build, or one dimension by name.

## After editing

```bash
cd skills/pre-ship-ux-audit
python3 scripts/build_agents.py       # rules/ into AGENTS.md
python3 scripts/check_consistency.py  # exit code is the error count
```

The checker catches drift that does not break loudly: a rule with no owner, two agents
claiming the same check id (which would double-count findings), an agent whose JSON identity
no longer matches its filename, a path that moved.
