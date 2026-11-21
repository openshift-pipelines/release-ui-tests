# Testing

## Triggering Tests

Invoke the skill with various failing test scenarios:

```bash
# Test with known locator issue
/bdd-test-code-healer broken_locators.feature

# Test with multiple failures
/bdd-test-code-healer file1.feature,file2.feature,file3.feature

# Test iterative repair (should need 2-3 attempts)
/bdd-test-code-healer complex_failure.feature
```

## Functional Tests

Verify the skill works correctly:

1. **Phase 1 stops and waits** for approval before applying any fixes
2. **Analysis is accurate** - Correctly identifies root cause
3. **Proposed fix is appropriate** - Addresses the actual issue
4. **Fix is applied correctly** - Code changes match proposal
5. **Verification runs** - Tests re-execute after fix
6. **Iterative repair works** - Loops up to 3 times if needed
7. **Success detection** - Stops when tests pass

## Expected Behavior

- **All tests pass initially** → Skill reports success, no healing needed
- **1 test fails** → Analysis report, wait for approval, fix, verify
- **Multiple tests fail** → Process each independently
- **Fix works on attempt 1** → Success, stop
- **Fix works on attempt 2-3** → Success, stop, report attempts needed
- **Still failing after attempt 3** → Report failure, recommend manual investigation
