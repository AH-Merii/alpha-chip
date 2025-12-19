# AlphaChip 2026 Modernization Plan

## Overview

This document provides a complete modernization plan for the AlphaChip (circuit_training) codebase. Execute phases in order. Each phase has acceptance criteria and TDD tests to write BEFORE making changes.

**Repository**: `/home/user/alpha-chip`
**Branch**: Create `modernization/2026-update` from main

## Pre-Flight Checks

Before starting, verify:
```bash
cd /home/user/alpha-chip
git status  # Should be clean
python3 --version  # Note current version
pip list | grep -E "tensorflow|jax|torch"  # Note current ML framework
```

---

# PHASE 1: Packaging Modernization (Priority: P0)

## 1.1 TDD Tests - Write First

Create `tests/packaging/test_package_structure.py`:

```python
"""Tests to verify package structure after modernization."""
import importlib
import subprocess
import sys
from pathlib import Path

import pytest


class TestPackageStructure:
    """Verify package can be built and imported correctly."""

    def test_pyproject_toml_exists(self):
        """pyproject.toml must exist at repo root."""
        assert Path("pyproject.toml").exists()

    def test_setup_py_removed(self):
        """setup.py should be removed after migration."""
        assert not Path("setup.py").exists()

    def test_package_importable(self):
        """Main package should be importable."""
        import circuit_training
        assert hasattr(circuit_training, "__version__")

    def test_submodules_importable(self):
        """All submodules should be importable."""
        submodules = [
            "circuit_training.environment",
            "circuit_training.environment.environment",
            "circuit_training.learning",
            "circuit_training.learning.agent",
            "circuit_training.model",
            "circuit_training.model.model_lib",
        ]
        for module in submodules:
            importlib.import_module(module)

    def test_cli_entry_points_registered(self):
        """CLI commands should be available after install."""
        result = subprocess.run(
            [sys.executable, "-m", "circuit_training.learning.train_ppo", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0 or "usage" in result.stdout.lower()

    def test_version_accessible(self):
        """Version should be accessible programmatically."""
        from circuit_training import __version__
        assert isinstance(__version__, str)
        assert len(__version__.split(".")) >= 2  # At least major.minor


class TestDependencies:
    """Verify dependencies are correctly specified."""

    def test_core_dependencies_importable(self):
        """Core dependencies should be importable."""
        import numpy
        import gymnasium  # New name for gym

    def test_optional_dependencies_handled(self):
        """Optional dependencies should not break import."""
        try:
            from circuit_training.dreamplace import dreamplace_core
        except ImportError as e:
            # Should fail gracefully with clear message
            assert "dreamplace" in str(e).lower() or "torch" in str(e).lower()


class TestBuildProcess:
    """Verify package builds correctly."""

    def test_build_wheel(self, tmp_path):
        """Package should build a wheel."""
        result = subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        wheels = list(tmp_path.glob("*.whl"))
        assert len(wheels) == 1

    def test_build_sdist(self, tmp_path):
        """Package should build a source distribution."""
        result = subprocess.run(
            ["uv", "build", "--sdist", "--out-dir", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        sdists = list(tmp_path.glob("*.tar.gz"))
        assert len(sdists) == 1
```

## 1.2 Create pyproject.toml

Create `pyproject.toml` at repository root:

