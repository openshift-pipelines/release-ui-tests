---
name: multi-page-pom
description: Analyze N related page URLs, detect shared elements across pages, propose a class hierarchy with base classes and commons composition, and after user approval generate all POM code integrated into the existing codebase. Use when asked to generate page objects for multiple related pages, create a page family, or build a shared base class for related UI pages.
allowed-tools: Read Write Edit Bash(python *) mcp__playwright__browser_navigate mcp__playwright__browser_snapshot mcp__playwright__browser_screenshot
---

# Multi-Page POM Generator

Analyze multiple related page URLs and generate an integrated Page Object Model hierarchy.

## Quick Reference

📖 **[Phase 1: Extract, Analyze, and Propose](references/phase1-extract-analyze-propose.md)** - 5 detailed steps (Load context, Parse URLs, Extract structures, Cross-page analysis, Present report)
📖 **[Phase 2: Generate Code](references/phase2-generate-code.md)** - 7 detailed steps (Generate locators, URL patterns, commons, base page, leaf pages, fixtures, summary)

---

## Input Format

**$ARGUMENTS**: Comma-separated or space-separated list of N URLs (minimum 2)

**Examples**:
```text
https://console.../k8s/ns/ui-test/tekton.dev~v1~Task/hello, https://console.../k8s/ns/ui-test/tekton.dev~v1~Task/hello/yaml

https://console.../pipelines/ns/foo https://console.../tasks/ns/foo/task-runs
```

---

## Two-Phase Workflow

**Phase 1: Extract, Analyze, and Propose**
1. Load project context (README, BasePage, locators, patterns, fixtures, commons, existing pages)
2. Parse input URLs → Infer page names, classify types (list/detail/create/overview), check conflicts
3. Extract page structures → Navigate, screenshot, snapshot, parse elements with semantic IDs
4. Cross-page analysis → Build shared-element map, classify into tiers (Existing Commons / New Base Class Candidates / Page-Specific)
5. Present analysis report → Show pages, shared elements, proposed hierarchy, files to create/modify

**🛑 MANDATORY STOP** - Wait for user approval

**Phase 2: Generate Code** (only after approval)
6. Generate locator classes → Append to `locators.py`
7. Generate URL patterns → Append to `console_url_patterns.py`
8. Generate new commons components (if any)
9. Generate intermediate base page (if approved)
10. Generate leaf page classes → Create `<page_name>_page.py` files
11. Update fixture registration → Modify `ui_fixtures.py`
12. Final summary → Show files created/modified, hierarchy, next steps

---

## Tier Classification Logic

**Tier A (Existing Commons)**: Elements matching known commons (ProjectSelector, Favorites, ActionsMenu) → Compose into pages
**Tier B (New Base Class Candidates)**: Shared elements NOT covered by commons → Create intermediate base class if >= 3 elements on >= 2 related pages
**Tier C (Page-Specific)**: Unique elements → Implement in leaf page classes only

---

## Hierarchy Decision Rules

- **Tier B >= 3 elements + >= 2 related pages** → Intermediate base class (`<Family>BasePage`)
- **Tier B = 2 elements (structurally important)** → Propose base class (borderline, let user decide)
- **Tier B = 0-1 elements** → No base class, each page extends BasePage directly
- **Sub-groups detected** → Propose separate hierarchies per sub-group

---

## Analysis Report Format

### Pages Analyzed
Table: # | URL | Inferred Class | Page Type | File Name

### Shared Elements Analysis
- Tier A: Existing Commons to Compose
- Tier B: Candidates for Shared Base Class
- Tier C: Page-Specific Elements

### Proposed Class Hierarchy
ASCII tree showing inheritance

### Proposed Locator Classes
List with element counts

### URL Verification Strategy
Table: Page | Method | Pattern/Suffix | Variable Name

### Files to Create/Modify
Tables showing what will be generated

---

## Code Generation Patterns

**Locators**: Append to `locators.py` following existing style
**URL Patterns**: Append to `console_url_patterns.py` as `UPPER_SNAKE_CASE_URL = re.compile(r"...")`
**Commons**: Create `commons/<name>.py` inheriting BasePage
**Base Page**: Create `<family>_base_page.py` with `self.base_locators`, commons composition, shared methods
**Leaf Pages**: Create `<name>_page.py` extending base or BasePage, with `self.locators`, page-specific methods
**Fixtures**: Update `ui_fixtures.py` with imports + dict entries (snake_case keys)

---

## Important Notes

- **MANDATORY STOP** after Phase 1 analysis report - Do NOT proceed to Phase 2 without user approval
- **Conflict checking**: Verify inferred class names don't collide with existing classes
- **Semantic IDs**: Normalize labels for cross-page comparison (`{type}:{normalized_label}`)
- **Base vs Leaf locators**: Base class uses `self.base_locators`, leaf uses `self.locators`
- **Fixture registration**: Only register leaf page classes, NOT intermediate base classes
- **Import ordering**: stdlib → playwright → framework.config → framework.ui_components
- **Method naming**: `async def <verb>_<noun>(self, ...) -> bool:`

---

## Detailed Steps

📖 See [Phase 1 Guide](references/phase1-extract-analyze-propose.md) for complete extraction and analysis steps
📖 See [Phase 2 Guide](references/phase2-generate-code.md) for complete code generation steps

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2026-04-12
