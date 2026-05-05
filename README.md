# Openshift Pipelines UI Automation Framework (opuiafw)

## Installation
- Clone this repository (if using virtualenvwrapper, be sure to clone from your virtual environment) using your local
user (do not clone using root):
```
git clone git@github.com:openshift-pipelines/release-ui-tests.git
```

### Dependencies Installation for Linux

#### Debian/Ubuntu

- Install required dependencies
```
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl \
    llvm libncursesw5-dev xz-utils tk-dev \
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
```
- Install pyenv and pyenv-virtualenv
```
curl https://pyenv.run | bash
```

- Add pyenv setup to your shell configuration file (e.g., ~/.bashrc or ~/.zshrc)
```
echo -e '\n# pyenv setup' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'eval "$(pyenv init --path)"\neval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
```
- Reload shell configuration
```
source ~/.bashrc
```

#### Fedora

- Install required dependencies
```
sudo dnf update -y
sudo dnf install @development-tools @c-development
sudo dnf install zlib-devel bzip2-devel openssl-devel ncurses-devel \
sqlite-devel readline-devel tk-devel gdbm-devel libpcap-devel \
xz-devel libffi-devel libuuid-devel
```
- Install pyenv and pyenv-virtualenv
```
curl https://pyenv.run | bash
```

- Add pyenv setup to your shell configuration file (e.g., ~/.bashrc or ~/.zshrc)
```
echo -e '\n# pyenv setup' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'eval "$(pyenv init --path)"\neval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
```
- Reload shell configuration
```
source ~/.bashrc
```

#### Mac OS
- Install pyenv and pyenv-virtualenv
```
brew install pyenv pyenv-virtualenv
```
- Add pyenv setup to your shell configuration file (e.g., ~/.bashrc or ~/.zshrc)
```
echo -e '\neval "$(pyenv init --path)"\neval "$(pyenv virtualenv-init -)"' >> ~/.zshrc
```
- Reload shell configuration
```
source ~/.zshrc
```
### Enter the project directory and install it using pip:

- Install Python version 3.13.6
```
pyenv install 3.13.6
```
- Navigate to the project directory
```
cd release-ui-tests
```
- Create virtual environment
```
pyenv virtualenv 3.13.6 .venv
```
- Set the local Python version to the newly created virtualenv
```
pyenv local .venv
```
- Install project dependencies
```
pip install -r requirements.txt
```

- Verify that the linter is functional:
```
pre-commit install
```
- To execute playwright based test, run the following setup:
```
### Linux/Mac OS
playwright install --with-deps

### Fedora
playwright install
```

## Configuration

Before running tests, you need to configure the framework with your OpenShift cluster details.

### Quick Setup (Local Development)

1. **Copy the configuration template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your cluster details:**
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
   pytest tests/features/task_crud_operations.feature
   ```

### Configuration Priority

The framework uses the **12-Factor App** methodology for configuration:

```
Environment Variables (CI) → .env file (local) → Defaults
     HIGHEST PRIORITY                              LOWEST
```

**For detailed configuration instructions**, including CI/CD setup, authentication methods, and troubleshooting, see:

📖 **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)**

## Executing tests

### Execution using pytest

**Basic execution:**
```bash
# Run single feature file
pytest tests/features/task_crud_operations.feature

# Run with specific marks
pytest -m "smoke"
pytest -m "smoke and sanity"

# Run in headed mode (visible browser)
pytest tests/features/task_crud_operations.feature --headed
```

**Advanced execution:**
```bash
# Run with specific markers
pytest -m "mark1 and mark2"

# Run with verbose output
pytest tests/features/ -v

# Run specific scenario by line number
pytest tests/features/task_crud_operations.feature::10
```


### Contribution guidelines ###

See ...WIP

### Who do I talk to? ###

* QE team members