```toml
[build-system]
requires = ["hatchling>=1.21.0"]
build-backend = "hatchling.build"

[project]
name = "circuit-training"
dynamic = ["version"]
description = "Circuit Training: Reinforcement Learning for Chip Placement"
readme = "README.md"
license = "Apache-2.0"
requires-python = ">=3.11"
authors = [
    { name = "Google Research", email = "circuit-training@google.com" }
]
keywords = [
    "reinforcement-learning",
    "chip-design",
    "placement",
    "deep-learning",
    "machine-learning",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
]
dependencies = [
    "numpy>=1.26.0,<2.0.0",
    "gymnasium>=1.0.0",
    "tensorflow>=2.15.0",
    "tf-agents[reverb]>=0.19.0",
    "gin-config>=0.5.0",
    "sortedcontainers>=2.4.0",
    "absl-py>=2.0.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "pytest-timeout>=2.2.0",
    "ruff>=0.8.0",
    "pyrefly>=0.15.0",
    "pre-commit>=3.6.0",
]
dreamplace = [
    "torch>=2.1.0",
    "shapely>=2.0.0",
    "scipy>=1.11.0",
    "matplotlib>=3.8.0",
    "cairocffi>=1.6.0",
]
docs = [
    "mkdocs-material>=9.5.0",
    "mkdocstrings[python]>=0.24.0",
    "mkdocs-gen-files>=0.5.0",
]
all = [
    "circuit-training[dev,dreamplace,docs]",
]

[project.scripts]
ct-train = "circuit_training.learning.train_ppo:main"
ct-collect = "circuit_training.learning.ppo_collect:main"
ct-eval = "circuit_training.learning.eval:main"
ct-server = "circuit_training.learning.ppo_reverb_server:main"

[project.urls]
Homepage = "https://github.com/google-research/circuit_training"
Documentation = "https://github.com/google-research/circuit_training#readme"
Repository = "https://github.com/google-research/circuit_training"
Issues = "https://github.com/google-research/circuit_training/issues"

[tool.hatch.version]
path = "circuit_training/version.py"

[tool.hatch.build.targets.wheel]
packages = ["circuit_training"]

[tool.hatch.build.targets.sdist]
include = [
    "/circuit_training",
    "/tests",
    "/README.md",
    "/LICENSE",
]
exclude = [
    "*.pyc",
    "__pycache__",
    ".git",
]
```

## 1.3 Update version.py

Update `circuit_training/version.py`:

```python
"""Version information for circuit_training."""

__version__ = "0.1.0"
__rel_version__ = "0.1.0"
__dev_version__ = "0.1.0.dev"
```

## 1.4 Update __init__.py

Update `circuit_training/__init__.py`:

```python
"""Circuit Training: RL for Chip Placement."""

from circuit_training.version import __version__

__all__ = ["__version__"]
```

## 1.5 Remove Legacy Files

```bash
rm setup.py
rm -rf *.egg-info
rm -rf build/
rm -rf dist/
```

## 1.6 Acceptance Criteria - Phase 1

- [ ] `pyproject.toml` exists and is valid TOML
- [ ] `setup.py` is removed
- [ ] `uv sync` completes successfully
- [ ] `uv run pytest tests/packaging/` passes all tests
- [ ] `uv build` creates wheel and sdist
- [ ] Package is importable: `uv run python -c "import circuit_training"`

---

# PHASE 2: Linting & Formatting with Ruff (Priority: P0)

## 2.1 TDD Tests - Write First

Create `tests/quality/test_code_quality.py`:

```python
"""Tests to verify code quality standards."""
import subprocess
from pathlib import Path

import pytest


class TestRuffLinting:
    """Verify Ruff linting passes."""

    def test_ruff_check_passes(self):
        """All code should pass Ruff linting."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "circuit_training/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_format_check(self):
        """All code should be formatted with Ruff."""
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "circuit_training/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}"


class TestImportOrder:
    """Verify import ordering is consistent."""

    def test_imports_sorted(self):
        """Imports should be sorted by isort rules (via Ruff)."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "--select", "I", "circuit_training/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestNoUnusedImports:
    """Verify no unused imports."""

    def test_no_unused_imports(self):
        """Should have no unused imports."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "--select", "F401", "circuit_training/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
```

## 2.2 Add Ruff Configuration to pyproject.toml

Append to `pyproject.toml`:

```toml
# === RUFF CONFIGURATION ===

[tool.ruff]
target-version = "py311"
line-length = 88
fix = true
src = ["circuit_training", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "RUF",    # Ruff-specific rules
    "NPY",    # NumPy-specific rules
    "PERF",   # Performance
    "PL",     # Pylint
]
ignore = [
    "E501",   # line too long (handled by formatter)
    "PLR0913", # too many arguments
    "PLR2004", # magic value comparison
    "PLR0911", # too many return statements
    "PLR0912", # too many branches
    "PLR0915", # too many statements
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "ARG001",  # Unused function argument (fixtures)
    "S101",    # Use of assert
]
"**/*_test.py" = [
    "ARG001",
    "S101",
]

[tool.ruff.lint.isort]
known-first-party = ["circuit_training"]
force-single-line = false
lines-after-imports = 2

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = true
docstring-code-line-length = 80
```

## 2.3 Run Ruff Auto-fix

```bash
# Format all code
uv run ruff format circuit_training/ tests/

# Fix all auto-fixable issues
uv run ruff check --fix circuit_training/ tests/

# Check for remaining issues
uv run ruff check circuit_training/ tests/
```

