from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ExpenseClaim(Base):
    __tablename__ = "expense_claims"

    __table_args__ = (
        CheckConstraint(
            "amount_paise > 0 AND amount_paise <= 10000000",
            name="ck_claim_amount",
        ),
        CheckConstraint(
            "category IN ('meal', 'travel', 'equipment')",
            name="ck_claim_category",
        ),
        CheckConstraint("currency = 'INR'", name="ck_claim_currency"),
        CheckConstraint(
            "status IN ('draft', 'submitted', 'approved', 'rejected')",
            name="ck_claim_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(20))
    amount_paise: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), server_default="INR")
    status: Mapped[str] = mapped_column(String(20), server_default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
    )