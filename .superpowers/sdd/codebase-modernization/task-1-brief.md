# Task 1: Update pyproject.toml and Setup Configuration

**Files:**
- Modify: `pyproject.toml`
- Modify: `setup.py`
- Modify: `aiopulse/__init__.py`
- Create: `aiopulse/py.typed`

**Interfaces:**
- Produces: Updated version (0.5.0), dev dependencies, tool configurations

- [ ] **Step 1: Update pyproject.toml with dev dependencies and tool configs**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aiopulse"
version = "0.5.0"
authors = [
  { name="Alan Murray", email="pypi@atmurray.net" },
]
description = """
Asynchronous library to control Rollease Acmeda Automate roller blinds via a version 1 Pulse Hub.
"""
readme = "README.md"
license = {file = 'LICENSE'}
requires-python = ">=3.10"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.4",
    "black>=24.0",
    "build>=1.0",
]

[project.urls]
Homepage = "https://github.com/atmurray/aiopulse"
Issues = "https://github.com/atmurray/aiopulse/issues"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
target-version = "py310"
line-length = 88
select = ["E", "F", "I", "N", "W", "UP"]

[tool.bumpver]
current_version = "0.5.0"
version_pattern = "MAJOR.MINOR.PATCH"
commit_message  = "Bump version {old_version} -> {new_version}"
commit          = true
tag             = true
push            = false

[tool.bumpver.file_patterns]
"pyproject.toml" = [
    'current_version = "{version}"',
    'version = "{version}"',
]
"setup.py" = [
    "{version}"
]
```

- [ ] **Step 2: Update setup.py version**

```python
"""Pip setup file for aiopulse library."""

from setuptools import setup

setup(
    name="aiopulse",
    packages=["aiopulse"],
    version="0.5.0",
    license="apache-2.0",
    description="Python module for Rollease Acmeda Automate integration.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alan Murray",
    author_email="pypi@atmurray.net",
    url="https://github.com/atmurray/aiopulse",
    download_url="https://github.com/atmurray/aiopulse/archive/v0.5.0.tar.gz",
    keywords=["automation"],
    python_requires=">=3.10",
    install_requires=["async_timeout"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
```

- [ ] **Step 3: Update aiopulse/__init__.py version**

```python
"""Rollease Acmeda Automate Pulse asyncio protocol implementation."""
import logging

from aiopulse.hub import Hub
from aiopulse.roller import Roller
from aiopulse.room import Room
from aiopulse.scene import Scene
from aiopulse.timer import Timer
from aiopulse.errors import (
    CannotConnectException,
    NotConnectedException,
    NotRunningException,
    InvalidResponseException,
)
from aiopulse.const import UpdateType

__all__ = [
    "Hub",
    "Roller",
    "Room",
    "Scene",
    "Timer",
    "CannotConnectException",
    "NotConnectedException",
    "NotRunningException",
    "InvalidResponseException",
    "UpdateType",
]
__version__ = "0.5.0"
__author__ = "Alan Murray"

_LOGGER = logging.getLogger(__name__)
```

- [ ] **Step 4: Create py.typed marker file**

Create empty file `aiopulse/py.typed` (no content needed).

- [ ] **Step 5: Run tests to verify nothing broke**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml setup.py aiopulse/__init__.py aiopulse/py.typed
git commit -m "chore: update version to 0.5.0 and add dev dependencies"
```
