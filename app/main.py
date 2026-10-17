from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import ExpenseClaim
from app.policy import evaluate_policy
from app.schemas import (
    ClaimCreate,
    ClaimRead,
    PolicyRequest,
    PolicyResult,
)
from fastapi import Depends, FastAPI, HTTPException, Path

app = FastAPI(title="ExpenseFlow", version="0.2.0")


@app.get("/healthz")
def health():
    return {"status": "ok"}


@app.post("/api/v1/policy/check", response_model=PolicyResult)
def check_policy(expense: PolicyRequest):
    return evaluate_policy(expense)


@app.post("/api/v1/claims", response_model=ClaimRead, status_code=201)
def create_claim(
    expense: ClaimCreate,
    session: Annotated[Session, Depends(get_session)],
):
    claim = ExpenseClaim(
        category=expense.category.value,
        amount_paise=expense.amount_paise,
        currency=expense.currency,
        status="draft",
    )

    try:
        with session.begin():
            session.add(claim)
            session.flush()
            session.refresh(claim)
            result = ClaimRead.model_validate(claim)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not save the claim. Please try again later.",
        ) from exc

    return result

@app.get("/api/v1/claims/{claim_id}", response_model=ClaimRead)
def get_claim(
    claim_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
):
    try:
        claim = session.get(ExpenseClaim, claim_id)

        if claim is None:
            raise HTTPException(
                status_code=404,
                detail="Claim not found.",
            )

        return ClaimRead.model_validate(claim)

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve the claim. Please try again later.",
        ) from exc