"""Tests to verify type checking passes."""

import subprocess

import pytest


class TestPyreflyTypeChecking:
    """Verify Pyrefly type checking passes."""

    @pytest.mark.slow
    def test_pyrefly_check_passes(self):
        """Core modules should pass type checking."""
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", "circuit_training/"],
            check=False,
            capture_output=True,
            text=True,
        )
        # Allow warnings but no errors
        assert result.returncode == 0, (
            f"Pyrefly failed:\n{result.stdout}\n{result.stderr}"
        )

    @pytest.mark.slow
    def test_environment_module_typed(self):
        """Environment module should be fully typed."""
        result = subprocess.run(
            [
                "uv",
                "run",
                "pyrefly",
                "check",
                "circuit_training/environment/environment.py",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    @pytest.mark.slow
    def test_model_module_typed(self):
        """Model module should be fully typed."""
        result = subprocess.run(
            ["uv", "run", "pyrefly", "check", "circuit_training/model/model_lib.py"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
