"""TA-28 (QR-CO-02): Schemathesis generates requests from /openapi.json and runs all its checks.

The app is called in-process (ASGI) on a freshly rebuilt test database. Every request carries a token so generated
data reaches the business logic instead of stopping at 401: the CUSTOMER's for the order and cancel operations,
the ADMIN's for everything else. Any 500 or any response outside the contract fails the test.

Generation uses valid UTF-8 text (codec utf-8): lone UTF-16 surrogates are not Unicode text, rejecting them is right.
One justified exclusion, recorded in docs/anomalies.md (ANO-06): `positive_data_acceptance` is skipped for the two
operations whose cross-field rules JSON Schema cannot express (min_price_cents <= max_price_cents, Q-05;
date_from <= date_to, Q-04). All other checks still run on them.
"""

import pytest
import schemathesis
from hypothesis import HealthCheck, settings
from schemathesis.config import SchemathesisConfig
from schemathesis.specs.openapi.checks import positive_data_acceptance

from app.core.security import create_access_token
from app.main import app

config = SchemathesisConfig()
config.projects.default.generation.update(codec="utf-8")
schema = schemathesis.openapi.from_asgi("/openapi.json", app, config=config)
ADMIN_ID = 2  # admin@example.com, seeded by db/migrations/003 (the only ADMIN at the start of each test)
CUSTOMER_ID = 1  # demo@example.com, seeded by db/migrations/002
# Operations only a CUSTOMER may call: fuzz them with a customer token so the body reaches validation and rules.
CUSTOMER_OPERATIONS = {"POST /api/orders", "POST /api/orders/{order_id}/cancel"}
CROSS_FIELD_RULES = {"GET /api/products", "GET /api/dashboard"}


@pytest.fixture(autouse=True)
def _isolated_database(fresh_db):
    yield


@pytest.mark.req("QR-CO-02")
@pytest.mark.case("TA-28")
@schema.parametrize()
@settings(max_examples=40, deadline=None, suppress_health_check=list(HealthCheck))
def test_api_respects_its_contract(case):
    excluded = [positive_data_acceptance] if f"{case.method} {case.path}" in CROSS_FIELD_RULES else []
    actor = CUSTOMER_ID if f"{case.method} {case.path}" in CUSTOMER_OPERATIONS else ADMIN_ID
    headers = {"Authorization": f"Bearer {create_access_token(actor)}"}
    case.call_and_validate(headers=headers, excluded_checks=excluded)
