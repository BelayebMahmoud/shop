"""Shared test setup. No database here: unit tests must run without one (F.I.R.S.T.)."""

import os

os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://shop:shop@localhost:5433/shop_test")
os.environ.setdefault("JWT_SECRET", "test-only-secret-0123456789abcdef0123456789")


def pytest_collection_modifyitems(items):
    """Write each test's requirement IDs into the JUnit report as <property name="req" value="BR-04"/>."""
    for item in items:
        for marker in item.iter_markers("req"):
            for req in marker.args:
                item.user_properties.append(("req", req))