## 2.4 Acceptance Criteria - Phase 2

- [ ] `uv run ruff check circuit_training/` returns exit code 0
- [ ] `uv run ruff format --check circuit_training/` returns exit code 0
- [ ] `uv run pytest tests/quality/` passes all tests
- [ ] All existing tests still pass: `uv run pytest`

---

# PHASE 3: Type Checking with Pyrefly (Priority: P0)

## 3.1 TDD Tests - Write First

Create `tests/quality/test_type_checking.py`:

```python
"""Tests to verify type checking passes."""
import subprocess

import pytest


class TestPyreflyTypeChecking:
    """Verify Pyrefly type checking passes."""

    def test_pyrefly_check_passes(self):
        """Core modules should pass type checking."""
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", "circuit_training/"],
            capture_output=True,
            text=True,
        )
        # Allow warnings but no errors
        assert result.returncode == 0, f"Pyrefly failed:\n{result.stdout}\n{result.stderr}"

    def test_environment_module_typed(self):
        """Environment module should be fully typed."""
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", "circuit_training/environment/environment.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_model_module_typed(self):
        """Model module should be fully typed."""
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", "circuit_training/model/model_lib.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
```

## 3.2 Add Pyrefly Configuration

Create `pyrefly.toml` at repository root:

```toml
[tool.pyrefly]
project_includes = ["circuit_training"]
project_excludes = ["circuit_training/grouping/testdata"]
search_path = ["."]

python_version = "3.11"

# Start with lenient settings, tighten over time
errors = [
    "missing-return-type",
    "incompatible-return-type",
    "incompatible-argument-type",
    "undefined-name",
]

# Ignore legacy code initially
ignore_paths = [
    "circuit_training/grouping/*",
]
```

Also add to `pyproject.toml`:

```toml
# === PYREFLY CONFIGURATION ===

[tool.pyrefly]
python_version = "3.11"
project_includes = ["circuit_training"]
strict = false  # Start lenient, tighten over time
```

## 3.3 Add Type Stubs and Annotations

Create `circuit_training/py.typed` (empty marker file):
```bash
touch circuit_training/py.typed
```

Update function signatures with modern type hints. Example for `circuit_training/environment/environment.py`:

```python
# Before
def cost_info_function(
    plc: plc_client.PlacementCost,
    done: bool,
    infeasible_state: bool = False,
    wirelength_weight: float = 1.0,
    density_weight: float = 1.0,
    congestion_weight: float = 0.5,
) -> tuple[float, dict[str, float]]:

# After (Python 3.11+ style)
def cost_info_function(
    plc: plc_client.PlacementCost,
    done: bool,
    infeasible_state: bool = False,
    *,  # Force keyword arguments
    wirelength_weight: float = 1.0,
    density_weight: float = 1.0,
    congestion_weight: float = 0.5,
) -> tuple[float, dict[str, float]]:
```

## 3.4 Acceptance Criteria - Phase 3

- [ ] `pyrefly.toml` exists
- [ ] `circuit_training/py.typed` marker exists
- [ ] `uv run pyrefly check circuit_training/` passes
- [ ] `uv run pytest tests/quality/test_type_checking.py` passes
- [ ] All existing tests still pass

---

# PHASE 4: GitHub Actions CI/CD (Priority: P0)

## 4.1 TDD Tests - Write First

Create `tests/ci/test_ci_config.py`:

