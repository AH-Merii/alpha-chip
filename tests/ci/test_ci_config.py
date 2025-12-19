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
        # YAML parses 'on' as True (boolean), need to check both
        on_triggers = ci_workflow.get("on", ci_workflow.get(True, {}))
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
