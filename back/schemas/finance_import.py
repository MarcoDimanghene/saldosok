from typing import Any

from pydantic import BaseModel, Field


class FinanceImportRequest(BaseModel):
    companies: list[dict[str, Any]] = Field(default_factory=list)
    sales: list[dict[str, Any]] = Field(default_factory=list)
    purchases: list[dict[str, Any]] = Field(default_factory=list)
    collections: list[dict[str, Any]] = Field(default_factory=list)
    payments: list[dict[str, Any]] = Field(default_factory=list)
