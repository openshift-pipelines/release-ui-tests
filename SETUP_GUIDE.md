# Setup Guide - Environment Configuration & CLI Integration

This guide covers secure credential storage and automatic test project isolation using OpenShift CLI.

---

## 1. Secure Credential Storage

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your credentials**:
   ```bash
   # .env - DO NOT COMMIT THIS FILE
   CONSOLE_URL=https://console-openshift-console.apps.aws-421-arm-5node-rn7c7.aws.ospqa.com
   CONSOLE_USERNAME=kubeadmin
   CONSOLE_PASSWORD=your-actual-password
   OC_TOKEN=sha256~your-actual-token
   OC_API_URL=https://api.aws-421-arm-5node-rn7c7.aws.ospqa.com:6443
   APP_TIMEOUT=90000
   ```

4. **Verify `.env` is in `.gitignore`** (already configured):
   ```bash
   grep -E "^\.env$" .gitignore  # Should return: .env
   ```

5. **Run tests**:
   ```bash
   pytest -m smoke -v
   ```

### How It Works

**Priority Order** (Config class):
1. **Environment variables** (highest priority)
2. **`.env` file** (loaded automatically if exists)
3. **Defaults** (lowest priority)

**Example**:
```bash
# Override .env for single test run
CONSOLE_URL=https://staging-console.example.com pytest tests/

# .env values used for all other vars
```

### Security Best Practices

✅ **DO**:
- Keep `.env` file local only (never commit)
- Use `.env.example` as template (safe to commit)
- Use different `.env` files for different environments:
  ```bash
  .env              # Default (your primary cluster)
  .env.staging      # Staging cluster
  .env.production   # Production cluster (for smoke tests only!)
  ```
- Load specific env file:
  ```bash
  set -a; source .env.staging; set +a
  pytest -m smoke
  ```

❌ **DON'T**:
- Commit `.env` to git
- Share `.env` file via email/chat
- Store `.env` in cloud drives (Dropbox, Google Drive, etc.)
- Use production credentials for full test suites

### Getting Your OC Token

```bash
# Method 1: From existing session
oc whoami -t

# Method 2: Login and extract
oc login https://api.cluster.example.com:6443
oc whoami -t

# Method 3: From web console
# OpenShift Console → Click your name (top right) → Copy login command → Extract token
```

---

## 2. Automatic Test Project Isolation

### How It Works

**Every feature file** runs in an isolated OpenShift project:

```
Feature: pipeline_navigation_pipelines_and_sub_pages.feature
  → Creates project: release-ui-test-a7k2m
  → Runs all scenarios in this project
  → Deletes project if all tests passed
  → Keeps project if any test failed (for debugging)
```

### Architecture

```
framework/cli/
├── __init__.py
└── openshift_cli.py              # OpenShift CLI wrapper

framework/fixtures/
├── cli_fixtures.py               # test_project fixture (module-scoped)
└── ui_fixtures.py                # Re-exports CLI fixtures

tests/conftest.py                 # Imports ui_fixtures (gets CLI fixtures)

Feature File Test Flow:
  1. pytest loads feature file (module scope)
  2. test_project fixture triggers (before first scenario)
  3. Creates project: release-ui-test-{5_random_chars}
  4. Switches to new project context
  5. All scenarios run in this isolated project
  6. After last scenario completes:
     - If all passed → delete project
     - If any failed → keep project for debugging
```

### Using test_project Fixture

**Option 1 - Automatic (recommended)**:

Just ensure you're importing fixtures:
```python
# tests/conftest.py
from framework.fixtures.ui_fixtures import *  # Includes CLI fixtures
```

The `test_project` fixture is **module-scoped**, so it automatically:
- Creates project before first scenario in feature file
- Deletes project after last scenario (if all passed)

**Option 2 - Explicit usage in BDD steps**:

If you need the project name in your steps:

```python
# tests/steps/test_pipeline_steps.py
from pytest_bdd import given


@given("a test pipeline exists in the project")
def create_test_pipeline(test_project: str, openshift_cli):
    # test_project = "release-ui-test-a7k2m" (automatically created)
    # Create test data in this project
    pass
```

### Manual Project Management

**List test projects**:
```bash
oc get projects | grep release-ui-test
```

**Delete leftover projects** (from failed tests):
```bash
# Delete all test projects
oc get projects -o name | grep release-ui-test | xargs oc delete

# Delete specific project
oc delete project release-ui-test-a7k2m
```

**Inspect failed test project**:
```bash
# When tests fail, project is kept for debugging
oc project release-ui-test-a7k2m
oc get all
oc get tasks,pipelines,pipelineruns
```

### CLI Authentication

**The test_project fixture automatically handles authentication** using:

