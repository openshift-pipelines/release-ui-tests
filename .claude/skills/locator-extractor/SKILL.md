---
name: locator-extractor
description: Extract UI locators from a live page and verify every one against the real DOM before it reaches generated code. Use when adding locators for a new page, when a test fails with "resolved to 0 elements", or before generating any POM/test code that needs selectors. Never guess a locator - this skill proves each one matches exactly one real element.
---

# Locator Extractor & Verifier

Produces locators that are **grounded**: every selector emitted by this skill has been
resolved against the live cluster with the same Playwright engine the tests run on.

A selector that was never probed is a guess, no matter how plausible it looks. This
skill exists to make guessing impossible.

## When to use

- Adding locators for a page that has none yet
- A test fails with `TimeoutError: ... resolved to 0 elements`
- Before `/bdd-test-code-generator` or `/multi-page-pom` needs selectors for a new page
- After a product upgrade, to re-verify locators recorded against an older version

## Workflow

### 1. Check the registry first

Verified locators are cached per page and product version. Read them before touching a browser:

```bash
python -c "
from framework.agent import locator_registry as r
from framework.agent.verify_locators import detect_version
v = detect_version()
print(v)
print(r.get_page('<page_key>', v))
"
```

If the page already has the locators you need at this version, **stop** — use them.
Re-extraction is only needed for missing locators or a changed version key.

### 2. Observe the live page

Use Playwright MCP, not assumption:

1. `browser_navigate` to the page URL
2. Wait for content — the console renders nothing for 10-15s on a cold load
3. `browser_snapshot` to get the accessibility tree
4. `browser_take_screenshot` for visual reference when the tree is ambiguous

Read the snapshot for the actual attributes present. Do not pattern-match from memory
of what OpenShift console selectors usually look like.

If you introspect the DOM with `browser_evaluate`, use Playwright locators rather than
`document.querySelectorAll` — the console renders into shadow roots, which the locator
engine pierces and raw DOM queries do not. A raw query returning nothing is not
evidence the element is absent.

### 3. Draft candidates in the project's strategy order

Prefer the most stable strategy the DOM actually offers:

| Priority | Strategy | Example |
|---|---|---|
| 1 | `data-test` / `data-ouia` | `[data-test="item-create"]` |
| 2 | ARIA role with name | `role=menuitem[name="Task"]` |
| 3 | `aria-label` | `button[aria-label="Actions"]` |
| 4 | Scoped text | `h1:has-text("Tasks")` |
| 5 | CSS structure | `div.pf-v6-c-login__main-body` |

Name constants `UPPER_SNAKE_CASE`, matching `framework/locators/*.py`.
Row/item selectors that vary per record stay templated: `tr:has-text("{task_name}")`.

Write them to a spec file:

```json
{
  "page_key": "tasks.list",
  "url": "/tasks/ns/openshift-pipelines",
  "ready": "table[data-ouia-component-type=\"PF6/Table\"]",
  "candidates": {
    "CREATE_BUTTON": "[data-test=\"item-create\"]",
    "SEARCH_INPUT": "input[aria-label=\"Search input\"]",
    "KEBAB_MENU_BUTTON": {
      "selector": "button[aria-label=\"Actions\"]",
      "expect": "many"
    },
    "TASK_ROW_BY_NAME": {
      "selector": "tr[data-ouia-component-type=\"PF6/TableRow\"]:has-text(\"{task_name}\")",
      "sample": {"task_name": "argocd-task-sync-and-wait"}
    }
  }
}
```

Three fields decide whether the run is trustworthy:

- **`ready`** — a selector that proves the page finished rendering. The console shows
  nothing for 10-15s on a cold load, so probing early reports *every* locator as
  missing. Set this to the page's main content element (the table, the form, the
  detail header). If it never appears the run aborts instead of recording false
  rejections. Without it a generic fallback is used, which is weaker.
- **`sample`** — required for templated selectors, and the value must exist on the
  page right now. A placeholder probed literally matches nothing.
- **`"expect": "many"`** — for selectors that are *supposed* to repeat because callers
  always scope them to a row or container first (per-row Actions buttons, row
  checkboxes). Without it a correct 45-match locator is scored 0.40 and rejected.
  Do not use it to silence a genuinely ambiguous selector.

### 4. Verify against the live cluster

```bash
python -m framework.agent.verify_locators /tmp/candidates.json --save
```

Each candidate is scored:

