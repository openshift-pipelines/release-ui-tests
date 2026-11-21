# Phase 1: Extract, Analyze, and Propose

## Step 1 — Load project context

Read these files to understand the current codebase state. You MUST do this before any navigation:

1. `README.md` — coding standards
2. `framework/ui_components/base_page.py` — BasePage API (methods available to all pages)
3. `framework/ui_components/locators.py` — ALL existing locator classes (to avoid name collisions and identify existing commons)
4. `framework/ui_components/console_url_patterns.py` — existing URL regex patterns
5. `framework/fixtures/ui_fixtures.py` — current fixture dict (to know which page keys exist)
6. ALL files in `framework/ui_components/commons/` — existing shared components (ProjectSelector, Favorites, ActionsMenu, etc.)
7. At least TWO existing page files that use an intermediate base class, e.g.:
   - `framework/ui_components/tasks_base_page.py` + `framework/ui_components/tasks_page.py` (intermediate base + leaf)
   - `framework/ui_components/task_details_page.py` (direct BasePage child with commons composition)

Note every class name, every locator class name, every fixture key, and every URL pattern variable name. You must not create conflicts.

## Step 2 — Parse input URLs

Split $ARGUMENTS into individual URLs. For each URL:

1. **Infer page name**: Extract from the URL path. Rules:
   - `/pipelines/ns/foo` → `PipelinesPage`
   - `/tasks/ns/foo/task-runs` → `TaskRunsPage`
   - `/k8s/ns/foo/tekton.dev~v1~Task/my-task` → `TaskDetailsPage`
   - `/k8s/ns/foo/tekton.dev~v1~Task/my-task/yaml` → `TaskYamlPage`
   - `/k8s/ns/foo/tekton.dev~v1~Task/~new` → `CreateTaskPage`
   - General rule: take the last meaningful path segment(s), convert hyphens to CamelCase, append "Page"
   - If the path contains `/~new`, prefix with "Create"
   - If the path ends with `/yaml`, append "Yaml" before "Page"

2. **Classify page type**:
   - `list` — has data grid/table, search bar, filter, tabs for related resources, kebab menus
   - `detail` — shows a specific resource, has breadcrumb, Details/YAML tabs, Actions dropdown
   - `create` — has YAML editor with Save/Create + Cancel buttons, for creating new resources
   - `overview` — dashboard-style page with summary widgets, no data grid

3. **Check for conflicts**: If the inferred class name already exists in the codebase, warn and suggest an alternative.

## Step 3 — Extract page structures

For EACH URL, sequentially:

1. Navigate: `browser_navigate` to the URL
2. Wait for stability: `browser_screenshot` — if you see loading spinners or empty content areas, wait 3-5 seconds and screenshot again
3. Capture: `browser_screenshot` for visual reference (save mentally for your analysis)
4. Extract: `browser_snapshot` to get the full accessibility tree
5. Parse the snapshot into structured data. For EACH interactive element found, record:
   - `type`: button, link, input, tab, heading, grid, editor, select, checkbox, radio, menuitem, columnheader
   - `role`: ARIA role from the snapshot
   - `label`: visible text, placeholder, or aria-label
   - `locator`: proposed Playwright locator string following project conventions:
     - Prefer `[data-test="..."]` or `[data-testid="..."]` if present
     - Then `role=<role>[name="<label>"]` for buttons, tabs, menuitems, columnheaders
     - Then `button:has-text("...")` or `a:has-text("...")` for text-based
     - Then `[aria-label="..."]` for icon buttons
     - Then `input[placeholder="..."]` for inputs
     - Then CSS selector as last resort
   - `locator_strategy`: testid, role, text, aria, css
   - `section`: which visual section the element belongs to (header, toolbar, tabs, table, editor, sidebar, breadcrumb, actions)
   - `semantic_id`: normalized identifier for cross-page comparison. Format: `{type}:{normalized_label}`. Normalize label by: lowercase, strip leading/trailing whitespace, replace non-alphanumeric sequences with underscore. Examples: `button:create`, `input:search_by_name`, `tab:details`, `heading:tasks`, `columnheader:name`.

6. Organize elements into sections and store the full structure for each page.

## Step 4 — Cross-page analysis

Now compare all extracted page structures:

### 4a. Build the shared-element map

Create a dictionary mapping each `semantic_id` to the list of pages where it appears.

### 4b. Classify each shared element into tiers

For each semantic_id that appears on 2+ pages:

- **Tier A (Existing Commons)**: Check if it matches a known commons component:
  - `button:project` or any button with "Project:" text → ProjectSelector (exists)
  - `button:add_to_favorites` or button with aria-label "Add to favorites" → Favorites (exists)
  - `button:actions` → ActionsMenu (exists)
  - If matched, note which pages need this commons component composed.

