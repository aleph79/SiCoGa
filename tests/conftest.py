"""Global pytest fixtures."""

import pytest


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Allow all tests to use the DB without re-declaring `db` fixture."""
    pass
