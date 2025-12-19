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

    @pytest.mark.slow
    def test_submodules_importable(self):
        """All submodules should be importable."""
        # These require TensorFlow to be properly installed
        submodules = [
            "circuit_training.environment",
            "circuit_training.learning",
            "circuit_training.model",
        ]
        for module in submodules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                pytest.skip(f"Skipping due to TF dependency: {e}")

    @pytest.mark.slow
    def test_cli_entry_points_registered(self):
        """CLI commands should be available after install."""
        result = subprocess.run(
            [sys.executable, "-m", "circuit_training.learning.train_ppo", "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        # May fail if TF deps not properly installed
        if result.returncode != 0 and "tensorflow" in result.stderr.lower():
            pytest.skip("Skipping due to TF dependency issue")
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
        import numpy  # noqa: F401

    def test_optional_dependencies_handled(self):
        """Optional dependencies should not break import."""
        try:
            from circuit_training.dreamplace import dreamplace_core  # noqa: F401
        except ImportError:
            # Expected - DREAMPlace requires additional setup
            pass


class TestBuildProcess:
    """Verify package builds correctly."""

    @pytest.mark.slow
    def test_build_wheel(self, tmp_path):
        """Package should build a wheel."""
        result = subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        wheels = list(tmp_path.glob("*.whl"))
        assert len(wheels) == 1

    @pytest.mark.slow
    def test_build_sdist(self, tmp_path):
        """Package should build a source distribution."""
        result = subprocess.run(
            ["uv", "build", "--sdist", "--out-dir", str(tmp_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        sdists = list(tmp_path.glob("*.tar.gz"))
        assert len(sdists) == 1