- **Tier B (New Base Class Candidates)**: Shared elements NOT covered by existing commons. These are candidates for an intermediate base class. Examples: shared page header, shared search input, shared filter button, shared tab navigation, shared data grid, shared kebab menu, shared Create dropdown.

- **Tier C (Page-Specific)**: Elements unique to a single page.

### 4c. Decide hierarchy structure

Apply these rules:

1. **If Tier B has >= 3 elements AND those elements appear on >= 2 pages that are clearly related (same URL prefix, same page family):**
   → Propose an intermediate base class: `<Family>BasePage(BasePage)` with Tier B elements.
   → Leaf pages extend `<Family>BasePage`.
   → The base class composes Tier A commons.

2. **If Tier B has exactly 2 elements and they are structurally important (e.g., page header + data verification):**
   → Still propose an intermediate base class but note it is a borderline case. Let the user decide.

3. **If Tier B has 0-1 elements:**
   → No intermediate base class. Each page extends BasePage directly.
   → Each page individually composes whatever Tier A commons it needs.
   → If the single shared element is a reusable widget (not just a heading), consider proposing a new commons component instead.

4. **If pages form sub-groups (e.g., 2 list pages share toolbar + 2 detail pages share breadcrumb+tabs):**
   → Propose separate hierarchies per sub-group, or note that these are separate families.

### 4d. URL verification strategy per page

For each page, determine the verification method:

- URL has `/all-namespaces` or `/ns/<variable>` with nothing after → `_verify_page_regex` with pattern like `re.compile(r"section/(?:all-namespaces|ns/[^/?#]+)")`
- URL has `/k8s/ns/<ns>/<api~group>/<resource-name>` → `_verify_page_regex` with pattern like `re.compile(r"k8s/ns/[^/?#]+/api\.group~v1~Resource/[^/?#]+$")`
- URL has `/k8s/ns/<ns>/<api~group>/<resource-name>/yaml` → `_verify_page_regex` with pattern ending in `/yaml`
- URL has `~new` → `wait_for_url_to_contain("api.group~v1~Resource/~new")`
- URL is a simple static path → `_verify_page` with suffix
- Multiple pages in the family share the same URL pattern (tabbed pages) → base class owns `verify_on_page()` using the common pattern

## Step 5 — Present analysis report

Present the findings in this EXACT format. Do NOT skip any section:

```
## Multi-Page POM Analysis Report

### Pages Analyzed
| # | URL | Inferred Class | Page Type | File Name |
|---|-----|---------------|-----------|-----------|
| 1 | <url> | <ClassName> | <type> | <file_name>.py |

### Shared Elements Analysis

#### Tier A — Existing Commons to Compose
| Commons Component | Pages That Need It |
|-------------------|--------------------|
| ProjectSelector   | Page1, Page2       |
| Favorites         | Page1, Page2       |
| ActionsMenu       | Page2              |

(If none: "No existing commons components needed.")

#### Tier B — Candidates for Shared Base Class
| Semantic ID | Element Type | Label | Locator | Pages |
|-------------|-------------|-------|---------|-------|
| button:create | button | "Create" | button:has-text("Create") | Page1, Page2 |

(If none: "No shared elements beyond existing commons. No intermediate base class needed.")

#### Tier C — Page-Specific Elements
**<PageName>** (<N> unique elements):
| Element | Type | Locator |
|---------|------|---------|
| ... | ... | ... |

### Proposed Class Hierarchy
<ASCII diagram showing inheritance tree, e.g.:>

BasePage
  └── <Family>BasePage (new intermediate base)
        ├── FooPage
        └── BarPage

[OR if no base class warranted:]

BasePage
  ├── FooPage (composes: ProjectSelector, Favorites)
  ├── BarPage (composes: ProjectSelector, Favorites, ActionsMenu)
  └── BazPage (composes: Favorites)

### Proposed Locator Classes
List each new locator class name and its element count.

### URL Verification Strategy
| Page | Method | Pattern/Suffix | Variable Name |
|------|--------|---------------|---------------|
| ... | _verify_page_regex | re.compile(r"...") | FOO_URL |

### Files to Create
| File Path | What It Contains |
|-----------|-----------------|
| framework/ui_components/<name>.py | <description> |

### Files to Modify
| File Path | What Changes |
|-----------|-------------|
| framework/ui_components/locators.py | Append: <LocatorClass1>, <LocatorClass2> |
| framework/ui_components/console_url_patterns.py | Append: <PATTERN_NAME> |
| framework/fixtures/ui_fixtures.py | Add import + dict entry for <key> |
```

**Do you approve this hierarchy and plan? Reply "yes" to proceed, or describe what you want changed.**
