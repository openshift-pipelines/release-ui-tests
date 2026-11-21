---
name: generate-pom
description: Generate a Python Page Object Model file from extracted page structure.
Use when asked to generate, create, or write a page object model or POM.
allowed-tools: Read Write Bash(python *)
---

Generate a Python Page Object Model file following the project's coding standards.

## Context to load first

Before writing any code:
1. Read `README.md` — it contains the coding standards for this project
2. Read one or two existing POM files from `pages/` — use them as style reference
3. Read the page structure JSON passed as $ARGUMENTS (or from the most recent extract-page-structure output)

## POM generation rules

Follow the README standards exactly. In addition:

- Class name: `<PageName>Page` (PascalCase)
- File name: `<page_name>_page.py` (snake_case)
- Constructor takes `page: Page` (Playwright async Page object)
- Locators defined as properties using `self._page.get_by_*` or `self._page.locator()`
- Selector priority order:
  1. `get_by_test_id()` if data-testid exists
  2. `get_by_role()` + `get_by_label()` for forms
  3. `get_by_text()` for buttons with visible text
  4. `locator("css=...")` as last resort
- Methods named as actions: `click_login_button()`, `fill_email()`, `select_dropdown()`
- Every method is `async`
- Add docstrings to the class and all public methods
- Add type hints everywhere

## Output

Write the file to `pages/<page_name>_page.py`
Then print a summary of what was generated: class name, number of locators, number of methods.
