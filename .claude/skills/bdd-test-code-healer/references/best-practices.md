# Best Practices

## 1. Run Tests First

Before using this skill, run tests manually to confirm they fail:
```bash
pytest tests/features/task_crud.feature -v
```

## 2. Review Proposed Fixes

Don't blindly approve. Check:
- Does the root cause make sense?
- Is the proposed fix appropriate?
- Are there side effects to consider?

## 3. One Feature at a Time Initially

When learning the skill, run on single features first:
```bash
/bdd-test-code-healer task_crud.feature
```

## 4. Check Git Diff After Fixes

After skill applies fixes, review changes:
```bash
git diff
```

## 5. Commit Successful Fixes

If tests pass after healing, commit the fixes:
```bash
git add .
git commit -m "Fix: Healed test failures in task_crud_operations

- Updated CREATE_BUTTON locator to use data-test attribute
- Increased wait time for task list data load
- Applied via /bdd-test-code-healer"
```
