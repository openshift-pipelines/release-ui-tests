# Error Handling

## Cannot Run Tests

**Error**: pytest command fails, can't execute tests
**Solution**: Check pytest installation, verify feature file exists, ensure step definitions are importable

## Analysis Fails

**Error**: Can't parse test output or identify failure pattern
**Solution**: Skill reports raw output for manual review, suggests running with `-vv` flag

## Fix Application Fails

**Error**: Edit tool fails, file not found, syntax error in fix
**Solution**: Skill reports the error, suggests manual fix, shows what it tried to change

## Verification Fails (Different Error)

**Error**: After applying fix, test fails with NEW error
**Solution**: Skill analyzes new error, proposes different fix (counts as next attempt)

## Max Attempts Reached

**Error**: Tests still fail after 3 fix attempts
**Solution**:
- Report all fixes tried
- Show final error message
- Recommend manual investigation
- Suggest possible next steps
