# Task 12: Update CI/CD Workflows

**Files:**
- Modify: `.github/workflows/python-app.yml`
- Create: `.github/workflows/python-release.yml`
- Modify: `.pre-commit-config.yaml`

**Interfaces:**
- Produces: Updated CI/CD with testing and release automation

- [ ] **Step 1: Update python-app.yml**

```yaml
name: Python application

on:
  push:
    branches: ["master"]
  pull_request:
    branches: ["master"]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Lint with ruff
      run: ruff check .
    - name: Type check with mypy
      run: mypy aiopulse
    - name: Test with pytest
      run: pytest --cov=aiopulse --cov-report=xml
    - name: Build package
      run: python -m build
```

- [ ] **Step 2: Create python-release.yml**

```yaml
name: Release to PyPI

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write
  id-token: write

jobs:
  release:
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/aiopulse

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.10
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    - name: Run tests
      run: pytest
    - name: Build package
      run: python -m build
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        generate_release_notes: true
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 3: Update .pre-commit-config.yaml**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        args:
          - --safe
          - --quiet
        files: ^((aiopulse)/.+)?[^/]+\.py$
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args:
          - --fix
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        files: ^aiopulse/.+\.py$
  - repo: https://github.com/codespell-project/codespell
    rev: v2.2.6
    hooks:
      - id: codespell
        args:
          - --ignore-words-list=aiopulse,acmeda
          - --skip="./.*,*.json"
          - --quiet-level=2
        exclude_types: [json]
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/python-app.yml .github/workflows/python-release.yml .pre-commit-config.yaml
git commit -m "ci: update workflows with testing and release automation"
```
