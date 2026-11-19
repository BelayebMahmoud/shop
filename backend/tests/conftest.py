"""Shared test setup. No database here: unit tests must run without one (F.I.R.S.T.)."""

import os

os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://shop:shop@localhost:5433/shop_test")
os.environ.setdefault("JWT_SECRET", "test-only-secret-0123456789abcdef0123456789")

pytest_plugins = ["tests.db_fixtures"]


def pytest_collection_modifyitems(items):
    """Write requirement IDs (and explicit case IDs) into the JUnit report as <property name="req" .../>."""
    for item in items:
        for marker in item.iter_markers("req"):
            for req in marker.args:
                item.user_properties.append(("req", req))
        for marker in item.iter_markers("case"):  # case ID when the pytest id cannot carry it (generated tests)
            item.user_properties.append(("case", marker.args[0]))
