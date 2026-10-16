from fastapi import FastAPI

from app.policy import evaluate_policy
from app.schemas import PolicyRequest, PolicyResult

app = FastAPI(title="ExpenseFlow", version="0.1.0")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/api/v1/policy/check", response_model=PolicyResult)
def check_policy(expense: PolicyRequest):
    # Preview only: creates no claim, grants no permission, approves no money.
    return evaluate_policy(expense)