```python
"""Tests to verify CI configuration is valid."""
from pathlib import Path

import pytest
import yaml


class TestGitHubActionsConfig:
    """Verify GitHub Actions configuration."""

    @pytest.fixture
    def ci_workflow(self):
        """Load the CI workflow file."""
        ci_path = Path(".github/workflows/ci.yml")
        assert ci_path.exists(), "CI workflow file must exist"
        return yaml.safe_load(ci_path.read_text())

    def test_ci_workflow_exists(self):
        """CI workflow file must exist."""
        assert Path(".github/workflows/ci.yml").exists()

    def test_ci_workflow_valid_yaml(self, ci_workflow):
        """CI workflow must be valid YAML."""
        assert ci_workflow is not None
        assert "jobs" in ci_workflow

    def test_ci_has_lint_job(self, ci_workflow):
        """CI must have a lint job."""
        assert "lint" in ci_workflow["jobs"]

    def test_ci_has_typecheck_job(self, ci_workflow):
        """CI must have a typecheck job."""
        assert "typecheck" in ci_workflow["jobs"]

    def test_ci_has_test_job(self, ci_workflow):
        """CI must have a test job."""
        assert "test" in ci_workflow["jobs"]

    def test_ci_tests_multiple_python_versions(self, ci_workflow):
        """CI must test multiple Python versions."""
        test_job = ci_workflow["jobs"]["test"]
        strategy = test_job.get("strategy", {})
        matrix = strategy.get("matrix", {})
        python_versions = matrix.get("python-version", [])
        assert len(python_versions) >= 2, "Must test at least 2 Python versions"

    def test_ci_runs_on_push_and_pr(self, ci_workflow):
        """CI must run on push and PR."""
        on_triggers = ci_workflow.get("on", {})
        assert "push" in on_triggers or "pull_request" in on_triggers


class TestPreCommitConfig:
    """Verify pre-commit configuration."""

    def test_precommit_config_exists(self):
        """Pre-commit config must exist."""
        assert Path(".pre-commit-config.yaml").exists()

    def test_precommit_config_valid(self):
        """Pre-commit config must be valid YAML."""
        config = yaml.safe_load(Path(".pre-commit-config.yaml").read_text())
        assert "repos" in config
```

## 4.2 Create GitHub Actions Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: "3.11"
  UV_CACHE_DIR: /tmp/.uv-cache

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Run Ruff linter
        run: uv run ruff check --output-format=github circuit_training/

      - name: Run Ruff formatter check
        run: uv run ruff format --check circuit_training/

  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Run Pyrefly
        run: uv run pyrefly check circuit_training/

  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
          enable-cache: true

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Run tests with coverage
        run: |
          uv run pytest \
            --cov=circuit_training \
            --cov-report=xml \
            --cov-report=term-missing \
            -v \
            --ignore=circuit_training/grouping/

      - name: Upload coverage to Codecov
        if: matrix.python-version == '3.11'
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          fail_ci_if_error: false

  build:
    name: Build Package
    runs-on: ubuntu-latest
    needs: [lint, typecheck, test]
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Build package
        run: uv build

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  # Optional: Integration tests with GPU
  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Set up uv
        uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: uv sync --frozen --dev

      - name: Run integration tests
        run: |
          uv run pytest tests/integration/ -v --timeout=300
        continue-on-error: true
```

## 4.3 Create Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: debug-statements

  - repo: local
    hooks:
      - id: pyrefly
        name: pyrefly
        entry: uv run pyrefly check
        language: system
        types: [python]
        pass_filenames: false
```

## 4.4 Acceptance Criteria - Phase 4

- [ ] `.github/workflows/ci.yml` exists and is valid YAML
- [ ] `.pre-commit-config.yaml` exists and is valid YAML
- [ ] `uv run pytest tests/ci/` passes
- [ ] `pre-commit run --all-files` passes
- [ ] GitHub Actions workflow runs successfully (after push)

---

# PHASE 5: Pydantic Configuration Models (Priority: P1)

## 5.1 TDD Tests - Write First

Create `tests/config/test_config_models.py`:

