import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/healthz").json() == {"status": "ok"}


@pytest.mark.parametrize(
    "category,amount,eligible,approver",
    [
        ("meal", 1, True, "manager"),
        ("meal", 100_000, True, "manager"),
        ("meal", 100_001, False, None),
        ("travel", 500_000, True, "manager"),
        ("travel", 500_001, False, None),
        ("equipment", 1_000_000, True, "manager"),
        ("equipment", 1_000_001, True, "finance"),
        ("equipment", 2_000_000, True, "finance"),
        ("equipment", 2_000_001, False, None),
    ],
)
def test_policy_boundaries(category, amount, eligible, approver):
    response = client.post(
        "/api/v1/policy/check",
        json={"category": category, "amount_paise": amount},
    )
    assert response.status_code == 200
    assert response.json()["eligible"] is eligible
    assert response.json()["required_approver"] == approver


@pytest.mark.parametrize(
    "changes",
    [
        {"amount_paise": 0},
        {"amount_paise": -1},
        {"amount_paise": 1.5},
        {"amount_paise": True},
        {"amount_paise": "500"},
        {"amount_paise": 10_000_001},
        {"category": "unknown"},
        {"currency": "USD"},
        {"role": "finance"},
    ],
)
def test_invalid_requests(changes):
    payload = {"category": "meal", "amount_paise": 500}
    payload.update(changes)
    assert client.post("/api/v1/policy/check", json=payload).status_code == 422
