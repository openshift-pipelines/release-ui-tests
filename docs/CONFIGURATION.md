# Configuration Guide

This document describes how to configure the OpenShift UI Test Framework for both local development and CI/CD environments.

## Quick Start

### Local Development

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values:**
   ```bash
   # Required
   CONSOLE_URL=https://console-openshift-console.apps.your-cluster.com
   CONSOLE_USERNAME=kubeadmin
   CONSOLE_PASSWORD=your-password

   # Optional
   APP_TIMEOUT=90000
   ```

3. **Run tests:**
   ```bash
   pytest tests/features/your_test.feature
   ```

### CI/CD Pipeline

Set environment variables in your CI system (GitHub Actions, Jenkins, etc.):

```yaml
# GitHub Actions example
env:
  CONSOLE_URL: ${{ secrets.CONSOLE_URL }}
  CONSOLE_USERNAME: ${{ secrets.CONSOLE_USERNAME }}
  CONSOLE_PASSWORD: ${{ secrets.CONSOLE_PASSWORD }}
  OC_TOKEN: ${{ secrets.OC_TOKEN }}        # Optional
  OC_API_URL: ${{ secrets.OC_API_URL }}    # Optional
```

---

## Configuration Priority (12-Factor App Methodology)

The framework follows the [12-Factor App](https://12factor.net/config) principle for configuration:

```
Environment Variables (CI/CD) → .env file (local) → Defaults (code)
     HIGHEST PRIORITY                                 LOWEST PRIORITY
```

### How It Works

1. **Environment Variables** - Set by CI/CD system or `export` in shell
   - Takes precedence over everything
   - Used in CI/CD pipelines
   - Example: `export CONSOLE_URL=https://...`

2. **.env File** - Git-ignored file for local development
   - Only used if environment variable is NOT set
   - Developer-specific configuration
   - Never committed to git

3. **Defaults** - Hardcoded in `Config` class
   - Last resort fallback
   - Only for optional values (e.g., `APP_TIMEOUT=90000`)

### Implementation

```python
# framework/config/config.py
from dotenv import load_dotenv

# Load .env file (override=False means env vars take priority)
load_dotenv(dotenv_path=".env", override=False)

# Read from environment (could be from .env or actual env var)
CONSOLE_URL = os.getenv("CONSOLE_URL")  # Priority: env var → .env → None
```

---

## Configuration Variables

### Required Variables

| Variable | Description | Example | Used By |
|----------|-------------|---------|---------|
| `CONSOLE_URL` | OpenShift Console URL | `https://console-openshift-console.apps.example.com` | UI tests, CLI |
| `CONSOLE_USERNAME` | Login username | `kubeadmin` | UI tests, CLI fallback |
| `CONSOLE_PASSWORD` | Login password | `your-password` | UI tests, CLI fallback |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `APP_TIMEOUT` | Element wait timeout (ms) | `90000` | `120000` |
| `OC_TOKEN` | OpenShift CLI token | None | `sha256~abc123...` |
| `OC_API_URL` | OpenShift API URL | None | `https://api.example.com:6443` |

---

## Authentication Methods

### UI Browser Authentication

**Always uses:** `CONSOLE_USERNAME` + `CONSOLE_PASSWORD`

The framework logs into the OpenShift Console UI using the provided credentials.

### CLI Authentication (3 methods, in priority order)

#### Method 1: Token Authentication (Recommended for CI)

**Requires:** `OC_TOKEN` + `OC_API_URL`

```bash
# .env file
OC_TOKEN=sha256~your-token-here
OC_API_URL=https://api.example.com:6443
```

**How to get your token:**
1. Login to OpenShift Console
2. Click your name (top-right) → **Copy login command**
3. Copy token from: `oc login --token=sha256~... --server=https://...`

**Advantages:**
- No password exposure
- Works well in CI/CD
- Can be scoped with specific permissions

#### Method 2: Existing `oc login` Session

**Requires:** Nothing (uses current session)

```bash
# Run this once before tests
oc login https://api.example.com:6443 --username=kubeadmin
```

**Advantages:**
- Convenient for local development
- No need to set OC_TOKEN/OC_API_URL

#### Method 3: Username/Password Fallback

**Requires:** `CONSOLE_USERNAME` + `CONSOLE_PASSWORD`

If no token and no existing session, the framework automatically:
1. Derives API URL from `CONSOLE_URL`
2. Runs `oc login` with username/password

**Advantages:**
- Automatic fallback
- Same credentials as UI tests

---

## Local Development Setup

### Option A: Use .env File (Recommended)

```bash
# 1. Copy example
cp .env.example .env

# 2. Edit .env with your values
vim .env

# 3. Run tests (automatically picks up .env)
pytest tests/features/task_crud_operations.feature
```

### Option B: Use Environment Variables

```bash
# 1. Export variables in your shell
export CONSOLE_URL=https://console-openshift-console.apps.example.com
export CONSOLE_USERNAME=kubeadmin
export CONSOLE_PASSWORD=your-password

# 2. Run tests
pytest tests/features/task_crud_operations.feature
```

### Option C: Use Existing oc login Session

```bash
# 1. Login via oc CLI
oc login https://api.example.com:6443 --username=kubeadmin

# 2. Create .env with minimal config (no OC_TOKEN needed)
cat > .env <<EOF
CONSOLE_URL=https://console-openshift-console.apps.example.com
CONSOLE_USERNAME=kubeadmin
CONSOLE_PASSWORD=your-password
EOF

# 3. Run tests
pytest tests/features/task_crud_operations.feature
```

---

## CI/CD Setup

### GitHub Actions Example

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run UI Tests
        env:
          CONSOLE_URL: ${{ secrets.CONSOLE_URL }}
          CONSOLE_USERNAME: ${{ secrets.CONSOLE_USERNAME }}
          CONSOLE_PASSWORD: ${{ secrets.CONSOLE_PASSWORD }}
          OC_TOKEN: ${{ secrets.OC_TOKEN }}
          OC_API_URL: ${{ secrets.OC_API_URL }}
        run: pytest tests/features/ --headed
```

**Required GitHub Secrets:**
- `CONSOLE_URL`
- `CONSOLE_USERNAME`
- `CONSOLE_PASSWORD`
- `OC_TOKEN` (optional)
- `OC_API_URL` (optional)

### Jenkins Example

```groovy
pipeline {
    agent any

    environment {
        CONSOLE_URL = credentials('openshift-console-url')
        CONSOLE_USERNAME = credentials('openshift-username')
        CONSOLE_PASSWORD = credentials('openshift-password')
        OC_TOKEN = credentials('openshift-token')
        OC_API_URL = credentials('openshift-api-url')
    }

    stages {
        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest tests/features/ --headed'
            }
        }
    }
}
```

---

## Troubleshooting

### Issue: "Missing required environment variables: CONSOLE_URL"

**Cause:** Neither environment variable nor .env file has `CONSOLE_URL` set.

**Solution:**
```bash
# Option 1: Create .env file
cp .env.example .env
# Edit .env and set CONSOLE_URL