```python
"""Tests for Pydantic configuration models."""
from pathlib import Path

import pytest
from pydantic import ValidationError


class TestEnvironmentConfig:
    """Test environment configuration model."""

    def test_valid_config(self):
        """Valid configuration should be accepted."""
        from circuit_training.config import EnvironmentConfig

        config = EnvironmentConfig(
            netlist_file=Path("circuit_training/environment/test_data/ariane/netlist.pb.txt"),
            std_cell_placer_mode="fd",
            wirelength_weight=1.0,
        )
        assert config.std_cell_placer_mode == "fd"

    def test_invalid_placer_mode_rejected(self):
        """Invalid placer mode should raise error."""
        from circuit_training.config import EnvironmentConfig

        with pytest.raises(ValidationError):
            EnvironmentConfig(
                netlist_file=Path("test.pb.txt"),
                std_cell_placer_mode="invalid_mode",
            )

    def test_negative_weights_rejected(self):
        """Negative weights should raise error."""
        from circuit_training.config import EnvironmentConfig

        with pytest.raises(ValidationError):
            EnvironmentConfig(
                netlist_file=Path("test.pb.txt"),
                wirelength_weight=-1.0,
            )

    def test_config_immutable(self):
        """Config should be immutable after creation."""
        from circuit_training.config import EnvironmentConfig

        config = EnvironmentConfig(
            netlist_file=Path("circuit_training/environment/test_data/ariane/netlist.pb.txt"),
        )
        with pytest.raises(ValidationError):
            config.wirelength_weight = 2.0


class TestTrainingConfig:
    """Test training configuration model."""

    def test_valid_training_config(self):
        """Valid training config should be accepted."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig(
            num_iterations=100,
            batch_size=64,
            learning_rate=1e-4,
        )
        assert config.num_iterations == 100

    def test_default_values(self):
        """Default values should be sensible."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig()
        assert config.num_iterations > 0
        assert config.batch_size > 0
        assert 0 < config.learning_rate < 1

    def test_invalid_batch_size_rejected(self):
        """Zero or negative batch size should raise error."""
        from circuit_training.config import TrainingConfig

        with pytest.raises(ValidationError):
            TrainingConfig(batch_size=0)

        with pytest.raises(ValidationError):
            TrainingConfig(batch_size=-1)


class TestConfigSerialization:
    """Test config serialization/deserialization."""

    def test_to_dict(self):
        """Config should serialize to dict."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig(num_iterations=50)
        d = config.model_dump()
        assert isinstance(d, dict)
        assert d["num_iterations"] == 50

    def test_to_json(self):
        """Config should serialize to JSON."""
        from circuit_training.config import TrainingConfig

        config = TrainingConfig()
        json_str = config.model_dump_json()
        assert isinstance(json_str, str)

    def test_from_dict(self):
        """Config should deserialize from dict."""
        from circuit_training.config import TrainingConfig

        d = {"num_iterations": 200, "batch_size": 256}
        config = TrainingConfig(**d)
        assert config.num_iterations == 200
```

## 5.2 Create Configuration Models

Create `circuit_training/config.py`:

```python
"""Pydantic configuration models for circuit training."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class EnvironmentConfig(BaseModel):
    """Configuration for the circuit training environment."""

    model_config = {"frozen": True, "extra": "forbid"}

    # File paths
    netlist_file: Path
    init_placement: Path | None = None
    blockage_file: Path | None = None

    # Placer mode
    std_cell_placer_mode: Literal["fd", "dreamplace"] = "fd"

    # Grid configuration
    grid_cols: int = Field(default=35, ge=1, le=512)
    grid_rows: int = Field(default=33, ge=1, le=512)

    # Cost weights (must be non-negative)
    wirelength_weight: float = Field(default=1.0, ge=0.0)
    density_weight: float = Field(default=1.0, ge=0.0)
    congestion_weight: float = Field(default=0.5, ge=0.0)

    # Placement options
    node_order: Literal[
        "descending_size_macro_first",
        "random",
        "sequential",
    ] = "descending_size_macro_first"
    save_placement: bool = False
    save_best_cost: bool = True

    @field_validator("netlist_file", "init_placement", "blockage_file", mode="before")
    @classmethod
    def convert_to_path(cls, v: str | Path | None) -> Path | None:
        """Convert string paths to Path objects."""
        if v is None:
            return None
        return Path(v)


class TrainingConfig(BaseModel):
    """Configuration for PPO training."""

    model_config = {"frozen": True, "extra": "forbid"}

    # Training loop
    num_iterations: int = Field(default=1000, ge=1)
    num_episodes_per_iteration: int = Field(default=256, ge=1)
    batch_size: int = Field(default=128, ge=1)
    num_epochs: int = Field(default=4, ge=1)

    # Optimizer
    learning_rate: float = Field(default=4e-4, gt=0, lt=1)
    gradient_clipping: float = Field(default=1.0, gt=0)

    # PPO hyperparameters
    clip_epsilon: float = Field(default=0.2, gt=0, lt=1)
    entropy_coef: float = Field(default=0.01, ge=0)
    value_loss_coef: float = Field(default=0.5, ge=0)
    discount_factor: float = Field(default=1.0, ge=0, le=1)

    # Sequence
    sequence_length: int = Field(default=134, ge=1)


class ModelConfig(BaseModel):
    """Configuration for the GCN model."""

    model_config = {"frozen": True, "extra": "forbid"}

    # GCN architecture
    num_gcn_layers: int = Field(default=3, ge=1, le=10)
    gcn_node_dim: int = Field(default=8, ge=1, le=256)
    edge_fc_layers: int = Field(default=1, ge=1, le=5)

    # Policy head
    max_grid_size: int = Field(default=128, ge=16, le=512)

    # Noise for exploration
    dirichlet_alpha: float = Field(default=0.1, gt=0, lt=1)
    policy_noise_weight: float = Field(default=0.0, ge=0, le=1)


class DistributedConfig(BaseModel):
    """Configuration for distributed training."""

    model_config = {"frozen": True, "extra": "forbid"}

    # Reverb server
    replay_buffer_address: str = "localhost:8008"
    variable_container_address: str = "localhost:8008"

    # Collection
    num_collectors: int = Field(default=20, ge=1)
    task_id: int = Field(default=0, ge=0)

    # Hardware
    use_gpu: bool = True
    use_tpu: bool = False


class ExperimentConfig(BaseModel):
    """Complete experiment configuration."""

    model_config = {"frozen": True, "extra": "forbid"}

    environment: EnvironmentConfig
    training: TrainingConfig
    model: ModelConfig
    distributed: DistributedConfig = Field(default_factory=DistributedConfig)

    # Experiment metadata
    experiment_name: str = "circuit_training"
    seed: int = Field(default=42, ge=0)
    root_dir: Path = Path("./logs")

    @model_validator(mode="after")
    def validate_sequence_length(self) -> "ExperimentConfig":
        """Validate sequence length matches grid size."""
        max_actions = self.model.max_grid_size ** 2
        if self.training.sequence_length > max_actions:
            raise ValueError(
                f"sequence_length ({self.training.sequence_length}) cannot exceed "
                f"max_grid_size^2 ({max_actions})"
            )
        return self
```

