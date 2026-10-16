from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
