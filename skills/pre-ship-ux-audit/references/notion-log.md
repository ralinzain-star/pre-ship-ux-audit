# Logging an audit to Notion

Past audits live in the **UX audit log** database, nested under the Pre-ship UX checklist page.

- Parent page: https://app.notion.com/p/36d997983434802fb763dbd3179242aa
- Data source: `collection://36899798-3434-80ae-998a-000b0f104be3`

## Schema

| Property | Type | Values |
|---|---|---|
| `Feature` | title | Feature name being audited |
| `Feature flag` | select | `Critical` / `Major` / `Nice to have` (the highest severity found) |
| `Audit Round` | select | `Round 1` / `Round 2` / `Round 3` |
| (unnamed date column) | date | Audit date. Set via `date:<column>:start` |

## Reading past audits

Before a Round 2 or Round 3 audit, query this database for the same feature. Re-finding an
issue that was already raised and deferred is a different (and more useful) finding than
raising it fresh: say "still open from Round 1" so the team sees it has been ignored once.

Use `notion-query-data-sources` against the data source URL above.

## Writing a new entry

Ask before creating the page. Logging an audit is a visible action in a shared workspace, and
Iris may want to review the findings first.

Create it with `notion-create-pages`, parented to the data source. Put the full report in the
page body, and set:
- `Feature`: the feature name
- `Feature flag`: the highest severity found in this audit
- `Audit Round`: which round this is (check existing entries for the same feature first)
- the date column: today