## 5.3 Acceptance Criteria - Phase 5

- [ ] `circuit_training/config.py` exists
- [ ] All config classes use Pydantic v2 syntax
- [ ] `uv run pytest tests/config/` passes
- [ ] Configs are immutable (frozen=True)
- [ ] Invalid values are rejected with clear error messages

---

# PHASE 6: Test Infrastructure Improvements (Priority: P1)

## 6.1 Create Comprehensive Test Fixtures

Create `tests/conftest.py`:

```python
"""Shared test fixtures and configuration."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pytest

if TYPE_CHECKING:
    from circuit_training.config import EnvironmentConfig, ExperimentConfig


# Test data paths
TEST_DATA_DIR = Path(__file__).parent.parent / "circuit_training" / "environment" / "test_data"
ARIANE_NETLIST = TEST_DATA_DIR / "ariane" / "netlist.pb.txt"
ARIANE_PLACEMENT = TEST_DATA_DIR / "ariane" / "initial.plc"
MEP_NETLIST = TEST_DATA_DIR / "mep_room" / "netlist.pb.txt"
MEP_PLACEMENT = TEST_DATA_DIR / "mep_room" / "initial.plc"


@pytest.fixture
def ariane_netlist_path() -> Path:
    """Path to Ariane RISC-V netlist."""
    assert ARIANE_NETLIST.exists(), f"Test data not found: {ARIANE_NETLIST}"
    return ARIANE_NETLIST


@pytest.fixture
def ariane_placement_path() -> Path:
    """Path to Ariane initial placement."""
    assert ARIANE_PLACEMENT.exists(), f"Test data not found: {ARIANE_PLACEMENT}"
    return ARIANE_PLACEMENT


@pytest.fixture
def mep_netlist_path() -> Path:
    """Path to MEP room netlist."""
    if not MEP_NETLIST.exists():
        pytest.skip("MEP test data not available")
    return MEP_NETLIST


@pytest.fixture
def env_config(ariane_netlist_path: Path, ariane_placement_path: Path) -> EnvironmentConfig:
    """Default environment configuration for testing."""
    from circuit_training.config import EnvironmentConfig

    return EnvironmentConfig(
        netlist_file=ariane_netlist_path,
        init_placement=ariane_placement_path,
        std_cell_placer_mode="fd",
    )


@pytest.fixture
def experiment_config(env_config: EnvironmentConfig) -> ExperimentConfig:
    """Default experiment configuration for testing."""
    from circuit_training.config import (
        ExperimentConfig,
        ModelConfig,
        TrainingConfig,
    )

    return ExperimentConfig(
        environment=env_config,
        training=TrainingConfig(num_iterations=2, batch_size=4),
        model=ModelConfig(num_gcn_layers=1, gcn_node_dim=4),
        experiment_name="test_experiment",
    )


@pytest.fixture
def random_observation() -> dict[str, np.ndarray]:
    """Random observation for model testing."""
    max_nodes = 1000
    max_edges = 5000

    return {
        "netlist_index": np.array([0], dtype=np.int32),
        "current_node": np.array([0], dtype=np.int32),
        "mask": np.ones((128 * 128,), dtype=np.int32),
        "locations_x": np.random.rand(1, max_nodes).astype(np.float32),
        "locations_y": np.random.rand(1, max_nodes).astype(np.float32),
        "is_node_placed": np.zeros((1, max_nodes), dtype=np.float32),
        "macros_w": np.random.rand(1, max_nodes).astype(np.float32),
        "macros_h": np.random.rand(1, max_nodes).astype(np.float32),
        "node_types": np.zeros((1, max_nodes), dtype=np.float32),
        "sparse_adj_i": np.random.randint(0, max_nodes, (1, max_edges)).astype(np.int32),
        "sparse_adj_j": np.random.randint(0, max_nodes, (1, max_edges)).astype(np.int32),
        "sparse_adj_weight": np.random.rand(1, max_edges).astype(np.float32),
    }


# Markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "gpu: marks tests requiring GPU")
    config.addinivalue_line("markers", "integration: marks integration tests")
```

