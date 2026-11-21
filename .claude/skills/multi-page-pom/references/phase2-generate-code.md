# Phase 2: Generate Code (only after user approval)

## Step 6 — Generate locator classes

Use the `Edit` tool to APPEND new locator classes to `framework/ui_components/locators.py`.

Rules:
- Insert after the LAST existing class in the file (find the last line of the last class)
- Two blank lines between classes
- If an intermediate base was approved, generate `<Family>BasePageLocators` FIRST, then each `<Page>PageLocators`
- Each class has:
  - A docstring: `"""Locators for the <description>."""`
  - Comments grouping locators: `# Page header`, `# Tab navigation`, `# Search/Filter toolbar`, `# Row actions`, `# Data load checks`, `# <Section>-specific`, etc.
  - Locators as class attributes (strings), using the locator values determined during extraction
- Follow the EXACT style of existing classes like `TasksBasePageLocators` and `TasksPageLocators`

## Step 7 — Generate URL patterns

Use the `Edit` tool to APPEND new patterns to `framework/ui_components/console_url_patterns.py`.

Rules:
- Insert after the last existing pattern
- One blank line between patterns
- Variable name: `UPPER_SNAKE_CASE_URL = re.compile(r"<pattern>")`
- Only add patterns for pages that use `_verify_page_regex`. Do NOT add patterns for pages using `_verify_page` or `wait_for_url_to_contain`.

## Step 8 — Generate new commons components (if any were proposed and approved)

For each new commons component:
1. Create `framework/ui_components/commons/<component_name>.py`
2. Add its locator class to `locators.py` (same Edit append)
3. Follow the EXACT pattern of existing commons (e.g., `favorites.py`):
   - Inherit BasePage
   - Constructor takes `(page: Page, config: Config)`
   - Calls `super().__init__(page, config)`
   - Sets `self.locators = <ComponentName>Locators()`
   - Async methods returning bool

## Step 9 — Generate intermediate base page (if approved)

Create `framework/ui_components/<family>_base_page.py`.

Follow the EXACT pattern of `tasks_base_page.py`:
- Imports: Page, Config, BasePage, locators class, URL pattern, commons classes
- Class docstring: `"""Abstract base class for <Page1> and <Page2> pages. Contains shared UI elements and behaviors common to both/all tabs."""`
- Constructor:
  ```python
  def __init__(self, page: Page, config: Config) -> None:
      super().__init__(page, config)
      self.base_locators = <Family>BasePageLocators()
      self.project_selector = ProjectSelector(page, config)
      self.favorites = Favorites(page, config)
  ```
- IMPORTANT: Use `self.base_locators` (NOT `self.locators`) for the base class locators. The leaf class uses `self.locators`.
- `verify_on_page()` method using the appropriate URL verification
- Shared action methods for all Tier B elements
- `verify_data_load()` method if any pages are list-type with data grids
- All methods async, returning bool, with full docstrings matching existing style

## Step 10 — Generate leaf page classes

For each page, create `framework/ui_components/<page_name>_page.py`.

**If extending intermediate base (like TasksPage extends TasksBasePage):**
```python
from playwright.async_api import Page

from framework.config.config import Config
from framework.ui_components.<family>_base_page import <Family>BasePage
from framework.ui_components.locators import <Page>PageLocators


class <Page>Page(<Family>BasePage):
    """Page object for the <description>. Inherits common functionality from <Family>BasePage."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = <Page>PageLocators()

    # Page-specific methods only (Tier C elements)
```

**If extending BasePage directly (like TaskDetailsPage):**
```python
from playwright.async_api import Page

from framework.config.config import Config
from framework.ui_components.base_page import BasePage
from framework.ui_components.commons.favorites import Favorites
from framework.ui_components.commons.project_selector import ProjectSelector
# ... other commons as needed
from framework.ui_components.console_url_patterns import <PATTERN>
from framework.ui_components.locators import <Page>PageLocators


class <Page>Page(BasePage):
    """Page object for the <description>."""

    def __init__(self, page: Page, config: Config) -> None:
        super().__init__(page, config)
        self.locators = <Page>PageLocators()
        self.project_selector = ProjectSelector(page, config)
        self.favorites = Favorites(page, config)
        # ... other commons

    async def verify_on_page(self) -> bool:
        # ...
```

Rules for ALL page classes:
- Imports alphabetically ordered, grouped: stdlib → playwright → framework.config → framework.ui_components
- Constructor pattern: super().__init__, locators, commons composition
- Every method: `async def <verb>_<noun>(self, ...) -> bool:`
- Every method has a full docstring with `:param`, `:return:`, `:raises:` as appropriate
- Methods that click elements return `await self.click_element(self.locators.LOCATOR)`
- Methods that fill inputs return `await self.fill_input(self.locators.LOCATOR, value)`
- Methods that check visibility return `await self.is_visible(self.locators.LOCATOR)`
- Data load methods call `await self._verify_data_load(...)` or `await self.verify_data_load(...)`
- Column header clicks follow the pattern: `click_<column_name>_column_header()`
- Tab navigation follows: `navigate_to_<tab_name>_tab()`

## Step 11 — Update fixture registration

Use the `Edit` tool to modify `framework/fixtures/ui_fixtures.py`:

1. Add import statements for each new leaf page class. Insert in alphabetical order among existing imports.
   Example: if adding `TaskDetailsPage`, insert between the `TasksPage` and `TriggersPage` imports.

2. Add entries to the dict in the `page` fixture's return statement. Use snake_case keys.
   Example: `"task_details": TaskDetailsPage(playwright_page, config),`

3. Update the fixture docstring's `:return:` section to list new page objects.

Do NOT import or register intermediate base classes in the fixture — only leaf page classes that tests will use directly.

## Step 12 — Final summary

Print:
```
## Generation Complete

### Files Created
| File | Class | Locators | Methods |
|------|-------|----------|---------|
| framework/ui_components/<file>.py | <ClassName> | N | M |

### Files Modified
| File | Changes |
|------|---------|
| locators.py | Added: <Class1>, <Class2> |
| console_url_patterns.py | Added: <PATTERN1>, <PATTERN2> |
| ui_fixtures.py | Added imports + fixture entries: <key1>, <key2> |

### Class Hierarchy (Final)
<ASCII tree>

### Next Steps
- Run `python -m py_compile framework/ui_components/<new_file>.py` for each generated file to verify syntax
- Run `pre-commit run --all-files` to verify formatting
- Review generated locators against actual page DOM
- Write test scenarios using the new page objects
```
