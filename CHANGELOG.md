# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern `pyproject.toml` packaging with uv support
- Ruff linting and formatting configuration
- Pyrefly type checking configuration
- GitHub Actions CI/CD workflows
- Semantic versioning with conventional commits
- Pydantic configuration models for type-safe config
- MkDocs documentation setup
- Comprehensive test infrastructure

### Changed
- Migrated from `setup.py` to `pyproject.toml`
- Updated Python version requirement to 3.11+
- Replaced tox with uv for testing

### Removed
- Legacy `setup.py` file
- Legacy `tox.ini` file