# Option 2: Export environment variable
export CONSOLE_URL=https://console-openshift-console.apps.example.com
```

### Issue: CLI tests fail with "Login with token failed"

**Cause:** `OC_TOKEN` or `OC_API_URL` is incorrect or expired.

**Solution:**
```bash
# Get fresh token from OpenShift Console
# 1. Login to console
# 2. Click your name → Copy login command
# 3. Update OC_TOKEN in .env or environment variable

# Or, remove OC_TOKEN and use username/password instead
unset OC_TOKEN
unset OC_API_URL
```

### Issue: Environment variable not taking precedence

**Cause:** `.env` file has `override=True` (incorrect).

**Verify:**
```python
# framework/config/config.py should have:
load_dotenv(dotenv_path=dotenv_path, override=False)  # ✓ Correct

# NOT:
load_dotenv(dotenv_path=dotenv_path, override=True)  # ✗ Wrong
```

### Issue: Different values in different test modules

**Cause:** Config is a singleton - once initialized, values don't change.

**Understanding:**
- `Config()` is initialized once per test session
- Values are read at initialization time
- Changing environment variables mid-session won't affect Config

**Solution:** Set all variables before running pytest.

---

## Best Practices

### 1. Never Commit Secrets

```bash
# ✓ Good: .env is in .gitignore
echo ".env" >> .gitignore

# ✗ Bad: Never do this
git add .env  # NEVER!
```

### 2. Use Token Authentication in CI

```yaml
# ✓ Good: Token-based (no password exposure)
env:
  OC_TOKEN: ${{ secrets.OC_TOKEN }}
  OC_API_URL: ${{ secrets.OC_API_URL }}

# ✗ Acceptable but less secure: Username/password
env:
  CONSOLE_USERNAME: ${{ secrets.CONSOLE_USERNAME }}
  CONSOLE_PASSWORD: ${{ secrets.CONSOLE_PASSWORD }}
```

### 3. Document Environment Variables

```bash
# ✓ Good: .env.example shows all available variables
cat .env.example

# ✓ Good: README references this doc
See docs/CONFIGURATION.md for setup
```

### 4. Use Config Class, Not Direct os.getenv()

```python
# ✓ Good: Use Config singleton
from framework.config.config import Config

config = Config()
url = config.base_url

# ✗ Bad: Direct os.getenv() bypasses priority logic
import os

url = os.getenv("CONSOLE_URL")  # Might miss .env file
```

**Exception:** CLI-specific variables (`OC_TOKEN`, `OC_API_URL`) use `os.getenv()` after `.env` is loaded.

---

## File Reference

| File | Purpose | Git Status |
|------|---------|------------|
| `.env.example` | Template with all variables | ✓ Committed |
| `.env` | Actual values (developer-specific) | ✗ Git-ignored |
| `framework/config/config.py` | Config singleton class | ✓ Committed |
| `framework/fixtures/cli_fixtures.py` | Loads .env for CLI | ✓ Committed |
| `docs/CONFIGURATION.md` | This document | ✓ Committed |

---

## Summary

**Local Development:**
1. Copy `.env.example` → `.env`
2. Fill in your values
3. Run tests

**CI/CD:**
1. Set environment variables in CI system
2. Variables override any .env file
3. Run tests

**Priority:** Environment Variable → .env file → Defaults

**Authentication:**
- UI: Always uses `CONSOLE_USERNAME` + `CONSOLE_PASSWORD`
- CLI: Token (if set) → Existing session → Username/Password fallback
