"""Tests to verify code quality standards."""

import subprocess


class TestRuffLinting:
    """Verify Ruff linting passes."""

    def test_ruff_check_passes(self):
        """All code should pass Ruff linting."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "circuit_training/"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Ruff check failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_ruff_format_check(self):
        """All code should be formatted with Ruff."""
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "circuit_training/"],
            check=False,
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
            check=False,
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
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