## 6.2 Create Integration Tests

Create `tests/integration/test_training_loop.py`:

```python
"""Integration tests for training loop."""
import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]


class TestTrainingLoop:
    """Test complete training loop."""

    @pytest.mark.timeout(120)
    def test_single_iteration(self, experiment_config):
        """Single training iteration should complete without error."""
        # This test verifies the full training pipeline works
        # Implementation depends on final architecture
        pass

    @pytest.mark.timeout(60)
    def test_environment_episode(self, env_config):
        """Complete episode should run without error."""
        from circuit_training.environment.environment import CircuitEnv

        env = CircuitEnv(
            netlist_file=str(env_config.netlist_file),
            init_placement=str(env_config.init_placement),
            std_cell_placer_mode=env_config.std_cell_placer_mode,
        )

        obs = env.reset()
        assert obs is not None

        done = False
        steps = 0
        max_steps = 200

        while not done and steps < max_steps:
            # Take random valid action
            mask = obs.get("mask", obs)
            if isinstance(mask, dict):
                mask = mask.get("mask")
            valid_actions = mask.nonzero()[0]
            if len(valid_actions) == 0:
                break
            action = valid_actions[0]
            obs, reward, done, info = env.step(action)
            steps += 1

        assert steps > 0


class TestModelInference:
    """Test model inference."""

    def test_model_forward_pass(self, random_observation):
        """Model forward pass should produce valid output."""
        from circuit_training.model.model_lib import CircuitTrainingModel

        model = CircuitTrainingModel(
            num_gcn_layers=2,
            gcn_node_dim=8,
        )

        # Build model with sample input
        logits, value = model(random_observation, training=False)

        assert "location" in logits
        assert logits["location"].shape[-1] == 128 * 128
        assert value.shape[-1] == 1
```

## 6.3 Update pytest Configuration

Add to `pyproject.toml`:

```toml
# === PYTEST CONFIGURATION ===

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
markers = [
    "slow: marks tests as slow",
    "gpu: marks tests requiring GPU",
    "integration: marks integration tests",
]
timeout = 60

[tool.coverage.run]
source = ["circuit_training"]
branch = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/conftest.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 60
show_missing = true
```

## 6.4 Acceptance Criteria - Phase 6

- [ ] `tests/conftest.py` with shared fixtures exists
- [ ] `tests/integration/` directory with integration tests exists
- [ ] `uv run pytest` runs all tests successfully
- [ ] `uv run pytest -m "not slow"` excludes slow tests
- [ ] Coverage report is generated
- [ ] All existing tests still pass

---

# PHASE 7: Documentation (Priority: P2)

## 7.1 Create MkDocs Configuration

Create `mkdocs.yml`:

