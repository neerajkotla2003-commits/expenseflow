from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class Category(StrEnum):
    MEAL = "meal"
    TRAVEL = "travel"
    EQUIPMENT = "equipment"


class PolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    amount_paise: int = Field(strict=True, gt=0, le=10_000_000)
    currency: Literal["INR"] = "INR"


class PolicyResult(BaseModel):
    policy_version: str = "demo-v1"
    eligible: bool
    required_approver: Literal["manager", "finance"] | None
    reason: str

class ClaimCreate(PolicyRequest):
    pass


class ClaimRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: Category
    amount_paise: int
    currency: Literal["INR"]
    status: Literal["draft", "submitted", "approved", "rejected"]
    created_at: datetime