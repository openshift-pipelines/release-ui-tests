---
name: bdd-test-code-generator
description: Generates complete BDD test code (feature files, step definitions, POM classes) from plain English test intent. Use when you need to create new automated tests for Tekton/OpenShift UI workflows without writing boilerplate code. Integrates with NotebookLM for domain knowledge, supports multiple test scenarios, and includes a mandatory approval gate before code generation.
---

# BDD Test Code Generator

Automatically generate complete BDD test implementations from plain English descriptions of test workflows.

## Quick Reference

📖 **[Examples](references/examples.md)** - Task CRUD, Pipeline workflows
📖 **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions
📖 **[PipelineRun CRUD Learnings](references/pipelinerun-crud-learnings.md)** - ⭐ **START HERE** - 12 critical patterns from production
📖 **[Implementation Guide](references/implementation-guide.md)** - Phase 1 and Phase 2 detailed steps
📖 **[User Guide](references/user-guide.md)** - Best practices
📖 **[Navigation Guide](references/navigation-guide.md)** - Navigation pattern details
📖 **[Monaco Editor Guide](references/monaco-editor-guide.md)** - YAML editor integration
📖 **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## What It Does

Converts plain English → production-ready BDD: Feature files, Step definitions, POM code, Test data, Locators

**Use when**: Creating new Tekton/OpenShift UI tests, extending test suites, ensuring project conventions
**Don't use**: CLI tests, unit tests, custom validation beyond visibility checks

**Features**: Two-phase workflow with approval gate, NotebookLM integration, smart code reuse, compilation verification, 3 input modes

---

## Quick Start

```bash
# Basic usage - creates new feature with single scenario
/bdd-test-code-generator Create a task with YAML, verify it appears in the task list

# Multiple scenarios in one feature
/bdd-test-code-generator NEW_FILE_MULTI Create task | Edit task YAML | Delete task

# Append to existing feature
/bdd-test-code-generator APPEND task_management.feature: Verify task list is empty
```

---

## Two-Phase Workflow

**Phase 1** (Analysis & Planning): Parse intent → Query NotebookLM → Map to UI workflow → Check existing code → Generate plan → **🛑 STOP** - Wait for approval

**Phase 2** (Code Generation): Generate test data → Locators → POM methods → Step definitions → Feature file → Cross-check → Verify compilation → Execute tests

---

## Input Modes

| Mode | Usage | Result |
|------|-------|--------|
| **NEW_FILE** (default) | `/bdd-test-code-generator Create task...` | New feature with 1 Scenario Outline |
| **NEW_FILE_MULTI** | `/bdd-test-code-generator NEW_FILE_MULTI Create \| Edit \| Delete` | New feature with 3 Scenario Outlines |
| **APPEND** | `/bdd-test-code-generator APPEND file.feature: Delete task...` | Appends to existing feature |

---

## Prerequisites

NotebookLM MCP (ID: `ce34f1af-5b8d-47c0-ad62-b21ae6734d95`), Playwright MCP, OpenShift Console access, POM framework (`framework/ui_components/`), Test data directory (`framework/resources/test_data/`), Navigation steps (`tests/steps/test_navigation_steps.py`)

---

## Testing

Phase 1 stops for approval, analysis accurate, code matches conventions, all files compile, tests runnable via pytest

---

## Error Handling

NotebookLM timeout (`nlm login` retry), Missing POM (`/multi-page-pom`), Invalid YAML (re-query), Compilation errors (review plan), Test failures (check locators/timing/cluster). See [troubleshooting.md](references/troubleshooting.md)

---

## Navigation Pattern (CRITICAL)

**For Tekton resources under Pipelines menu**, Background must include **FOUR steps**:

```gherkin
Background:
  Given the user is logged into openshift console
  When the user expands Pipelines in left navigation bar    # Step 1: Smart expand
  And the user navigates to the Tasks page                  # Step 2: Navigate to page
  And user switches to current project                      # Step 3: Project selector
```

**CRITICAL**: Step 3 (project switch) is MANDATORY. Why: Pipelines is toggle, links hidden when collapsed, shared sessions, namespace isolation. CRUD steps auto-navigate to list page. See [Navigation Guide](references/navigation-guide.md)

## Configuration

NotebookLM: "Introducing Tekton" (`ce34f1af-5b8d-47c0-ad62-b21ae6734d95`), UI Workflows: `framework/resources/ui_workflows.yaml`

## Code Generation Best Practices (CRITICAL)

**Before generating**, consult [PipelineRun CRUD Learnings](references/pipelinerun-crud-learnings.md) for production patterns.

**Mandatory Checks**:
- **Navigation**: Detect tab vs page; Background→parent, Scenario→tabs; Check existing steps
- **Fixtures**: `page["pipelines"].list.*` NOT `.base.*`; Structure: `.list`/`.runs`/`.details`
- **Methods**: Check for combos (`click_create_pipeline_run()`); Search base classes
- **Mirroring**: PipelineRun mirrors TaskRun (`pipelineruns/` dir)
- **Async**: Status polling (3 attempts, 20s intervals); Use `verify_taskrun_status()` pattern
- **Logger**: `self.logger = logging.getLogger(__name__)` + `import logging`
- **Monaco**: `page[resource].create_run.monaco_editor.set_content()` + verify
- **Defensive**: Try-except for optional UI; Retry+verify for critical ops
- **Imports**: Add `logging`, `asyncio`, `Path`; Correct paths

---

## Limitations

UI-only, complex modals need refinement, standard waits (tune for slow clusters), basic validations, Tekton-optimized

## Advanced Topics

See references: [PipelineRun CRUD Learnings](references/pipelinerun-crud-learnings.md) ⭐, [Implementation Guide](references/implementation-guide.md), [User Guide](references/user-guide.md), [Navigation Guide](references/navigation-guide.md), [Monaco Editor Guide](references/monaco-editor-guide.md)

## Use Case Category

**Workflow Automation** - Automates creating BDD test code from plain English intent.

---

**Status**: ✅ Production Ready
**Version**: 2.1.0
**Last Updated**: 2026-05-05

📖 **[View Changelog](CHANGELOG.md)**