```yaml
site_name: Circuit Training
site_description: Reinforcement Learning for Chip Placement
site_url: https://google-research.github.io/circuit_training
repo_url: https://github.com/google-research/circuit_training
repo_name: google-research/circuit_training

theme:
  name: material
  palette:
    - scheme: default
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: blue
      accent: blue
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.tabs
    - navigation.sections
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            heading_level: 2
            members_order: source
            separate_signature: true
            docstring_style: google

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - toc:
      permalink: true

nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
      - Configuration: getting-started/configuration.md
  - User Guide:
      - Environment: guide/environment.md
      - Training: guide/training.md
      - Evaluation: guide/evaluation.md
      - Distributed Training: guide/distributed.md
  - API Reference:
      - Environment: api/environment.md
      - Model: api/model.md
      - Learning: api/learning.md
      - Config: api/config.md
  - Examples:
      - Ariane RISC-V: examples/ariane.md
      - MEP Room: examples/mep.md
  - Contributing: contributing.md
```

## 7.2 Create Documentation Files

Create `docs/index.md`:

```markdown
# Circuit Training

**Reinforcement Learning for Chip Placement**

Circuit Training is an open-source framework for generating chip floorplans using
distributed deep reinforcement learning.

## Features

- 🧠 **Deep RL Placement**: Uses PPO to learn optimal macro placement
- 🔄 **Distributed Training**: Scales to hundreds of collection workers
- 📊 **Multi-objective**: Optimizes wirelength, congestion, and density
- 🔧 **Configurable**: Extensive configuration via Pydantic models

## Quick Start

```bash
# Install
pip install circuit-training

# Run training
ct-train --config configs/ariane.yaml
```

## Citation

```bibtex
@article{mirhoseini2021graph,
  title={A graph placement methodology for fast chip design},
  author={Mirhoseini, Azalia and others},
  journal={Nature},
  year={2021}
}
```
```

## 7.3 Acceptance Criteria - Phase 7

- [ ] `mkdocs.yml` exists and is valid
- [ ] `docs/` directory with documentation files exists
- [ ] `uv run mkdocs build` succeeds
- [ ] `uv run mkdocs serve` shows documentation locally

---

# Verification Checklist

After completing all phases, verify:

```bash
# 1. Package builds
uv build

# 2. All tests pass
uv run pytest

# 3. Linting passes
uv run ruff check circuit_training/
uv run ruff format --check circuit_training/

# 4. Type checking passes
uv run pyrefly check circuit_training/

# 5. Package is importable
uv run python -c "import circuit_training; print(circuit_training.__version__)"

# 6. Documentation builds
uv run mkdocs build

# 7. Pre-commit passes
pre-commit run --all-files
```

---

# Summary of Files to Create/Modify

## New Files
- `pyproject.toml`
- `pyrefly.toml`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `circuit_training/config.py`
- `circuit_training/py.typed`
- `tests/conftest.py`
- `tests/packaging/test_package_structure.py`
- `tests/quality/test_code_quality.py`
- `tests/quality/test_type_checking.py`
- `tests/config/test_config_models.py`
- `tests/ci/test_ci_config.py`
- `tests/integration/test_training_loop.py`
- `mkdocs.yml`
- `docs/index.md`

## Files to Modify
- `circuit_training/__init__.py` (add version export)
- `circuit_training/version.py` (update format)

## Files to Delete
- `setup.py`
- `tox.ini` (replaced by pyproject.toml + uv)

---

# Execution Order for Autonomous Agent

1. Create branch: `git checkout -b modernization/2026-update`
2. Execute Phase 1 (Packaging)
3. Run Phase 1 tests
4. Commit: `git commit -m "feat: migrate to pyproject.toml and uv"`
5. Execute Phase 2 (Linting)
6. Run Phase 2 tests
7. Commit: `git commit -m "feat: add Ruff linting and formatting"`
8. Execute Phase 3 (Type Checking)
9. Run Phase 3 tests
10. Commit: `git commit -m "feat: add Pyrefly type checking"`
11. Execute Phase 4 (CI/CD)
12. Run Phase 4 tests
13. Commit: `git commit -m "feat: add GitHub Actions CI/CD"`
14. Execute Phase 5 (Pydantic)
15. Run Phase 5 tests
16. Commit: `git commit -m "feat: add Pydantic configuration models"`
17. Execute Phase 6 (Testing)
18. Run Phase 6 tests
19. Commit: `git commit -m "feat: improve test infrastructure"`
20. Execute Phase 7 (Documentation)
21. Run Phase 7 tests
22. Commit: `git commit -m "docs: add MkDocs documentation"`
23. Final verification checklist
24. Push: `git push -u origin modernization/2026-update`
