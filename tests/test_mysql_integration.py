import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import get_engine
from app.main import app
from app.models import ExpenseClaim


@pytest.mark.skipif(
    os.getenv("RUN_MYSQL_TESTS") != "1",
    reason="MySQL integration tests are not enabled.",
)
def test_mysql_create_and_retrieve_claim():
    engine = get_engine()

    # Run only against the dedicated CI database.
    assert engine.url.database == "expenseflow_ci"

    with TestClient(app) as client:
        created = client.post(
            "/api/v1/claims",
            json={
                "category": "meal",
                "amount_paise": 75000,
                "currency": "INR",
            },
        )

        assert created.status_code == 201
        claim_id = created.json()["id"]

        # Verify that MySQL stored the record.
        with Session(engine) as session:
            saved = session.get(ExpenseClaim, claim_id)
            assert saved is not None
            assert saved.amount_paise == 75000
            assert saved.status == "draft"

        fetched = client.get(f"/api/v1/claims/{claim_id}")

        assert fetched.status_code == 200
        assert fetched.json() == created.json()