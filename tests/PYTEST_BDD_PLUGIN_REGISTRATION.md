# pytest-bdd Plugin Registration - Important Notes

## The Problem

When organizing test steps into multiple files, pytest-bdd requires explicit registration of step definition modules. However, there's a critical constraint:

**Files that call `scenarios()` cannot be registered as pytest plugins.**

## Why This Matters

pytest-bdd's `scenarios()` function needs access to pytest's configuration (CONFIG_STACK), which is only available after pytest initialization completes. When a module is registered in `pytest_plugins`, it's imported during pytest's plugin loading phase, BEFORE the configuration is fully initialized.

### The Error
If you register a file with `scenarios()` call in `pytest_plugins`, you'll get:
```
IndexError: list index out of range
  File "pytest_bdd/scenario.py", line 400, in get_from_ini
    config = CONFIG_STACK[-1]
```

## The Solution

### Separate Files by Purpose

**Files with ONLY step definitions** → Register in `pytest_plugins`
```python
# tests/conftest.py
pytest_plugins = [
    "tests.steps.test_auth_steps",  # ✅ Only step definitions
    "tests.steps.test_navigation_steps",  # ✅ Only step definitions
    "tests.steps.test_shared_steps",  # ✅ Only step definitions
]
```

**Files with `scenarios()` calls** → Do NOT register (auto-discovered)
```python
# tests/steps/test_pipelines_operator_navigation_steps.py
from pytest_bdd import scenarios

scenarios(FEATURE_FILE)  # ❌ Do NOT register in pytest_plugins
```

## File Organization Pattern

```
tests/steps/
├── test_auth_steps.py                            # ✅ Register as plugin (no scenarios)
├── test_navigation_steps.py                      # ✅ Register as plugin (no scenarios)
├── test_shared_steps.py                          # ✅ Register as plugin (no scenarios)
├── test_task_crud_steps.py                       # ❌ NOT in plugins (has scenarios() call)
└── test_pipelines_operator_navigation_steps.py   # ❌ NOT in plugins (has scenarios() call)
```

> A module that is neither registered in `pytest_plugins` nor calls `scenarios()` is
> dead code: its step definitions are never loaded. Three navigation modules sat in
> that state before being removed - they looked active but pytest-bdd never saw them.

## Current Configuration

```python
# tests/conftest.py
from framework.fixtures.ui_fixtures import *  # noqa: F403, F401

pytest_plugins = [
    "tests.steps.test_auth_steps",  # Step definitions only
    "tests.steps.test_navigation_steps",  # Step definitions only
    "tests.steps.test_shared_steps",  # Step definitions only
    # Note: modules that call scenarios() - the *_crud_steps and
    # test_pipelines_operator_navigation_steps - are NOT registered here;
    # pytest auto-discovers them as test modules.
]
```

## How pytest-bdd Discovers Steps

### For Registered Plugins
Step definitions in plugin-registered files are globally available to ALL scenarios.

### For Test Files
pytest discovers `test_*.py` files that call `scenarios()`, and can use step definitions from:
1. The same file
2. Plugin-registered step modules
3. Imported modules

## Best Practices

### Option 1: Separate Step Definitions from Scenarios (Current Approach)

**Pros:**
- Clear separation of concerns
- Step definitions are shared across all scenarios
- Easier to reuse steps

**Cons:**
- More files to maintain

**Structure:**
```
tests/steps/
├── test_auth_steps.py           # Steps only → Register
├── test_navigation_steps.py     # Steps only → Register
├── test_domain_steps.py         # Steps only → Register
└── test_domain_scenarios.py     # Scenarios + domain steps → Don't register
```

### Option 2: Co-locate When Possible

**Pros:**
- Related steps and scenarios together
- Fewer total files

**Cons:**
- Files can't be registered as plugins
- Steps only available within that test module (unless manually imported elsewhere)

**Structure:**
```
tests/
├── test_pipelines.py  # scenarios() + pipeline steps → Don't register
├── test_tasks.py      # scenarios() + task steps → Don't register
└── conftest.py        # pytest_plugins = [] (or shared steps only)
```

## Migration Notes

When reorganizing tests:

1. **Identify files with `scenarios()` calls**
   ```bash
   grep -l "scenarios(" tests/steps/*.py
   ```

2. **Remove them from `pytest_plugins`**
   - They will be auto-discovered as tests
   - Their step definitions will be local to that module

3. **Register shared step modules**
   - Files with only `@given`, `@when`, `@then` decorators
   - No `scenarios()` calls
   - Steps will be globally available

## Troubleshooting

### "Step definition is not found" error
**Cause:** Step definition module not registered or imported
**Solution:** Add the module to `pytest_plugins` in conftest.py

### "IndexError: list index out of range" during collection
**Cause:** File with `scenarios()` call is registered in pytest_plugins
**Solution:** Remove it from pytest_plugins (it will be auto-discovered)

### Steps not available across test files
**Cause:** Step definitions are in a test file, not a plugin
**Solution:** Either:
- Move shared steps to a plugin-registered module, OR
- Import the steps module in the test file that needs them

## Summary

✅ **DO register:** Step-definition-only modules (no scenarios() call)
❌ **DON'T register:** Test modules that call scenarios()
🔍 **Auto-discovered:** All test_*.py files in tests/ directory
🌍 **Global steps:** Steps in pytest_plugins files
📍 **Local steps:** Steps in test files (not registered as plugins)

## Current Status

Our current configuration follows **Option 1** with a hybrid approach:
- Shared steps (auth, navigation, trigger navigation) → Registered as plugins
- Domain-specific scenarios + steps (pipeline, task) → Auto-discovered, not registered

This gives us the best of both worlds:
- Shared steps available everywhere
- Domain-specific steps co-located with scenarios
- Clean separation of concerns
