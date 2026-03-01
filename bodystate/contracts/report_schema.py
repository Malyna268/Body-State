"""Schemas for forecast or report outputs."""

from __future__ import annotations

from pydantic import BaseModel


class ReportEntry(BaseModel):
    timestamp: str
    values: dict[str, float]


class ForecastReport(BaseModel):
    entries: list[ReportEntry]
    summary: dict[str, float]
