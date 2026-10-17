import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.models import ExpenseClaim


@pytest.fixture
def claim_api():
    # A fresh temporary database for each test case.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)

    def override_get_session():
        with Session(test_engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as client:
            yield client, test_engine
    finally:
        app.dependency_overrides.pop(get_session, None)
        test_engine.dispose()


def test_create_claim_saves_draft(claim_api):
    client, test_engine = claim_api

    response = client.post(
        "/api/v1/claims",
        json={
            "category": "meal",
            "amount_paise": 75000,
            "currency": "INR",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"

    # Check storage separately from the API response.
    with Session(test_engine) as session:
        saved = session.get(ExpenseClaim, data["id"])
        assert saved is not None
        assert saved.category == "meal"
        assert saved.amount_paise == 75000
        assert saved.currency == "INR"
        assert saved.status == "draft"


@pytest.mark.parametrize(
    "changes",
    [
        {"amount_paise": -1},
        {"status": "approved"},
    ],
)
def test_invalid_claim_is_not_saved(claim_api, changes):
    client, test_engine = claim_api

    payload = {
        "category": "meal",
        "amount_paise": 75000,
        "currency": "INR",
    }
    payload.update(changes)

    response = client.post("/api/v1/claims", json=payload)

    assert response.status_code == 422

    with Session(test_engine) as session:
        count = session.scalar(
            select(func.count()).select_from(ExpenseClaim)
        )
        assert count == 0
        
def test_get_saved_claim(claim_api):
    client, _ = claim_api

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
    response = client.get(f"/api/v1/claims/{claim_id}")

    assert response.status_code == 200
    assert response.json() == created.json()


def test_get_missing_claim(claim_api):
    client, _ = claim_api

    response = client.get("/api/v1/claims/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Claim not found."


def test_get_claim_requires_positive_id(claim_api):
    client, _ = claim_api

    response = client.get("/api/v1/claims/0")

    assert response.status_code == 422