**Method 1 - Use existing `oc login` session** (recommended for local dev):
```bash
# Login once
oc login https://api.cluster.example.com:6443 --username=kubeadmin

# Run tests (uses existing session)
pytest -m smoke
```

**Method 2 - Use token from `.env`** (recommended for CI/CD):
```env
# .env
OC_TOKEN=sha256~your-token-here
OC_API_URL=https://api.cluster.example.com:6443
```

**Priority**:
1. Check if already logged in (`oc whoami`)
2. If not, try to login with OC_TOKEN from env
3. If neither, raise error with instructions

### Troubleshooting

**Error: "Not logged into OpenShift cluster"**

**Solution**:
```bash
# Option A: Login via CLI
oc login https://api.cluster.example.com:6443

# Option B: Set token in .env
echo "OC_TOKEN=$(oc whoami -t)" >> .env
echo "OC_API_URL=https://api.cluster.example.com:6443" >> .env
```

**Error: "Failed to create project release-ui-test-xxxxx"**

**Possible causes**:
- Insufficient permissions (need project creation rights)
- Cluster quota exceeded
- Project name conflict (very rare - uses random suffix)

**Solution**:
```bash
# Check permissions
oc policy who-can create projects

# Check quotas
oc describe quota

# Manual test
oc new-project release-ui-test-manual
```

**Projects not being deleted after tests**

**This is expected** when tests fail - projects are kept for debugging.

**Manual cleanup**:
```bash
oc get projects | grep release-ui-test | awk '{print $1}' | xargs -I {} oc delete project {}
```

---

## 3. Dependencies

### Required System Tools

**OpenShift CLI (`oc`)**:

```bash
# Check if installed
oc version

# Install (Linux)
curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz
tar -xzf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/

# Install (macOS)
brew install openshift-cli

# Verify
oc version --client
```

**Python Dependencies**:

All Python dependencies are in `requirements.txt`:
- `python-dotenv==1.0.1` - Load `.env` files
- All other existing dependencies

No additional libraries needed for CLI integration (uses standard `asyncio.subprocess`).

---

## 4. CI/CD Integration

### GitHub Actions Example

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps chromium

      - name: Install OpenShift CLI
        run: |
          curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz
          tar -xzf openshift-client-linux.tar.gz
          sudo mv oc /usr/local/bin/

      - name: Run smoke tests
        env:
          CONSOLE_URL: ${{ secrets.CONSOLE_URL }}
          CONSOLE_USERNAME: ${{ secrets.CONSOLE_USERNAME }}
          CONSOLE_PASSWORD: ${{ secrets.CONSOLE_PASSWORD }}
          OC_TOKEN: ${{ secrets.OC_TOKEN }}
          OC_API_URL: ${{ secrets.OC_API_URL }}
        run: |
          pytest -m smoke -v --tb=short
```

**GitHub Secrets to configure**:
- `CONSOLE_URL`
- `CONSOLE_USERNAME`
- `CONSOLE_PASSWORD`
- `OC_TOKEN`
- `OC_API_URL`

---

## 5. Quick Reference

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `CONSOLE_URL` | Yes | OpenShift Console URL | `https://console-openshift-console.apps...` |
| `CONSOLE_USERNAME` | Yes | Console login username | `kubeadmin` |
| `CONSOLE_PASSWORD` | Yes | Console login password | `your-password` |
| `OC_TOKEN` | Optional* | OpenShift CLI token | `sha256~abc123...` |
| `OC_API_URL` | Optional* | OpenShift API URL | `https://api.cluster.example.com:6443` |
| `APP_TIMEOUT` | No | UI timeout (ms) | `90000` (default) |

\* Optional if already logged in via `oc login`

### Common Commands

```bash
# Setup
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
playwright install chromium

# Run tests
pytest -m smoke -v

# Run with different env
set -a; source .env.staging; set +a
pytest -m smoke -v

# Cleanup test projects
oc get projects | grep release-ui-test | awk '{print $1}' | xargs -I {} oc delete project {}

# Check CLI status
oc whoami
oc project
```

---

## 6. Next Steps

1. ✅ Setup `.env` file with your credentials
2. ✅ Install `oc` CLI tool
3. ✅ Login to cluster: `oc login`
4. ✅ Run tests: `pytest -m smoke -v`
5. 🔜 Ready to generate tests with `test-from-intent` skill!

---

## Security Notes

- `.env` is in `.gitignore` - your credentials are safe
- CLI tokens expire - refresh periodically
- Never use production clusters for full test suites
- Test projects are isolated - safe for parallel test runs
- Failed test projects persist for debugging - cleanup manually

**Need help?** Check the main [README.md](README.md) for framework documentation.
