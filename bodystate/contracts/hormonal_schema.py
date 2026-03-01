"""Pydantic schemas for hormonal data exchange."""

from __future__ import annotations

from pydantic import BaseModel


class HormonalInput(BaseModel):
    hormone: str
    level: float


class HormonalOutput(BaseModel):
    status: str
    updated_levels: dict[str, float]