| Match count | Confidence | Verdict |
|---|---|---|
| 1, via `data-test`/`id` | 0.95 | use |
| 1, via role/aria | 0.90 | use |
| 1, via text | 0.80 | use |
| 1, via CSS | 0.75 | use |
| more than 1, `expect: many` | strategy score | use — scoped by caller |
| more than 1 | 0.40 | **reject** — ambiguous, will break when the list changes |
| 0 | 0.00 | **reject** — does not exist |

`--save` records only the locators at or above 0.7 into
`.agent/memory/locator_registry.json`, keyed by page and version.

### 5. Fix rejections, do not rationalise them

- **0 matches** — the element is not there, or not there *yet*. Re-snapshot; the page may
  need an interaction first (open a menu, switch a tab). Never widen the selector just to
  make it match something.
- **more than 1 match** — scope it. Add a container (`[data-test="x"] button`), a
  structural qualifier, or `.first` at the call site if the first match is genuinely correct.

Re-run step 4 until zero rejections.

### 6. Emit locator code

Only now write to `framework/locators/<area>.py`, following the existing file's style:
a docstring, one class per page, comment-grouped sections.

```python
class TasksPageLocators:
    """Locators specific to the Tasks tab (Task resource listing)."""

    # Create actions
    CREATE_BUTTON = '[data-test="item-create"]'
```

## Sweeping for drift across the whole codebase

The steps above add or repair locators one page at a time. To check *every* committed
locator at once — after a console or operator upgrade, or before a release:

```bash
oc apply -f .agent/sweep/seed.yaml          # detail pages need a resource to show
python -m framework.agent.sweep             # ~44 pages, one login, ~20 min
oc delete namespace qa-forge-sweep          # when finished
```

Useful flags: `--only <substr>` to sweep a subset, `--json out.json` for full results,
`--save` to record passing locators, `--headed` to watch. Exit code is non-zero if
anything drifted or a page was unreachable.

`.agent/sweep/page_map.yaml` maps each locator class to a live URL. When you add a
locator class, add it there too or it is never checked.

**Map by what the page object verifies, never by name.** The sweep refuses to run if a
mapping is wrong, because probing the wrong page finds correct locators "missing" and
acting on that report breaks working tests:

```bash
python -m framework.agent.audit_map     # also runs automatically before every sweep
```

This is not hypothetical. `OverViewPageLocators` was once mapped to `/pipelines-overview`
because the names matched; it actually describes the console home page, whose page object
waits for a URL ending in `dashboards`. The sweep duly reported its correct `h1` header as
drift, the "fix" to `h2` was applied, and every test in the suite failed at login.

Three more fields prevent false drift:

- **`ready`** must be the element the probes depend on. For a list page that is the
  *table* — never the empty-state, which renders seconds earlier and makes every
  locator look missing.
- **`skip`** for locators only reachable after an interaction (menu items, builder
  nodes), and for empty-state locators on pages seeded with data — those two states
  are mutually exclusive, so one must always "fail".
- **`samples`** / **`many`** as in the spec format above.

A page reported `UNREACHABLE` means the seed is missing or the route changed — fix that
before reading anything else in the report, since its locators were never probed.

## Verifying a locator change actually works

Probing proves a selector resolves; it does not prove the test passes. After changing
any locator, run the project's sanity suite:

```bash
pytest -m sanity
```

Use a single node id only to reproduce one specific failure, never as the evidence that
a change is good. `python -m framework.agent.diagnose` defaults to the sanity suite for
this reason, and turns a failure into a verdict:

| Verdict | Meaning |
|---|---|
| `locator_absent` | re-probed live and matched nothing - the locator really is wrong |
| `locator_present` | re-probed live and DID match - **do not touch the locator**, it is timing or state |
| `data` / `assertion` | test data, or possibly a real product bug - read before changing |
| `timing_unverified` | could not re-probe; establish the page's ready signal first |

## Hard rules

- **Never** write a selector into `framework/locators/` that has not passed step 4.
- **Never** raise a confidence score or lower the 0.7 threshold to get a locator accepted.
- If a locator cannot be verified after re-snapshotting, report it as unresolved and say
  what you observed. An honest gap is useful; a plausible guess is a future test failure.
- The registry is keyed by version. If `detect_version()` returns `unknown` for a
  component, say so — cached locators may not apply to the cluster under test.

## Output

Report: page key, version, verified count, the locator code written, and any unresolved
elements with what the snapshot actually showed.
