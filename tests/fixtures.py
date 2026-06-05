"""Test fixtures to make life easier."""

from pathlib import Path

import pytest


@pytest.fixture(name="repo_path")
def fixture_repo_path(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath


@pytest.fixture(name="tests_base_path")
def fixture_tests_base_path(request: pytest.FixtureRequest) -> Path:
    return request.config.rootpath / "tests"


@pytest.fixture(name="data_path")
def fixture_data_path(tests_base_path: Path) -> Path:
    return tests_base_path / "data"
